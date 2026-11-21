#!/usr/bin/env python3
"""Builds the ProDenki static site into ./dist.

    python3 build.py

Content lives in content/*.py, styles and scripts in src/assets.
"""
import datetime
import hashlib
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "content"))

from config import SITE, LANGS  # noqa: E402
from services import SERVICES  # noqa: E402
from strings import ROUTES, LANG_META, T  # noqa: E402

DIST = ROOT / "dist"
SRC = ROOT / "src"
TODAY = datetime.date.today().isoformat()
YEAR = datetime.date.today().year
DEFAULT = LANGS[0]

e = html.escape
CUR = ' aria-current="true"'


def a(s):
    """Escape for attributes."""
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------------------
# Icons (24x24, stroke)
# ---------------------------------------------------------------------------
ICONS = {
    "panel": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8M8 11h8M8 15h3"/><circle cx="15.5" cy="15.5" r="1.5"/>',
    "bolt": '<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z"/>',
    "motor": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M2 12h3M19 12h3M4.9 19.1 7 17M17 7l2.1-2.1"/>',
    "chip": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/><rect x="10" y="10" width="4" height="4"/>',
    "wiring": '<path d="M3 6h5a4 4 0 0 1 4 4v4a4 4 0 0 0 4 4h5"/><path d="M3 12h3M18 6h3M18 6v0"/><circle cx="3" cy="6" r="1"/><circle cx="21" cy="18" r="1"/>',
    "thermo": '<path d="M14 14.8V5a2 2 0 1 0-4 0v9.8a4 4 0 1 0 4 0z"/><path d="M12 9v7"/>',
    "blueprint": '<path d="M3 21h18M5 21V7l7-4 7 4v14"/><path d="M9 21v-6h6v6M9 10h6"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "factory": '<path d="M2 21V10l6 4V10l6 4V6l8 4v11z"/><path d="M6 17h2M11 17h2M16 17h2"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "store": '<path d="M3 9l1.5-5h15L21 9"/><path d="M3 9a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0"/><path d="M5 12v9h14v-9M10 21v-5h4v5"/>',
    "building": '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2M10 21v-3h4v3"/>',
    "hardhat": '<path d="M2 18h20v2H2z"/><path d="M4 18a8 8 0 0 1 16 0"/><path d="M10 10V5h4v5"/>',
    "gauge": '<path d="M12 14l4-4"/><path d="M3.3 19a10 10 0 1 1 17.4 0z"/><path d="M12 5v2M5.6 8.6l1.4 1.4M18.4 8.6 17 10M4 14h2M18 14h2"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "close": '<path d="M18 6 6 18M6 6l12 12"/>',
    "zoom": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3M11 8v6M8 11h6"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.5 13 17 22l-5-3-5 3 1.5-9"/>',
    "ruler": '<path d="M21.3 8.7 8.7 21.3a1 1 0 0 1-1.4 0l-4.6-4.6a1 1 0 0 1 0-1.4L15.3 2.7a1 1 0 0 1 1.4 0l4.6 4.6a1 1 0 0 1 0 1.4z"/><path d="m7.5 10.5 2 2M10.5 7.5l2 2M13.5 4.5l2 2M4.5 13.5l2 2"/>',
    "test": '<path d="M9 3h6M10 3v6L4.5 18.5A2 2 0 0 0 6.2 21.5h11.6a2 2 0 0 0 1.7-3L14 9V3"/><path d="M7 15h10"/>',
    "box": '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
    "send": '<path d="m22 2-11 11M22 2l-7 20-4-9-9-4z"/>',
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/>',
    "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
    "instagram": '<rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h0"/>',
    "ext": '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
    "whatsapp": '<path d="M3 21l1.6-4.8A9 9 0 1 1 8 19.6z"/><path d="M9 9.5c.3 1.6 2 3.8 3.9 4.6l1.2-1.1 2 1c-.2 1-1 1.7-2 1.7-3 0-6.6-3.4-6.6-6.4 0-1 .7-1.8 1.7-2l1 2z"/>',
}


