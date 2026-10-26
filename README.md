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

Every frame (15 per second):

1. **Fuel** – each cell of the bottom hidden row gets a random heat between 0.6
   and 1.0. About 10% of cells become a full-heat *spark* and about 8% a dark
   *gap* (0.2), which keeps the flicker irregular.
2. **Rise** – working from the bottom up, each cell takes the weighted average
   of the three cells below it (left, centre counted twice, right).
3. **Cool** – a random cooling amount between `COOLING_MIN` and `COOLING_MAX` is
   subtracted from each cell. Cooling increases toward the top (up to 1.5× at
   the top row, set by `TOP_EXTRA_COOLING`), so the flames taper into tongues.
4. **Render** – only the top 8 rows are shown. Each heat value is mapped to a
   colour and all 64 pixels are sent to the matrix at once.

## Colour palette

Heat is mapped to colour through a 16-entry lookup table, built once at
startup by interpolating between these stops:

| Heat | Colour   | RGB           |
|------|----------|---------------|
| 0.00 | black    | (0, 0, 0)     |
| 0.15 | black    | (0, 0, 0)     |
| 0.35 | deep red | (120, 0, 0)   |
| 0.55 | red      | (255, 30, 0)  |
| 0.80 | orange   | (255, 120, 0) |
| 1.00 | yellow   | (255, 200, 40)|

Heat below 0.15 stays black, so the flames get clean edges instead of a dim
red haze. The palette tops out at a warm yellow rather than white, which keeps
the fire looking like burning wood instead of a gas flame.

## Tweaking

The constants at the top of `fireplace.py`:

| Constant            | Default | Effect |
|---------------------|---------|--------|
| `FPS`               | 15      | Animation speed. |
| `COOLING_MIN/MAX`   | 0.04 / 0.10 | Range of cooling per row. Higher values give lower flames. |
| `TOP_EXTRA_COOLING` | 0.5     | Extra cooling near the top. Higher values give more pointed flames. |
| `ROTATION`          | 0       | 0/90/180/270. Change this if the flames don't rise upward on your setup. |
| `LOW_LIGHT`         | True    | Dims the LEDs. Set to False for full brightness. |
