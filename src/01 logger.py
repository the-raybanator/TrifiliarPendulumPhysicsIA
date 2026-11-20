import time

import serial
from serial.tools import list_ports

import csv

BAUD = 9600           # must match bt.begin(...) on the Arduino
PROBE_SECONDS = 8     # how long to wait for data on each candidate port


def bluetooth_ports():
    """Ports that Windows lists as Bluetooth serial links."""
    found = []
    for p in list_ports.comports():
        text = f"{p.description} {p.hwid}".lower()
        if "bluetooth" in text or "bthenum" in text:
            found.append(p.device)
    return found


def probe(port):
    """Open the port and wait for a line of data. Returns the open port or None."""
    print(f"  trying {port} ...", end=" ", flush=True)
    try:
        ser = serial.Serial(port, BAUD, timeout=1)
    except (serial.SerialException, OSError) as e:
        print(f"could not open ({type(e).__name__})")
        return None
    deadline = time.time() + PROBE_SECONDS
    while time.time() < deadline:
        line = ser.readline()
        if line.strip():
            print("data received!")
            return ser
    print("silent")
    ser.close()
    return None


def find_port():
    while True:
        ports = bluetooth_ports()
        if not ports:
            print("No Bluetooth COM ports found. Is the HC-05 paired with Windows? Retrying ...")
        else:
            print(f"Scanning Bluetooth ports: {', '.join(ports)}")
            for port in ports:
                ser = probe(port)
                if ser:
                    return ser
            print("No port sent data. Is the Arduino powered and the sketch running? Retrying ...")
        time.sleep(3)


def stream(ser):
    global f

    print(f"Connected on {ser.port}. Press Ctrl+C to stop.")

    with ser:
        filename = f"{trial_distance}mmTrial{trial_number}.csv"
        f = open(filename, mode="w", newline="", encoding="utf-8")
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Acceleration"])
    
        while True:
            line = ser.readline().decode("utf-8", errors="replace").strip()
            if line:
                print(line)
                writer.writerow(line.split(","))


def main():
    global trial_distance, trial_number
    trial_distance = int(input("Enter distance of mass from centre: "))
    trial_number = int(input("Enter trial number: "))

    while True:
        try:
            ser = find_port()
            stream(ser)
        except (serial.SerialException, OSError) as e:
            print(f"Connection lost: {e}. Reconnecting in 3 s ...")
            time.sleep(3)
        except KeyboardInterrupt:
            print("\nStopped.")
            f.close()
            break


if __name__ == "__main__":
    main()