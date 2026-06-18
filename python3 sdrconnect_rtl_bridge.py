import asyncio
import json
import numpy as np
import websockets
from collections import deque
import contextlib

# --- KONFIG ---
SDRCONNECT_WS_URL = "ws://127.0.0.1:5454"
RTL_TCP_HOST = "0.0.0.0"
RTL_TCP_PORT = 5555

SAMPLE_RATE = 1_000_000
DEFAULT_CENTER_FREQ_HZ = 136_725_000

MAX_BUFFER_BYTES = 2_000_000
START_RETRY_DELAY = 0.5
NO_DATA_TIMEOUT = 3.0
# ----------------

iq_buffer = deque()
buffer_lock = asyncio.Lock()
clients = set()
tuning_queue: asyncio.Queue[int] = asyncio.Queue()
current_center_freq = DEFAULT_CENTER_FREQ_HZ


# ---------------------------------------------------------
# Antennenlogik
# ---------------------------------------------------------
def choose_antenna(freq_hz):
    if freq_hz < 30_000_000:
        return "Antenna C"   # HF/VLF
    else:
        return "Antenna A"   # VHF/UHF


# ---------------------------------------------------------
# WebSocket Helper
# ---------------------------------------------------------
async def send_cmd(ws, evt, prop, val, device="primary"):
    await ws.send(json.dumps({
        "event_type": evt,
        "property": prop,
        "value": val,
        "device": device
    }))


# ---------------------------------------------------------
# SDRconnect Startsequenz
# ---------------------------------------------------------
async def start_sdr(ws):
    global current_center_freq
    print("[*] Sende Startsequenz an SDRconnect…")

    await send_cmd(ws, "selected_device", "", "0")
    await asyncio.sleep(START_RETRY_DELAY)

    await send_cmd(ws, "device_stream_enable", "", "true")
    await asyncio.sleep(START_RETRY_DELAY)

    await send_cmd(ws, "set_property", "started", "true")
    await asyncio.sleep(START_RETRY_DELAY)

    # Initiale Mitte setzen
    await send_cmd(ws, "set_property", "device_center_frequency", str(current_center_freq))
    await send_cmd(ws, "set_property", "device_vfo_frequency", str(current_center_freq))
    print(f"[+] Initiale Mitte: {current_center_freq/1e6:.6f} MHz")
    await asyncio.sleep(START_RETRY_DELAY)

    # Initiale Antenne setzen
    antenna = choose_antenna(current_center_freq)
    await send_cmd(ws, "set_property", "active_antenna", antenna)
    print(f"[+] Initiale Antenne: {antenna}")
    await asyncio.sleep(START_RETRY_DELAY)

    await send_cmd(ws, "iq_stream_enable", "", "true")
    await asyncio.sleep(START_RETRY_DELAY)

    print("[+] Startsequenz abgeschlossen.")


# ---------------------------------------------------------
# IQ-Konvertierung
# ---------------------------------------------------------
def convert_iq(iq16: np.ndarray) -> np.ndarray:
    I = iq16[0::2].astype(np.float32) / 32768.0
    Q = iq16[1::2].astype(np.float32) / 32768.0

    I8 = ((I * 127.0) + 128.0).clip(0, 255).astype(np.uint8)
    Q8 = ((Q * 127.0) + 128.0).clip(0, 255).astype(np.uint8)

    iq8 = np.empty(I8.size + Q8.size, dtype=np.uint8)
    iq8[0::2] = I8
    iq8[1::2] = Q8
    return iq8


# ---------------------------------------------------------
# Tuning-Worker: RTL-TCP → SDRconnect
# ---------------------------------------------------------
async def tuning_worker(ws):
    global current_center_freq
    print("[*] Tuning-Worker gestartet…")

    while True:
        freq = await tuning_queue.get()
        current_center_freq = freq

        print(f"[TUNE] Neue Mitte: {freq/1e6:.6f} MHz")

        # Frequenz setzen
        await send_cmd(ws, "set_property", "device_center_frequency", str(freq))
        await send_cmd(ws, "set_property", "device_vfo_frequency", str(freq))

        # Antenne automatisch wählen
        antenna = choose_antenna(freq)
        print(f"[ANT] Schalte auf {antenna}")

        await send_cmd(ws, "set_property", "active_antenna", antenna)


