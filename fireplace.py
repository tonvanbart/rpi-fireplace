"""Flickering fireplace animation for the Sense HAT 8x8 LED matrix.

Run with:  python3 fireplace.py
Stop with Ctrl+C (or `kill <pid>`); the LEDs are cleared on exit.
"""

import random
import signal
import time

from sense_hat import SenseHat

FPS = 7
COOLING_MIN = 0.04
COOLING_MAX = 0.10
TOP_EXTRA_COOLING = 0.5   # extra cooling factor at the top row, tapers the flames
ROTATION = 180              # 0/90/180/270 - adjust so the flames rise upward
LOW_LIGHT = True

WIDTH = 8
VISIBLE_ROWS = 8
FUEL_ROWS = 2             # hidden rows below the display
HEIGHT = VISIBLE_ROWS + FUEL_ROWS

PALETTE_SIZE = 16
PALETTE_STOPS = [         # (heat, colour)
    (0.00, (0, 0, 0)),
    (0.15, (0, 0, 0)),
    (0.35, (120, 0, 0)),
    (0.55, (255, 30, 0)),
    (0.80, (255, 120, 0)),
    (1.00, (255, 200, 40)),
]


def build_palette():
    palette = []
    for i in range(PALETTE_SIZE):
        heat = i / (PALETTE_SIZE - 1)
        for (h0, c0), (h1, c1) in zip(PALETTE_STOPS, PALETTE_STOPS[1:]):
            if h0 <= heat <= h1:
                t = (heat - h0) / (h1 - h0)
                palette.append(tuple(round(a + (b - a) * t) for a, b in zip(c0, c1)))
                break
    return palette


def add_fuel(heat):
    bottom = heat[HEIGHT - 1]
    for x in range(WIDTH):
        r = random.random()
        if r < 0.10:
            bottom[x] = 1.0          # spark
        elif r < 0.18:
            bottom[x] = 0.2          # dark gap
        else:
            bottom[x] = random.uniform(0.6, 1.0)


def rise(heat):
    # Rows are indexed top (0) to bottom (HEIGHT - 1); work upward from the fuel row.
    for y in range(HEIGHT - 2, -1, -1):
        below = heat[y + 1]
        taper = 1 + TOP_EXTRA_COOLING * (1 - y / (HEIGHT - 1))
        for x in range(WIDTH):
            left = below[max(x - 1, 0)]
            right = below[min(x + 1, WIDTH - 1)]
            value = (left + 2 * below[x] + right) / 4
            value -= random.uniform(COOLING_MIN, COOLING_MAX) * taper
            heat[y][x] = min(max(value, 0.0), 1.0)


def render(heat, palette):
    pixels = []
    for row in heat[:VISIBLE_ROWS]:
        for value in row:
            pixels.append(palette[round(value * (PALETTE_SIZE - 1))])
    return pixels


def handle_sigterm(signum, frame):
    raise SystemExit(0)


def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    sense = SenseHat()
    sense.low_light = LOW_LIGHT
    sense.set_rotation(ROTATION)

    palette = build_palette()
    heat = [[0.0] * WIDTH for _ in range(HEIGHT)]
    try:
        while True:
            add_fuel(heat)
            rise(heat)
            sense.set_pixels(render(heat, palette))
            time.sleep(1 / FPS)
    except KeyboardInterrupt:
        pass
    finally:
        sense.clear()


if __name__ == "__main__":
    main()