def icon(name, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


# ---------------------------------------------------------------------------
# URLs
# ---------------------------------------------------------------------------
def svc_url(lang, svc):
    return f'{ROUTES[lang]["services"]}{svc[lang]["slug"]}/'


SVC_BY_KEY = {s["key"]: s for s in SERVICES}


def abs_url(path):
    return SITE["domain"].rstrip("/") + path


def asset_hash():
    h = hashlib.md5()
    for p in sorted((SRC / "assets").rglob("*")):
        if p.is_file() and p.suffix in (".css", ".js"):
            h.update(p.read_bytes())
    return h.hexdigest()[:8]


VER = None


# ---------------------------------------------------------------------------
# Layout pieces
# ---------------------------------------------------------------------------
def tel_href():
    return "tel:" + SITE["phone"].replace(" ", "")


def by_setair(lang, white=False, cls="by-setair"):
    """'by Setair' signature: the parent group's logo, linking to setair.pt in a new tab."""
    if not SITE.get("setair_url"):
        return ""
    f = "setair-logo-white" if white else "setair-logo"
    return (f'<a class="{cls}" href="{a(SITE["setair_url"])}" target="_blank" rel="noopener" '
            f'aria-label="{a(T[lang]["setair_aria"])}" data-track="setair_click"><span class="by">by</span>'
            f'<picture><source srcset="/assets/img/{f}.webp" type="image/webp"><img src="/assets/img/{f}.png" alt="Setair" width="227" height="80"></picture></a>')


def weg_link_open(lang, cls):
    """Opening <a> tag for links to the WEG website (new tab)."""
    return (f'<a class="{cls}" href="{a(SITE["weg_url"])}" target="_blank" rel="noopener" '
            f'aria-label="{a(T[lang]["weg_aria"])}" data-track="weg_click">')


def topbar(lang):
    """Slim strip above the header: group line on the left, LinkedIn and 'by Setair' on the right."""
    t = T[lang]
    li = (f'<a class="tb-link" href="{a(SITE["linkedin"])}" target="_blank" rel="noopener" aria-label="{a(t["linkedin_aria"])}" '
          f'data-track="linkedin_click">{icon("linkedin")}<span>LinkedIn</span></a>' if SITE["linkedin"] else "")
    sep = '<span class="tb-sep" aria-hidden="true"></span>' if li and SITE.get("setair_url") else ""
    return f'''
<div class="topbar">
  <div class="wrap topbar-in">
    <p class="tb-group">{e(t["group"])}</p>
    <div class="tb-right">{li}{sep}{by_setair(lang)}</div>
  </div>
</div>'''


def header(lang, alternates, current="home"):
    t = T[lang]
    nav = t["nav"]
    r = ROUTES[lang]
    home = r["home"]
    svc_items = "".join(
        f'<li><a href="{svc_url(lang, s)}">{icon(s["icon"])}<span><span class="mg-t">{e(s[lang]["name"])}</span>'
        f'<small>{e(s[lang]["short"])}</small></span></a></li>' for s in SERVICES)
    langs = "".join(
        f'<li><a href="{alternates[l]}" hreflang="{LANG_META[l]["html"]}" lang="{LANG_META[l]["html"]}" '
        f'data-lang="{l}"{CUR if l == lang else ""}>'
        f'<span class="lang-code">{LANG_META[l]["short"]}</span>{LANG_META[l]["label"]}</a></li>' for l in LANGS)
    system = (f'<a class="btn btn-ghost btn-sm hdr-sys" href="{a(SITE["system_url"])}" target="_blank" rel="noopener" data-track="system_click">{icon("lock")}<span>{e(nav["system"])}</span></a>'
              if SITE.get("system_url") else "")
    phone = (f'<a class="hdr-phone" href="{tel_href()}">{icon("phone")}<span>{e(SITE["phone"])}</span></a>'
             if SITE["phone"] else "")
    return f'''
<a class="skip" href="#main">{e(nav["skip"])}</a>
{topbar(lang)}
<header class="hdr" data-hdr>
  <div class="wrap hdr-in">
    <a class="brand" href="{home}" aria-label="ProDenki — {e(nav["home"])}">
      <picture><source srcset="/assets/img/logo.webp" type="image/webp"><img src="/assets/img/logo.png" alt="ProDenki — {e(t["tagline"])}" width="720" height="259"></picture>
    </a>
    <nav class="nav" id="site-nav" aria-label="Main" data-nav>
      <ul class="nav-list">
        <li class="has-mega">
          <button class="nav-link mega-btn" aria-expanded="false" aria-controls="mega-{lang}" data-mega-btn>{e(nav["services"])}{icon("chevron", "ic chev")}</button>
          <div class="mega" id="mega-{lang}" data-mega>
            <ul class="mega-grid">{svc_items}</ul>
            <a class="mega-all" href="{r["services"]}">{e(nav["all_services"])} {icon("arrow")}</a>
          </div>
        </li>
        <li><a class="nav-link" href="{home}#paineis">{e(nav["panels"])}</a></li>
        <li><a class="nav-link" href="{home}#processo">{e(nav["process"])}</a></li>
        <li><a class="nav-link" href="{r["gallery"]}">{e(nav["gallery"])}</a></li>
        {f'<li><a class="nav-link" href="{r["cases"]}">{e(t["nav_cases"])}</a></li>' if CASES else ""}
        <li><a class="nav-link" href="{home}#faq">{e(nav["faq"])}</a></li>
      </ul>
      <div class="nav-extra">
        {phone}
        <div class="lang" data-lang-menu>
          <button class="lang-btn" aria-expanded="false" aria-label="{e(nav["language"])}" data-lang-btn>{icon("globe")}<span>{LANG_META[lang]["short"]}</span>{icon("chevron", "ic chev")}</button>
          <ul class="lang-list">{langs}</ul>
        </div>
        {system}
        <a class="btn btn-primary btn-sm" href="{r["quote"]}">{e(nav["quote"])}</a>
      </div>
    </nav>
    <button class="burger" aria-expanded="false" aria-controls="site-nav" aria-label="{e(nav["menu"])}" data-burger><span></span><span></span><span></span></button>
  </div>
</header>'''


def footer(lang, alternates):
    t = T[lang]
    r = ROUTES[lang]
    svc_links = "".join(f'<li><a href="{svc_url(lang, s)}">{e(s[lang]["name"])}</a></li>' for s in SERVICES)
    contact = [f'<li>{icon("mail")}<a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li>']
    if SITE["phone"]:
        contact.append(f'<li>{icon("phone")}<a href="{tel_href()}">{e(SITE["phone"])}</a></li>')
    addr = ", ".join(x for x in [SITE["street"], " ".join(x for x in [SITE["postal_code"], SITE["city"]] if x)] if x)
    contact.append(f'<li>{icon("pin")}<span>{e(addr) if addr else e(t["contact_area_v"])}</span></li>')
    social_names = {"linkedin": t["linkedin_aria"], "facebook": "Facebook", "instagram": "Instagram"}
    social = "".join(
        f'<a href="{a(SITE[k])}" target="_blank" rel="noopener" aria-label="{a(social_names[k])}" data-track="{k}_click">{icon(k)}</a>'
        for k in ("linkedin", "facebook", "instagram") if SITE[k])
    partner_items = []
    if SITE.get("setair_url"):
        partner_items.append(by_setair(lang, white=True, cls="by-setair by-setair-ftr"))
    if SITE.get("weg_url"):
        partner_items.append(weg_link_open(lang, "ftr-weg")
                             + f'<img src="/assets/img/weg-logo.svg" alt="WEG" width="63" height="44" loading="lazy"><span>{e(t["weg_badge"])}</span></a>')
    partners = (f'<div class="wrap ftr-partners"><p class="ftr-h">{e(t["partners"])}</p>'
                f'<div class="ftr-partners-in">{"".join(partner_items)}</div></div>' if partner_items else "")
    langs = " · ".join(
        f'<a href="{alternates[l]}" hreflang="{LANG_META[l]["html"]}"{CUR if l == lang else ""}>{LANG_META[l]["label"]}</a>'
        for l in LANGS)
    cookie_btn = (f'<button class="linklike" data-cookie-open>{e(t["cookie_prefs"])}</button>'
                  if tracking_on() else "")
    return f'''
<footer class="ftr">
  <div class="wrap ftr-grid">
    <div class="ftr-brand">
      <img src="/assets/img/icon-192.png" alt="ProDenki" width="56" height="56" loading="lazy">
      <p class="ftr-name">ProDenki</p>
      <p class="ftr-tag">{e(t["tagline"])}</p>
      <p class="ftr-group">{e(t["group"])}</p>
      <p>{e(t["footer_desc"])}</p>
      {f'<div class="social">{social}</div>' if social else ''}
    </div>
    <div><p class="ftr-h">{e(t["footer_services"])}</p><ul class="ftr-links">{svc_links}</ul></div>
    <div><p class="ftr-h">{e(t["footer_company"])}</p><ul class="ftr-links">
      <li><a href="{r["home"]}#processo">{e(t["nav"]["process"])}</a></li>
      <li><a href="{r["home"]}#qualidade">{e(t["nav"]["quality"])}</a></li>
      <li><a href="{r["gallery"]}">{e(t["nav"]["gallery"])}</a></li>
      {f'<li><a href="{r["cases"]}">{e(t["nav_cases"])}</a></li>' if CASES else ""}
      <li><a href="{r["home"]}#faq">{e(t["nav"]["faq"])}</a></li>
      <li><a href="{r["quote"]}">{e(t["nav"]["quote"])}</a></li>
      {f'<li><a href="{a(SITE["system_url"])}" target="_blank" rel="noopener">{e(t["nav"]["system"])}</a></li>' if SITE.get("system_url") else ""}
    </ul></div>
    <div><p class="ftr-h">{e(t["footer_contact"])}</p><ul class="ftr-contact">{"".join(contact)}</ul>
      <a class="btn btn-primary btn-sm" href="{r["quote"]}">{e(t["nav"]["quote"])}</a></div>
  </div>
  {partners}
  <div class="wrap ftr-bottom">
    <p>© {YEAR} {e(SITE["legal_name"])} · {e(t["group"])}. {e(t["rights"])}</p>
    <p class="ftr-legal"><a href="{r["privacy"]}">{e(t["privacy_link"])}</a>{cookie_btn}<span class="ftr-langs">{langs}</span></p>
  </div>
</footer>'''


def floating(lang):
    t = T[lang]
    btns = []
    if SITE["whatsapp"]:
        btns.append(f'<a class="fab fab-wa" href="https://wa.me/{SITE["whatsapp"]}" target="_blank" rel="noopener" aria-label="{e(t["whatsapp"])}" data-track="whatsapp_click">{icon("whatsapp")}</a>')
    if SITE["phone"]:
        btns.append(f'<a class="fab fab-tel" href="{tel_href()}" aria-label="{e(t["call"])}" data-track="phone_click">{icon("phone")}</a>')
    btns.append(f'<button class="fab fab-top" aria-label="{e(t["back_top"])}" data-top>{icon("chevron")}</button>')
    return f'<div class="fabs">{"".join(btns)}</div>'


def tracking_on():
    return bool(SITE["ga4_id"] or SITE["gtm_id"] or SITE["meta_pixel_id"])


def cookie_banner(lang):
    if not tracking_on():
        return ""
    t = T[lang]
    return f'''
<div class="cookie" role="dialog" aria-live="polite" aria-label="Cookies" data-cookie hidden>
  <p>{e(t["cookie_text"])} <a href="{ROUTES[lang]["privacy"]}">{e(t["privacy_link"])}</a></p>
  <div class="cookie-btns"><button class="btn btn-ghost btn-sm" data-cookie-no>{e(t["cookie_reject"])}</button>
  <button class="btn btn-primary btn-sm" data-cookie-yes>{e(t["cookie_accept"])}</button></div>
</div>'''


def lightbox():
    return '''
<div class="lb" data-lb hidden role="dialog" aria-modal="true">
  <button class="lb-close" data-lb-close aria-label="Close">''' + icon("close") + '''</button>
  <button class="lb-nav lb-prev" data-lb-prev aria-label="Previous">''' + icon("chevron") + '''</button>
  <figure class="lb-fig"><img alt="ProDenki" data-lb-img><figcaption data-lb-cap></figcaption></figure>
  <button class="lb-nav lb-next" data-lb-next aria-label="Next">''' + icon("chevron") + '''</button>
</div>'''


def org_schema(lang):
    t = T[lang]
    data = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "@id": abs_url("/#org"),
        "name": SITE["name"],
        "alternateName": SITE["legal_name"],
        "description": t["footer_desc"],
        "url": abs_url(ROUTES[lang]["home"]),
        "logo": abs_url("/assets/img/logo.png"),
        "image": abs_url("/assets/img/og-image.jpg"),
        "email": SITE["email"],
        "areaServed": {"@type": "Country", "name": "Portugal"},
        "knowsLanguage": ["pt", "en", "es"],
        "parentOrganization": {"@type": "Organization", "name": "Grupo Setair",
                               **({"url": SITE["setair_url"]} if SITE.get("setair_url") else {})},
        "address": {"@type": "PostalAddress", "addressCountry": "PT"},
    }
    if SITE["phone"]:
        data["telephone"] = SITE["phone"]
    for k, sk in (("street", "streetAddress"), ("postal_code", "postalCode"), ("city", "addressLocality"), ("region", "addressRegion")):
        if SITE[k]:
            data["address"][sk] = SITE[k]
    same = [SITE[k] for k in ("linkedin", "facebook", "instagram") if SITE[k]]
    if same:
        data["sameAs"] = same
    data["hasOfferCatalog"] = {
        "@type": "OfferCatalog", "name": t["svc_index_title"],
        "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s[lang]["name"], "url": abs_url(svc_url(lang, s))}} for s in SERVICES],
    }
    return data


def ld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'


