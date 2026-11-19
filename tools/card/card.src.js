/* Ruling card of ספריית ההלכות, drawn in the page from the card JSON.
   Mirror of ruling-analyzer/scripts/render.py. Keep the two in step.
   Usage in a widget
     <div id="hl-root"></div>
     <script>window.HLData={...card json...};if(window.HLCard)HLCard.render(window.HLData)</script>
     <script src="https://cdn.jsdelivr.net/gh/idob4474/rulings-index@COMMIT/card/card.js"></script> */
(function () {
  "use strict";
  var CSS = __CSS__;
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

  window.HLCard = { render: render, html: html, version: __VERSION__ };
  if (window.HLData) render(window.HLData);
})();
