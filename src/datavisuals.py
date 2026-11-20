"""Scrollable acceleration-time graph from a CSV log (timestamps are shown as-is, in ms).

Expects a CSV with a header and lines like:
    time_ms,x_ms2
    23901,0.07

Usage:
    pip install matplotlib
    python csv_plot.py data.csv        (path to the CSV; defaults to data.csv)

Controls:
    - "Position" slider, or drag it, to scroll through the data
    - "Window" slider to zoom (how many ms are visible at once)
    - Left / Right arrow keys, or the mouse wheel, to scroll
    - Home / End to jump to the start / end
"""

import csv
import sys

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

WINDOW_MS = 10_000     # starting window width in ms


def load(path):
    """Read the CSV into two lists (time_ms, x), skipping the header and any bad lines."""
    ts, xs = [], []
    with open(path, newline="") as f:
        for row in csv.reader(f):
            try:
                ts.append(int(row[0]))
                xs.append(float(row[1]))
            except (ValueError, IndexError):
                continue          # header, blank or garbled line
    return ts, xs


def main():
    trial_distance = int(input("Enter distance of mass from centre: "))
    trial_number = int(input("Enter trial number: "))
    filename = f"{trial_distance}mmTrial{trial_number}.csv"
    # filename = "data.csv"

    ts, xs = load(filename)
    if not ts:
        sys.exit(f"No valid data found in {filename}")

    t_min, t_max = ts[0], ts[-1]
    total = max(t_max - t_min, 1)
    window = min(WINDOW_MS, total)

    fig, ax = plt.subplots(figsize=(11, 6))
    plt.subplots_adjust(bottom=0.22)

    ax.plot(ts, xs, lw=1.2)
    ax.axhline(0, color="gray", lw=0.8)
    pad = max((max(xs) - min(xs)) * 0.05, 0.1)
    ax.set_ylim(min(xs) - pad, max(xs) + pad)
    ax.set_xlim(t_min, t_min + window)
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Tangential acceleration (m/s²)")
    ax.set_title(f"Acceleration-time graph: {filename}")
    ax.grid(True, alpha=0.4)

    ax_pos = fig.add_axes([0.12, 0.10, 0.76, 0.03])
    ax_win = fig.add_axes([0.12, 0.04, 0.76, 0.03])
    s_pos = Slider(ax_pos, "Position", t_min, max(t_max - window, t_min + 1), valinit=t_min, valfmt="%d ms")
    s_win = Slider(ax_win, "Window", min(500, total), total, valinit=window, valfmt="%d ms")

    def redraw(_=None):
        w = s_win.val
        s_pos.valmax = max(t_max - w, t_min + 1)
        s_pos.ax.set_xlim(s_pos.valmin, s_pos.valmax)
        left = min(max(s_pos.val, t_min), s_pos.valmax)
        ax.set_xlim(left, left + w)
        fig.canvas.draw_idle()

    s_pos.on_changed(redraw)
    s_win.on_changed(redraw)

    def scroll_by(frac):
        step = s_win.val * frac
        s_pos.set_val(min(max(s_pos.val + step, t_min), s_pos.valmax))

    def on_key(event):
        if event.key == "right":
            scroll_by(0.1)
        elif event.key == "left":
            scroll_by(-0.1)
        elif event.key == "home":
            s_pos.set_val(t_min)
        elif event.key == "end":
            s_pos.set_val(s_pos.valmax)

    def on_scroll(event):
        scroll_by(0.1 if event.button == "up" else -0.1)

    fig.canvas.mpl_connect("key_press_event", on_key)
    fig.canvas.mpl_connect("scroll_event", on_scroll)

    plt.show()


if __name__ == "__main__":
    main()