# card

`card.js` draws a ruling card of ספריית ההלכות from the card JSON, inside a chat widget. It carries the style and the small scripts of the card (seal, pins switch, copy, report), so the widget only has to hold the card data.

The `ruling-analyzer` skill loads it through jsDelivr, pinned to a commit so a card never changes after it is shown. Keep the commits it points to reachable (merge this branch with a merge commit, or keep the branch).

```html
<div id="hl-root"></div>
<script>window.HLData={...};if(window.HLCard)HLCard.render(window.HLData)</script>
<script src="https://cdn.jsdelivr.net/gh/idob4474/rulings-index@COMMIT/card/card.js"></script>
```

`card.js` mirrors `scripts/render.py` of the skill, which builds the same card as one self-contained HTML. A change to the design goes into both, and the skill then points at the new commit.