# ---------------------------------------------------------
# SDRconnect IQ-Receiver
# ---------------------------------------------------------
async def sdrconnect_receiver():
    global iq_buffer, clients

    while True:
        try:
            print(f"[*] Verbinde mit SDRconnect: {SDRCONNECT_WS_URL}")
            async with websockets.connect(SDRCONNECT_WS_URL, max_size=2**24) as ws:
                print("[+] Mit SDRconnect verbunden.")

                # ⭐ Auto‑Reconnect: alle RTL‑TCP Clients hart trennen
                for c in list(clients):
                    try:
                        c.transport.abort()
                    except:
                        pass

                await start_sdr(ws)

                tuning_task = asyncio.create_task(tuning_worker(ws))
                last_data_time = asyncio.get_event_loop().time()

                try:
                    async for message in ws:
                        now = asyncio.get_event_loop().time()

                        if now - last_data_time > NO_DATA_TIMEOUT:
                            print("[!] 3s keine IQ-Daten → Neustart…")

                            # ⭐ Auto‑Reconnect: hart trennen
                            for c in list(clients):
                                try:
                                    c.transport.abort()
                                except:
                                    pass

                            break

                        if isinstance(message, bytes) and len(message) > 2:
                            if message[0:2] == b"\x02\x00":
                                last_data_time = now
                                iq16 = np.frombuffer(message[2:], dtype=np.int16)
                                iq8 = convert_iq(iq16)
                                data = iq8.tobytes()

                                async with buffer_lock:
                                    iq_buffer.append(data)
                                    total = sum(len(chunk) for chunk in iq_buffer)
                                    while total > MAX_BUFFER_BYTES and iq_buffer:
                                        removed = iq_buffer.popleft()
                                        total -= len(removed)

                        await asyncio.sleep(0.0001)

                finally:
                    tuning_task.cancel()
                    with contextlib.suppress(Exception):
                        await tuning_task

        except Exception as e:
            print(f"[!] SDRconnect-Verbindung verloren: {e}, neuer Versuch in 3s…")
            await asyncio.sleep(3)


# ---------------------------------------------------------
# RTL-TCP: IQ-Sender
# ---------------------------------------------------------
async def rtl_tcp_sender(writer):
    while True:
        chunk = None
        async with buffer_lock:
            if iq_buffer:
                chunk = iq_buffer.popleft()

        if chunk:
            writer.write(chunk)
            await writer.drain()
        else:
            await asyncio.sleep(0.001)


# ---------------------------------------------------------
# RTL-TCP: Control-Reader (Tuning)
# ---------------------------------------------------------
async def rtl_tcp_control(reader):
    while True:
        cmd = await reader.read(1)
        if not cmd:
            break

        c = cmd[0]

        if c == 0x01:  # Set frequency
            data = await reader.readexactly(4)
            freq = int.from_bytes(data, "big")
            await tuning_queue.put(freq)
        else:
            try:
                await reader.readexactly(4)
            except asyncio.IncompleteReadError:
                break


# ---------------------------------------------------------
# RTL-TCP Client Handler
# ---------------------------------------------------------
async def handle_client(reader, writer):
    global clients
    addr = writer.get_extra_info("peername")
    print(f"[+] Client verbunden: {addr}")
    clients.add(writer)

    try:
        # RTL‑TCP Header
        writer.write(b"RTL0" + (1).to_bytes(4, "big") + (0).to_bytes(4, "big"))
        await writer.drain()

        sender_task = asyncio.create_task(rtl_tcp_sender(writer))
        ctrl_task = asyncio.create_task(rtl_tcp_control(reader))

        done, pending = await asyncio.wait(
            {sender_task, ctrl_task},
            return_when=asyncio.FIRST_COMPLETED
        )

        for t in pending:
            t.cancel()
            with contextlib.suppress(Exception):
                await t

    except Exception:
        print(f"[-] Client getrennt (Fehler): {addr}")
    finally:
        clients.discard(writer)
        try:
            writer.transport.abort()
        except:
            pass
        print(f"[-] Client getrennt: {addr}")


# ---------------------------------------------------------
# RTL-TCP Server
# ---------------------------------------------------------
async def rtl_tcp_server():
    print(f"[*] Starte RTL‑TCP‑Server auf {RTL_TCP_HOST}:{RTL_TCP_PORT}…")
    server = await asyncio.start_server(handle_client, RTL_TCP_HOST, RTL_TCP_PORT)
    async with server:
        await server.serve_forever()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
async def main():
    await asyncio.gather(
        sdrconnect_receiver(),
        rtl_tcp_server()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Bridge beendet.")
