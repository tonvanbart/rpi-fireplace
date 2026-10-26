# rpi-fireplace

A flickering fireplace on the 8x8 LED matrix of a Raspberry Pi Sense HAT.

## Running it

```sh
python3 fireplace.py
```

Stop it with Ctrl+C (or `kill <pid>`). The LEDs are cleared on exit. Only the
`sense_hat` library and the Python standard library are needed.

## How the fire works

The script keeps a grid of "heat" values between 0.0 and 1.0. The grid is 8
columns wide and 10 rows tall: the 8 visible rows plus 2 hidden rows below the
display that act as the fuel bed. Hiding the fuel keeps the bottom row of LEDs
from looking uniformly bright.

Each column has its own *fuel strength* (0.25–1.0). Every frame it drifts up
or down by a small random step (up to `FUEL_DRIFT`), so a column burns tall or
low for a few seconds before changing. This keeps neighbouring flames from
settling at the same height.

Every frame (`FPS` times per second):

1. **Fuel** – each cell of the bottom hidden row gets 80–100% of its column's
   fuel strength. About 10% of cells become a full-heat *spark* and about 8% a
   dark *gap* (0.2), which keeps the flicker irregular.
2. **Rise** – working from the bottom up, each cell takes the heat of the cell
   directly below it (50% of the time) or of the cell diagonally below-left or
   below-right (25% each). Heat travels up in separate tongues that wander a
   little sideways, instead of blurring into its neighbours.
3. **Cool** – a random cooling amount between `COOLING_MIN` and `COOLING_MAX` is
   subtracted from each cell. Cooling increases toward the top (up to 2.5× at
   the top row, set by `TOP_EXTRA_COOLING`), so the flames come to a point
   before reaching the edge of the display.
4. **Render** – only the top 8 rows are shown. Each heat value is mapped to a
   colour and all 64 pixels are sent to the matrix at once.

The display is dimmed with a linear gamma table scaled by `BRIGHTNESS`, rather
than the Sense HAT's built-in low-light mode. Low-light mode squeezes each
colour channel into about 11 levels and turns most low values into the same
level, so red, red-orange and orange would all look alike.

## Colour palette

Heat is mapped to colour through a 16-entry lookup table, built once at
startup by interpolating between these stops:

| Heat | Colour   | RGB           |
|------|----------|---------------|
| 0.00 | black    | (0, 0, 0)     |
| 0.12 | black    | (0, 0, 0)     |
| 0.25 | deep red | (120, 0, 0)   |
| 0.40 | red      | (255, 30, 0)  |
| 0.55 | orange   | (255, 70, 0)  |
| 0.75 | yellow   | (255, 130, 0) |
| 1.00 | yellow   | (255, 130, 0) |

Heat below 0.12 stays black, so the flames get clean edges instead of a dim
red haze. The stops sit low on the heat scale because the visible rows rarely
get much hotter than 0.75 (the hottest heat is in the hidden fuel rows);
anything above 0.75 is the same yellow. With these stops, roughly a third of
the lit pixels are orange or yellow. The palette tops out at a warm yellow rather than white, which keeps
the fire looking like burning wood instead of a gas flame.

## Tweaking

The constants at the top of `fireplace.py`:

| Constant            | Example | Effect |
|---------------------|---------|--------|
| `FPS`               | 7       | Animation speed. |
| `COOLING_MIN/MAX`   | 0.0 / 0.12 | Range of cooling per row. Higher values give lower flames; a wider range gives more varied flame heights. |
| `TOP_EXTRA_COOLING` | 1.5     | Extra cooling near the top. Higher values give more pointed flames that stay further from the top edge. |
| `FUEL_DRIFT`        | 0.10    | How fast each column's fuel strength changes. Higher values make the flames change height more quickly. |
| `ROTATION`          | 180     | 0/90/180/270. Change this if the flames don't rise upward on your setup. |
| `BRIGHTNESS`        | 0.4     | 0.0–1.0. Scales the LED gamma table; 1.0 is full brightness. |
