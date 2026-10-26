"""Flickering fireplace animation for the Sense HAT 8x8 LED matrix.

Run with:  python3 fireplace.py
Stop with Ctrl+C (or `kill <pid>`); the LEDs are cleared on exit.
"""

import random
import signal
import time

from sense_hat import SenseHat

FPS = 7
COOLING_MIN = 0.0
COOLING_MAX = 0.12
TOP_EXTRA_COOLING = 1.5   # extra cooling factor at the top row, tapers the flames
ROTATION = 180              # 0/90/180/270 - adjust so the flames rise upward
BRIGHTNESS = 0.4          # 0.0-1.0, scales a linear gamma table
FUEL_DRIFT = 0.10         # how fast each column's fuel strength wanders

WIDTH = 8
VISIBLE_ROWS = 8
FUEL_ROWS = 2             # hidden rows below the display
HEIGHT = VISIBLE_ROWS + FUEL_ROWS

PALETTE_SIZE = 16
PALETTE_STOPS = [         # (heat, colour)
    (0.00, (0, 0, 0)),
    (0.12, (0, 0, 0)),
    (0.25, (120, 0, 0)),
    (0.40, (255, 30, 0)),
    (0.55, (255, 120, 0)),
    (0.75, (255, 200, 40)),
    (1.00, (255, 200, 40)),
]

column_strength = [random.uniform(0.6, 1.0) for _ in range(WIDTH)]


def build_palette():
    """Build the heat-to-colour lookup table.

    Interpolates linearly between the PALETTE_STOPS colours and returns a list
    of PALETTE_SIZE (r, g, b) tuples, where index 0 is the coldest colour and
    the last index the hottest.
    """
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
    """Refill the bottom (hidden) row of the heat grid with fresh fuel.

    Each column's strength in column_strength takes a small random-walk step
    first. Each cell then gets a spark (1.0), a dark gap (0.2), or 80-100% of
    its column's strength. Modifies heat in place.
    """
    bottom = heat[HEIGHT - 1]
    for x in range(WIDTH):
        # Random walk, so a column stays tall or short for a while.
        strength = column_strength[x] + random.uniform(-FUEL_DRIFT, FUEL_DRIFT)
        column_strength[x] = min(max(strength, 0.25), 1.0)
        r = random.random()
        if r < 0.10:
            bottom[x] = 1.0          # spark
        elif r < 0.18:
            bottom[x] = 0.2          # dark gap
        else:
            bottom[x] = column_strength[x] * random.uniform(0.8, 1.0)


def rise(heat):
    """Move heat one row up the grid and cool it.

    Each cell takes the heat of the cell below it, or of the cell one column
    to the left or right of that, and loses a random cooling amount. Cooling
    is stronger toward the top so the flames taper. Values are clamped to
    0.0-1.0. Modifies heat in place.
    """
    # Rows are indexed top (0) to bottom (HEIGHT - 1); work upward from the fuel row.
    for y in range(HEIGHT - 2, -1, -1):
        below = heat[y + 1]
        taper = 1 + TOP_EXTRA_COOLING * (1 - y / (HEIGHT - 1))
        for x in range(WIDTH):
            # Take heat from directly below, or drift in from one column aside.
            source = min(max(x + random.choice((-1, 0, 0, 1)), 0), WIDTH - 1)
            value = below[source]
            value -= random.uniform(COOLING_MIN, COOLING_MAX) * taper
            heat[y][x] = min(max(value, 0.0), 1.0)


def render(heat, palette):
    """Convert the visible rows of the heat grid to a list of 64 pixels.

    Each heat value is mapped to the nearest palette entry. The result is in
    the row-major order that SenseHat.set_pixels() expects.
    """
    pixels = []
    for row in heat[:VISIBLE_ROWS]:
        for value in row:
            pixels.append(palette[round(value * (PALETTE_SIZE - 1))])
    return pixels


def handle_sigterm(signum, frame):
    """Turn SIGTERM into SystemExit so main() clears the LEDs on `kill`."""
    raise SystemExit(0)


def main():
    """Set up the Sense HAT and run the animation until interrupted.

    The LEDs are cleared on exit, whether the script is stopped by Ctrl+C,
    SIGTERM, or an error.
    """
    signal.signal(signal.SIGTERM, handle_sigterm)
    sense = SenseHat()
    # Linear gamma keeps colour steps distinct when dimmed; low_light crushes them.
    sense.gamma = [round(i * BRIGHTNESS) for i in range(32)]
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
