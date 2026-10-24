# PANEL BURN (vertical slice)

Build the page. Burn the story. A turn-based comic duel for two players on one device.

Status: **prototype.** It runs in a browser and the rules are covered by tests. Playtesting and art review are still needed.

## Play

Open `index.html` in a browser (no build step, no server, no dependencies).

1. **Build:** Player 1 places one Story Core and up to four other panels on the top page, then presses Ready. Player 2 does the same on the bottom page. Pages are sealed while the other player builds.
2. **Battle:** Players alternate turns on the shared device. Each turn you get one action:
   - **Throw torch:** click any column of the opposing page. The torch crosses the gutter and hits the first intact panel in that column.
   - **Reinforce:** click one of your own panels to put out its fire, or to repair 1 HP if it is not burning.
3. **Win:** destroy the opponent's Story Core.

## Rules (current values, all tunable in `src/logic.js`)

| Thing | Value |
| --- | --- |
| Page grid | 6 × 4 cells |
| Panels per page | 5 max, exactly one Story Core |
| Panel HP | Core 5 · Small 4 · Wide 5 · Tall 5 · Large 7 |
| Torch damage | 2, and it sets the panel alight |
| Burn | 1 HP at the start of the owner's turn, until extinguished or destroyed |
| Reinforce | Extinguish, or repair 1 HP |
| Destroyed panel | Leaves a gap, which opens a lane for later torches |

Torches enter each page from the gutter. Player 1 fires down into the bottom page; Player 2 fires up into the top page.

## Not in this slice

Props (fans, water, barrels), character abilities, sound, online play, and the art kit. The panels are plain boxes for now. The art pass comes after the rules are proven in play.

## Tests

```
node --test projects/panel-burn/tests/logic.test.js
```

Browser smoke test (not checked in): drive `index.html` with Playwright, build both pages, ready up, throw a torch, and reinforce. The last run reported no page or console errors.
