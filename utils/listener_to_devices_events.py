import os
import sys
import requests


def stream_events(url: str) -> None:
    try:
        with requests.get(url, stream=True) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith("data:"):
                    print(line[len("data:"):].strip())
                else:
                    print(line)
    except KeyboardInterrupt:
        print("\nInterrotto dall'utente.", file=sys.stderr)
    except Exception as exc:
        print(f"Errore durante la lettura dello stream: {exc}", file=sys.stderr)


if __name__ == "__main__":
    base_url = os.getenv("OWRX_BASE_URL", "http://localhost:8000").rstrip("/")
    stream_url = f"{base_url}/devicesEvents"
    print(f"Connessione a {stream_url} ...")
    stream_events(stream_url)

# {"RTL-SDR v4": "Stopped", "SDRPlay": "Stopped", "Nooelec sdr": "DAB 9C"}
# {"RTL-SDR v4": "Stopped", "SDRPlay": "Stopped", "Nooelec sdr": "DAB 9C"}
# {"RTL-SDR v4": "Stopped", "SDRPlay": "Stopped", "Nooelec sdr": "Stopped"}
# {"RTL-SDR v4": "21.5 MHz", "SDRPlay": "Stopped", "Nooelec sdr": "Stopped"}
# {"RTL-SDR v4": "5.5 MHz", "SDRPlay": "Stopped", "Nooelec sdr": "Stopped"}
# {"RTL-SDR v4": "5.5 MHz", "SDRPlay": "Stopped", "Nooelec sdr": "Stopped"}
# {"RTL-SDR v4": "Stopped", "SDRPlay": "Stopped", "Nooelec sdr": "Stopped"}
# {"RTL-SDR v4": "5.5 MHz", "SDRPlay": "Stopped", "Nooelec sdr": "Stopped"}
# {"RTL-SDR v4": "5.5 MHz", "SDRPlay": "Stopped", "Nooelec sdr": "Stopped"}
# {"RTL-SDR v4": "Stopped", "SDRPlay": "Stopped", "Nooelec sdr": "Stopped"}
# {"RTL-SDR v4": "Stopped", "SDRPlay": "22m Broadcast", "Nooelec sdr": "Stopped"}
# {"RTL-SDR v4": "Stopped", "SDRPlay": "10m", "Nooelec sdr": "Stopped"}