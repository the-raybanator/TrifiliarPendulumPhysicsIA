"""Live acceleration-time graph from the HC-05 stream (also logs everything to a CSV).

Expects lines like "123456,-1.43":  time in ms since the Arduino started, x acceleration in m/s^2.

Usage:
    pip install pyserial matplotlib
    python live_plot.py            (auto-finds the Bluetooth port)
    python live_plot.py COM3       (skip the scan, use this port)
"""

import sys
import time
from collections import deque

import matplotlib.pyplot as plt
import serial
from matplotlib.animation import FuncAnimation
from serial.tools import list_ports

BAUD = 9600            # must match bt.begin(...) on the Arduino
PROBE_SECONDS = 8      # how long to wait for data on each candidate port while scanning
WINDOW_S = 10.0        # seconds of data visible at once (about 10 swings at T = 1 s)
Y_LIMIT = 6.0          # starting y-axis range (+/- m/s^2); it grows if the signal exceeds it


# ---------- finding the HC-05 ----------
def bluetooth_ports():
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
        if ser.readline().strip():
            print("data received!")
            return ser
    print("silent")
    ser.close()
    return None


def open_port():
    if len(sys.argv) > 1:
        return serial.Serial(sys.argv[1], BAUD, timeout=1)
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


# ---------- parsing ----------
def parse(raw):
    """b'123456,-1.43\\r' -> (123456, -1.43), or None for a half-received / garbled line."""
    try:
        t_ms, x = raw.decode("ascii", errors="ignore").strip().split(",")
        return int(t_ms), float(x)
    except ValueError:
        return None


# ---------- main ----------
def main():
    ser = open_port()
    ser.timeout = 0            # from here on, never block: just take whatever has arrived
    ser.reset_input_buffer()   # drop anything that piled up while connecting
    print(f"Connected on {ser.port}.")

    ts, xs = deque(), deque()
    state = {"t0": None, "last_ms": None, "buf": b"", "ylim": Y_LIMIT}

    fig, ax = plt.subplots(figsize=(10, 5))
    (line,) = ax.plot([], [], lw=1.5)
    readout = ax.text(0.01, 0.96, "", transform=ax.transAxes, va="top")
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_xlim(0, WINDOW_S)
    ax.set_ylim(-Y_LIMIT, Y_LIMIT)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Tangential acceleration (m/s²)")
    ax.set_title("Live acceleration-time graph")
    ax.grid(True, alpha=0.4)

    def update(_frame):
        try:
            waiting = ser.in_waiting
            if waiting:
                state["buf"] += ser.read(waiting)
        except (serial.SerialException, OSError):
            ax.set_title("Disconnected")
            ani.event_source.stop()
            return line, readout

        parts = state["buf"].split(b"\n")
        state["buf"] = parts.pop()            # last piece may be an unfinished line, keep it

        for raw in parts:
            sample = parse(raw)
            if sample is None:
                continue
            t_ms, x = sample
            if state["last_ms"] is None or t_ms < state["last_ms"]:
                if state["last_ms"] is not None:
                    print("Time went backwards: the Arduino reset? Restarting the graph at 0 s.")
                state["t0"] = t_ms            # first timestamp becomes t = 0
                ts.clear()
                xs.clear()
            state["last_ms"] = t_ms
            t = (t_ms - state["t0"]) / 1000.0
            ts.append(t)
            xs.append(x)

        if ts:
            t_now = ts[-1]
            while ts[0] < t_now - WINDOW_S:   # only keep the visible window
                ts.popleft()
                xs.popleft()
            line.set_data(list(ts), list(xs))

            left = max(0.0, t_now - WINDOW_S)
            ax.set_xlim(left, left + WINDOW_S)

            peak = max(abs(v) for v in xs)
            if peak > state["ylim"] - 0.5:    # grow the y-axis if the signal gets close to the edge
                state["ylim"] = float(int(peak) + 2)
                ax.set_ylim(-state["ylim"], state["ylim"])

            readout.set_text(f"x = {xs[-1]:+.2f} m/s²    t = {t_now:.1f} s")
        return line, readout

    ani = FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)
    try:
        plt.show()
    finally:
        ser.close()


if __name__ == "__main__":
    main()