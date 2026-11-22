/* Ruling card of ספריית ההלכות, drawn in the page from the card JSON.
   The one renderer of the card. tools/card/build.py adds the style from card.css and writes
   card/card.js (served by jsDelivr) and the skill's assets/card.js (inlined by render.py --inline).
   Usage in a widget
     <div id="hl-root"></div>
     <script>window.HLData={...card json...};if(window.HLCard)HLCard.render(window.HLData)</script>
     <script src="https://cdn.jsdelivr.net/gh/idob4474/rulings-index@COMMIT/card/card.js"></script> */
(function () {
  "use strict";
  var CSS = ".hl{--t1:#1f1e1d;--t2:#5f5e5a;--t3:#6f6e69;--bd:rgba(31,30,29,.14);--bd2:rgba(31,30,29,.26);--nb:rgba(31,30,29,.05);--bg:#ffffff;--hi:rgba(239,159,39,.2);--ok:#3B6D11;--okbg:#EAF3DE;--wn:#854F0B;--wnbg:#FAEEDA;--link:#185FA5;--knob:#ffffff;--ac:#993556;--acbg:#FBEAF0;--display:\"Suez One\",serif;color-scheme:light}\n.hl[data-vol=corp]{--ac:#854F0B;--acbg:#FAEEDA}\n.hl.dk{--t1:#f5f4ef;--t2:#c3c1b8;--t3:#a09e96;--bd:rgba(255,255,255,.13);--bd2:rgba(255,255,255,.26);--nb:rgba(255,255,255,.065);--bg:#262624;--hi:rgba(239,159,39,.22);--ok:#97C459;--okbg:rgba(99,153,34,.2);--wn:#FAC775;--wnbg:rgba(186,117,23,.22);--link:#85B7EB;--knob:#1f1e1d;--ac:#ED93B1;--acbg:rgba(212,83,126,.22);color-scheme:dark}\n.hl.dk[data-vol=corp]{--ac:#FAC775;--acbg:rgba(186,117,23,.22)}\n.hl.solid{background:var(--bg);border:.5px solid var(--bd);border-radius:12px;padding:16px}\n.hl{direction:rtl;text-align:right;font-family:\"Rubik\",var(--font-sans,system-ui),sans-serif;color:var(--t1);font-size:15px;line-height:1.7;padding:4px 0 8px}\n.hl *{box-sizing:border-box}.hl p,.hl h1,.hl h3,.hl h4,.hl h5{margin:0}.hl h1,.hl h3,.hl h4,.hl h5{color:var(--t1)}.hl strong,.hl b{font-weight:500}\n.hl mark{background:var(--hi);color:inherit;padding:1px 0;border-radius:3px;-webkit-box-decoration-break:clone;box-decoration-break:clone}\n.hl .pin{display:inline-block;font-size:11px;line-height:17px;font-weight:400;color:var(--t2);background:var(--nb);border-radius:4px;padding:0 5px;margin-inline-start:4px;white-space:nowrap;vertical-align:1px;font-variant-numeric:tabular-nums}\n.hl .pin+.pin{margin-inline-start:2px}.hl.no-pins .pin{display:none}\n.hl .top{display:flex;flex-wrap:wrap;align-items:center;gap:2px 8px;font-size:13px;color:var(--t2)}\n.hl .vol{display:inline-flex;align-items:center;gap:6px;color:var(--ac);font-weight:500}.hl .vol::before{content:\"\";width:7px;height:7px;border-radius:50%;background:currentColor}\n.hl .top .sep{color:var(--t3)}\n.hl h1{font-family:var(--display);font-weight:400;font-size:30px;line-height:1.25;margin-top:6px}\n.hl .aka{color:var(--t2);font-size:14px;line-height:1.6;margin-top:2px}\n.hl .lead{margin-top:16px;font-size:17px;line-height:1.8}\n.hl .facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:18px 0 0}\n.hl .fact{background:var(--nb);border-radius:8px;padding:8px 12px;min-width:0}\n.hl .fact dt{font-size:12px;color:var(--t2)}.hl .fact dd{margin:0;font-size:14px;font-weight:500;line-height:1.5}\n.hl .meta{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin-top:12px}.hl .meta .end{margin-inline-start:auto;display:flex;align-items:center;gap:6px}\n.hl .trust{display:inline-flex;align-items:center;gap:5px;font-size:12px;font-weight:500;line-height:1.5;color:var(--ok);background:var(--okbg);border-radius:6px;padding:3px 8px}\n.hl .trust.draft{color:var(--wn);background:var(--wnbg)}.hl .trust i{font-size:15px}\n.hl .switch{display:inline-flex;align-items:center;gap:8px;font:inherit;font-size:13px;color:var(--t2);background:none;border:0;box-shadow:none;height:36px;min-height:0;padding:0 4px;border-radius:8px;cursor:pointer}\n.hl .switch i{width:30px;height:18px;border-radius:999px;background:var(--bd2);position:relative;flex:none;transition:background .15s}\n.hl .switch i::after{content:\"\";position:absolute;top:2px;right:2px;width:14px;height:14px;border-radius:50%;background:var(--knob);transition:right .15s}\n.hl .switch[aria-checked=true] i{background:var(--ac)}.hl .switch[aria-checked=true] i::after{right:14px}\n.hl .cite{font-size:12px;line-height:1.5;color:var(--t3);margin-top:10px}\n.hl .lbl{font-size:13px;font-weight:500;color:var(--ac);margin-bottom:10px}\n.hl .keys-b{margin-top:26px}\n.hl .keys{list-style:none;margin:0;padding:0;display:grid;gap:14px;counter-reset:k}\n.hl .keys li{display:grid;grid-template-columns:24px minmax(0,1fr);gap:10px;counter-increment:k}\n.hl .keys li::before{content:counter(k);width:24px;height:24px;border-radius:50%;background:var(--acbg);color:var(--ac);font-size:13px;font-weight:500;line-height:24px;text-align:center;margin-top:1px}\n.hl .keys b{display:block}\n.hl .write{margin-top:22px;background:var(--nb);border-radius:12px;padding:12px 16px 14px}\n.hl .write .head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:4px}.hl .write .lbl{margin:0}\n.hl .actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}\n.hl .btn{display:inline-flex;align-items:center;gap:6px;height:34px;min-height:0;padding:0 12px;border:.5px solid var(--bd2);border-radius:var(--radius,8px);background:transparent;box-shadow:none;color:var(--t1);font:inherit;font-size:14px;line-height:1;cursor:pointer}\n.hl .btn:hover{background:var(--nb)}.hl .btn i{font-size:17px;color:var(--t2)}\n.hl .btn.sm{height:36px;padding:0 8px;font-size:13px;border-color:transparent}\n.hl .sections{margin-top:26px;border-top:.5px solid var(--bd)}\n.hl .sec{border-bottom:.5px solid var(--bd)}\n.hl .sec>summary{list-style:none;display:flex;align-items:center;gap:10px;padding:13px 0;cursor:pointer;font-size:16px;font-weight:500}\n.hl .sec>summary::-webkit-details-marker{display:none}\n.hl .sec>summary>.ic{font-size:19px;color:var(--ac)}\n.hl .cnt{font-size:13px;font-weight:400;color:var(--t3)}\n.hl .chev{margin-inline-start:auto;font-size:18px;color:var(--t3);transition:transform .15s}.hl .sec[open]>summary .chev{transform:rotate(180deg)}\n.hl .body{padding:0 0 20px;display:grid;gap:12px}\n.hl .body h4{font-size:13px;font-weight:500;color:var(--t2);margin-top:4px}\n.hl ul.plain,.hl ol.plain{margin:0;padding-inline-start:18px;display:grid;gap:8px}.hl .plain li::marker{color:var(--t3)}\n.hl .holdings{list-style:none;margin:0;padding:0;display:grid;gap:14px}.hl .holdings b{display:block}\n.hl .box{background:var(--nb);border-radius:12px;padding:12px 16px;display:grid;gap:6px}.hl .box .lbl{margin:0}\n.hl .box ol{margin:0;padding-inline-start:20px;display:grid;gap:4px}\n.hl .justice{padding:14px 0;border-top:.5px solid var(--bd)}.hl .justice:first-child{border-top:0;padding-top:0}\n.hl .justice header{display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px}\n.hl .justice h5{font-size:16px;font-weight:500}\n.hl .tag{font-size:12px;line-height:1.5;color:var(--t2);background:var(--nb);border-radius:6px;padding:1px 7px}\n.hl .tag.solo{color:var(--wn);background:var(--wnbg)}\n.hl .theory{font-size:14px;font-weight:500;color:var(--ac);margin:4px 0 2px}\n.hl blockquote{margin:4px 0 0;padding:2px 14px 2px 0;border-right:2px solid var(--ac);border-radius:0;font-size:17px;line-height:1.75}\n.hl .quote-src{font-size:13px;color:var(--t2)}\n.hl .path{display:flex;flex-wrap:wrap;align-items:center;gap:6px;list-style:none;margin:0;padding:0}\n.hl .path li{font-size:13px;line-height:1.5;border:.5px solid var(--bd2);border-radius:999px;padding:3px 10px;color:var(--t2)}\n.hl .path li.here{background:var(--acbg);color:var(--ac);border-color:transparent;font-weight:500}\n.hl .path li.arr{border:0;padding:0;color:var(--t3);font-size:14px}\n.hl .traps li::marker{color:var(--wn)}\n.hl .qa{border:.5px solid var(--bd);border-radius:8px}\n.hl .qa summary{list-style:none;cursor:pointer;padding:12px 14px;display:grid;gap:6px}.hl .qa summary::-webkit-details-marker{display:none}\n.hl .qa .open{font-size:13px;color:var(--ac);font-weight:500}.hl .qa[open] .open{display:none}.hl .qa .ans{padding:0 14px 14px}\n.hl .rel{display:grid;gap:2px;padding:12px 0;border-top:.5px solid var(--bd)}.hl .rel:first-child{border-top:0;padding-top:0}\n.hl .rel.go{cursor:pointer}.hl .rel.go:hover b{color:var(--ac)}\n.hl .kw{font-size:12px;font-weight:500;color:var(--ac)}.hl .rel p{font-size:14px;color:var(--t2)}\n.hl .sources{margin:0;padding-inline-start:18px;font-size:14px;display:grid;gap:4px;color:var(--t2)}.hl .sources a{color:var(--link)}\n.hl .mode{width:36px;height:36px;padding:0;justify-content:center;border-color:transparent}.hl .mode i{font-size:18px}\n.hl button:focus-visible,.hl summary:focus-visible,.hl .rel.go:focus-visible{outline:2px solid var(--ac);outline-offset:2px}\n@media print{.hl.solid{border:0;padding:0}.hl .mode,.hl .switch,.hl .actions,.hl .chev,.hl .write .btn{display:none}}";
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


  /* Lecture card. c.type = "lecture". Same header, pins, switch and sections as the ruling card.
     Fields: courseName, chapter, eyebrow, short (topic), aka, oneLine (core), meta, cite, status, draft,
     keys [3 indexes into concepts], concepts [[title, text]], outline [[title, text]], cases [[name, kw, text]],
     open [text], verify [text], traps [text], write, practice [{q, a[]}], sources */
  function lectureHtml(c) {
    var concepts = c.concepts || [], keys = c.keys || [0, 1, 2], parts = [];
    var top = [];
    if (c.courseName) top.push('<span class="vol">' + esc(c.courseName) + "</span>");
    [c.chapter, c.eyebrow].forEach(function (x) { if (x) top.push("<span>" + esc(x) + "</span>"); });
    var facts = (c.meta || []).map(function (m) { return '<div class="fact"><dt>' + esc(m[0]) + "</dt><dd>" + rich(m[1]) + "</dd></div>"; }).join("");
    var trust = c.draft
      ? '<span class="trust draft">' + icon("alert-triangle") + "טיוטה, לא נבדק מול ההרצאה</span>"
      : '<span class="trust">' + icon("shield-check") + esc(c.status) + "</span>";
    parts.push('<div class="hl" data-vol="corp">');
    parts.push("<header>\n" + (top.length ? '<div class="top">' + top.join('<span class="sep">·</span>') + "</div>\n" : "") +
      "<h1>" + esc(c.short) + "</h1>\n" + '<p class="aka">' + rich(c.aka) + "</p>\n" + '<p class="lead">' + rich(c.oneLine) + "</p>\n" +
      '<dl class="facts">' + facts + "</dl>\n" +
      '<div class="meta">' + trust + '<div class="end"><button type="button" class="switch" role="switch" aria-checked="true" data-act="pins">' +
      '<i aria-hidden="true"></i>מראי מקום</button>' +
      '<button type="button" class="btn mode" data-act="mode" aria-label="מצב כהה" title="מצב כהה">' + icon("moon") + "</button></div></div>\n" +
      (c.cite ? '<p class="cite">' + esc(c.cite) + "</p>\n" : "") + "</header>");
    var keyItems = keys.filter(function (k) { return k >= 0 && k < concepts.length; }).map(function (k) {
      return "<li><div><b>" + esc(concepts[k][0]) + "</b>" + rich(concepts[k][1]) + "</div></li>";
    }).join("\n");
    parts.push('<section class="keys-b"><h3 class="lbl">שלושת הרעיונות לזכור</h3><ol class="keys">\n' + keyItems + "\n</ol></section>");
    if (c.write) parts.push('<section class="write"><div class="head"><h3 class="lbl">מה לכתוב במבחן</h3><button type="button" class="btn sm" data-act="copy">' +
      icon("copy") + '<span>העתקה</span></button></div><p data-write>' + rich(c.write) + "</p></section>");
    var report = "מצאתי טעות בסיכום של " + (c.short || "ההרצאה") + ". בוא נבדוק אותו שוב מול ההרצאה";
    parts.push('<div class="actions"><button type="button" class="btn" data-prompt="' + esc(report) + '">' + icon("flag") + "דיווח על טעות ↗</button>" +
      '<button type="button" class="btn" data-act="print">' + icon("printer") + "הדפסה</button></div>");
    var secs = [], body;
    var ol = c.outline || [];
    if (ol.length) secs.push(section("מהלך ההרצאה", "list-details", "<div>\n" + ol.map(function (o) {
      return '<div class="rel"><b>' + esc(o[0]) + "</b><p>" + rich(o[1]) + "</p></div>"; }).join("\n") + "\n</div>", ol.length));
    if (concepts.length) secs.push(section("מושגים והלכות", "bulb", '<ul class="holdings">\n' + concepts.map(function (h) {
      return "<li><b>" + esc(h[0]) + "</b>" + rich(h[1]) + "</li>"; }).join("\n") + "\n</ul>", concepts.length));
    var cs = c.cases || [];
    if (cs.length) secs.push(section("פסיקה שהוזכרה", "gavel", "<div>\n" + cs.map(function (r) {
      var m = String(r[2]).match(DOCKET_LEAD);
      if (m) { var ask = "נתח את " + m[1] + " " + String(r[0]).replace(/\s*\(\s*\d+\/\d+\s*\)/g, "");
        return '<div class="rel go" role="button" tabindex="0" data-prompt="' + esc(ask) + '"><span class="kw">' + esc(r[1]) + "</span><b>" + esc(r[0]) + " ↗</b><p>" + rich(r[2]) + "</p></div>"; }
      return '<div class="rel"><span class="kw">' + esc(r[1]) + "</span><b>" + esc(r[0]) + "</b><p>" + rich(r[2]) + "</p></div>";
    }).join("\n") + "\n</div>", cs.length));
    if ((c.open || []).length) secs.push(section("שאלות פתוחות ומחלוקות", "help-circle", '<ul class="plain">' + c.open.map(li).join("") + "</ul>"));
    if ((c.traps || []).length) secs.push(section("מלכודות למבחן", "target", '<ul class="plain traps">\n' + c.traps.map(li).join("\n") + "\n</ul>"));
    if ((c.verify || []).length) secs.push(section("לאימות מול המקור", "alert-circle", '<ul class="plain">' + c.verify.map(li).join("") + "</ul>"));
    var pr = c.practice || [];
    if (pr.length) secs.push(section("תרגול", "help", pr.map(function (p) {
      return '<details class="qa"><summary><span>' + rich(p.q) + '</span><span class="open">הצגת ראשי פרקים</span></summary>' +
        '<div class="ans"><ul class="plain">' + p.a.map(li).join("") + "</ul></div></details>"; }).join("\n"), pr.length));
    var src = (c.sources || []).map(function (x) { return Array.isArray(x) ? '<li><a href="' + esc(x[1]) + '">' + esc(x[0]) + "</a></li>" : "<li>" + rich(x) + "</li>"; }).join("");
    if (src) secs.push(section("מקורות", "file-text", '<ul class="sources">' + src + "</ul>"));
    parts.push('<div class="sections">\n' + secs.join("\n") + "\n</div>\n</div>");
    return parts.join("\n");
  }

  function html(c) {
    if (c.type === "lecture") return lectureHtml(c);
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

  window.HLCard = { render: render, html: html, version: "card-v3" };
  if (window.HLData) render(window.HLData);
})();