def page(lang, path, alternates, title, desc, body, schema=(), og_image="/assets/img/og-image.jpg", noindex=False):
    t = T[lang]
    alt_links = "".join(
        f'<link rel="alternate" hreflang="{LANG_META[l]["html"]}" href="{abs_url(alternates[l])}">' for l in LANGS)
    alt_links += f'<link rel="alternate" hreflang="x-default" href="{abs_url(alternates[DEFAULT])}">'
    og_alt = "".join(f'<meta property="og:locale:alternate" content="{LANG_META[l]["og"]}">' for l in LANGS if l != lang)
    cfg = {
        "lang": lang,
        "alternates": alternates,
        "langNames": {l: T[l]["lang_suggest"] for l in LANGS},
        "langGo": {l: T[l]["lang_suggest_go"] for l in LANGS},
        "ga4": SITE["ga4_id"], "gtm": SITE["gtm_id"], "pixel": SITE["meta_pixel_id"],
        "w3f": SITE["web3forms_key"], "email": SITE["email"],
        "wiz": {k: v for k, v in t["wizard"].items() if k not in ("modes", "types")},
    }
    verify = (f'<meta name="google-site-verification" content="{a(SITE["google_site_verification"])}">'
              if SITE["google_site_verification"] and lang == DEFAULT and path == ROUTES[lang]["home"] else "")
    schemas = "".join(ld(s) for s in schema)
    return f'''<!doctype html>
<html lang="{LANG_META[lang]["html"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{a(desc)}">
<meta name="robots" content="{"noindex, follow" if noindex else "index, follow, max-image-preview:large"}">
<link rel="canonical" href="{abs_url(path)}">
{alt_links}
{verify}
<meta name="theme-color" content="#04213F">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/icon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="/assets/img/icon-192.png">
<link rel="apple-touch-icon" href="/assets/img/icon-180.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ProDenki">
<meta property="og:url" content="{abs_url(path)}">
<meta property="og:title" content="{a(title)}">
<meta property="og:description" content="{a(desc)}">
<meta property="og:image" content="{abs_url(og_image)}">
<meta property="og:locale" content="{LANG_META[lang]["og"]}">
{og_alt}
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<script>document.documentElement.className+=' js'</script>
<link rel="stylesheet" href="/assets/css/site.css?v={VER}">
{schemas}
<script type="application/json" id="pd-config">{json.dumps(cfg, ensure_ascii=False)}</script>
</head>
<body>
{header(lang, alternates)}
<main id="main">
{body}
</main>
{footer(lang, alternates)}
{floating(lang)}
{cookie_banner(lang)}
<div class="lang-tip" data-lang-tip hidden></div>
{lightbox()}
<script src="/assets/js/site.js?v={VER}" defer></script>
</body>
</html>
'''


# ---------------------------------------------------------------------------
# Shared sections
# ---------------------------------------------------------------------------
def section_head(kicker, title, sub="", center=False, light=False):
    cls = "sec-head" + (" center" if center else "") + (" on-dark" if light else "")
    return (f'<div class="{cls} reveal"><p class="kicker">{e(kicker)}</p><h2>{e(title)}</h2>'
            + (f'<p class="sec-sub">{e(sub)}</p>' if sub else "") + '</div>')


def faq_block(items, id_prefix):
    out = []
    for i, (q, ans) in enumerate(items):
        out.append(f'''<div class="acc-item">
  <h3><button class="acc-btn" aria-expanded="false" aria-controls="{id_prefix}-{i}" id="{id_prefix}-b{i}" data-acc>{e(q)}<span class="acc-ic" aria-hidden="true"></span></button></h3>
  <div class="acc-panel" id="{id_prefix}-{i}" role="region" aria-labelledby="{id_prefix}-b{i}"><div><p>{e(ans)}</p></div></div>
</div>''')
    return f'<div class="acc reveal">{"".join(out)}</div>'


def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in items]}


def picture(name, alt, cls="", sizes="(max-width: 800px) 100vw, 50vw", eager=False, w=1050, h=1400):
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture class="{cls}"><source type="image/webp" srcset="/assets/img/{name}-sm.webp 700w, /assets/img/{name}.webp 1400w" sizes="{sizes}">'
            f'<img src="/assets/img/{name}.jpg" alt="{a(alt)}" width="{w}" height="{h}" {load}></picture>')


IMG_DIMS = {"galeria-cablagem": (1400, 1050), "galeria-botoeiras": (1050, 1400), "galeria-solar": (788, 1400)}

GALLERY = []


def slugify(text):
    import unicodedata
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    t = "".join(c if c.isalnum() else "-" for c in t)
    return "-".join(x for x in t.split("-") if x)[:50] or "foto"


def load_gallery():
    """Reads content/gallery.json (edited in /admin), resizes each photo into dist/assets/gallery."""
    from PIL import Image, ImageOps
    data = json.loads((ROOT / "content" / "gallery.json").read_text(encoding="utf-8"))
    out_dir = DIST / "assets" / "gallery"
    out_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for it in data.get("items", []):
        if not it.get("image") or it.get("published") is False:
            continue
        src = SRC / it["image"].lstrip("/")
        if not src.exists():
            print("  ! foto em falta:", it["image"])
            continue
        photo = process_photo(src, out_dir)
        if not photo:
            continue
        name, w, h = photo
        items.append(dict(it, name=name, w=w, h=h, date=str(it.get("date") or "")[:10]))
    items.sort(key=lambda x: x["date"], reverse=True)
    return items


def process_photo(src, out_dir):
    """Resizes one uploaded photo (phone photos welcome) into webp/jpg versions; returns (name, w, h).

    A photo that cannot be read (damaged file, unsupported format...) is reported and skipped
    (returns None), so one bad upload never stops the whole site from being published.
    """
    from PIL import Image, ImageOps
    name = None
    try:
        raw = src.read_bytes()
        name = f'{slugify(src.stem)}-{hashlib.md5(raw).hexdigest()[:6]}'
        if not (out_dir / f"{name}.jpg").exists():
            with Image.open(src) as opened:
                im = ImageOps.exif_transpose(opened).convert("RGB")
            big = im.copy(); big.thumbnail((1400, 1400), Image.LANCZOS)
            big.save(out_dir / f"{name}.webp", quality=78, method=6)
            big.save(out_dir / f"{name}.jpg", quality=80, optimize=True, progressive=True)
            sm = im.copy(); sm.thumbnail((700, 700), Image.LANCZOS)
            sm.save(out_dir / f"{name}-sm.webp", quality=75, method=6)
        with Image.open(out_dir / f"{name}.jpg") as done:
            w, h = done.size
        return name, w, h
    except Exception as exc:  # noqa: BLE001 - any bad photo must not break the build
        print(f"  ! AVISO: foto ignorada (não foi possível ler '{src.name}'): {exc}")
        if name:
            for suffix in (".webp", ".jpg", "-sm.webp"):
                (out_dir / f"{name}{suffix}").unlink(missing_ok=True)
        return None


CASES = []


def load_cases():
    """Reads content/cases.json (edited in /admin)."""
    path = ROOT / "content" / "cases.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    out_dir = DIST / "assets" / "gallery"
    out_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for it in data.get("items", []):
        if it.get("published") is False or not it.get("title"):
            continue
        it = dict(it, date=str(it.get("date") or "")[:10], name=None)
        if it.get("image"):
            src = SRC / it["image"].lstrip("/")
            if src.exists():
                photo = process_photo(src, out_dir)
                if photo:
                    it["name"], it["w"], it["h"] = photo
            else:
                print("  ! foto em falta:", it["image"])
        items.append(it)
    items.sort(key=lambda x: x["date"], reverse=True)
    return items


def case_cards(lang, items):
    t = T[lang]
    out = []
    for it in items:
        title, sector, desc = gtext(it, lang, "title"), gtext(it, lang, "sector"), gtext(it, lang, "description")
        pic = ""
        if it.get("name"):
            n = it["name"]
            pic = (f'<picture class="case-pic"><source type="image/webp" srcset="/assets/gallery/{n}-sm.webp 700w, /assets/gallery/{n}.webp 1400w" sizes="(max-width: 800px) 100vw, 33vw">'
                   f'<img src="/assets/gallery/{n}.jpg" alt="{a(title)}" width="{it["w"]}" height="{it["h"]}" loading="lazy" decoding="async"></picture>')
        metrics = "".join(
            f'<li><span class="cm-n">{e(str(m.get("value", "")))}</span><span class="cm-l">{e(gtext(m, lang, "label"))}</span></li>'
            for m in (it.get("results") or [])[:3] if m.get("value"))
        client = f'<p class="case-client">{e(t["cases_client"])}: {e(it["client"])}</p>' if it.get("client") else ""
        out.append(f'''
<article class="case reveal">
  {pic}
  <div class="case-body">
    {f'<p class="case-sector">{e(sector)}</p>' if sector else ""}
    <h3>{e(title)}</h3>
    {client}
    {f"<p>{e(desc)}</p>" if desc else ""}
    {f'<ul class="case-metrics">{metrics}</ul>' if metrics else ""}
  </div>
</article>''')
    return "".join(out)


TESTIMONIALS = []


def load_testimonials():
    """Reads content/testimonials.json (edited in /admin). Only items with the customer's consent are shown."""
    path = ROOT / "content" / "testimonials.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    out_dir = DIST / "assets" / "gallery"
    out_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for it in data.get("items", []):
        if it.get("published") is False or not it.get("consent") or not it.get("quote"):
            continue
        it = dict(it, date=str(it.get("date") or "")[:10], name_img=None)
        if it.get("photo"):
            src = SRC / it["photo"].lstrip("/")
            photo = process_photo(src, out_dir) if src.exists() else None
            if photo:
                it["name_img"] = photo[0]
        items.append(it)
    items.sort(key=lambda x: x["date"], reverse=True)
    return items


