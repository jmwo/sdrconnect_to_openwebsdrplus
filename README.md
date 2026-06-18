# SDRconnect RTL‑TCP Bridge  
English / Deutsch

A lightweight Python bridge that exposes SDRconnect as an RTL‑TCP server for OpenWebRX+.  
Eine leichte Python‑Bridge, die SDRconnect als RTL‑TCP‑Server für OpenWebRX+ bereitstellt.

---

# 🇬🇧 English

## 🚀 Purpose
This script connects SDRconnect to OpenWebRX+ by:
- receiving IQ data from SDRconnect
- converting 16‑bit IQ to RTL‑TCP‑compatible 8‑bit IQ
- providing a full RTL‑TCP server
- forwarding tuning commands from OpenWebRX+ to SDRconnect
- automatically selecting the correct antenna

This turns SDRconnect into a fully compatible RTL‑TCP backend.

---

## ✨ Features
- RTL‑TCP server (port 5555)
- Tuning forwarding
- Automatic antenna switching  
  < 30 MHz → Antenna C  
  ≥ 30 MHz → Antenna A
- 16‑bit → 8‑bit IQ conversion
- Multiple simultaneous clients
- Stable IQ buffering
- Automatic SDRconnect initialization

---

## ⚠️ Important Sample‑Rate Notice
SDRconnect, the script and OpenWebRX+ **must use the same sample rate**.

- SDRconnect defines the hardware sample rate  
- The script reports this rate in the RTL‑TCP header  
- OpenWebRX+ does **not** support all SDRconnect sample rates  

Recommended for beginners:
- SDRconnect: 1 MHz  
- Script: SAMPLE_RATE = 1_000_000  
- OpenWebRX+: set profile to 1 MHz  

This ensures maximum stability.

---

## 🐳 OpenWebRX+ when running in Docker
If OpenWebRX+ runs inside Docker, configure RTL‑TCP like this:

    rtl_tcp=host.docker.internal:5555

Required settings:
- Host: host.docker.internal
- Port: 5555
- Mode: RTL‑TCP
- Sample rate: must match SDRconnect & script

Docker containers cannot access localhost directly,  
so host.docker.internal must be used.

---

## 🧩 Requirements
- Python 3.10+
- SDRconnect with WebSocket API enabled
- OpenWebRX+
- Python dependencies:
    pip install websockets numpy

---

## ▶️ Starting the Bridge
Start SDRconnect first, then run:

    python3 sdrconnect_rtl_bridge.py

OpenWebRX+ connects via:

    rtl_tcp=host.docker.internal:5555

---

## 🛠 How It Works
- Connects to ws://127.0.0.1:5454
- Enables IQ stream, device stream, center frequency, VFO
- Converts 16‑bit IQ → 8‑bit IQ
- Provides RTL‑TCP server
- Forwards tuning commands
- Selects antenna automatically

---

## 📜 License
MIT License

---

# 🇩🇪 Deutsch

## 🚀 Zweck der Bridge
Dieses Script verbindet SDRconnect mit OpenWebRX+, indem es:
- IQ‑Daten von SDRconnect empfängt
- diese in RTL‑TCP‑kompatible 8‑bit‑IQ‑Daten umwandelt
- einen vollständigen RTL‑TCP‑Server bereitstellt
- Tuning‑Kommandos weitergibt
- automatisch die passende Antenne auswählt

Damit wird SDRconnect zu einem vollwertigen RTL‑TCP‑Backend.

---

## ✨ Funktionen
- RTL‑TCP‑Server (Port 5555)
- Tuning‑Weitergabe
- Automatische Antennenumschaltung  
  < 30 MHz → Antenna C  
  ≥ 30 MHz → Antenna A
- 16‑bit → 8‑bit IQ‑Konvertierung
- Mehrere gleichzeitige Clients
- Stabile IQ‑Pufferung
- Automatische Initialisierung von SDRconnect

---

## ⚠️ Wichtiger Hinweis zur Sample‑Rate
SDRconnect, das Script und OpenWebRX+ **müssen dieselbe Sample‑Rate verwenden**.

- SDRconnect setzt die echte Hardware‑Sample‑Rate  
- Das Script sendet diese Rate im RTL‑TCP‑Header  
- OpenWebRX+ unterstützt nicht alle Sample‑Raten  

Empfehlung für den Anfang:
- SDRconnect: 1 MHz  
- Script: SAMPLE_RATE = 1_000_000  
- OpenWebRX+: Profil ebenfalls auf 1 MHz  

Damit läuft die Bridge am stabilsten.

---

## 🐳 OpenWebRX+ im Docker‑Betrieb
Wenn OpenWebRX+ in Docker läuft, muss RTL‑TCP so eingestellt werden:

    rtl_tcp=host.docker.internal:5555

Erforderliche Einstellungen:
- Host: host.docker.internal
- Port: 5555
- Modus: RTL‑TCP
- Sample‑Rate: identisch zu SDRconnect & Script

Docker‑Container können nicht direkt auf localhost zugreifen,  
darum muss host.docker.internal verwendet werden.

---

## 🧩 Voraussetzungen
- Python 3.10+
- SDRconnect (WebSocket‑API aktiv)
- OpenWebRX+
- Python‑Module:
    pip install websockets numpy

---

## ▶️ Start
SDRconnect starten, dann:

    python3 sdrconnect_rtl_bridge.py

OpenWebRX+ verbindet sich mit:

    rtl_tcp=host.docker.internal:5555

---

## 🛠 Funktionsweise
- Verbindung zu ws://127.0.0.1:5454
- Aktiviert IQ‑Stream, Device‑Stream, Center‑Frequency, VFO
- Konvertiert 16‑bit IQ → 8‑bit IQ
- Stellt RTL‑TCP‑Server bereit
- Leitet Tuning‑Kommandos weiter
- Wählt automatisch die passende Antenne

---

## 📜 Lizenz
MIT License
