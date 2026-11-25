# Astvaldr lighting effects

This lists every RGB matrix effect QMK offers, in the order the Effect +/- keys step through them on the test build. Effect + goes down the list, Effect - goes up, and it wraps around at the ends. Number 0 is off.

- **Now:** the 19 effects in the current firmware.
- **Hue / Sat:** whether the Hue and Saturation keys change the effect.
  - *rainbow*: the effect makes its own colors, so hue does nothing.
- **Typing:** whether the effect reacts to key presses.
- **Keep:** mark each row `x` to keep or `-` to toss. The final firmware includes only the kept effects, and their numbers close up.

Speed changes how fast every animated effect moves. On gradients it changes how wide the color spread is instead.

| # | Effect | What it looks like | Now | Hue / Sat | Typing | Keep |
|---|---|---|---|---|---|---|
| 1 | Solid Color | Every key one steady color | yes | both | no | x |
| 2 | Alphas Mods | Letter keys one color, modifier keys a second color (speed sets how far apart the two colors are) | | both | no | x |
| 3 | Gradient Up/Down | Color fades from the bottom row to the top around your hue | yes | both | no | - |
| 4 | Gradient Left/Right | Same, fading across the board | yes | both | no | - |
| 5 | Breathing | Whole board pulses brighter and dimmer | yes | both | no | x |
| 6 | Band Sat | A band sweeps across, fading from white to your color | | both | no | x |
| 7 | Band Val | A bright band sweeps across a dim board | | both | no | x |
| 8 | Band Pinwheel Sat | White-to-color blades rotating around the center | | both | no | x |
| 9 | Band Pinwheel Val | Bright blades rotating around the center on a dim board | | both | no | x |
| 10 | Band Spiral Sat | White-to-color spiral rotating | | both | no | x |
| 11 | Band Spiral Val | Bright spiral rotating on a dim board | | both | no | x |
| 12 | Cycle All | Whole board fades through the rainbow together | yes | sat only (rainbow) | no | - |
| 13 | Cycle Left/Right | Rainbow scrolling sideways | yes | sat only (rainbow) | no | - |
| 14 | Cycle Up/Down | Rainbow scrolling vertically | yes | sat only (rainbow) | no | - |
| 15 | Rainbow Moving Chevron | Rainbow V-shapes sliding across | yes | sat only (rainbow) | no | - |
| 16 | Cycle Out/In | Rainbow rings moving out from the center | yes | sat only (rainbow) | no | - |
| 17 | Cycle Out/In Dual | Rainbow rings from two centers, one each side | | sat only (rainbow) | no | - |
| 18 | Cycle Pinwheel | Rainbow pinwheel spinning | yes | sat only (rainbow) | no | - |
| 19 | Cycle Spiral | Rainbow spiral spinning | yes | sat only (rainbow) | no | - |
| 20 | Dual Beacon | Two opposite colors sweeping around like a lighthouse | | both | no | - |
| 21 | Rainbow Beacon | Rainbow sweeping around like a lighthouse | | sat only (rainbow) | no | - |
| 22 | Rainbow Pinwheels | Two rainbow pinwheels spinning against each other | | sat only (rainbow) | no | - |
| 23 | Flower Blooming | Rainbow bands opening out from the middle like petals | | sat only (rainbow) | no | - |
| 24 | Raindrops | Random keys flicker to colors around your hue (your current effect) | yes | loosely | no | x |
| 25 | Jellybean Raindrops | Random keys flicker to fully random colors | | sat only | no | - |
| 26 | Hue Breathing | Whole board drifts slightly either side of your hue and back | | both | no | - |
| 27 | Hue Pendulum | Colors near your hue swing back and forth across the board | | both | no | - |
| 28 | Hue Wave | Colors near your hue rippling across | yes | both | no | - |
| 29 | Pixel Rain | Single random keys light in random colors, one at a time | | sat only | no | x |
| 30 | Pixel Flow | Colored pixels streaming across the board | | sat only | no | x |
| 31 | Pixel Fractal | Mirrored pixel patterns flowing out from the center | | both | no | - |
| 32 | Typing Heatmap | Keys you press glow, getting hotter the more you use them, then cool off | | no | yes | x |
| 33 | Digital Rain | Green streams falling down the board, Matrix style | | no | no | x |
| 34 | Solid Reactive Simple | Dark until pressed; pressed keys light up and fade | yes | both | yes | x |
| 35 | Solid Reactive | Your color; pressed keys shift color and fade back | yes | both | yes | x |
| 36 | Solid Reactive Wide | A wide glow around each pressed key | | both | yes | x |
| 37 | Solid Reactive Multi-Wide | Same, for several keys at once | yes | both | yes | x |
| 38 | Solid Reactive Cross | A pressed key lights its whole row and column | | both | yes | x |
| 39 | Solid Reactive Multi-Cross | Same, for several keys at once | | both | yes | x |
| 40 | Solid Reactive Nexus | Lines shoot out along the row and column from a pressed key | | both | yes | x |
| 41 | Solid Reactive Multi-Nexus | Same, for several keys at once | | both | yes | x |
| 42 | Splash | A rainbow ripple spreads from each pressed key | yes | sat only (rainbow) | yes | - |
| 43 | Multisplash | Same, several ripples at once | yes | sat only (rainbow) | yes | x |
| 44 | Solid Splash | A ripple in your color spreads from each pressed key | yes | both | yes | x |
| 45 | Solid Multisplash | Same, several ripples at once | | both | yes | x |
| 46 | Starlight Smooth | Keys gently twinkle in your color | | both | no | x |
| 47 | Starlight | Keys twinkle in your color | | both | no | x |
| 48 | Starlight Dual Sat | Twinkle in your color at mixed saturations | | both | no | x |
| 49 | Starlight Dual Hue | Twinkle in your color and a second nearby color | | both | no | x |
| 50 | Riverflow | Slow waves of brightness flowing like a river | | both | no | x |

## Notes for the tour

- **Reactive effects (34-45):** press keys on both halves, to check that the ripples cross between them.
- **Typing Heatmap (32) and Digital Rain (33):** these need extra memory. If either misbehaves, note it here.
- **Raindrops:** keep it, since it is your default. It will be number 24 on the test build.