def testimonials_section(lang):
    if not TESTIMONIALS:
        return ""
    t = T[lang]
    cards = []
    for it in TESTIMONIALS[:6]:
        quote = gtext(it, lang, "quote")
        who = it.get("name") or ""
        role = gtext(it, lang, "role")
        org = it.get("company") or gtext(it, lang, "sector")
        meta = " · ".join(x for x in (role, org) if x)
        initials = "".join(w[0] for w in (who or org or "P").split()[:2]).upper()
        avatar = (f'<img src="/assets/gallery/{it["name_img"]}-sm.webp" alt="" width="52" height="52" loading="lazy">'
                  if it.get("name_img") else f'<span aria-hidden="true">{e(initials)}</span>')
        cards.append(f'''
<figure class="testi reveal">
  <span class="testi-q" aria-hidden="true">“</span>
  <blockquote><p>{e(quote)}</p></blockquote>
  <figcaption><span class="testi-av">{avatar}</span><span>{f'<span class="testi-n">{e(who)}</span>' if who else ""}{f'<span class="testi-m">{e(meta)}</span>' if meta else ""}</span></figcaption>
</figure>''')
    return f'''
<section class="sec sec-alt" id="depoimentos">
  <div class="wrap">
    {section_head(t["testi_kicker"], t["testi_title"], center=True)}
    <div class="testis">{"".join(cards)}</div>
  </div>
</section>'''


def cases_section(lang):
    if not CASES:
        return ""
    t = T[lang]
    more = (f'<div class="g-more reveal"><a class="btn btn-ghost" href="{ROUTES[lang]["cases"]}">{e(t["cases_all_btn"])} {icon("arrow")}</a></div>'
            if len(CASES) > 3 else "")
    return f'''
<section class="sec" id="casos">
  <div class="wrap">
    {section_head(t["cases_kicker"], t["cases_title"], t["cases_sub"])}
    <div class="cases">{case_cards(lang, CASES[:3])}</div>
    {more}
  </div>
</section>'''


def gtext(item, lang, field):
    return item.get(f"{field}_{lang}") or item.get(field) or ""


def gallery_items(lang, items):
    t = T[lang]
    out = []
    for it in items:
        ti, d = gtext(it, lang, "title"), gtext(it, lang, "description")
        cap = ti + (" — " + d if d else "")
        n = it["name"]
        cat = t["gallery_cats"].get(it.get("category", ""), "")
        out.append(f'''
<figure class="g-item reveal" data-cat="{a(it.get("category", ""))}">
  <button class="g-btn" data-lb-open data-full="/assets/gallery/{n}.webp" data-fallback="/assets/gallery/{n}.jpg" data-cap="{a(cap)}" aria-label="{a(t["gallery_open"] + ': ' + ti)}">
    <picture class="g-pic"><source type="image/webp" srcset="/assets/gallery/{n}-sm.webp 700w, /assets/gallery/{n}.webp 1400w" sizes="(max-width: 800px) 100vw, 33vw"><img src="/assets/gallery/{n}.jpg" alt="{a(ti)}" width="{it["w"]}" height="{it["h"]}" loading="lazy" decoding="async"></picture>
    <span class="g-zoom">{icon("zoom")}</span>
    {f'<span class="g-tag">{e(cat)}</span>' if cat else ""}
  </button>
  <figcaption><span class="g-t">{e(ti)}</span>{f"<span>{e(d)}</span>" if d else ""}</figcaption>
</figure>''')
    return "".join(out)


def wizard_modes(w):
    """The last mode is WEG equipment sold separately; hidden unless switched on in config."""
    return w["modes"] if SITE.get("weg_separate_supply") else w["modes"][:-1]


def wizard(lang, preset_mode=None, preset_type=None):
    w = T[lang]["wizard"]
    r = ROUTES[lang]
    steps = "".join(f'<li data-step-dot="{i}"><span>{i + 1}</span><em>{e(s)}</em></li>' for i, s in enumerate(w["steps"]))
    modes = "".join(
        f'<label class="opt"><input type="radio" name="modalidade" value="{a(m)}" required{" checked" if preset_mode == i else ""}>'
        f'<span class="opt-box"><span class="opt-t">{e(m)}</span><small>{e(d)}</small></span></label>'
        for i, (m, d) in enumerate(wizard_modes(w)))
    types = "".join(
        f'<label class="opt opt-sm"><input type="radio" name="tipo" value="{a(m + " — " + d)}" required{" checked" if preset_type == i else ""}>'
        f'<span class="opt-box"><span class="opt-t">{e(m)}</span><small>{e(d)}</small></span></label>'
        for i, (m, d) in enumerate(w["types"]))
    deadlines = "".join(f'<option value="{a(d)}">{e(d)}</option>' for d in w["deadlines"])
    docs = "".join(
        f'<label class="pill"><input type="radio" name="esquemas" value="{a(d)}"><span>{e(d)}</span></label>' for d in w["docs_opts"])
    return f'''
<div class="wiz" data-wiz>
  <ol class="wiz-steps" aria-hidden="true">{steps}</ol>
  <div class="wiz-bar"><span data-wiz-bar></span></div>
  <p class="wiz-count" data-wiz-count aria-live="polite"></p>
  <form class="wiz-form" novalidate data-wiz-form>
    <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
    <fieldset class="wiz-step" data-step="0">
      <legend>{e(w["q1"])}</legend>
      <div class="opts">{modes}</div>
    </fieldset>
    <fieldset class="wiz-step" data-step="1" hidden>
      <legend>{e(w["q2"])}</legend>
      <div class="opts opts-3">{types}</div>
    </fieldset>
    <fieldset class="wiz-step" data-step="2" hidden>
      <legend>{e(w["q3"])}</legend>
      <div class="grid-3">
        <label class="fld"><span>{e(w["qty"])}</span><input type="number" name="quantidade" min="1" step="1" inputmode="numeric" placeholder="1"></label>
        <label class="fld"><span>{e(w["deadline"])}</span><select name="prazo"><option value="">—</option>{deadlines}</select></label>
        <label class="fld"><span>{e(w["location"])}</span><input type="text" name="local" placeholder="{a(w["location_ph"])}" autocomplete="address-level2"></label>
      </div>
      <div class="fld"><span>{e(w["docs"])}</span><div class="pills">{docs}</div></div>
      <label class="fld"><span>{e(w["desc"])}</span><textarea name="descricao" rows="5" placeholder="{a(w["desc_ph"])}"></textarea></label>
    </fieldset>
    <fieldset class="wiz-step" data-step="3" hidden>
      <legend>{e(w["q4"])}</legend>
      <div class="grid-2">
        <label class="fld"><span>{e(w["name"])} *</span><input type="text" name="nome" required autocomplete="name"></label>
        <label class="fld"><span>{e(w["company"])}</span><input type="text" name="empresa" autocomplete="organization"></label>
        <label class="fld"><span>{e(w["email"])} *</span><input type="email" name="email" required autocomplete="email"></label>
        <label class="fld"><span>{e(w["phone"])} *</span><input type="tel" name="telefone" required autocomplete="tel"></label>
      </div>
      <div class="wiz-summary" data-wiz-summary></div>
      <label class="check"><input type="checkbox" name="consentimento" value="sim" required>
        <span>{e(w["consent"])} <a href="{r["privacy"]}" target="_blank">{e(w["consent_link"])}</a>. *</span></label>
    </fieldset>
    <p class="wiz-err" data-wiz-err role="alert"></p>
    <div class="wiz-nav">
      <button type="button" class="btn btn-ghost" data-wiz-back hidden>{e(w["back"])}</button>
      <button type="button" class="btn btn-primary" data-wiz-next>{e(w["next"])} {icon("arrow")}</button>
      <button type="submit" class="btn btn-primary" data-wiz-submit hidden>{icon("send")} {e(w["submit"])}</button>
    </div>
  </form>
  <div class="wiz-ok" data-wiz-ok hidden tabindex="-1">
    <div class="ok-ic">{icon("check")}</div>
    <p class="ok-t">{e(w["ok_title"])}</p>
    <p>{e(w["ok_text"])}</p>
    <button type="button" class="btn btn-ghost" data-wiz-again>{e(w["again"])}</button>
  </div>
</div>'''


def cta_band(lang):
    t = T[lang]
    return f'''
<section class="cta-band">
  <div class="wrap cta-in reveal">
    <div><h2>{e(t["cta_title"])}</h2><p>{e(t["cta_sub"])}</p></div>
    <div class="cta-actions"><a class="btn btn-primary btn-lg" href="{ROUTES[lang]["quote"]}">{e(t["cta_btn"])} {icon("arrow")}</a>
    <p class="cta-mail">{e(t["cta_mail"])} <a href="mailto:{SITE["email"]}">{SITE["email"]}</a></p></div>
  </div>
</section>'''


