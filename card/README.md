# card

`card.js` draws a ruling card of ספריית ההלכות from the card JSON, inside a chat widget. It carries the style and the small scripts of the card (pins switch, light and dark mode, copy, report), so the widget only has to hold the card data. It follows the chat's light or dark theme on its own, and a button switches it by hand.

The `ruling-analyzer` skill loads it through jsDelivr, pinned to a commit so a card never changes after it is shown. Keep the commits it points to reachable (merge this branch with a merge commit, or keep the branch).

```html
<div id="hl-root"></div>
<script>window.HLData={...};if(window.HLCard)HLCard.render(window.HLData)</script>
<script src="https://cdn.jsdelivr.net/gh/idob4474/rulings-index@COMMIT/card/card.js"></script>
```

`card.js` is built by `tools/card/build.py` from `tools/card/card.src.js` and `tools/card/card.css`. The build also writes the same file to `skills/ruling-analyzer/assets/card.js`, which `render.py --inline` puts inside the widget when the CDN is blocked. After a change to the design, commit the build, then point `CARD_JS` in `render.py` at that commit. CI fails while it points at an older card.js.
