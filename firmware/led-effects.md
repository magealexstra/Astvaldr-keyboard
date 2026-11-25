# Astvaldr lighting effects

Every RGB matrix effect QMK offers, in the order the Effect +/- keys step through them. Effect + goes down the list, Effect - goes up, and it wraps around at the ends. Number 0 is off.

There are two builds, so a builder can choose:

- **Default build** (`astvaldr-left.uf2` / `astvaldr-right.uf2`): the 30 effects marked **yes** below, chosen on the lighting tour. Use the **Default #** column.
- **Full build** (`astvaldr-full-left.uf2` / `astvaldr-full-right.uf2`, or `gen_astvaldr.py --all-effects`): all 50. Use the **Full #** column.

The numbers are what VIA shows as the effect, and what the Effect keys count through. Both builds start on Raindrops (Default 10, Full 24), hue 200, saturation 223, speed 95, at the brightness cap of 96. The gaming layer switches to Digital Rain (Default 14, Full 33) while it is on, without saving it.

- **Hue / Sat:** whether the Hue and Saturation keys change the effect.
  - *rainbow*: the effect makes its own colors, so hue does nothing.
- **Typing:** whether the effect reacts to key presses.

Speed changes how fast every animated effect moves. On gradients it changes how wide the color spread is instead.

| Full # | Default # | Effect | What it looks like | Hue / Sat | Typing | In default build |
|---|---|---|---|---|---|---|
| 1 | 1 | Solid Color | Every key one steady color | both | no | **yes** |
| 2 | 2 | Alphas Mods | Letter keys one color, modifier keys a second color (speed sets how far apart the two colors are) | both | no | **yes** |
| 3 | - | Gradient Up/Down | Color fades from the bottom row to the top around your hue | both | no | - |
| 4 | - | Gradient Left/Right | Same, fading across the board | both | no | - |
| 5 | 3 | Breathing | Whole board pulses brighter and dimmer | both | no | **yes** |
| 6 | 4 | Band Sat | A band sweeps across, fading from white to your color | both | no | **yes** |
| 7 | 5 | Band Val | A bright band sweeps across a dim board | both | no | **yes** |
| 8 | 6 | Band Pinwheel Sat | White-to-color blades rotating around the center | both | no | **yes** |
| 9 | 7 | Band Pinwheel Val | Bright blades rotating around the center on a dim board | both | no | **yes** |
| 10 | 8 | Band Spiral Sat | White-to-color spiral rotating | both | no | **yes** |
| 11 | 9 | Band Spiral Val | Bright spiral rotating on a dim board | both | no | **yes** |
| 12 | - | Cycle All | Whole board fades through the rainbow together | sat only (rainbow) | no | - |
| 13 | - | Cycle Left/Right | Rainbow scrolling sideways | sat only (rainbow) | no | - |
| 14 | - | Cycle Up/Down | Rainbow scrolling vertically | sat only (rainbow) | no | - |
| 15 | - | Rainbow Moving Chevron | Rainbow V-shapes sliding across | sat only (rainbow) | no | - |
| 16 | - | Cycle Out/In | Rainbow rings moving out from the center | sat only (rainbow) | no | - |
| 17 | - | Cycle Out/In Dual | Rainbow rings from two centers, one each side | sat only (rainbow) | no | - |
| 18 | - | Cycle Pinwheel | Rainbow pinwheel spinning | sat only (rainbow) | no | - |
| 19 | - | Cycle Spiral | Rainbow spiral spinning | sat only (rainbow) | no | - |
| 20 | - | Dual Beacon | Two opposite colors sweeping around like a lighthouse | both | no | - |
| 21 | - | Rainbow Beacon | Rainbow sweeping around like a lighthouse | sat only (rainbow) | no | - |
| 22 | - | Rainbow Pinwheels | Two rainbow pinwheels spinning against each other | sat only (rainbow) | no | - |
| 23 | - | Flower Blooming | Rainbow bands opening out from the middle like petals | sat only (rainbow) | no | - |
| 24 | 10 | Raindrops | Random keys flicker to colors around your hue (the default effect) | loosely | no | **yes** |
| 25 | - | Jellybean Raindrops | Random keys flicker to fully random colors | sat only | no | - |
| 26 | - | Hue Breathing | Whole board drifts slightly either side of your hue and back | both | no | - |
| 27 | - | Hue Pendulum | Colors near your hue swing back and forth across the board | both | no | - |
| 28 | - | Hue Wave | Colors near your hue rippling across | both | no | - |
| 29 | 11 | Pixel Rain | Single random keys light in random colors, one at a time | sat only | no | **yes** |
| 30 | 12 | Pixel Flow | Colored pixels streaming across the board | sat only | no | **yes** |
| 31 | - | Pixel Fractal | Mirrored pixel patterns flowing out from the center | both | no | - |
| 32 | 13 | Typing Heatmap | Keys you press glow, getting hotter the more you use them, then cool off | no | yes | **yes** |
| 33 | 14 | Digital Rain | Green streams falling down the board, Matrix style | no | no | **yes** |
| 34 | 15 | Solid Reactive Simple | Dark until pressed; pressed keys light up and fade | both | yes | **yes** |
| 35 | 16 | Solid Reactive | Your color; pressed keys shift color and fade back | both | yes | **yes** |
| 36 | 17 | Solid Reactive Wide | A wide glow around each pressed key | both | yes | **yes** |
| 37 | 18 | Solid Reactive Multi-Wide | Same, for several keys at once | both | yes | **yes** |
| 38 | 19 | Solid Reactive Cross | A pressed key lights its whole row and column | both | yes | **yes** |
| 39 | 20 | Solid Reactive Multi-Cross | Same, for several keys at once | both | yes | **yes** |
| 40 | 21 | Solid Reactive Nexus | Lines shoot out along the row and column from a pressed key | both | yes | **yes** |
| 41 | 22 | Solid Reactive Multi-Nexus | Same, for several keys at once | both | yes | **yes** |
| 42 | - | Splash | A rainbow ripple spreads from each pressed key | sat only (rainbow) | yes | - |
| 43 | 23 | Multisplash | Same, several ripples at once | sat only (rainbow) | yes | **yes** |
| 44 | 24 | Solid Splash | A ripple in your color spreads from each pressed key | both | yes | **yes** |
| 45 | 25 | Solid Multisplash | Same, several ripples at once | both | yes | **yes** |
| 46 | 26 | Starlight Smooth | Keys gently twinkle in your color | both | no | **yes** |
| 47 | 27 | Starlight | Keys twinkle in your color | both | no | **yes** |
| 48 | 28 | Starlight Dual Sat | Twinkle in your color at mixed saturations | both | no | **yes** |
| 49 | 29 | Starlight Dual Hue | Twinkle in your color and a second nearby color | both | no | **yes** |
| 50 | 30 | Riverflow | Slow waves of brightness flowing like a river | both | no | **yes** |

## Notes

- **Reactive effects (Full 34-45):** they react to keys on both halves, since the halves share their key state.
- **Typing Heatmap and Digital Rain** need extra memory; both are in both builds.