def service_cards(lang, exclude=None):
    t = T[lang]
    out = []
    for s in SERVICES:
        if s["key"] == exclude:
            continue
        c = s[lang]
        out.append(f'''<a class="svc-card reveal" href="{svc_url(lang, s)}">
  <span class="svc-ic">{icon(s["icon"])}</span>
  <h3>{e(c["name"])}</h3>
  <p>{e(c["short"])}</p>
  <span class="more">{e(t["learn_more"])} {icon("arrow")}</span>
</a>''')
    return "".join(out)


def weg_band(lang):
    t = T[lang]
    pts = "".join(f"<li>{icon('check')}{e(x)}</li>" for x in t["weg_points"])
    mode = len(t["wizard"]["modes"]) - 1
    cta = (f'<a class="btn btn-primary" href="{ROUTES[lang]["quote"]}#m{mode}">{e(t["weg_cta"])} {icon("arrow")}</a>'
           if SITE.get("weg_separate_supply") else "")
    return f'''
<section class="weg" id="weg">
  <div class="wrap weg-in reveal">
    {weg_link_open(lang, "weg-mark")}<img class="weg-logo" src="/assets/img/weg-logo.svg" alt="WEG" width="180" height="126"><span class="weg-badge">{e(t["weg_badge"])}</span></a>
    <div class="weg-txt">
      <p class="kicker kicker-light">{e(t["weg_kicker"])}</p>
      <h2>{e(t["weg_title"])}</h2>
      <p>{e(t["weg_text"])}</p>
      <ul class="weg-pts">{pts}</ul>
      <div class="weg-actions">{cta}{weg_link_open(lang, "weg-site")}{e(t["weg_link"])} {icon("ext")}</a></div>
    </div>
  </div>
</section>'''


def brands_strip(lang):
    names = [("abb", "ABB"), ("schneider", "Schneider Electric"), ("siemens", "Siemens"),
             ("weidmuller", "Weidmüller"), ("phoenix-contact", "Phoenix Contact"), ("rittal", "Rittal")]
    others = "".join(f'<li><img src="/assets/img/brand-{f}.png" alt="{a(n)}" loading="lazy" height="44"></li>' for f, n in names)
    weg = (weg_link_open(lang, "brand-link") + '<img src="/assets/img/weg-logo.svg" alt="WEG" loading="lazy" height="44" width="63"></a>')
    items = f'<li>{weg}</li>{others}'
    # Second copy only exists for the endless scroll: hidden from screen readers and keyboard.
    weg_copy = weg.replace("<a ", '<a tabindex="-1" ', 1)
    copy = (f'<li aria-hidden="true">{weg_copy}</li>'
            + others.replace("<li>", '<li aria-hidden="true">'))
    return f'''
<section class="brands" aria-label="{a(T[lang]["brands_title"])}">
  <div class="wrap"><p class="brands-title">{e(T[lang]["brands_title"])}</p></div>
  <div class="marquee"><ul class="marquee-track">{items}{copy}</ul></div>
</section>'''


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def home_alternates():
    return {l: ROUTES[l]["home"] for l in LANGS}


def build_home(lang):
    t = T[lang]
    r = ROUTES[lang]
    h = t["hero"]
    chips = "".join(f'<li>{icon("check")}{e(c)}</li>' for c in h["chips"])
    facts = "".join(f'<div class="fact"><strong data-count="{n}">{n}</strong><span>{e(l)}</span></div>' for n, l in t["facts"])

    tabs = "".join(
        f'<button role="tab" class="ptab" id="ptab-{p["id"]}" aria-controls="ppanel-{p["id"]}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}" data-ptab>{e(p["tab"])}</button>'
        for i, p in enumerate(t["panels"]))
    panels = "".join(f'''
<div role="tabpanel" class="ppanel" id="ppanel-{p["id"]}" aria-labelledby="ptab-{p["id"]}"{"" if i == 0 else " hidden"}>
  <div class="ppanel-art" aria-hidden="true">{panel_art(p["id"])}</div>
  <div class="ppanel-txt">
    <p class="kicker">{e(p["tab"])}</p>
    <p class="ppanel-h">{e(p["title"])}</p>
    <p>{e(p["desc"])}</p>
    <ul class="ticks">{"".join(f"<li>{icon('check')}{e(x)}</li>" for x in p["points"])}</ul>
    <a class="btn btn-ghost" href="{svc_url(lang, SVC_BY_KEY[p["service"]])}">{e(t["learn_more"])} {icon("arrow")}</a>
  </div>
</div>''' for i, p in enumerate(t["panels"]))

    models = "".join(f'''
<div class="model reveal">
  <span class="model-n">0{i + 1}</span>
  <h3>{e(m["title"])}</h3>
  <p>{e(m["desc"])}</p>
  <a class="btn btn-ghost btn-sm" href="{r["quote"]}#m{i}" data-pick-mode="{i}">{e(m["cta"])} {icon("arrow")}</a>
</div>''' for i, m in enumerate(t["models"]))

    step_icons = ["ruler", "box", "wiring", "test", "send"]
    process = "".join(f'''
<li class="step reveal" style="--i:{i}">
  <span class="step-ic">{icon(step_icons[i])}</span>
  <span class="step-n">{i + 1}</span>
  <p class="step-t">{e(s)}</p><p>{e(d)}</p>
</li>''' for i, (s, d) in enumerate(t["process"]))

    gallery = gallery_items(lang, GALLERY[:6])
    more = (f'<div class="g-more reveal"><a class="btn btn-ghost" href="{r["gallery"]}">{e(t["gallery_all_btn"])} {icon("arrow")}</a></div>'
            if len(GALLERY) > 3 else "")

    who = "".join(f'<div class="who-item reveal"><span class="who-ic">{icon(ic)}</span><h3>{e(ti)}</h3><p>{e(d)}</p></div>' for ic, ti, d in t["who"])
    q_icons = ["shield", "award", "wiring", "test"]
    quality = "".join(f'<div class="q-item reveal"><span class="q-ic">{icon(q_icons[i])}</span><h3>{e(ti)}</h3><p>{e(d)}</p></div>' for i, (ti, d) in enumerate(t["quality"]))

    body = f'''
<section class="hero">
  <div class="hero-bg" aria-hidden="true">{circuit_svg()}</div>
  <div class="wrap hero-in">
    <div class="hero-txt">
      <p class="kicker kicker-light">{e(h["kicker"])}</p>
      <h1>{e(h["title"])}</h1>
      <p class="hero-sub">{e(h["sub"])}</p>
      <div class="hero-cta">
        <a class="btn btn-primary btn-lg" href="{r["quote"]}">{e(h["cta1"])} {icon("arrow")}</a>
        <a class="btn btn-outline-light btn-lg" href="#solucoes">{e(h["cta2"])}</a>
      </div>
      <ul class="hero-chips">{chips}</ul>
      <p class="hero-group">{e(t["group"])}</p>
    </div>
    <div class="hero-media">
      <div class="hero-frame" data-tilt>
        {picture("galeria-cablagem", t["gallery"][0][1], "hero-pic", "(max-width: 900px) 100vw, 45vw", eager=True, w=1400, h=1050)}
        <div class="hero-card c1">{icon("test")}<div><span class="hc-t">{e(h["card1_t"])}</span><span>{e(h["card1_d"])}</span></div></div>
        <div class="hero-card c2">{icon("wiring")}<div><span class="hc-t">{e(h["card2_t"])}</span><span>{e(h["card2_d"])}</span></div></div>
      </div>
    </div>
  </div>
  <div class="wrap facts">{facts}</div>
</section>
{brands_strip(lang)}
{weg_band(lang)}
<section class="sec" id="solucoes">
  <div class="wrap">
    {section_head(t["services_kicker"], t["services_title"], t["services_sub"])}
    <div class="svc-grid">{service_cards(lang)}</div>
  </div>
</section>
<section class="sec sec-alt" id="paineis">
  <div class="wrap">
    {section_head(t["panels_kicker"], t["panels_title"], t["panels_sub"], center=True)}
    <div class="ptabs reveal" role="tablist" aria-label="{a(t["panels_title"])}">{tabs}</div>
    <div class="ppanels reveal">{panels}</div>
  </div>
</section>
<section class="sec" id="modalidades">
  <div class="wrap">
    {section_head(t["models_kicker"], t["models_title"])}
    <div class="models">{models}</div>
  </div>
</section>
<section class="sec sec-dark" id="processo">
  <div class="wrap">
    {section_head(t["process_kicker"], t["process_title"], light=True)}
    <ol class="steps" data-steps>{process}</ol>
  </div>
</section>
{cases_section(lang)}
{testimonials_section(lang)}
<section class="sec" id="galeria">
  <div class="wrap">
    {section_head(t["gallery_kicker"], t["gallery_title"])}
    <div class="gallery" data-gallery>{gallery}</div>
    {more}
  </div>
</section>
<section class="sec sec-alt" id="clientes">
  <div class="wrap">
    {section_head(t["who_kicker"], t["who_title"], center=True)}
    <div class="who">{who}</div>
  </div>
</section>
<section class="sec" id="qualidade">
  <div class="wrap">
    {section_head(t["quality_kicker"], t["quality_title"])}
    <div class="quality">{quality}</div>
  </div>
</section>
<section class="sec sec-alt" id="faq">
  <div class="wrap narrow">
    {section_head(t["faq_kicker"], t["faq_title"], center=True)}
    {faq_block(t["faq"], "hfaq")}
  </div>
</section>
<section class="sec sec-quote" id="orcamento">
  <div class="wrap quote-grid">
    <div class="quote-side reveal">
      <p class="kicker">{e(t["nav"]["quote"])}</p>
      <h2>{e(t["cta_title"])}</h2>
      <p>{e(t["cta_sub"])}</p>
      {contact_list(lang)}
    </div>
    <div class="quote-card reveal">{wizard(lang)}</div>
  </div>
</section>'''
    schema = [org_schema(lang), faq_schema(t["faq"]),
              {"@context": "https://schema.org", "@type": "WebSite", "name": "ProDenki", "url": abs_url(r["home"]), "inLanguage": LANG_META[lang]["html"]}]
    return page(lang, r["home"], home_alternates(), t["home_meta_title"], t["home_meta_desc"], body, schema)


