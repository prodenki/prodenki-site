/* ProDenki — site interactions (no dependencies) */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  var CFG = {};
  try { CFG = JSON.parse(doc.getElementById("pd-config").textContent); } catch (e) {}
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  window.dataLayer = window.dataLayer || [];
  function track(name, params) {
    window.dataLayer.push(Object.assign({ event: name }, params || {}));
    if (window.gtag) window.gtag("event", name, params || {});
  }

  /* Header shadow + back to top ---------------------------------------- */
  var hdr = $("[data-hdr]"), topBtn = $("[data-top]");
  function onScroll() {
    var y = window.scrollY || 0;
    if (hdr) hdr.classList.toggle("scrolled", y > 8);
    if (topBtn) topBtn.classList.toggle("show", y > 700);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (topBtn) topBtn.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); });

  /* Mobile menu ---------------------------------------------------------- */
  var burger = $("[data-burger]"), nav = $("[data-nav]");
  function setMenu(open) {
    if (!burger || !nav) return;
    burger.setAttribute("aria-expanded", open ? "true" : "false");
    nav.classList.toggle("open", open);
    doc.body.style.overflow = open ? "hidden" : "";
  }
  if (burger) burger.addEventListener("click", function () { setMenu(burger.getAttribute("aria-expanded") !== "true"); });
  $$(".nav a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); closeMega(); }); });
  window.addEventListener("resize", function () { if (window.innerWidth > 1060) setMenu(false); });

  /* Mega menu ------------------------------------------------------------ */
  var megaBtn = $("[data-mega-btn]"), mega = $("[data-mega]"), megaTimer;
  function openMega() { if (!mega) return; clearTimeout(megaTimer); mega.classList.add("open"); megaBtn.setAttribute("aria-expanded", "true"); }
  function closeMega() { if (!mega) return; mega.classList.remove("open"); megaBtn.setAttribute("aria-expanded", "false"); }
  if (megaBtn) {
    megaBtn.addEventListener("click", function (e) { e.stopPropagation(); mega.classList.contains("open") ? closeMega() : openMega(); });
    var li = megaBtn.parentNode;
    li.addEventListener("mouseenter", function () { if (window.innerWidth > 1060) openMega(); });
    li.addEventListener("mouseleave", function () { if (window.innerWidth > 1060) megaTimer = setTimeout(closeMega, 180); });
  }

  /* Language menu -------------------------------------------------------- */
  var langWrap = $("[data-lang-menu]"), langBtn = $("[data-lang-btn]");
  if (langBtn) langBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    var open = !langWrap.classList.contains("open");
    langWrap.classList.toggle("open", open);
    langBtn.setAttribute("aria-expanded", open ? "true" : "false");
  });
  $$("[data-lang]").forEach(function (a) { a.addEventListener("click", function () { store.set("pd-lang", a.getAttribute("data-lang")); }); });
  doc.addEventListener("click", function (e) {
    if (langWrap && !langWrap.contains(e.target)) { langWrap.classList.remove("open"); langBtn.setAttribute("aria-expanded", "false"); }
    if (mega && !mega.contains(e.target) && window.innerWidth > 1060) closeMega();
  });
  doc.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { closeMega(); if (langWrap) langWrap.classList.remove("open"); setMenu(false); }
  });

  /* Suggest the visitor's language (never auto-redirects) --------------- */
  (function () {
    var tip = $("[data-lang-tip]");
    if (!tip || !CFG.alternates || store.get("pd-lang")) return;
    var want = null;
    (navigator.languages || [navigator.language || ""]).some(function (l) {
      var c = String(l).slice(0, 2).toLowerCase();
      if (CFG.alternates[c]) { want = c; return true; }
      return false;
    });
    if (!want || want === CFG.lang) { store.set("pd-lang", CFG.lang); return; }
    tip.innerHTML = '<p></p><a class="btn btn-primary btn-sm"></a><button class="x" aria-label="Close">✕</button>';
    tip.querySelector("p").textContent = CFG.langNames[want];
    var go = tip.querySelector("a");
    go.textContent = CFG.langGo[want];
    go.href = CFG.alternates[want];
    go.addEventListener("click", function () { store.set("pd-lang", want); });
    tip.querySelector(".x").addEventListener("click", function () { store.set("pd-lang", CFG.lang); tip.hidden = true; });
    setTimeout(function () { tip.hidden = false; }, 1200);
  })();

  /* Reveal on scroll + counters + process steps ------------------------- */
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      var el = en.target;
      if (el.hasAttribute("data-count")) countUp(el);
      else if (el.hasAttribute("data-steps")) runSteps(el);
      else el.classList.add("in");
      io.unobserve(el);
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }) : null;
  $$(".reveal, [data-count], [data-steps]").forEach(function (el) {
    if (io) io.observe(el);
    else { el.classList.add("in"); if (el.hasAttribute("data-steps")) runSteps(el); }
  });
  function countUp(el) {
    var end = parseInt(el.getAttribute("data-count"), 10) || 0;
    if (reduce) { el.textContent = end; return; }
    var t0 = null, dur = 1100;
    el.textContent = "0";
    function step(ts) {
      if (!t0) t0 = ts;
      var p = Math.min((ts - t0) / dur, 1);
      el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  function runSteps(list) {
    var steps = $$(".step", list), i = 0;
    steps.forEach(function (s) { s.classList.add("in"); });
    (function next() {
      if (i >= steps.length) return;
      steps[i].classList.add("on");
      list.style.setProperty("--progress", steps.length > 1 ? i / (steps.length - 1) : 1);
      i++;
      setTimeout(next, reduce ? 0 : 420);
    })();
  }

  /* Hero tilt ------------------------------------------------------------ */
  var tilt = $("[data-tilt]");
  if (tilt && !reduce && window.matchMedia("(pointer: fine)").matches) {
    var hero = tilt.closest(".hero");
    hero.addEventListener("mousemove", function (e) {
      var r = tilt.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      tilt.style.transform = "perspective(900px) rotateY(" + (x * 6).toFixed(2) + "deg) rotateX(" + (-y * 6).toFixed(2) + "deg)";
    });
    hero.addEventListener("mouseleave", function () { tilt.style.transform = ""; });
  }

  /* Panel-type tabs ------------------------------------------------------ */
  var tabs = $$("[data-ptab]");
  function selectTab(tab, focus) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      var panel = doc.getElementById(t.getAttribute("aria-controls"));
      if (panel) panel.hidden = !on;
    });
    if (focus) tab.focus();
    track("panel_tab", { panel: tab.textContent.trim() });
  }
  tabs.forEach(function (t, i) {
    t.addEventListener("click", function () { selectTab(t); });
    t.addEventListener("keydown", function (e) {
      var k = e.key, n = null;
      if (k === "ArrowRight") n = tabs[(i + 1) % tabs.length];
      if (k === "ArrowLeft") n = tabs[(i - 1 + tabs.length) % tabs.length];
      if (k === "Home") n = tabs[0];
      if (k === "End") n = tabs[tabs.length - 1];
      if (n) { e.preventDefault(); selectTab(n, true); }
    });
  });

  /* Accordions ------------------------------------------------------------ */
  $$("[data-acc]").forEach(function (b) {
    b.addEventListener("click", function () {
      var open = b.getAttribute("aria-expanded") !== "true";
      b.setAttribute("aria-expanded", open ? "true" : "false");
      b.closest(".acc-item").classList.toggle("open", open);
    });
  });

  /* Gallery filters ------------------------------------------------------ */
  $$("[data-filter]").forEach(function (b) {
    b.addEventListener("click", function () {
      var f = b.getAttribute("data-filter");
      $$("[data-filter]").forEach(function (x) { var on = x === b; x.classList.toggle("on", on); x.setAttribute("aria-pressed", on ? "true" : "false"); });
      $$(".g-item[data-cat]").forEach(function (it) { it.classList.toggle("off", !!f && it.getAttribute("data-cat") !== f); it.classList.add("in"); });
    });
  });

  /* Lightbox ------------------------------------------------------------- */
  var lb = $("[data-lb]"), lbImg = $("[data-lb-img]"), lbCap = $("[data-lb-cap]"), allItems = $$("[data-lb-open]"), items = allItems, cur = 0, lastFocus;
  function visible() { return allItems.filter(function (it) { var g = it.closest(".g-item"); return !g || !g.classList.contains("off"); }); }
  function show(i) {
    cur = (i + items.length) % items.length;
    var it = items[cur];
    lbImg.src = it.getAttribute("data-full");
    lbImg.onerror = function () { lbImg.onerror = null; lbImg.src = it.getAttribute("data-fallback"); };
    lbImg.alt = it.getAttribute("data-cap");
    lbCap.textContent = it.getAttribute("data-cap");
  }
  function openLb(el) { lastFocus = doc.activeElement; items = visible(); show(Math.max(items.indexOf(el), 0)); lb.hidden = false; doc.body.style.overflow = "hidden"; $("[data-lb-close]").focus(); }
  function closeLb() { lb.hidden = true; doc.body.style.overflow = ""; if (lastFocus) lastFocus.focus(); }
  if (lb && allItems.length) {
    allItems.forEach(function (it) { it.addEventListener("click", function () { openLb(it); }); });
    $("[data-lb-close]").addEventListener("click", closeLb);
    $("[data-lb-prev]").addEventListener("click", function () { show(cur - 1); });
    $("[data-lb-next]").addEventListener("click", function () { show(cur + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) closeLb(); });
    doc.addEventListener("keydown", function (e) {
      if (lb.hidden) return;
      if (e.key === "Escape") closeLb();
      if (e.key === "ArrowLeft") show(cur - 1);
      if (e.key === "ArrowRight") show(cur + 1);
      if (e.key === "Tab") {
        var f = $$("button", lb), first = f[0], last = f[f.length - 1];
        if (e.shiftKey && doc.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && doc.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    var sx = null;
    lb.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      if (sx === null) return;
      var dx = e.changedTouches[0].clientX - sx;
      if (Math.abs(dx) > 50) show(cur + (dx < 0 ? 1 : -1));
      sx = null;
    });
  }

  /* Click tracking for phone / WhatsApp ---------------------------------- */
  $$("[data-track]").forEach(function (a) { a.addEventListener("click", function () { track(a.getAttribute("data-track")); }); });

  /* Quote wizard ---------------------------------------------------------- */
  $$("[data-wiz]").forEach(function (wiz) {
    var W = CFG.wiz || {};
    var form = $("[data-wiz-form]", wiz), steps = $$(".wiz-step", wiz), dots = $$("[data-step-dot]", wiz);
    var bar = $("[data-wiz-bar]", wiz), count = $("[data-wiz-count]", wiz), err = $("[data-wiz-err]", wiz);
    var back = $("[data-wiz-back]", wiz), next = $("[data-wiz-next]", wiz), submit = $("[data-wiz-submit]", wiz);
    var ok = $("[data-wiz-ok]", wiz), summary = $("[data-wiz-summary]", wiz), idx = 0, started = false;

    var m = new URLSearchParams(location.search).get("m");
    if (m !== null) {
      var r = $$('input[name="modalidade"]', form)[parseInt(m, 10)];
      if (r) { r.checked = true; }
    }

    function go(i, focus) {
      idx = i;
      steps.forEach(function (s, k) { s.hidden = k !== i; });
      dots.forEach(function (d, k) { d.classList.toggle("active", k === i); d.classList.toggle("done", k < i); });
      bar.style.width = ((i + 1) / steps.length * 100) + "%";
      count.textContent = (W.step_of || "{n}/{t}").replace("{n}", i + 1).replace("{t}", steps.length);
      back.hidden = i === 0;
      next.hidden = i === steps.length - 1;
      submit.hidden = i !== steps.length - 1;
      err.textContent = "";
      if (i === steps.length - 1) renderSummary();
      if (focus) {
        var top = wiz.getBoundingClientRect().top + window.scrollY - 100;
        if (wiz.getBoundingClientRect().top < 80) window.scrollTo({ top: top, behavior: reduce ? "auto" : "smooth" });
        var leg = steps[i].querySelector("legend");
        if (leg) { leg.tabIndex = -1; leg.focus({ preventScroll: true }); }
      }
    }
    function valid(i) {
      var s = steps[i], good = true;
      err.textContent = "";
      var radios = {};
      $$("input[type=radio][required]", s).forEach(function (r) { radios[r.name] = radios[r.name] || !!$('input[name="' + r.name + '"]:checked', s); });
      Object.keys(radios).forEach(function (k) { if (!radios[k]) { good = false; err.textContent = W.choose; } });
      $$("input[required]:not([type=radio]), textarea[required], select[required]", s).forEach(function (f) {
        var bad = f.type === "checkbox" ? !f.checked : !f.value.trim();
        if (!bad && f.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(f.value.trim())) { bad = true; err.textContent = W.invalid_email; }
        var tgt = f.type === "checkbox" ? f.closest(".check") : f;
        tgt.classList.toggle("invalid", bad);
        if (bad) { if (good) f.focus(); good = false; if (!err.textContent) err.textContent = W.required; }
      });
      return good;
    }
    function renderSummary() {
      var fd = new FormData(form), rows = [];
      [["modalidade", W.steps[0]], ["tipo", W.steps[1]], ["quantidade", W.qty], ["prazo", W.deadline], ["local", W.location]].forEach(function (p) {
        var v = fd.get(p[0]);
        if (v) rows.push("<dt>" + esc(p[1]) + "</dt><dd>" + esc(v) + "</dd>");
      });
      summary.innerHTML = rows.length ? "<b>" + esc(W.summary) + "</b><dl>" + rows.join("") + "</dl>" : "";
    }
    function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

    form.addEventListener("change", function (e) {
      if (!started) { started = true; track("form_start", { form: "quote" }); }
      if (e.target.classList) e.target.classList.remove("invalid");
      var chk = e.target.closest && e.target.closest(".check");
      if (chk) chk.classList.remove("invalid");
      if (e.target.type === "radio" && e.target.required && idx < 2) setTimeout(function () { if (valid(idx)) go(idx + 1, true); }, 220);
    });
    form.addEventListener("input", function (e) {
      if (e.target.classList && e.target.classList.contains("invalid") && e.target.value.trim()) { e.target.classList.remove("invalid"); err.textContent = ""; }
    });
    next.addEventListener("click", function () { if (valid(idx)) go(idx + 1, true); });
    back.addEventListener("click", function () { go(idx - 1, true); });
    form.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && e.target.tagName !== "TEXTAREA" && idx < steps.length - 1) { e.preventDefault(); next.click(); }
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!valid(idx)) return;
      var fd = new FormData(form);
      if (fd.get("botcheck")) return;
      var data = {
        access_key: CFG.w3f,
        subject: "Novo Pedido de Orçamento — ProDenki [" + (CFG.lang || "pt").toUpperCase() + "]",
        from_name: "Website ProDenki",
        idioma: CFG.lang,
        pagina: location.href
      };
      fd.forEach(function (v, k) { if (k !== "botcheck") data[k] = v; });
      if (data.email) data.replyto = data.email;
      var label = submit.innerHTML;
      submit.disabled = true; back.disabled = true;
      submit.textContent = W.sending;
      fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(data)
      }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok && j.success, j: j }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error((res.j && res.j.message) || "error");
          form.hidden = true; $(".wiz-steps", wiz).hidden = true; $(".wiz-bar", wiz).hidden = true; count.hidden = true;
          ok.hidden = false; ok.focus();
          track("generate_lead", { form: "quote", modalidade: data.modalidade || "", tipo: data.tipo || "" });
          if (window.fbq) window.fbq("track", "Lead");
        })
        .catch(function () {
          err.innerHTML = esc(W.err) + ' <a href="mailto:' + esc(CFG.email) + '">' + esc(CFG.email) + "</a>.";
        })
        .then(function () { submit.disabled = false; back.disabled = false; submit.innerHTML = label; });
    });
    $("[data-wiz-again]", wiz).addEventListener("click", function () {
      form.reset(); form.hidden = false; ok.hidden = true;
      $(".wiz-steps", wiz).hidden = false; $(".wiz-bar", wiz).hidden = false; count.hidden = false;
      started = false; go(0, true);
    });
    go(0, false);
  });

  /* Cookie consent + analytics (only when IDs are configured) ----------- */
  var banner = $("[data-cookie]");
  function loadTracking() {
    if (window.__pdTracking) return;
    window.__pdTracking = true;
    var s;
    if (CFG.gtm) {
      window.dataLayer.push({ "gtm.start": Date.now(), event: "gtm.js" });
      s = doc.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtm.js?id=" + encodeURIComponent(CFG.gtm); doc.head.appendChild(s);
    } else if (CFG.ga4) {
      s = doc.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(CFG.ga4); doc.head.appendChild(s);
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag("js", new Date());
      window.gtag("config", CFG.ga4);
    }
    if (CFG.pixel) {
      !function (f, b, e, v, n, t, s2) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); }; if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v; s2 = b.getElementsByTagName(e)[0]; s2.parentNode.insertBefore(t, s2); }(window, doc, "script", "https://connect.facebook.net/en_US/fbevents.js");
      window.fbq("init", CFG.pixel); window.fbq("track", "PageView");
    }
  }
  if (banner) {
    var choice = store.get("pd-consent");
    if (choice === "yes") loadTracking();
    else if (!choice) setTimeout(function () { banner.hidden = false; }, 800);
    $("[data-cookie-yes]").addEventListener("click", function () { store.set("pd-consent", "yes"); banner.hidden = true; loadTracking(); });
    $("[data-cookie-no]").addEventListener("click", function () { store.set("pd-consent", "no"); banner.hidden = true; });
    $$("[data-cookie-open]").forEach(function (b) { b.addEventListener("click", function () { banner.hidden = false; }); });
  }
})();
