/* Elitron Labs — site behaviour. No third-party scripts, no cookies. */
(function () {
  "use strict";
  document.documentElement.classList.add("js");
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var saveData = !!(navigator.connection && navigator.connection.saveData);

  /* Analytics hook: dispatches a DOM event only. Wire a consent-aware analytics
     provider to "elitron:track" if/when one is approved. Nothing is sent today. */
  function track(name, detail) {
    try { document.dispatchEvent(new CustomEvent("elitron:track", { detail: { name: name, data: detail || {} } })); } catch (e) {}
  }
  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest("[data-track]");
    if (el) track(el.getAttribute("data-track"));
  });

  /* Year */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* Header */
  var header = $(".site-header");
  var onScroll = function () { if (header) header.classList.toggle("scrolled", window.scrollY > 8); };
  onScroll(); window.addEventListener("scroll", onScroll, { passive: true });

  /* Mobile nav */
  var menuBtn = $(".menu-btn"), mobileNav = $("#mobile-nav");
  function setMenu(open) {
    if (!menuBtn || !mobileNav) return;
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    mobileNav.hidden = !open;
    document.body.style.overflow = open ? "hidden" : "";
  }
  if (menuBtn) {
    menuBtn.addEventListener("click", function () { setMenu(menuBtn.getAttribute("aria-expanded") !== "true"); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && menuBtn.getAttribute("aria-expanded") === "true") { setMenu(false); menuBtn.focus(); } });
    window.addEventListener("resize", function () { if (window.innerWidth > 960) setMenu(false); });
  }

  /* Reveal on scroll */
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add("in"); io.unobserve(x.target); } });
    }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });
    $$(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    $$(".reveal").forEach(function (el) { el.classList.add("in"); });
  }

  /* Video: attach sources only when motion is welcome, then fade in once playable */
  function loadVideo(v, onReady) {
    $$("source[data-src]", v).forEach(function (s) { s.src = s.getAttribute("data-src"); s.removeAttribute("data-src"); });
    v.addEventListener("canplay", function () {
      var p = v.play();
      if (p && p.then) p.then(function () { v.classList.add("ready"); if (onReady) onReady(); }).catch(function () {});
      else { v.classList.add("ready"); if (onReady) onReady(); }
    }, { once: true });
    v.load();
  }
  var motionOk = !reduceMotion && !saveData;
  var heroVideo = $("[data-hero-video]"), toggle = $("[data-media-toggle]");
  if (heroVideo && motionOk && window.innerWidth >= 760) {
    var start = function () {
      loadVideo(heroVideo, function () { if (toggle) toggle.hidden = false; });
    };
    if (document.readyState === "complete") setTimeout(start, 300); else window.addEventListener("load", function () { setTimeout(start, 300); });
  }
  if (toggle && heroVideo) {
    toggle.addEventListener("click", function () {
      var paused = heroVideo.paused;
      if (paused) heroVideo.play(); else heroVideo.pause();
      toggle.setAttribute("aria-pressed", String(!paused));
      $("use", toggle).setAttribute("href", "assets/icons.svg#" + (paused ? "pause" : "play"));
      $("span", toggle).textContent = paused ? "Pause background" : "Play background";
    });
  }
  if (motionOk && "IntersectionObserver" in window) {
    var vio = new IntersectionObserver(function (entries) {
      entries.forEach(function (x) {
        var v = x.target;
        if (x.isIntersecting) { if (!v.dataset.loaded) { v.dataset.loaded = "1"; loadVideo(v); } else v.play().catch(function () {}); }
        else if (v.dataset.loaded) v.pause();
      });
    }, { threshold: 0.25 });
    $$("[data-lazy-video]").forEach(function (v) { vio.observe(v); });
  }

  /* Brand film: nothing loads until the visitor presses play (user gesture = sound allowed) */
  $$("[data-film]").forEach(function (box) {
    var btn = $("[data-film-play]", box);
    if (!btn) return;
    btn.addEventListener("click", function () {
      var small = window.innerWidth < 900 || saveData;
      var v = document.createElement("video");
      v.controls = true; v.playsInline = true; v.preload = "auto";
      v.poster = "assets/film/poster-1920.webp";
      v.setAttribute("aria-label", "What We Build at Elitron Labs, brand film");
      var srcs = small
        ? [["assets/film/elitron-film-720.mp4", "video/mp4"]]
        : [["assets/film/elitron-film-1080.mp4", "video/mp4"]];
      srcs.forEach(function (s) { var e = document.createElement("source"); e.src = s[0]; e.type = s[1]; v.appendChild(e); });
      var tr = document.createElement("track");
      tr.kind = "captions"; tr.srclang = "en"; tr.label = "English"; tr.src = "assets/film/elitron-film.en.vtt"; tr.default = true;
      v.appendChild(tr);
      box.replaceChild(v, btn);
      v.focus();
      var p = v.play(); if (p && p.catch) p.catch(function () {});
      track("film_play", { size: small ? "720" : "1080" });
      v.addEventListener("ended", function () { track("film_complete"); });
    });
  });

  /* Work filters */
  var filters = $$("[data-filter]");
  filters.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var f = btn.getAttribute("data-filter");
      filters.forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
      $$("[data-status]").forEach(function (card) { card.hidden = f !== "all" && card.getAttribute("data-status") !== f; });
    });
  });

  /* ------------------------------------------------------------------ */
  /* Interactive automation demo (synthetic data, runs locally only)     */
  /* ------------------------------------------------------------------ */
  var demo = $("[data-demo]");
  if (demo) initDemo(demo);

  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  function initDemo(root) {
    var panel = $("[data-demo-panel]", root), next = $("[data-demo-next]", root), prev = $("[data-demo-prev]", root);
    var labels = $$("[data-step-label]", root);
    var state = { step: 0, name: "Jordan Example", service: "AC not cooling", urgency: "This week", zip: "48127", message: "Upstairs unit runs but blows warm air.", slot: null, ref: null };
    var services = ["AC not cooling", "Furnace repair", "New system estimate", "Routine maintenance"];
    var urgencies = ["Today", "This week", "Just planning"];

    function slots() {
      var out = [], d = new Date(), times = ["9:00 AM", "1:30 PM", "4:00 PM"];
      while (out.length < 3) {
        d.setDate(d.getDate() + 1);
        if (d.getDay() === 0 || d.getDay() === 6) continue;
        out.push(d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" }) + " · " + times[out.length]);
      }
      return out;
    }
    function score() {
      var s = 30, why = [];
      if (state.urgency === "Today") { s += 30; why.push("Urgent request (+30)"); }
      else if (state.urgency === "This week") { s += 20; why.push("Needed this week (+20)"); }
      else why.push("Planning ahead (+0)");
      if (/^48\d{3}$/.test(state.zip)) { s += 20; why.push("Inside service area (+20)"); } else why.push("Outside example service area (+0)");
      if (state.service === "New system estimate") { s += 15; why.push("High-value job type (+15)"); }
      else if (state.service !== "Routine maintenance") { s += 10; why.push("Repair request (+10)"); }
      if (state.message.trim().length > 15) { s += 5; why.push("Clear description (+5)"); }
      return { value: Math.min(s, 100), why: why };
    }
    function opts(list, cur) { return list.map(function (o) { return '<option' + (o === cur ? " selected" : "") + ">" + esc(o) + "</option>"; }).join(""); }

    var views = [
      function () {
        return '<h3>A customer contacts your business</h3><p>A website visitor requests a service estimate. Edit the details. They are made up and never leave this page.</p>' +
          '<form class="demo-form" data-demo-form novalidate>' +
          '<div class="form-grid"><div class="field"><label for="d-name">Name</label><input class="input" id="d-name" name="name" value="' + esc(state.name) + '" maxlength="60"></div>' +
          '<div class="field"><label for="d-zip">ZIP code</label><input class="input" id="d-zip" name="zip" value="' + esc(state.zip) + '" inputmode="numeric" maxlength="5"></div>' +
          '<div class="field"><label for="d-service">Service needed</label><select class="select" id="d-service" name="service">' + opts(services, state.service) + "</select></div>" +
          '<div class="field"><label for="d-urg">When?</label><select class="select" id="d-urg" name="urgency">' + opts(urgencies, state.urgency) + "</select></div>" +
          '<div class="field field--full"><label for="d-msg">Message</label><textarea class="textarea" id="d-msg" name="message" maxlength="240">' + esc(state.message) + "</textarea></div></div>" +
          '<div><button class="btn btn-primary" type="submit">Submit inquiry <span class="sr-only">(demo)</span><svg aria-hidden="true"><use href="assets/icons.svg#arrow"/></svg></button></div></form>';
      },
      function () {
        var sc = score();
        return '<h3>The inquiry is qualified in seconds</h3><p>The request is checked against your business rules. In production an AI model reads the free-text message too, and borderline leads go to a person.</p>' +
          '<div class="score"><strong class="h3" data-score>0</strong><div class="score-bar" role="img" aria-label="Lead score ' + sc.value + ' out of 100"><i data-score-bar></i></div><span class="muted small">/ 100</span></div>' +
          '<div class="demo-out">' + sc.why.map(function (w) { return '<span class="c">›</span> ' + esc(w); }).join("\n") +
          '\n<span class="c">›</span> Route: <span class="s">' + (sc.value >= 60 ? "priority follow-up" : "standard follow-up") + "</span></div>";
      },
      function () {
        state.ref = state.ref || "DEMO-" + Math.random().toString(36).slice(2, 7).toUpperCase();
        var sc = score().value;
        var rec = '{\n  <span class="k">"record"</span>: <span class="s">"' + state.ref + '"</span>,\n  <span class="k">"contact"</span>: <span class="s">"' + esc(state.name) + '"</span>,\n  <span class="k">"zip"</span>: <span class="s">"' + esc(state.zip) + '"</span>,\n  <span class="k">"service"</span>: <span class="s">"' + esc(state.service) + '"</span>,\n  <span class="k">"urgency"</span>: <span class="s">"' + esc(state.urgency) + '"</span>,\n  <span class="k">"lead_score"</span>: ' + sc + ',\n  <span class="k">"stage"</span>: <span class="s">"New lead"</span>,\n  <span class="k">"source"</span>: <span class="s">"Website form"</span>\n}';
        return '<h3>A CRM record is created automatically</h3><p>No copy-and-paste. The lead lands in your CRM with the details and score attached, ready for your team.</p><div class="demo-out" aria-label="Example CRM record">' + rec + "</div>";
      },
      function () {
        var first = esc(state.name.split(" ")[0] || "there");
        return '<h3>The customer is offered appointment times</h3><p>A follow-up goes out right away with open slots from your calendar. Pick one as the customer would.</p>' +
          '<div class="chat"><div class="bubble bot">Hi ' + first + ", thanks for reaching out about “" + esc(state.service) + "”. We have these openings. Which works best?</div></div>" +
          '<div class="slots" role="group" aria-label="Available times">' + slots().map(function (s) {
            return '<button type="button" class="slot" data-slot="' + esc(s) + '" aria-pressed="' + (state.slot === s) + '">' + esc(s) + "</button>";
          }).join("") + "</div>";
      },
      function () {
        return '<h3>Booked and confirmed</h3><p>The calendar is updated, the customer gets a confirmation, and your team is notified. All without anyone touching a keyboard.</p>' +
          '<div class="confirm"><svg aria-hidden="true"><use href="assets/icons.svg#check"/></svg><div><strong>' + esc(state.service) + "</strong><br>" + esc(state.slot || "") + " · " + esc(state.name) + '<br><span class="muted small">Reference ' + esc(state.ref || "") + "</span></div></div>" +
          '<div class="demo-out"><span class="c">›</span> Calendar event created\n<span class="c">›</span> Confirmation message queued to customer\n<span class="c">›</span> Technician notified\n<span class="c">›</span> Reminder scheduled for the day before</div>' +
          '<div class="btn-row mt-s"><button type="button" class="btn btn-secondary btn-sm" data-demo-restart>Run it again</button><a class="btn btn-primary btn-sm" href="contact.html?path=discovery" data-track="cta_discovery_demo">Talk about your workflow</a></div>';
      }
    ];

    function render(focus) {
      panel.innerHTML = views[state.step]();
      labels.forEach(function (l, i) {
        l.classList.toggle("active", i === state.step);
        l.classList.toggle("done", i < state.step);
        if (i === state.step) l.setAttribute("aria-current", "step"); else l.removeAttribute("aria-current");
      });
      prev.hidden = state.step === 0;
      next.hidden = state.step === 0 || state.step === 4;
      next.disabled = state.step === 3 && !state.slot;
      if (state.step === 1) {
        var target = score().value, el = $("[data-score]", panel), bar = $("[data-score-bar]", panel);
        requestAnimationFrame(function () { bar.style.width = target + "%"; });
        if (reduceMotion) el.textContent = target;
        else { var t0 = performance.now(); (function tick(t) { var k = Math.min((t - t0) / 900, 1); el.textContent = Math.round(target * k); if (k < 1) requestAnimationFrame(tick); })(t0); }
      }
      if (focus) { var h = $("h3", panel); if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); } }
    }
    function go(n) { state.step = Math.max(0, Math.min(4, n)); render(true); track("demo_step", { step: state.step + 1 }); }

    panel.addEventListener("submit", function (e) {
      e.preventDefault();
      var f = e.target;
      state.name = (f.name.value || "").trim().slice(0, 60) || "Jordan Example";
      state.zip = (f.zip.value || "").replace(/\D/g, "").slice(0, 5);
      state.service = f.service.value; state.urgency = f.urgency.value;
      state.message = (f.message.value || "").slice(0, 240);
      state.slot = null; state.ref = null;
      go(1);
    });
    panel.addEventListener("click", function (e) {
      var s = e.target.closest("[data-slot]");
      if (s) { state.slot = s.getAttribute("data-slot"); go(4); return; }
      if (e.target.closest("[data-demo-restart]")) { state.slot = null; state.ref = null; go(0); }
    });
    next.addEventListener("click", function () { go(state.step + 1); });
    prev.addEventListener("click", function () { go(state.step - 1); });
    render(false);
  }

  /* ------------------------------------------------------------------ */
  /* Contact: two acquisition paths, server-side submission              */
  /* ------------------------------------------------------------------ */
  var tabs = $$("[data-path-tab]");
  if (tabs.length) {
    var params = new URLSearchParams(location.search);
    var select = function (path, focus) {
      tabs.forEach(function (t) {
        var on = t.getAttribute("data-path-tab") === path;
        t.setAttribute("aria-selected", String(on)); t.tabIndex = on ? 0 : -1;
        $("#" + t.getAttribute("aria-controls")).hidden = !on;
        if (on && focus) t.focus();
      });
    };
    var initial = params.get("path") === "preview" ? "preview" : "discovery";
    select(initial, false);
    var type = params.get("type");
    if (type) { var sel = $("#d-type"); if (sel && $$("option", sel).some(function (o) { return o.value === type; })) sel.value = type; }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t.getAttribute("data-path-tab"), false); });
      t.addEventListener("keydown", function (e) {
        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
        var n = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
        select(n.getAttribute("data-path-tab"), true);
      });
    });
  }

  $$("form[data-lead-form]").forEach(function (form) {
    var started = Date.now();
    var status = $("[data-form-status]", form);
    var btn = $("button[type=submit]", form);
    var requestId = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2);

    function fieldError(input, msg) {
      var err = $("#" + input.id + "-err");
      input.setAttribute("aria-invalid", msg ? "true" : "false");
      if (err) err.textContent = msg || "";
    }
    function validate() {
      var firstBad = null;
      $$("input,select,textarea", form).forEach(function (el) {
        if (el.type === "hidden" || el.closest(".hp")) return;
        var msg = "";
        var v = el.type === "checkbox" ? el.checked : el.value.trim();
        if (el.required && !v) msg = el.type === "checkbox" ? "Please confirm to continue." : "This field is required.";
        else if (el.type === "email" && v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) msg = "Enter a valid email address.";
        else if (el.type === "url" && v && !/^(https?:\/\/)?[\w-]+(\.[\w-]+)+(\/\S*)?$/i.test(v)) msg = "Enter a valid website address.";
        fieldError(el, msg);
        if (msg && !firstBad) firstBad = el;
      });
      if (firstBad) firstBad.focus();
      return !firstBad;
    }
    function show(kind, html) {
      status.className = "form-status show " + kind;
      status.innerHTML = html;
      status.setAttribute("role", kind === "err" ? "alert" : "status");
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validate()) return;
      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = typeof v === "string" ? v.trim() : v; });
      data.path = form.getAttribute("data-lead-form");
      data.elapsed_ms = Date.now() - started;
      data.request_id = requestId;
      data.page = location.pathname;
      btn.setAttribute("aria-busy", "true"); btn.disabled = true;
      var ctrl = "AbortController" in window ? new AbortController() : null;
      var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, 20000) : null;
      fetch("/api/contact", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data), signal: ctrl ? ctrl.signal : undefined })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, status: r.status, body: j }; }); })
        .then(function (res) {
          if (res.ok && res.body.ok) {
            form.reset(); $$("input,select,textarea", form).forEach(function (el) { el.setAttribute("aria-invalid", "false"); });
            show("ok", "<strong>Thanks, we have your request.</strong> Reference <code>" + esc(res.body.reference || "") + "</code>. We review every inquiry personally and reply by email, usually within one business day.");
            track(data.path === "preview" ? "lead_preview_submitted" : "lead_discovery_submitted");
            requestId = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : String(Date.now());
          } else if (res.status === 400 && res.body.fields) {
            Object.keys(res.body.fields).forEach(function (k) { var el = form.elements[k]; if (el && el.id) fieldError(el, res.body.fields[k]); });
            show("err", "Please check the highlighted fields.");
          } else {
            show("err", "We couldn't send your request right now. Please email <a href=\"mailto:admin@elitronlabs.io\">admin@elitronlabs.io</a> or call <a href=\"tel:+13132427470\">(313) 242-7470</a>. Your details are still in the form.");
          }
        })
        .catch(function () {
          show("err", "The connection failed before we could confirm receipt. Please try again, or email <a href=\"mailto:admin@elitronlabs.io\">admin@elitronlabs.io</a>.");
        })
        .then(function () { if (timer) clearTimeout(timer); btn.removeAttribute("aria-busy"); btn.disabled = false; });
    });
  });
})();