def contact_list(lang):
    t = T[lang]
    items = [f'<li>{icon("mail")}<div><small>{e(t["contact_email"])}</small><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></div></li>']
    if SITE["phone"]:
        items.append(f'<li>{icon("phone")}<div><small>{e(t["contact_phone"])}</small><a href="{tel_href()}" data-track="phone_click">{e(SITE["phone"])}</a></div></li>')
    if SITE["whatsapp"]:
        items.append(f'<li>{icon("whatsapp")}<div><small>WhatsApp</small><a href="https://wa.me/{SITE["whatsapp"]}" target="_blank" rel="noopener" data-track="whatsapp_click">+{SITE["whatsapp"]}</a></div></li>')
    addr = ", ".join(x for x in [SITE["street"], " ".join(x for x in [SITE["postal_code"], SITE["city"]] if x)] if x)
    if addr:
        items.append(f'<li>{icon("pin")}<div><small>{e(t["contact_address"])}</small><span>{e(addr)}</span></div></li>')
    items.append(f'<li>{icon("globe")}<div><small>{e(t["contact_area"])}</small><span>{e(t["contact_area_v"])}</span></div></li>')
    if SITE["linkedin"]:
        items.append(f'<li>{icon("linkedin")}<div><small>LinkedIn</small><a href="{a(SITE["linkedin"])}" target="_blank" rel="noopener" '
                     f'aria-label="{a(t["linkedin_aria"])}" data-track="linkedin_click">{e(t["linkedin_follow"])}</a></div></li>')
    return f'<ul class="contact-list">{"".join(items)}</ul>'


def breadcrumbs(lang, trail):
    """trail: list of (name, path or None)"""
    t = T[lang]
    full = [(t["breadcrumb_home"], ROUTES[lang]["home"])] + trail
    html_items = []
    for i, (n, p) in enumerate(full):
        if p and i < len(full) - 1:
            html_items.append(f'<li><a href="{p}">{e(n)}</a></li>')
        else:
            html_items.append(f'<li aria-current="page">{e(n)}</li>')
    schema = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": abs_url(p)} if p else {})} for i, (n, p) in enumerate(full)]}
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(html_items)}</ol></nav>', schema


def page_hero(lang, kicker, h1, lead, crumbs_html, extra=""):
    return f'''
<section class="phero">
  <div class="hero-bg" aria-hidden="true">{circuit_svg()}</div>
  <div class="wrap phero-in">
    {crumbs_html}
    <p class="kicker kicker-light">{e(kicker)}</p>
    <h1>{e(h1)}</h1>
    <p class="hero-sub">{e(lead)}</p>
    {extra}
  </div>
</section>'''


