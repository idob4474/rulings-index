/* Ruling card of ספריית ההלכות, drawn in the page from the card JSON.
   Mirror of ruling-analyzer/scripts/render.py. Keep the two in step.
   Usage in a widget
     <div id="hl-root"></div>
     <script>window.HLData={...card json...};if(window.HLCard)HLCard.render(window.HLData)</script>
     <script src="https://cdn.jsdelivr.net/gh/idob4474/rulings-index@COMMIT/card/card.js"></script> */
(function () {
  "use strict";
  var CSS = ".hl{--paper:#FFF6F1;--card:#FFFFFF;--ink:#2B1A26;--muted:#7E6873;--rule:#F0DED5;--rule-soft:#F9EDE6;--marker:#FFE39A;--marker-ink:#2B1A26;--violet:#5A49B4;--violet-soft:#EEEAFB;--amber:#8F5000;--amber-soft:#FFF0D3;--green:#2C7A57;--green-soft:#E2F3E9;--on-accent:#FFFFFF;--shadow-sm:0 1px 2px rgba(96,40,32,.07);--shadow:0 2px 6px rgba(96,40,32,.06),0 14px 32px rgba(96,40,32,.09);--a:#FAC862;--b:#EE972C;--accent:#974B00;--accent-soft:#FFF0D8;--display:\"Suez One\",\"Frank Ruhl Libre\",serif;--body:\"Rubik\",\"Assistant\",Arial,sans-serif}\n.hl[data-vol=torts]{--a:#F8A593;--b:#E2527A;--accent:#AE2649;--accent-soft:#FDE6EC}\n@media (prefers-color-scheme:dark){:root:not([data-mode=light]) .hl{--paper:#1A1116;--card:#251820;--ink:#F8EAF0;--muted:#BCA4B0;--rule:#3A2833;--rule-soft:#2E1F28;--marker:rgba(255,210,90,.28);--marker-ink:#FFF1C4;--violet:#B9ADFF;--violet-soft:#2B2449;--amber:#FFC47A;--amber-soft:#3A2A12;--green:#84D7AE;--green-soft:#173223;--on-accent:#1A1116;--shadow-sm:0 1px 2px rgba(0,0,0,.35);--shadow:0 2px 6px rgba(0,0,0,.3);--a:#F5BC57;--b:#E2891F;--accent:#FFC56E;--accent-soft:#3A2813}:root:not([data-mode=light]) .hl[data-vol=torts]{--a:#F29486;--b:#D9476E;--accent:#FF9EB6;--accent-soft:#3B1A26}}\n:root[data-mode=dark] .hl{--paper:#1A1116;--card:#251820;--ink:#F8EAF0;--muted:#BCA4B0;--rule:#3A2833;--rule-soft:#2E1F28;--marker:rgba(255,210,90,.28);--marker-ink:#FFF1C4;--violet:#B9ADFF;--violet-soft:#2B2449;--amber:#FFC47A;--amber-soft:#3A2A12;--green:#84D7AE;--green-soft:#173223;--on-accent:#1A1116;--shadow-sm:0 1px 2px rgba(0,0,0,.35);--shadow:0 2px 6px rgba(0,0,0,.3);--a:#F5BC57;--b:#E2891F;--accent:#FFC56E;--accent-soft:#3A2813}:root[data-mode=dark] .hl[data-vol=torts]{--a:#F29486;--b:#D9476E;--accent:#FF9EB6;--accent-soft:#3B1A26}\n.hl{direction:rtl;text-align:right;font-family:var(--body);color:var(--ink);background:var(--paper);border-radius:24px;padding:16px 16px 20px;font-size:16px;line-height:1.65}\n.hl *{box-sizing:border-box}.hl p{margin:0}.hl h1,.hl h3,.hl h4,.hl h5{margin:0;color:inherit}\n.hl mark{background:var(--marker);color:var(--marker-ink);padding:0 3px;border-radius:4px;-webkit-box-decoration-break:clone;box-decoration-break:clone}\n.hl .pin{font-size:.7rem;font-weight:500;color:var(--muted);background:var(--rule-soft);border:1px solid var(--rule);border-radius:6px;padding:0 6px;white-space:nowrap;vertical-align:1px;font-variant-numeric:tabular-nums}\n.hl.no-pins .pin{display:none}\n.hl .crumbs{display:flex;flex-wrap:wrap;gap:6px}.hl .crumbs span{background:var(--card);border:1px solid var(--rule);border-radius:999px;padding:3px 11px;font-size:.84rem}\n.hl .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--b);margin-inline-end:6px}\n.hl .case-h{padding-top:16px}.hl .row{display:grid;grid-template-columns:1fr auto;gap:16px;align-items:center}.hl .row>div{min-width:0}\n.hl .sub{color:var(--accent);font-weight:500;font-size:.9rem}\n.hl h1{font-family:var(--display);font-weight:400;font-size:clamp(2.2rem,8vw,3.2rem);line-height:1.05;margin-top:4px}\n.hl .seal{width:84px;height:84px;display:block}.hl .seal .sg{fill:none;stroke:var(--accent)}.hl .seal .disc{fill:var(--accent-soft)}.hl .seal .ltr{font-family:var(--display);fill:var(--accent)}\n.hl .aka{color:var(--muted);font-size:1.02rem;margin-top:6px}\n.hl .facts{display:flex;flex-wrap:wrap;gap:1px;margin:18px 0 0;background:var(--rule);border:1px solid var(--rule);border-radius:18px;overflow:hidden}\n.hl .fact{flex:1 1 140px;background:var(--card);padding:10px 13px;display:grid;gap:1px;align-content:start}\n.hl .fact dt{color:var(--muted);font-size:.76rem}.hl .fact dd{margin:0;font-weight:500;font-size:.92rem;line-height:1.4}\n.hl .cite{color:var(--muted);font-size:.82rem;margin-top:12px}\n.hl .statusrow{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin-top:12px}\n.hl .trust{display:inline-flex;align-items:center;gap:7px;font-size:.8rem;font-weight:600;border-radius:999px;padding:4px 12px;color:var(--green);background:var(--green-soft)}\n.hl .trust.draft{color:var(--amber);background:var(--amber-soft)}\n.hl .switch{display:inline-flex;align-items:center;gap:8px;font:inherit;font-size:.84rem;color:var(--muted);cursor:pointer;border:0;background:transparent;padding:2px}\n.hl .switch i{width:34px;height:20px;border-radius:999px;background:var(--rule);position:relative}\n.hl .switch i::after{content:\"\";position:absolute;top:2px;right:2px;width:16px;height:16px;border-radius:50%;background:var(--card);transition:right .15s}\n.hl .switch[aria-checked=true] i{background:var(--accent)}.hl .switch[aria-checked=true] i::after{right:16px}\n.hl .brief{margin-top:22px;background:var(--card);border-radius:28px;padding:22px 20px;box-shadow:var(--shadow);display:grid;gap:22px;border:1px solid var(--rule)}\n.hl .brief h3{font-size:.92rem;font-weight:600;color:var(--accent);margin-bottom:10px}\n.hl .lead{font-size:1.16rem;line-height:1.8}\n.hl .keys{list-style:none;margin:0;padding:0;display:grid;gap:14px}.hl .keys li{display:grid;grid-template-columns:22px 1fr;gap:12px}\n.hl .keys li>i{font-size:22px;color:var(--accent);margin-top:2px}.hl .keys b{display:block;font-weight:600}.hl .keys .txt{font-size:.95rem}\n.hl .write{background:var(--accent-soft);border:1px solid var(--rule);border-radius:20px;padding:16px}\n.hl .write .head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px}.hl .write .head h3{margin:0}.hl .write p{font-size:.97rem}\n.hl .actions{display:flex;flex-wrap:wrap;gap:10px}\n.hl .btn{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--rule);background:var(--card);border-radius:999px;padding:9px 16px;font:inherit;font-size:.9rem;font-weight:500;cursor:pointer;color:var(--ink);box-shadow:var(--shadow-sm)}\n.hl .btn:hover{border-color:var(--accent)}.hl .btn.ghost{background:transparent;box-shadow:none;border-color:transparent;color:var(--accent);padding-inline:8px}.hl .btn i{font-size:18px}\n.hl .sections{margin-top:24px;display:grid;gap:10px}\n.hl .sec{background:var(--card);border:1px solid var(--rule);border-radius:20px;overflow:hidden}\n.hl .sec>summary{list-style:none;display:flex;align-items:center;gap:12px;padding:15px 16px;cursor:pointer;font-weight:500;font-size:1.02rem}.hl .sec>summary::-webkit-details-marker{display:none}\n.hl .ic{width:36px;height:36px;border-radius:12px;background:var(--accent-soft);color:var(--accent);display:grid;place-items:center;font-size:19px}\n.hl .cnt{color:var(--muted);font-weight:400;font-size:.86rem}\n.hl .chev{margin-inline-start:auto;color:var(--muted);font-size:18px;transition:transform .18s}.hl .sec[open]>summary .chev{transform:rotate(180deg)}\n.hl .body{padding:0 16px 20px;display:grid;gap:12px}.hl .body h4{font-size:.9rem;font-weight:600;color:var(--accent);margin:6px 0 0}\n.hl .plain{margin:0;padding-inline-start:20px;display:grid;gap:7px}\n.hl .holdings{list-style:none;margin:0;padding:0;display:grid;gap:14px}.hl .holdings li{padding-inline-start:14px;border-inline-start:3px solid var(--accent-soft)}.hl .holdings b{display:block;font-weight:600}\n.hl .clause{background:var(--rule-soft);border-radius:16px;padding:14px 16px}.hl .clause .lbl{font-weight:600;font-size:.9rem}.hl .clause ol{margin:8px 0 0;padding-inline-start:20px;display:grid;gap:5px}\n.hl .justices{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(190px,1fr))}\n.hl .justice{border:1px solid var(--rule);border-radius:16px;padding:14px;background:var(--paper);min-width:0}\n.hl .justice header{display:flex;justify-content:space-between;align-items:baseline;gap:8px}.hl .justice h5{font-family:var(--display);font-weight:400;font-size:1.2rem}\n.hl .tag{font-size:.74rem;color:var(--muted);font-weight:500}.hl .tag.solo{color:var(--amber)}\n.hl .theory{font-weight:600;font-size:.9rem;color:var(--accent);margin:4px 0}.hl .justice p{font-size:.92rem}\n.hl .quote{font-family:var(--display);font-size:1.3rem;line-height:1.55;padding:4px 18px 4px 0;border-right:4px solid var(--b)}.hl .quote-src{font-size:.86rem;color:var(--muted)}\n.hl .layer{background:var(--violet-soft);border-radius:16px;padding:14px 16px;display:grid;gap:6px}.hl .layer .lbl{color:var(--violet);font-weight:600;font-size:.9rem}\n.hl .path{display:flex;flex-wrap:wrap;gap:6px;align-items:center;list-style:none;margin:0;padding:0}\n.hl .path li{font-size:.86rem;border:1px solid var(--rule);border-radius:999px;padding:4px 12px;background:var(--paper)}\n.hl .path li.here{background:var(--accent);color:var(--on-accent);border-color:var(--accent);font-weight:500}.hl .path li.arr{border:0;padding:0;background:none;color:var(--muted)}\n.hl .qa{border:1px solid var(--rule);border-radius:16px;background:var(--paper)}\n.hl .qa summary{list-style:none;cursor:pointer;padding:13px 15px;display:grid;gap:8px}.hl .qa summary::-webkit-details-marker{display:none}\n.hl .qa .open{font-size:.82rem;color:var(--accent);font-weight:600}.hl .qa[open] .open{display:none}.hl .qa .ans{padding:0 15px 15px}\n.hl .related{display:grid;gap:8px}.hl .rel{display:grid;gap:2px;border:1px solid var(--rule);border-radius:16px;background:var(--paper);padding:11px 14px;text-align:right}\n.hl .rel.go{cursor:pointer}.hl .rel.go:hover{border-color:var(--accent)}\n.hl .kw{font-size:.78rem;color:var(--accent);font-weight:600}.hl .rel b{font-weight:600}.hl .rel p{font-size:.9rem;color:var(--muted)}\n.hl .sources{margin:0;padding-inline-start:20px;font-size:.92rem;display:grid;gap:4px}\n@media (max-width:520px){.hl .fact{flex-basis:100%}.hl .seal{width:70px;height:70px}}\n@media print{.hl .switch,.hl .actions{display:none}}";
  var FONTS = "https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600&family=Suez+One&display=swap";
  var HEB = /[א-ת]/;
  var DOCKET_LEAD = /^\s*([^\s.]{1,8}\s+\d{1,6}\/\d{2,4})\.\s*/;

  function esc(s) {
    return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
  }
  function rich(s) {
    return esc(s).replace(/==(.+?)==/g, "<mark>$1</mark>").replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\[\[(.+?)\]\]/g, '<span class="pin">$1</span>');
  }
  function icon(name) { return '<i class="ti ti-' + name + '" aria-hidden="true"></i>'; }
  function section(title, ic, body, count) {
    var cnt = count != null ? '<span class="cnt">' + count + "</span>" : "";
    return '<details class="sec" open><summary><span class="ic">' + icon(ic) + "</span><span>" + esc(title) + "</span>" + cnt +
      '<i class="ti ti-chevron-down chev" aria-hidden="true"></i></summary><div class="body">\n' + body + "\n</div></details>";
  }
  function seal(id, letter) {
    return '<svg class="seal" data-seal="' + esc(id) + '" viewBox="-50 -50 100 100" aria-hidden="true">' +
      '<circle class="disc" r="47"></circle><path class="sg p1" stroke-width="0.7" opacity="0.9"></path>' +
      '<path class="sg p2" stroke-width="0.55" opacity="0.65"></path><circle class="sg" r="47" stroke-width="1.4"></circle>' +
      '<circle class="sg" r="22" stroke-width="0.8" opacity="0.6"></circle><circle r="20" fill="var(--card)"></circle>' +
      '<text class="ltr" x="0" y="1" text-anchor="middle" dominant-baseline="central" font-size="24">' + esc(letter) + "</text></svg>";
  }
  function li(x) { return "<li>" + rich(x) + "</li>"; }

  function html(c) {
    var vol = c.course === "torts" ? "torts" : "corp";
    var docket = c.docket || c.cite;
    var sm = docket.match(/\d+\/\d+|\d+-\d+-\d+/);
    var sealId = sm ? sm[0] : docket;
    var lm = String(c.short).match(HEB) || String(c.name || "").match(HEB);
    var letter = lm ? lm[0] : "?";
    var holdings = c.holdings || [];
    var keys = c.keys || [0, 1, 2];
    var parts = [];

    var crumbs = c.courseName ? ['<span><i class="dot"></i>' + esc(c.courseName) + "</span>"] : [];
    if (c.chapter) crumbs.push("<span>" + esc(c.chapter) + "</span>");
    parts.push('<div class="hl" data-vol="' + vol + '">');
    if (crumbs.length) parts.push('<div class="crumbs">' + crumbs.join("") + "</div>");

    var facts = (c.meta || []).map(function (m) { return '<div class="fact"><dt>' + esc(m[0]) + "</dt><dd>" + rich(m[1]) + "</dd></div>"; }).join("");
    var trust = c.draft
      ? '<span class="trust draft">' + icon("alert-triangle") + "טיוטה, לא נבדק מול הנוסח</span>"
      : '<span class="trust">' + icon("shield-check") + esc(c.status) + "</span>";
    parts.push('<header class="case-h">\n' +
      '<div class="row"><div><p class="sub">' + esc(c.eyebrow) + "</p><h1>" + esc(c.short) + "</h1></div>" + seal(sealId, letter) + "</div>\n" +
      '<p class="aka">' + rich(c.aka) + "</p>\n" +
      '<dl class="facts">' + facts + "</dl>\n" +
      '<p class="cite">' + esc(c.cite) + "</p>\n" +
      '<div class="statusrow">' + trust + '<button type="button" class="switch" role="switch" aria-checked="true" data-act="pins">' +
      '<i aria-hidden="true"></i>מראי מקום</button></div>\n</header>');

    var keyItems = keys.filter(function (k) { return k >= 0 && k < holdings.length; }).map(function (k) {
      return "<li>" + icon("circle-check") + "<span><b>" + esc(holdings[k][0]) + '</b><span class="txt">' + rich(holdings[k][1]) + "</span></span></li>";
    }).join("\n");
    var report = "מצאתי טעות בכרטיס של " + docket + ". בוא נבדוק אותו שוב מול הנוסח";
    parts.push('<section class="brief" aria-label="בקצרה">\n' +
      '<div><h3>ההלכה בשורה אחת</h3><p class="lead">' + rich(c.oneLine) + "</p></div>\n" +
      '<div><h3>שלוש הלכות לזכור</h3><ul class="keys">\n' + keyItems + "\n</ul></div>\n" +
      '<div class="write"><div class="head"><h3>מה לכתוב במבחן</h3><button type="button" class="btn ghost" data-act="copy">' +
      icon("copy") + '<span>העתקה</span></button></div><p data-write>' + rich(c.exam.write) + "</p></div>\n" +
      '<div class="actions"><button type="button" class="btn" data-act="print">' + icon("printer") + "הדפסה</button>" +
      '<button type="button" class="btn ghost" data-prompt="' + esc(report) + '">' + icon("flag") + "דיווח על טעות ↗</button></div>\n" +
      "</section>");

    var secs = [], body;
    body = (c.background || []).map(function (p) { return "<p>" + rich(p) + "</p>"; }).join("\n");
    if ((c.questions || []).length) body += '\n<h4>השאלות המשפטיות</h4><ul class="plain">' + c.questions.map(li).join("") + "</ul>";
    secs.push(section("רקע והשאלות", "book", body));
    secs.push(section("ההכרעה", "gavel", "<p>" + rich(c.decision) + "</p>"));

    body = '<ul class="holdings">\n' + holdings.map(function (h) { return "<li><b>" + esc(h[0]) + "</b>" + rich(h[1]) + "</li>"; }).join("\n") + "\n</ul>";
    var cl = c.clause;
    if (cl) {
      body += '\n<div class="clause"><p class="lbl">' + esc(cl.label) + "</p><ol>" + cl.items.map(li).join("") + "</ol>" +
        (cl.after ? "<p>" + rich(cl.after) + "</p>" : "") + "</div>";
    }
    secs.push(section("כל ההלכות", "list", body, holdings.length));

    var js = c.justices || [];
    if (js.length) {
      body = '<div class="justices">\n' + js.map(function (j) {
        return '<div class="justice"><header><h5>' + esc(j.name) + '</h5><span class="tag' + (j.solo ? " solo" : "") + '">' + esc(j.tag) + "</span></header>" +
          '<p class="theory">' + esc(j.theory) + "</p><p>" + rich(j.text) + "</p></div>";
      }).join("\n") + "\n</div>";
      if (c.common) body += "\n<p>" + rich(c.common) + "</p>";
      if (c.quote) body += '\n<p class="quote">' + rich(c.quote.text) + '</p>\n<p class="quote-src">' + rich(c.quote.src) + "</p>";
      secs.push(section(c.justicesTitle || "מי אמר מה", "users", body, js.length));
    }

    var ly = c.layer;
    if (ly && (ly.reading || ly.note)) {
      var inner = ly.title ? '<p class="lbl">' + esc(ly.title) + "</p>" : "";
      ["reading", "note"].forEach(function (k) { if (ly[k]) inner += "<p>" + rich(ly[k]) + "</p>"; });
      secs.push(section("בקורס של המרצה", "school", '<div class="layer">' + inner + "</div>"));
    }

    var ex = c.exam;
    var steps = ex.path.map(function (p, i) { return i === ex.here ? '<li class="here">' + esc(p) + "</li>" : "<li>" + esc(p) + "</li>"; })
      .join('<li class="arr" aria-hidden="true">←</li>');
    body = "<h4>" + esc(ex.pathLabel) + '</h4><ol class="path">' + steps + "</ol>";
    if ((ex.traps || []).length) body += '\n<h4>מלכודות שמורידות נקודות</h4><ul class="plain">\n' + ex.traps.map(li).join("\n") + "\n</ul>";
    secs.push(section("למבחן", "target", body));

    var pr = c.practice || [];
    if (pr.length) {
      body = pr.map(function (p) {
        return '<details class="qa"><summary><span>' + rich(p.q) + '</span><span class="open">הצגת ראשי פרקים</span></summary>' +
          '<div class="ans"><ul class="plain">' + p.a.map(li).join("") + "</ul></div></details>";
      }).join("\n");
      secs.push(section("תרגול", "help", body, pr.length));
    }

    var rel = c.related || [];
    if (rel.length) {
      body = '<div class="related">\n' + rel.map(function (r) {
        var m = String(r[2]).match(DOCKET_LEAD);
        if (m) {
          var ask = "נתח את " + m[1] + " " + String(r[0]).replace(/\s*\(\s*\d+\/\d+\s*\)/g, "");
          return '<div class="rel go" data-prompt="' + esc(ask) + '"><span class="kw">' + esc(r[1]) + "</span><b>" + esc(r[0]) + " ↗</b><p>" + rich(r[2]) + "</p></div>";
        }
        return '<div class="rel"><span class="kw">' + esc(r[1]) + "</span><b>" + esc(r[0]) + "</b><p>" + rich(r[2]) + "</p></div>";
      }).join("\n") + "\n</div>";
      secs.push(section("פסקי דין קשורים", "link", body));
    }

    if (c.context) secs.push(section("הקשר אקטואלי", "world", "<p>" + rich(c.context) + "</p>"));

    var src = (c.sources || []).map(function (s) {
      return Array.isArray(s) ? '<li><a href="' + esc(s[1]) + '">' + esc(s[0]) + "</a></li>" : "<li>" + rich(s) + "</li>";
    }).join("");
    secs.push(section("מקורות", "file-text", '<ul class="sources">' + src + "</ul>"));

    parts.push('<div class="sections">\n' + secs.join("\n") + "\n</div>\n</div>");
    return parts.join("\n");
  }

  function rng(s) { var h = 2166136261 >>> 0; for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; } return function () { h = (h + 0x6d2b79f5) >>> 0; var t = h; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function tr(n, d, sc, rot, st) { var r = 1 / n, k = n - 1, p = [], m = (1 - r) + d * r, c = Math.cos(rot), s = Math.sin(rot); for (var i = 0; i <= st; i++) { var t = 2 * Math.PI * i / st, x = (1 - r) * Math.cos(t) + d * r * Math.cos(k * t), y = (1 - r) * Math.sin(t) - d * r * Math.sin(k * t); p.push(((x * c - y * s) / m * sc).toFixed(2) + " " + ((x * s + y * c) / m * sc).toFixed(2)); } return "M" + p.join("L") + "Z"; }

  function wire(root) {
    var el = root.querySelector("[data-seal]");
    if (el) {
      var R = rng(el.getAttribute("data-seal")), n1 = 7 + Math.floor(R() * 7), n2 = n1 + 3 + Math.floor(R() * 5), d1 = .55 + R() * .4, d2 = .7 + R() * .3, rot = R() * Math.PI;
      el.querySelector(".p1").setAttribute("d", tr(n1, d1, 44, rot, 420));
      el.querySelector(".p2").setAttribute("d", tr(n2, d2, 39, -rot, 480));
    }
    var hl = root.querySelector(".hl");
    root.addEventListener("click", function (e) {
      var t = e.target.closest("[data-act],[data-prompt]");
      if (!t || !root.contains(t)) return;
      var act = t.getAttribute("data-act");
      if (t.hasAttribute("data-prompt")) {
        if (typeof window.sendPrompt === "function") window.sendPrompt(t.getAttribute("data-prompt"));
      } else if (act === "pins") {
        var on = t.getAttribute("aria-checked") !== "true";
        t.setAttribute("aria-checked", String(on));
        hl.classList.toggle("no-pins", !on);
      } else if (act === "print") {
        window.print();
      } else if (act === "copy") {
        var w = root.querySelector("[data-write]").cloneNode(true);
        w.querySelectorAll(".pin").forEach(function (x) { x.remove(); });
        var txt = w.textContent.replace(/\s+/g, " ").trim(), lab = t.querySelector("span");
        var done = function () { lab.textContent = "הועתק"; setTimeout(function () { lab.textContent = "העתקה"; }, 1600); };
        if (navigator.clipboard) navigator.clipboard.writeText(txt).then(done, function () {});
      }
    });
  }

  function styles() {
    if (document.getElementById("hl-style")) return;
    var l = document.createElement("link");
    l.rel = "stylesheet"; l.href = FONTS;
    document.head.appendChild(l);
    var s = document.createElement("style");
    s.id = "hl-style"; s.textContent = CSS;
    document.head.appendChild(s);
  }

  function render(data, root) {
    root = root || document.getElementById("hl-root");
    if (!root || !data) return;
    styles();
    root.innerHTML = html(data);
    wire(root);
  }

  window.HLCard = { render: render, html: html, version: "card-v1" };
  if (window.HLData) render(window.HLData);
})();
