---
layout: page
title: "OpenWebRX+ Quickstart"
description: "Setup guide for using SDRconnect with OpenWebRX+ (Local + Docker)"
---

# OpenWebRX+ Quickstart Guide  
For the SDRconnect RTL‑TCP Bridge  
English + Deutsch  
Jekyll‑optimized — no screenshots.

Official OpenWebRX+ documentation:  
https://fms.komkon.org/OWRX/

---

# 🇬🇧 English — Quickstart

## 1. Add a new Receiver
Open OpenWebRX+ → Settings → Receivers → Add Receiver

Set:
- Mode: RTL‑TCP  
- Name: SDRconnect Bridge  
- Enabled: Yes  

---

## 2. Configure RTL‑TCP (Local Host)
If OpenWebRX+ runs directly on your machine:

Host:  
    127.0.0.1

Port:  
    5555

Receiver string:  
    rtl_tcp=127.0.0.1:5555

---

## 3. Configure RTL‑TCP (Docker Container)
If OpenWebRX+ runs inside Docker, it cannot access localhost.

Use:

Host:  
    host.docker.internal

Port:  
    5555

Receiver string:  
    rtl_tcp=host.docker.internal:5555

---

## 4. Create a Profile (Initial Frequency + Sample Rate + Center Frequency)

In OpenWebRX+ the **profile** defines how the receiver starts up and how the UI behaves.  
Important fields (see “Rig Control – Profile” in the official docs):

- Initial frequency  
- Sample rate  
- Center frequency  
- Step size / tuning step  
- Demodulator / mode defaults  

**The profile does not limit the tunable frequency range** — that comes from the SDR backend (here: SDRconnect).

### Recommended settings for the SDRconnect bridge

1. Go to **Settings → Profiles → Add Profile**  
2. Set **Sample rate** to the same value as SDRconnect and the bridge script  
   - Recommended:  
         Sample rate: 1 MHz  
         Script: SAMPLE_RATE = 1_000_000  
3. Set **Initial frequency** to a sensible default (e.g. a local FM, airband or ham band frequency)  
4. Set **Center frequency** so that the initial frequency lies well inside the visible spectrum  
   - For wideband use you can simply set center frequency = initial frequency  
5. Adjust step size / mode defaults as you like  
6. Save the profile and assign it to your RTL‑TCP receiver  

If the waterfall looks distorted or “tilted” → sample rate mismatch.

---

## 5. Test the Connection
1. Start SDRconnect  
2. Set sample rate to 1 MHz  
3. Start the bridge  
4. Open OpenWebRX+  
5. Select your RTL‑TCP receiver and the created profile  
6. Tune a frequency  
7. SDRconnect should follow immediately  

---

# ASCII Signal Flow Diagram

    SDR Hardware
         │
         ▼
    SDRconnect (WebSocket API)
         │ 16‑bit IQ
         ▼
    SDRconnect RTL‑TCP Bridge
         │ 8‑bit IQ
         ▼
    OpenWebRX+ (RTL‑TCP Input)
         │
         ▼
    Web UI (Waterfall + Audio)

---

# 🇩🇪 Deutsch — Schnellstart

## 1. Neuen Receiver hinzufügen
OpenWebRX+ → Einstellungen → Receiver → Add Receiver

Einstellungen:
- Modus: RTL‑TCP  
- Name: SDRconnect Bridge  
- Aktiviert: Ja  

---

## 2. RTL‑TCP konfigurieren (Lokaler Host)
Wenn OpenWebRX+ direkt auf dem Rechner läuft:

Host:  
    127.0.0.1

Port:  
    5555

Receiver‑String:  
    rtl_tcp=127.0.0.1:5555

---

## 3. RTL‑TCP konfigurieren (Docker Container)
Docker‑Container können nicht auf localhost zugreifen.

Daher:

Host:  
    host.docker.internal

Port:  
    5555

Receiver‑String:  
    rtl_tcp=host.docker.internal:5555

---

## 4. Profil anlegen (Initial Frequency + Sample‑Rate + Center Frequency)

Im Profil legst du fest, **wie der Empfänger startet** und wie sich die UI verhält.  
Wichtige Felder (siehe „Rig Control – Profile“ in der Originaldoku):

- Initial frequency (Startfrequenz)  
- Sample rate  
- Center frequency (Mittenfrequenz)  
- Schrittweite / Step size  
- Standard‑Modus / Demodulator  

**Das Profil begrenzt NICHT den Frequenzbereich** – der kommt vom SDR‑Backend (hier: SDRconnect).

### Empfohlene Einstellungen für die SDRconnect‑Bridge

1. Einstellungen → Profiles → Add Profile  
2. **Sample‑Rate** auf denselben Wert wie in SDRconnect und im Script setzen  
   - Empfehlung:  
         Sample‑Rate: 1 MHz  
         Script: SAMPLE_RATE = 1_000_000  
3. **Initial frequency** auf eine sinnvolle Startfrequenz setzen  
   (z. B. lokaler FM‑Sender, Airband, Amateurfunk‑Relais)  
4. **Center frequency** so wählen, dass die Startfrequenz gut im Spektrum liegt  
   - Für den Anfang kannst du Center frequency = Initial frequency setzen  
5. Schrittweite / Modus nach Wunsch einstellen  
6. Profil speichern und dem RTL‑TCP‑Receiver zuweisen  

Wenn der Wasserfall „schief“ oder verzerrt aussieht → Sample‑Rate stimmt nicht.

---

## 5. Verbindung testen
1. SDRconnect starten  
2. Sample‑Rate auf 1 MHz setzen  
3. Bridge starten  
4. OpenWebRX+ öffnen  
5. RTL‑TCP‑Receiver und Profil auswählen  
6. Frequenz ändern  
7. SDRconnect muss sofort folgen  

---

# ASCII Signalfluss‑Diagramm

    SDR Hardware
         │
         ▼
    SDRconnect (WebSocket‑API)
         │ 16‑bit IQ
         ▼
    SDRconnect RTL‑TCP Bridge
         │ 8‑bit IQ
         ▼
    OpenWebRX+ (RTL‑TCP Eingang)
         │
         ▼
    Web‑UI (Wasserfall + Audio)

---

# End of Quickstart.md  
Everything above is Jekyll‑compatible and ready for GitHub Pages.