def build_service(lang, svc):
    t = T[lang]
    c = svc[lang]
    r = ROUTES[lang]
    alternates = {l: svc_url(l, svc) for l in LANGS}
    crumbs, crumb_schema = breadcrumbs(lang, [(t["svc_index_title"], r["services"]), (c["name"], None)])
    cta = f'<div class="hero-cta"><a class="btn btn-primary btn-lg" href="{r["quote"]}">{e(t["nav"]["quote"])} {icon("arrow")}</a></div>'
    img = svc["image"]
    includes = "".join(f'<li>{icon("check")}<span>{e(x)}</span></li>' for x in c["includes"])
    apps = "".join(f'<li>{e(x)}</li>' for x in c["applications"])
    specs = "".join(f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td></tr>' for k, v in c["specs"])
    intro = "".join(f'<p>{e(p)}</p>' for p in c["intro"])
    body = f'''
{page_hero(lang, t["svc_index_title"], c["h1"], c["lead"], crumbs, cta)}
<section class="sec">
  <div class="wrap svc-layout">
    <div class="svc-main">
      <div class="prose reveal">{intro}</div>
      <h2 class="h-sm reveal">{e(t["svc_includes"])}</h2>
      <ul class="incl reveal">{includes}</ul>
      <h2 class="h-sm reveal">{e(t["svc_apps"])}</h2>
      <ul class="apps reveal">{apps}</ul>
      <h2 class="h-sm reveal">{e(t["svc_faq"])}</h2>
      {faq_block(c["faq"], "sfaq")}
    </div>
    <aside class="svc-aside">
      <div class="aside-card reveal">
        {picture(img, c["name"], "aside-pic", "(max-width: 900px) 100vw, 360px", w=IMG_DIMS[img][0], h=IMG_DIMS[img][1])}
        <div class="aside-body">
          <h2 class="h-xs">{e(t["svc_specs"])}</h2>
          <table class="specs"><tbody>{specs}</tbody></table>
          <a class="btn btn-primary btn-block" href="{r["quote"]}">{e(t["nav"]["quote"])}</a>
        </div>
      </div>
    </aside>
  </div>
</section>
<section class="sec sec-alt">
  <div class="wrap">
    {section_head(t["svc_related"], t["services_title"])}
    <div class="svc-grid svc-grid-sm">{service_cards(lang, exclude=svc["key"])}</div>
  </div>
</section>
{cta_band(lang)}'''
    service_schema = {
        "@context": "https://schema.org", "@type": "Service", "name": c["name"], "description": c["meta_desc"],
        "serviceType": c["name"], "url": abs_url(svc_url(lang, svc)), "inLanguage": LANG_META[lang]["html"],
        "provider": {"@id": abs_url("/#org"), "@type": "ProfessionalService", "name": "ProDenki", "url": SITE["domain"]},
        "areaServed": {"@type": "Country", "name": "Portugal"},
    }
    return page(lang, svc_url(lang, svc), alternates, c["meta_title"], c["meta_desc"], body,
                [service_schema, crumb_schema, faq_schema(c["faq"])], og_image=f"/assets/img/{img}.jpg")


def build_services_index(lang):
    t = T[lang]
    r = ROUTES[lang]
    alternates = {l: ROUTES[l]["services"] for l in LANGS}
    crumbs, crumb_schema = breadcrumbs(lang, [(t["svc_index_title"], None)])
    body = f'''
{page_hero(lang, t["services_kicker"], t["svc_index_h1"], t["svc_index_lead"], crumbs)}
<section class="sec"><div class="wrap"><div class="svc-grid">{service_cards(lang)}</div></div></section>
{cta_band(lang)}'''
    title = f'{t["svc_index_h1"]} | ProDenki'
    return page(lang, r["services"], alternates, title, t["svc_index_meta_desc"], body, [crumb_schema])


def build_quote(lang):
    t = T[lang]
    r = ROUTES[lang]
    alternates = {l: ROUTES[l]["quote"] for l in LANGS}
    crumbs, crumb_schema = breadcrumbs(lang, [(t["quote_h1"], None)])
    body = f'''
{page_hero(lang, t["nav"]["quote"], t["quote_h1"], t["quote_lead"], crumbs)}
<section class="sec sec-quote">
  <div class="wrap quote-grid">
    <div class="quote-card reveal">{wizard(lang)}</div>
    <div class="quote-side reveal">
      <h2 class="h-sm">{e(t["contact_title"])}</h2>
      {contact_list(lang)}
      <div class="mini-steps">
        <p class="kicker">{e(t["process_kicker"])}</p>
        <ol>{"".join(f"<li><span class='ms-t'>{e(s)}</span> {e(d)}</li>" for s, d in t["process"])}</ol>
      </div>
    </div>
  </div>
</section>'''
    return page(lang, r["quote"], alternates, t["quote_meta_title"], t["quote_meta_desc"], body, [org_schema(lang), crumb_schema])


def build_gallery(lang):
    t = T[lang]
    r = ROUTES[lang]
    alternates = {l: ROUTES[l]["gallery"] for l in LANGS}
    crumbs, crumb_schema = breadcrumbs(lang, [(t["gallery_kicker"], None)])
    present = [c for c in t["gallery_cats"] if any(it.get("category") == c for it in GALLERY)]
    filters = (f'<button class="gf on" data-filter="" aria-pressed="true">{e(t["gallery_filter_all"])}</button>'
               + "".join(f'<button class="gf" data-filter="{c}" aria-pressed="false">{e(t["gallery_cats"][c])}</button>' for c in present))
    body = f'''
{page_hero(lang, t["gallery_kicker"], t["gallery_title"], t["gallery_page_lead"], crumbs)}
<section class="sec">
  <div class="wrap">
    {f'<div class="gfilters reveal" role="toolbar">{filters}</div>' if len(present) > 1 else ""}
    <div class="gallery" data-gallery>{gallery_items(lang, GALLERY)}</div>
  </div>
</section>
{cta_band(lang)}'''
    og = f"/assets/gallery/{GALLERY[0]['name']}.jpg" if GALLERY else "/assets/img/og-image.jpg"
    return page(lang, r["gallery"], alternates, t["gallery_page_title"], t["gallery_page_desc"], body, [crumb_schema], og_image=og)


def build_cases(lang):
    t = T[lang]
    r = ROUTES[lang]
    alternates = {l: ROUTES[l]["cases"] for l in LANGS}
    crumbs, crumb_schema = breadcrumbs(lang, [(t["cases_kicker"], None)])
    body = f'''
{page_hero(lang, t["cases_kicker"], t["cases_title"], t["cases_page_lead"], crumbs)}
<section class="sec">
  <div class="wrap"><div class="cases">{case_cards(lang, CASES)}</div></div>
</section>
{cta_band(lang)}'''
    first = next((c for c in CASES if c.get("name")), None)
    og = f"/assets/gallery/{first['name']}.jpg" if first else "/assets/img/og-image.jpg"
    return page(lang, r["cases"], alternates, t["cases_page_title"], t["cases_page_desc"], body, [crumb_schema], og_image=og)


def build_admin():
    """Decap CMS panel at /admin (login with GitHub). Needs SITE['github_repo']."""
    repo = SITE.get("github_repo")
    if not repo:
        return False
    (DIST / "admin").mkdir(parents=True, exist_ok=True)
    (DIST / "admin" / "index.html").write_text('''<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Painel ProDenki</title>
<link rel="icon" type="image/png" href="/assets/img/icon-32.png">
</head>
<body>
<script src="https://unpkg.com/decap-cms@3.17.3/dist/decap-cms.js"></script>
</body>
</html>
''', encoding="utf-8")
    cats = T["pt"]["gallery_cats"]
    options = "\n".join(f'                  - {{label: "{v}", value: "{k}"}}' for k, v in cats.items())
    (DIST / "admin" / "config.yml").write_text(f'''backend:
  name: github
  repo: {repo}
  branch: main
  commit_messages:
    update: "Site atualizado no painel"
    uploadMedia: "Nova foto: {{{{path}}}}"
    deleteMedia: "Foto apagada: {{{{path}}}}"

locale: pt
site_url: {SITE["domain"]}
display_url: {SITE["domain"]}
logo_url: {SITE["domain"]}/assets/img/logo.png
media_folder: src/uploads
public_folder: /uploads

collections:
  - name: galeria
    label: Galeria
    editor: {{preview: false}}
    files:
      - name: fotos
        label: Fotos dos quadros
        file: content/gallery.json
        format: json
        fields:
          - label: Fotos
            name: items
            widget: list
            add_to_top: true
            label_singular: foto
            summary: "{{{{fields.title}}}} — {{{{fields.date}}}}"
            fields:
              - {{label: "Foto", name: image, widget: image, choose_url: false, hint: "Foto do telemóvel serve: o site reduz o tamanho sozinho."}}
              - {{label: "Título (português)", name: title, widget: string, hint: "Ex.: CCM com 6 variadores WEG"}}
              - {{label: "Descrição (português)", name: description, widget: text, required: false}}
              - label: "Categoria"
                name: category
                widget: select
                options:
{options}
              - {{label: "Data", name: date, widget: datetime, format: "YYYY-MM-DD", date_format: "DD/MM/YYYY", time_format: false}}
              - {{label: "Mostrar no site", name: published, widget: boolean, default: true}}
              - {{label: "Título (inglês) — opcional", name: title_en, widget: string, required: false}}
              - {{label: "Descrição (inglês) — opcional", name: description_en, widget: text, required: false}}
              - {{label: "Título (espanhol) — opcional", name: title_es, widget: string, required: false}}
              - {{label: "Descrição (espanhol) — opcional", name: description_es, widget: text, required: false}}

  - name: casos
    label: Casos de sucesso
    editor: {{preview: false}}
    files:
      - name: casos
        label: Casos de sucesso
        file: content/cases.json
        format: json
        fields:
          - label: Casos
            name: items
            widget: list
            add_to_top: true
            label_singular: caso
            summary: "{{{{fields.title}}}} — {{{{fields.date}}}}"
            fields:
              - {{label: "Título da obra (português)", name: title, widget: string, hint: "Ex.: 11 quadros CCM para linha de extrusão"}}
              - {{label: "Setor (português)", name: sector, widget: string, required: false, hint: "Ex.: Indústria de plásticos"}}
              - {{label: "Cliente — deixe vazio se não tiver autorização para o nome", name: client, widget: string, required: false}}
              - {{label: "Descrição (português)", name: description, widget: text, hint: "O que o cliente precisava, o que a ProDenki fez e o resultado. 3 a 5 frases."}}
              - label: "Resultados em números (até 3)"
                name: results
                widget: list
                max: 3
                required: false
                summary: "{{{{fields.value}}}} {{{{fields.label}}}}"
                fields:
                  - {{label: "Número", name: value, widget: string, hint: "Ex.: 11, 22 dias, 1000 kVA"}}
                  - {{label: "Legenda (português)", name: label, widget: string, hint: "Ex.: quadros entregues"}}
                  - {{label: "Legenda (inglês) — opcional", name: label_en, widget: string, required: false}}
                  - {{label: "Legenda (espanhol) — opcional", name: label_es, widget: string, required: false}}
              - {{label: "Foto", name: image, widget: image, required: false, choose_url: false}}
              - {{label: "Data", name: date, widget: datetime, format: "YYYY-MM-DD", date_format: "DD/MM/YYYY", time_format: false}}
              - {{label: "Mostrar no site", name: published, widget: boolean, default: true}}
              - {{label: "Título (inglês) — opcional", name: title_en, widget: string, required: false}}
              - {{label: "Setor (inglês) — opcional", name: sector_en, widget: string, required: false}}
              - {{label: "Descrição (inglês) — opcional", name: description_en, widget: text, required: false}}
              - {{label: "Título (espanhol) — opcional", name: title_es, widget: string, required: false}}
              - {{label: "Setor (espanhol) — opcional", name: sector_es, widget: string, required: false}}
              - {{label: "Descrição (espanhol) — opcional", name: description_es, widget: text, required: false}}

  - name: depoimentos
    label: Depoimentos
    editor: {{preview: false}}
    files:
      - name: depoimentos
        label: Depoimentos de clientes
        file: content/testimonials.json
        format: json
        fields:
          - label: Depoimentos
            name: items
            widget: list
            add_to_top: true
            label_singular: depoimento
            summary: "{{{{fields.name}}}} {{{{fields.company}}}} — {{{{fields.date}}}}"
            fields:
              - {{label: "Depoimento (português)", name: quote, widget: text, hint: "As palavras do cliente, 2 a 4 frases. Pode corrigir a escrita, mas não o sentido."}}
              - {{label: "Nome — vazio se o cliente preferir não aparecer", name: name, widget: string, required: false}}
              - {{label: "Cargo (português)", name: role, widget: string, required: false, hint: "Ex.: Diretor de manutenção"}}
              - {{label: "Empresa — vazio se não autorizar o nome", name: company, widget: string, required: false}}
              - {{label: "Setor (português) — usado quando não há empresa", name: sector, widget: string, required: false, hint: "Ex.: Indústria alimentar"}}
              - {{label: "Foto ou logótipo — opcional", name: photo, widget: image, required: false, choose_url: false}}
              - {{label: "Data", name: date, widget: datetime, format: "YYYY-MM-DD", date_format: "DD/MM/YYYY", time_format: false}}
              - {{label: "O cliente autorizou a publicação deste depoimento", name: consent, widget: boolean, default: false, hint: "Obrigatório: sem esta autorização o depoimento não aparece no site."}}
              - {{label: "Mostrar no site", name: published, widget: boolean, default: true}}
              - {{label: "Depoimento (inglês) — opcional", name: quote_en, widget: text, required: false}}
              - {{label: "Cargo (inglês) — opcional", name: role_en, widget: string, required: false}}
              - {{label: "Setor (inglês) — opcional", name: sector_en, widget: string, required: false}}
              - {{label: "Depoimento (espanhol) — opcional", name: quote_es, widget: text, required: false}}
              - {{label: "Cargo (espanhol) — opcional", name: role_es, widget: string, required: false}}
              - {{label: "Setor (espanhol) — opcional", name: sector_es, widget: string, required: false}}
''', encoding="utf-8")
    return True


def build_privacy(lang):
    t = T[lang]
    r = ROUTES[lang]
    alternates = {l: ROUTES[l]["privacy"] for l in LANGS}
    crumbs, crumb_schema = breadcrumbs(lang, [(t["privacy_h1"], None)])
    items = "".join(f'<h2 class="h-sm">{e(h)}</h2><p>{e(p.format(email=SITE["email"]))}</p>' for h, p in t["privacy"])
    body = f'''
{page_hero(lang, "ProDenki", t["privacy_h1"], f'{t["updated"]}: {TODAY}', crumbs)}
<section class="sec"><div class="wrap narrow prose">{items}</div></section>'''
    return page(lang, r["privacy"], alternates, t["privacy_meta_title"], t["privacy_h1"] + " — ProDenki", body, [crumb_schema])


def build_404():
    lang = DEFAULT
    t = T[lang]
    alternates = home_alternates()
    links = " · ".join(f'<a href="{ROUTES[l]["home"]}">{LANG_META[l]["label"]}</a>' for l in LANGS)
    body = f'''
<section class="phero nf">
  <div class="hero-bg" aria-hidden="true">{circuit_svg()}</div>
  <div class="wrap phero-in">
    <p class="kicker kicker-light">404</p>
    <h1>{e(t["nf_h1"])}</h1>
    <p class="hero-sub">{e(t["nf_text"])}</p>
    <div class="hero-cta"><a class="btn btn-primary btn-lg" href="/">{e(t["nav"]["home"])}</a>
    <a class="btn btn-outline-light btn-lg" href="{ROUTES[lang]["services"]}">{e(t["nav"]["services"])}</a></div>
    <p class="nf-langs">{links}</p>
  </div>
</section>'''
    return page(lang, "/404.html", alternates, t["nf_meta_title"], t["nf_text"], body, noindex=True)


# ---------------------------------------------------------------------------
# Decorative SVGs
# ---------------------------------------------------------------------------
def circuit_svg():
    return '''<svg viewBox="0 0 1200 600" preserveAspectRatio="xMidYMid slice">
<defs><linearGradient id="cg" x1="0" x2="1"><stop offset="0" stop-color="#2F80ED" stop-opacity="0"/><stop offset=".5" stop-color="#5DA9FF"/><stop offset="1" stop-color="#E65000" stop-opacity="0"/></linearGradient>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0v40" fill="none" stroke="#ffffff" stroke-opacity=".04"/></pattern></defs>
<rect width="1200" height="600" fill="url(#grid)"/>
<g fill="none" stroke-width="1.5" class="traces">
<path d="M0 120h220l40 40h260l30-30h180" stroke="#5DA9FF" stroke-opacity=".18"/>
<path d="M1200 90H960l-40 40H760" stroke="#5DA9FF" stroke-opacity=".18"/>
<path d="M0 480h160l60-60h300l40 40h220l50-50h370" stroke="#5DA9FF" stroke-opacity=".14"/>
<path d="M600 600V500l40-40h200" stroke="#E65000" stroke-opacity=".2"/>
<path class="pulse p1" d="M0 120h220l40 40h260l30-30h180" stroke="url(#cg)" stroke-width="2.5"/>
<path class="pulse p2" d="M0 480h160l60-60h300l40 40h220l50-50h370" stroke="url(#cg)" stroke-width="2.5"/>
<path class="pulse p3" d="M1200 90H960l-40 40H760" stroke="url(#cg)" stroke-width="2.5"/>
</g>
<g fill="#5DA9FF" fill-opacity=".35"><circle cx="730" cy="130" r="4"/><circle cx="760" cy="130" r="4"/><circle cx="520" cy="160" r="3"/><circle cx="840" cy="460" r="4"/><circle cx="1200" cy="410" r="3"/></g>
</svg>'''


def panel_art(kind):
    """Small schematic illustration of a panel front, varied per type."""
    rows = {
        "qgbt": [("brk", 1), ("brk", 4), ("brk", 4), ("meter", 2)],
        "ccm": [("drive", 3), ("brk", 5), ("ctr", 5)],
        "qcm": [("plc", 1), ("io", 6), ("relay", 6)],
        "qta": [("brk", 2), ("ctr", 2), ("meter", 2)],
        "qd": [("brk", 6), ("brk", 6), ("sock", 3)],
        "solar": [("mppt", 1), ("brk", 4), ("spd", 3)],
    }[kind]
    parts = []
    y = 46
    for typ, n in rows:
        h = {"brk": 44, "meter": 40, "drive": 70, "ctr": 34, "plc": 46, "io": 40, "relay": 30, "sock": 46, "mppt": 70, "spd": 40}[typ]
        gap = 8
        width = 232
        cw = (width - gap * (n - 1)) / n
        for i in range(n):
            x = 44 + i * (cw + gap)
            color = {"drive": "#2F80ED", "plc": "#2F80ED", "mppt": "#E65000", "meter": "#0F2B4C", "spd": "#E65000"}.get(typ, "#e7edf5")
            stroke = "#9fb3c8"
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{h}" rx="4" fill="{color}" stroke="{stroke}"/>')
            if typ in ("brk", "ctr", "relay", "io"):
                parts.append(f'<rect x="{x + cw / 2 - 4:.1f}" y="{y + h / 2 - 7}" width="8" height="14" rx="2" fill="#04213F"/>')
            if typ in ("meter", "drive", "plc", "mppt"):
                parts.append(f'<rect x="{x + 8:.1f}" y="{y + 8}" width="{max(cw - 16, 10):.1f}" height="{min(h - 30, 22)}" rx="2" fill="#bfe3ff" class="screen"/>')
            if typ == "sock":
                parts.append(f'<circle cx="{x + cw / 2:.1f}" cy="{y + h / 2}" r="12" fill="#E65000"/>')
        y += h + 16
        parts.append(f'<rect x="38" y="{y - 10}" width="244" height="4" rx="2" fill="#c9d6e3"/>')
    return (f'<svg viewBox="0 0 320 {max(y + 30, 300)}" class="panel-svg"><rect x="20" y="20" width="280" height="{max(y + 30, 300) - 40}" rx="10" fill="#f6f9fc" stroke="#04213F" stroke-width="3"/>'
            f'<rect x="20" y="20" width="280" height="14" rx="6" fill="#04213F"/>' + "".join(parts) + '</svg>')


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def write(path, content):
    out = DIST / (path.lstrip("/") + ("index.html" if path.endswith("/") else ""))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return out


def sitemap(entries):
    rows = []
    for alts in entries:
        for l in LANGS:
            links = "".join(f'<xhtml:link rel="alternate" hreflang="{LANG_META[x]["html"]}" href="{abs_url(alts[x])}"/>' for x in LANGS)
            links += f'<xhtml:link rel="alternate" hreflang="x-default" href="{abs_url(alts[DEFAULT])}"/>'
            rows.append(f'<url><loc>{abs_url(alts[l])}</loc><lastmod>{TODAY}</lastmod>{links}</url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n")


def main():
    global VER
    VER = asset_hash()
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SRC / "assets", DIST / "assets")
    global GALLERY
    GALLERY = load_gallery()
    global CASES
    CASES = load_cases()
    global TESTIMONIALS
    TESTIMONIALS = load_testimonials()
    pages = 0
    entries = [home_alternates(), {l: ROUTES[l]["services"] for l in LANGS}, {l: ROUTES[l]["quote"] for l in LANGS},
               {l: ROUTES[l]["gallery"] for l in LANGS},
               *([{l: ROUTES[l]["cases"] for l in LANGS}] if CASES else []),
               {l: ROUTES[l]["privacy"] for l in LANGS}]
    for lang in LANGS:
        write(ROUTES[lang]["home"], build_home(lang)); pages += 1
        write(ROUTES[lang]["services"], build_services_index(lang)); pages += 1
        write(ROUTES[lang]["quote"], build_quote(lang)); pages += 1
        write(ROUTES[lang]["gallery"], build_gallery(lang)); pages += 1
        if CASES:
            write(ROUTES[lang]["cases"], build_cases(lang)); pages += 1
        write(ROUTES[lang]["privacy"], build_privacy(lang)); pages += 1
        for s in SERVICES:
            write(svc_url(lang, s), build_service(lang, s)); pages += 1
    for s in SERVICES:
        entries.append({l: svc_url(l, s) for l in LANGS})
    (DIST / "404.html").write_text(build_404(), encoding="utf-8"); pages += 1
    (DIST / "sitemap.xml").write_text(sitemap(entries), encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {abs_url('/sitemap.xml')}\n", encoding="utf-8")
    (DIST / "site.webmanifest").write_text(json.dumps({
        "name": SITE["legal_name"], "short_name": "ProDenki", "start_url": "/", "display": "standalone",
        "background_color": "#ffffff", "theme_color": "#04213F",
        "icons": [{"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False), encoding="utf-8")
    (DIST / "_headers").write_text(
        "/assets/css/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        "/assets/js/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        "/assets/img/*\n  Cache-Control: public, max-age=604800\n"
        "/assets/gallery/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  X-Frame-Options: SAMEORIGIN\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n", encoding="utf-8")
    # Old single-page assets kept working for anyone linking to them.
    redirects = ["/Logo.png /assets/img/logo.png 301", "/index.html / 301"]
    (DIST / "_redirects").write_text("\n".join(redirects) + "\n", encoding="utf-8")
    if build_admin():
        print("Admin panel: /admin")
    print(f"Built {pages} pages and {len(GALLERY)} gallery photos into {DIST}")


if __name__ == "__main__":
    main()
