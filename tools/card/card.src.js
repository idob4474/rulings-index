/* Ruling card of ספריית ההלכות, drawn in the page from the card JSON.
   The one renderer of the card. tools/card/build.py adds the style from card.css and writes
   card/card.js (served by jsDelivr) and the skill's assets/card.js (inlined by render.py --inline).
   Usage in a widget
     <div id="hl-root"></div>
     <script>window.HLData={...card json...};if(window.HLCard)HLCard.render(window.HLData)</script>
     <script src="https://cdn.jsdelivr.net/gh/idob4474/rulings-index@COMMIT/card/card.js"></script> */
(function () {
  "use strict";
  var CSS = __CSS__;
  var FONTS = "https://fonts.googleapis.com/css2?family=Rubik:wght@400;500&family=Suez+One&display=swap";
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
    return '<details class="sec" open><summary><i class="ti ti-' + ic + ' ic" aria-hidden="true"></i><span>' + esc(title) + "</span>" + cnt +
      '<i class="ti ti-chevron-down chev" aria-hidden="true"></i></summary><div class="body">\n' + body + "\n</div></details>";
  }
  function li(x) { return "<li>" + rich(x) + "</li>"; }

  function html(c) {
    var vol = c.course === "torts" ? "torts" : "corp";
    var docket = c.docket || c.cite;
    var holdings = c.holdings || [];
    var keys = c.keys || [0, 1, 2];
    var parts = [];

    var top = [];
    if (c.courseName) top.push('<span class="vol">' + esc(c.courseName) + "</span>");
    [c.chapter, c.eyebrow].forEach(function (x) { if (x) top.push("<span>" + esc(x) + "</span>"); });
    var facts = (c.meta || []).map(function (m) { return '<div class="fact"><dt>' + esc(m[0]) + "</dt><dd>" + rich(m[1]) + "</dd></div>"; }).join("");
    var trust = c.draft
      ? '<span class="trust draft">' + icon("alert-triangle") + "טיוטה, לא נבדק מול הנוסח</span>"
      : '<span class="trust">' + icon("shield-check") + esc(c.status) + "</span>";
    parts.push('<div class="hl" data-vol="' + vol + '">');
    parts.push("<header>\n" +
      (top.length ? '<div class="top">' + top.join('<span class="sep">·</span>') + "</div>\n" : "") +
      "<h1>" + esc(c.short) + "</h1>\n" +
      '<p class="aka">' + rich(c.aka) + "</p>\n" +
      '<p class="lead">' + rich(c.oneLine) + "</p>\n" +
      '<dl class="facts">' + facts + "</dl>\n" +
      '<div class="meta">' + trust + '<div class="end"><button type="button" class="switch" role="switch" aria-checked="true" data-act="pins">' +
      '<i aria-hidden="true"></i>מראי מקום</button>' +
      '<button type="button" class="btn mode" data-act="mode" aria-label="מצב כהה" title="מצב כהה">' + icon("moon") + "</button></div></div>\n" +
      '<p class="cite">' + esc(c.cite) + "</p>\n</header>");

    var keyItems = keys.filter(function (k) { return k >= 0 && k < holdings.length; }).map(function (k) {
      return "<li><div><b>" + esc(holdings[k][0]) + "</b>" + rich(holdings[k][1]) + "</div></li>";
    }).join("\n");
    var report = "מצאתי טעות בכרטיס של " + docket + ". בוא נבדוק אותו שוב מול הנוסח";
    parts.push('<section class="keys-b"><h3 class="lbl">שלוש הלכות לזכור</h3><ol class="keys">\n' + keyItems + "\n</ol></section>");
    parts.push('<section class="write"><div class="head"><h3 class="lbl">מה לכתוב במבחן</h3><button type="button" class="btn sm" data-act="copy">' +
      icon("copy") + '<span>העתקה</span></button></div><p data-write>' + rich(c.exam.write) + "</p></section>");
    parts.push('<div class="actions"><button type="button" class="btn" data-prompt="' + esc(report) + '">' + icon("flag") + "דיווח על טעות ↗</button>" +
      '<button type="button" class="btn" data-act="print">' + icon("printer") + "הדפסה</button></div>");

    var secs = [], body;
    body = (c.background || []).map(function (p) { return "<p>" + rich(p) + "</p>"; }).join("\n");
    if ((c.questions || []).length) body += '\n<h4>השאלות המשפטיות</h4><ul class="plain">' + c.questions.map(li).join("") + "</ul>";
    secs.push(section("רקע והשאלות", "book", body));
    secs.push(section("ההכרעה", "gavel", "<p>" + rich(c.decision) + "</p>"));

    body = '<ul class="holdings">\n' + holdings.map(function (h) { return "<li><b>" + esc(h[0]) + "</b>" + rich(h[1]) + "</li>"; }).join("\n") + "\n</ul>";
    var cl = c.clause;
    if (cl) {
      body += '\n<div class="box"><p class="lbl">' + esc(cl.label) + "</p><ol>" + cl.items.map(li).join("") + "</ol>" +
        (cl.after ? "<p>" + rich(cl.after) + "</p>" : "") + "</div>";
    }
    secs.push(section("כל ההלכות", "list", body, holdings.length));

    var js = c.justices || [];
    if (js.length) {
      body = "<div>\n" + js.map(function (j) {
        return '<div class="justice"><header><h5>' + esc(j.name) + '</h5><span class="tag' + (j.solo ? " solo" : "") + '">' + esc(j.tag) + "</span></header>" +
          '<p class="theory">' + esc(j.theory) + "</p><p>" + rich(j.text) + "</p></div>";
      }).join("\n") + "\n</div>";
      if (c.common) body += "\n<p>" + rich(c.common) + "</p>";
      if (c.quote) body += "\n<blockquote>" + rich(c.quote.text) + '</blockquote>\n<p class="quote-src">' + rich(c.quote.src) + "</p>";
      secs.push(section(c.justicesTitle || "מי אמר מה", "users", body, js.length));
    }

    var ly = c.layer;
    if (ly && (ly.reading || ly.note)) {
      var inner = ly.title ? '<p class="lbl">' + esc(ly.title) + "</p>" : "";
      ["reading", "note"].forEach(function (k) { if (ly[k]) inner += "<p>" + rich(ly[k]) + "</p>"; });
      secs.push(section("בקורס של המרצה", "school", '<div class="box">' + inner + "</div>"));
    }

    var ex = c.exam;
    var steps = ex.path.map(function (p, i) { return i === ex.here ? '<li class="here">' + esc(p) + "</li>" : "<li>" + esc(p) + "</li>"; })
      .join('<li class="arr" aria-hidden="true">←</li>');
    body = "<h4>" + esc(ex.pathLabel) + '</h4><ol class="path">' + steps + "</ol>";
    if ((ex.traps || []).length) body += '\n<h4>מלכודות שמורידות נקודות</h4><ul class="plain traps">\n' + ex.traps.map(li).join("\n") + "\n</ul>";
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
      body = "<div>\n" + rel.map(function (r) {
        var m = String(r[2]).match(DOCKET_LEAD);
        if (m) {
          var ask = "נתח את " + m[1] + " " + String(r[0]).replace(/\s*\(\s*\d+\/\d+\s*\)/g, "");
          return '<div class="rel go" role="button" tabindex="0" data-prompt="' + esc(ask) + '"><span class="kw">' + esc(r[1]) + "</span><b>" + esc(r[0]) + " ↗</b><p>" + rich(r[2]) + "</p></div>";
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

  var KEY = "hl-theme";
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function store(v) { try { if (v) localStorage.setItem(KEY, v); else localStorage.removeItem(KEY); } catch (e) {} }
  // The chat's own theme. The host colors the text of the page, so light text means a dark chat.
  function chatDark() {
    var de = document.documentElement, mode = de.getAttribute("data-mode") || de.getAttribute("data-theme");
    if (mode === "dark") return true;
    if (mode === "light") return false;
    var m = (getComputedStyle(document.body || de).color || "").match(/\d+(\.\d+)?/g);
    if (m && m.length >= 3 && !(+m[0] === 0 && +m[1] === 0 && +m[2] === 0)) return (0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2]) / 255 > 0.5;
    return !!(window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches);
  }
  function theme(hl) {
    var pick = stored(), auto = chatDark(), dark = pick ? pick === "dark" : auto;
    hl.classList.toggle("dk", dark);
    hl.classList.toggle("solid", !!pick && dark !== auto);
    var b = hl.querySelector("[data-act=mode]");
    if (b) {
      var lab = dark ? "מצב בהיר" : "מצב כהה";
      b.innerHTML = icon(dark ? "sun" : "moon");
      b.setAttribute("aria-label", lab); b.setAttribute("title", lab);
    }
  }

  function wire(root) {
    var hl = root.querySelector(".hl");
    theme(hl);
    var again = function () { theme(hl); };
    if (window.matchMedia) { var mq = matchMedia("(prefers-color-scheme: dark)"); if (mq.addEventListener) mq.addEventListener("change", again); }
    if (window.MutationObserver) new MutationObserver(again).observe(document.documentElement, { attributes: true, attributeFilter: ["class", "data-mode", "data-theme", "style"] });
    root.addEventListener("keydown", function (e) {
      if ((e.key === "Enter" || e.key === " ") && e.target.matches(".rel.go")) { e.preventDefault(); e.target.click(); }
    });
    window.addEventListener("beforeprint", function () { root.querySelectorAll("details").forEach(function (d) { d.open = true; }); });
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
      } else if (act === "mode") {
        var next = hl.classList.contains("dk") ? "light" : "dark";
        store(next === (chatDark() ? "dark" : "light") ? null : next);
        theme(hl);
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
