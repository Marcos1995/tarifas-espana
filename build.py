"""Genera el sitio estatico en _site/ desde project.json + data/items.json.

Copia de templates/site-kit: no editar en cada repo (mejora en el kit y recopia). Solo stdlib.
Pagina con menos de MIN_FACTS datos propios: noindex y fuera del sitemap (anti contenido escaso).
"""
import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
MIN_FACTS = 3
SLUG_RE = re.compile(r"[a-z0-9][a-z0-9-]*")

CSS = """:root{--bg:#FAFAF9;--surface:#fff;--ink:#1C1917;--muted:#57534E;--line:#E7E5E4;--accent:#0F7B5F;--on:#fff;--radius:10px;color-scheme:light dark}
@media(prefers-color-scheme:dark){:root{--bg:#0C0A09;--surface:#1C1917;--ink:#FAFAF9;--muted:#A8A29E;--line:#292524;--accent:#4FD1A5;--on:#0C0A09}}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;font:400 clamp(1rem,.96rem + .2vw,1.125rem)/1.6 system-ui,-apple-system,"Segoe UI",Inter,sans-serif;color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-underline-offset:.2em}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
.wrap{width:min(100% - 2rem,64rem);margin-inline:auto}
.top{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.75rem 1rem;min-height:56px}
.brand{font-weight:600;letter-spacing:-.01em;color:var(--ink);text-decoration:none}
.top nav{display:flex;gap:1rem;font-size:.9375rem}.top nav a{color:var(--muted);text-decoration:none}.top nav a:hover{color:var(--ink)}
main{padding-block:clamp(2rem,6vw,4.5rem)}
h1,h2{line-height:1.15;letter-spacing:-.02em;text-wrap:balance}
h1{font-size:clamp(2.25rem,1.6rem + 3vw,3.75rem);margin:0 0 .4em}
h2{font-size:clamp(1.25rem,1.1rem + .6vw,1.5rem);margin:2.5rem 0 1rem}
.lead{font-size:clamp(1.125rem,1rem + .5vw,1.375rem);color:var(--muted);max-width:60ch;margin:0 0 1.5rem;text-wrap:pretty}
.crumb{font-size:.9375rem;color:var(--muted);margin-bottom:1rem}.crumb a{color:var(--muted)}
.chip{display:inline-block;padding:.15rem .7rem;border:1px solid var(--line);border-radius:99px;font-size:.875rem;color:var(--muted)}
.search{width:100%;max-width:32rem;min-height:48px;padding:.6rem 1rem;font:inherit;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:var(--radius)}
.meta{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1rem}
.facts{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr));margin:2rem 0}
.fact{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:1rem 1.25rem}
.fact dt{font-size:.875rem;color:var(--muted);margin-bottom:.25rem}.fact dd{margin:0;font-size:1.25rem;font-weight:600;letter-spacing:-.01em;overflow-wrap:anywhere}
.fact.lead-fact dd{font-size:clamp(1.6rem,1.1rem + 1.4vw,2.15rem)}
.kpis,.picks{display:grid;gap:.75rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,14rem),1fr))}
.kpi,.pick{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:1rem 1.1rem;color:var(--ink);text-decoration:none}
.kpi span,.pick small{display:block;color:var(--muted);font-size:.875rem;line-height:1.4}
.kpi strong,.pick b{display:block;font-size:clamp(1.35rem,1rem + 1vw,1.85rem);font-weight:600;letter-spacing:-.03em;line-height:1.15;margin:.2rem 0}
.pick{display:flex;flex-direction:column;gap:.25rem;min-height:100%}
.pick:hover,.pick.best{border-color:var(--accent)}
.pick.best{box-shadow:inset 0 0 0 1px var(--accent)}
.note{color:var(--muted);max-width:65ch;margin:0 0 1rem}
.bars{display:grid;gap:.35rem;margin:1.25rem 0}.bar{display:grid;grid-template-columns:2.75rem minmax(0,1fr) auto;align-items:center;gap:.5rem;font-size:.875rem}
.bar i{display:block;height:.7rem;border-radius:99px;background:var(--line);min-width:2%}.bar.best i{background:var(--accent)}.bar span:last-child{color:var(--muted);font-variant-numeric:tabular-nums}
.src,footer{color:var(--muted);font-size:.9375rem}.src a{overflow-wrap:anywhere}
footer{border-top:1px solid var(--line);padding-block:2rem}footer a{color:var(--muted)}
.app{display:grid;grid-template-columns:15.5rem minmax(0,1fr);min-height:100vh}
.side{position:sticky;top:0;height:100vh;display:flex;flex-direction:column;gap:.35rem;padding:1.25rem .9rem;background:var(--surface);border-right:1px solid var(--line)}
.side .brand{display:block;margin:0 .35rem .85rem;color:var(--ink);text-decoration:none}
.tab{display:flex;align-items:center;gap:.65rem;width:100%;min-height:44px;padding:.5rem .7rem;border:0;border-radius:var(--radius);background:transparent;color:var(--muted);font:500 1rem inherit;text-align:left;cursor:pointer}
.tab svg{width:1.25rem;height:1.25rem;flex:none;stroke:currentColor;fill:none;stroke-width:1.5}
.tab[aria-selected="true"]{background:var(--bg);color:var(--ink);box-shadow:inset 0 0 0 1px var(--line)}
.stage{padding:clamp(1.15rem,2.5vw,2rem) clamp(1rem,3vw,2.25rem) 2.5rem;width:min(100%,76rem)}
.panel[hidden]{display:none}
.stage h1{font-size:clamp(1.85rem,1.2rem + 2vw,2.6rem);margin:0}
.sub{color:var(--muted);margin:.35rem 0 1.1rem;max-width:62ch}
.stats{display:grid;gap:.75rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,10.5rem),1fr));margin:0 0 1.1rem}
.stat{min-width:0;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:.9rem 1rem}
.stat span{display:block;color:var(--muted);font-size:.8125rem}
.stat strong{display:block;margin-top:.15rem;font-size:clamp(1.05rem,.85rem + .8vw,1.7rem);font-weight:600;letter-spacing:-.03em;line-height:1.15;overflow-wrap:anywhere}
.seg{display:inline-flex;gap:.15rem;padding:.2rem;margin-bottom:1rem;background:var(--surface);border:1px solid var(--line);border-radius:999px}
.seg button{min-height:40px;padding:.3rem .95rem;border:0;border-radius:999px;background:transparent;color:var(--muted);font:500 .9375rem inherit;cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--accent);color:var(--on)}
.hours{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:.4rem;min-width:0}
.hour{display:flex;flex-direction:column;justify-content:flex-end;align-items:stretch;gap:.35rem;min-width:0;min-height:7.25rem;padding:.4rem .2rem;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink);font:500 .72rem inherit;cursor:pointer}
.hour i{display:block;width:46%;margin-inline:auto;height:calc(var(--h) * 4.2rem);min-height:3px;border-radius:99px;background:var(--line)}
.hour.best i,.hour[aria-pressed="true"] i{background:var(--accent)}
.hour[aria-pressed="true"]{box-shadow:inset 0 0 0 1px var(--accent)}
.controls{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,16rem),1fr));align-items:end;margin:0 0 1rem}
.field{display:flex;flex-direction:column;gap:.35rem;color:var(--muted);font-size:.875rem}
.field input,.field select{width:100%;min-height:48px;padding:.5rem .75rem;font:500 1rem inherit;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:var(--radius)}
input[type=range]{accent-color:var(--accent);padding:0}
.result{padding:1.15rem 1.25rem;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius)}
.result b{display:block;font-size:clamp(2rem,1.1rem + 2.2vw,3.1rem);font-weight:600;letter-spacing:-.03em;line-height:1}
.result em{font-style:normal;color:var(--muted)}
.tariffs{display:grid;gap:.45rem;margin-top:1rem}
.tariff{display:grid;grid-template-columns:4.5rem minmax(0,1fr) auto;gap:.6rem;align-items:center;padding:.65rem .8rem;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);min-width:0}
.tariff.on{border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent)}
.tariff small{color:var(--muted);min-width:0}
.fine{margin-top:.8rem;color:var(--muted);font-size:.875rem;max-width:68ch;overflow-wrap:anywhere}
#luz-out b{display:block;font-size:clamp(2rem,1.1rem + 2.2vw,3.1rem);font-weight:600;letter-spacing:-.03em;line-height:1;color:var(--ink)}
#luz-out em{font-style:normal}
.hour span{font-variant-numeric:tabular-nums}
@media(max-width:900px){.hours{grid-template-columns:repeat(6,minmax(0,1fr))}}
@media(max-width:767px){
.app{display:block;max-width:100%}
.side{position:sticky;top:0;z-index:6;height:auto;width:100%;min-width:0;flex-direction:row;align-items:center;gap:.25rem;padding:.45rem .6rem;border-right:0;border-bottom:1px solid var(--line);overflow-x:auto}
.side .brand{margin:0 .4rem 0 0;white-space:nowrap}
.tab{width:auto;flex:none}
.stage{width:100%;max-width:100%;padding:1rem .85rem 2rem}
.panel,.result,.controls,.field{min-width:0;max-width:100%}
.tariff{grid-template-columns:1fr auto}
.tariff small{grid-column:1 / -1}
.stats{grid-template-columns:1fr 1fr}
}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}"""


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def lookup(item: dict | None, label: str) -> str:
    if not item:
        return ""
    for key, value in item.get("facts") or []:
        if key == label or str(key).startswith(label):
            return str(value)
    return ""


def es_eur(n: float) -> str:
    whole, frac = f"{abs(n):.2f}".split(".")
    grouped = f"{int(whole):,}".replace(",", ".")
    return f"{'-' if n < 0 else ''}{grouped},{frac} €"


def euro(text: str) -> float | None:
    match = re.search(r"(\d{1,3}(?:\.\d{3})*),(\d+)", text or "")
    if not match:
        return None
    return float(match.group(1).replace(".", "") + "." + match.group(2))


def bars_html(item: dict) -> str:
    rows = item.get("bars") or []
    if not rows:
        return ""
    top = max(row[1] for row in rows) or 1
    inner = "".join(
        f'<div class="bar{" best" if len(row) > 3 and row[3] else ""}"><span>{esc(row[0])}</span>'
        f'<i aria-hidden="true" style="width:{max(2, round(row[1] / top * 100))}%"></i><span>{esc(row[2])}</span></div>'
        for row in rows
    )
    return f'<div class="bars">{inner}</div>'


def ordered_facts(facts: list) -> list:
    head, tail = [], []
    for key, value in facts:
        if str(key).startswith(("Hora más barata", "Término variable", "Total")):
            head.append((key, value))
        else:
            tail.append((key, value))
    return head + tail


def validate(items: list) -> list[str]:
    errors, seen = [], set()
    for i, item in enumerate(items):
        for key in ("slug", "title", "summary", "facts"):
            if not item.get(key):
                errors.append(f"item {i}: falta '{key}'")
        slug = str(item.get("slug", ""))
        if not SLUG_RE.fullmatch(slug):
            errors.append(f"item {i}: slug invalido '{slug}'")
        if slug in seen:
            errors.append(f"item {i}: slug repetido '{slug}'")
        seen.add(slug)
        for fact in item.get("facts") or []:
            if not (isinstance(fact, list) and len(fact) == 2):
                errors.append(f"item {i}: fact invalido {fact!r}")
        for bar in item.get("bars") or []:
            if not (isinstance(bar, list) and len(bar) in (3, 4) and isinstance(bar[1], (int, float))):
                errors.append(f"item {i}: bar invalida {bar!r} (etiqueta, valor, texto[, mejor])")
    return errors


def page(cfg: dict, title: str, body: str, path: str, desc: str, ld: dict | None = None, index: bool = True, shell: str = "doc") -> str:
    base = cfg["site_url"].rstrip("/")
    analytics = (
        f'<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
        f"data-cf-beacon='{{\"token\": \"{esc(cfg['analytics_token'])}\"}}'></script>"
        if cfg.get("analytics_token")
        else ""
    )
    ld_tag = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ""
    robots = "" if index else '<meta name="robots" content="noindex">'
    tone = ""
    if cfg.get("accent"):
        tone = f":root{{--accent:{esc(cfg['accent'])}}}"
        if cfg.get("accent_dark"):
            tone += f"@media(prefers-color-scheme:dark){{:root{{--accent:{esc(cfg['accent_dark'])}}}}}"
    icon = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='12' fill='%230F7B5F'/%3E%3C/svg%3E"
    doc = (
        f'<!doctype html><html lang="{esc(cfg.get("lang", "es"))}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>'
        f'<meta name="description" content="{esc(desc[:160])}"><link rel="canonical" href="{esc(base + path)}">'
        f'<meta name="theme-color" content="#FAFAF9"><link rel="icon" href="{icon}">'
        f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc[:160])}">'
        f'{robots}<style>{CSS}{tone}</style>{ld_tag}{cfg.get("head_html", "")}{analytics}</head><body>'
    )
    if shell == "app":
        return doc + body + "</body></html>"
    return (
        doc
        + f'<header class="top"><div class="wrap"><a class="brand" href="{esc(base)}/">Tarifas</a>'
        f'<nav aria-label="Secciones"><a href="{esc(base)}/#luz">Luz</a><a href="{esc(base)}/#gas">Gas</a><a href="{esc(base)}/#agua">Agua</a></nav></div></header>'
        f'<main class="wrap">{body}</main>'
        f'<footer><div class="wrap">{esc(cfg["title"])} · datos abiertos · <a href="{esc(base)}/api/items.json">JSON</a> · '
        f'<a href="{esc(base)}/openapi.json">OpenAPI</a> · <a href="{esc(base)}/llms.txt">llms.txt</a></div></footer></body></html>'
    )


AGUA_CALC = [
    {"slug": "agua-madrid", "name": "Madrid", "kind": "madrid", "note": "60 días, contador 15 mm, 1 vivienda, invierno. Tarifas máximas, sin IVA."},
    {"slug": "agua-barcelona", "name": "Barcelona", "kind": "tiers", "fixed": 3.59, "note": "Vivienda tipo A. Sin tasa de alcantarillado.", "tiers": [[6, 0.8229], [9, 1.6460], [15, 2.5607], [18, 3.4140], [None, 4.2674]]},
    {"slug": "agua-hospitalet", "name": "L'Hospitalet", "kind": "tiers", "fixed": 3.59, "note": "Misma tarifa metropolitana, vivienda tipo A.", "tiers": [[6, 0.8229], [9, 1.6460], [15, 2.5607], [18, 3.4140], [None, 4.2674]]},
    {"slug": "agua-valencia", "name": "València", "kind": "valencia", "note": "Contador 15 mm, sin IVA y sin mantenimiento del contador."},
    {"slug": "agua-sevilla", "name": "Sevilla", "kind": "sevilla", "note": "Mes de 30 días, sin habitantes acreditados, K=1, sin IVA."},
    {"slug": "agua-zaragoza", "name": "Zaragoza", "kind": "zaragoza", "note": "30 días, calibre hasta 20 mm, sin coeficientes de hogar."},
    {"slug": "agua-malaga", "name": "Málaga", "kind": "tiers", "fixed": 3.230, "note": "Sin habitantes acreditados, hasta 15 mm, IVA excluido.", "tiers": [[2, 0.467], [3, 1.130], [5, 1.619], [None, 3.048]]},
    {"slug": "agua-murcia", "name": "Murcia", "kind": "tiers", "fixed": 6.899110, "note": "Contador de menos de 15 mm. Solo agua potable.", "tiers": [[2.5, 0.632586], [10, 1.061759], [13, 1.502518], [30, 2.447747], [None, 3.038728]]},
    {"slug": "agua-cordoba", "name": "Córdoba", "kind": "cordoba", "note": "Factura del bimestre (el doble de m³ al mes). IVA excluido."},
    {"slug": "agua-granada", "name": "Granada", "kind": "tiers", "fixed": 2.3592, "note": "Contador hasta 15 mm, IVA excluido, sin alcantarillado.", "tiers": [[2, 0.4377], [10, 0.7777], [18, 1.6515], [None, 2.2238]]},
]
GAS_BAND = {"gas-tur1": (0, 5000), "gas-tur2": (5000, 15000), "gas-tur3": (15000, 50000), "gas-tur4": (50000, 300000)}
ICON = {
    "luz": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z" stroke-linejoin="round" stroke-linecap="round"/></svg>',
    "gas": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22a5 5 0 0 0 5-5c0-3-5-9-5-14 0 5-5 11-5 14a5 5 0 0 0 5 5z" stroke-linejoin="round"/></svg>',
    "agua": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3s6 7 6 11a6 6 0 0 1-12 0c0-4 6-11 6-11z" stroke-linejoin="round"/></svg>',
}


def hour_grid(item: dict | None, pressed: str) -> str:
    rows = (item or {}).get("bars") or []
    if not rows:
        return ""
    top = max(row[1] for row in rows) or 1
    out = []
    for row in rows:
        label, value, text = row[0], row[1], row[2]
        best = len(row) > 3 and bool(row[3])
        out.append(
            f'<button type="button" class="hour{" best" if best else ""}" '
            f'aria-pressed="{"true" if label == pressed else "false"}" '
            f'data-h="{esc(label)}" data-t="{esc(text)}" data-best="{"1" if best else "0"}" '
            f'style="--h:{max(0.08, value / top):.3f}"><i></i><span>{esc(label)}</span></button>'
        )
    return "".join(out)


def stat_row(item: dict | None, labels: list[str]) -> str:
    cells = []
    for label in labels:
        value = lookup(item, label).split(" (")[0]
        if value:
            cells.append(f'<div class="stat"><span>{esc(label)}</span><strong>{esc(value)}</strong></div>')
    return f'<div class="stats">{"".join(cells)}</div>' if cells else ""


def dashboard(cfg: dict, indexable: list, base: str) -> str:
    by_slug = {it["slug"]: it for it in indexable}
    hoy = by_slug.get("luz-hoy")
    semana = by_slug.get("luz-semana")
    cheap = lookup(hoy, "Hora más barata")
    hour = cheap.split(" ", 1)[0] if cheap else ""
    price = ""
    found = re.search(r"\(([^)]+)\)", cheap)
    if found:
        price = found.group(1)
    luz_labels = ["Precio medio PVPC", "Hora más cara", "Diferencia con la media de 7 días", "Precio medio mercado spot"]
    week_labels = ["Precio medio PVPC", "Hora más cara", "Día más barato", "Día más caro"]
    series = ""
    if hoy:
        series += (
            f'<div class="series" data-series="hoy">{stat_row(hoy, luz_labels)}'
            f'<div class="hours">{hour_grid(hoy, hour)}</div></div>'
        )
    if semana:
        series += (
            f'<div class="series" data-series="semana" hidden>{stat_row(semana, week_labels)}'
            f'<div class="hours">{hour_grid(semana, lookup(semana, "Hora más barata").split(" ", 1)[0])}</div></div>'
        )
    gas_rows = []
    for it in sorted((it for it in indexable if it["slug"] in GAS_BAND), key=lambda it: it["slug"]):
        lo, hi = GAS_BAND[it["slug"]]
        variable = euro(lookup(it, "Término variable"))
        fijo = euro(lookup(it, "Término fijo"))
        if variable is None or fijo is None:
            continue
        gas_rows.append({
            "id": it["title"].split(" de ")[0],
            "slug": it["slug"],
            "min": lo,
            "max": hi,
            "fijo": fijo,
            "v": variable,
            "scope": lookup(it, "Consumo de la tarifa"),
        })
    cards = []
    chosen = None
    for row in gas_rows:
        fijo_txt = f'{row["fijo"]:.2f}'.replace(".", ",")
        on = row["min"] < 9000 <= row["max"]
        if on:
            chosen = row
        cards.append(
            f'<div class="tariff{" on" if on else ""}" data-id="{esc(row["id"])}"><strong>{esc(row["id"])}</strong>'
            f'<small>{esc(row["scope"])}</small><b>{fijo_txt} €/mes</b></div>'
        )
    gas_html = "".join(cards)
    gas_seed = ""
    if chosen:
        month = chosen["fijo"] + (9000 / 12) * chosen["v"]
        gas_seed = (
            f"<b>{es_eur(month)}</b><em>{esc(chosen['id'])} al mes, sin impuestos. "
            f"Fijo {es_eur(chosen['fijo'])} más el consumo.</em>"
        )
    cities = [c for c in AGUA_CALC if c["slug"] in by_slug]
    options = "".join(f'<option value="{esc(c["slug"])}">{esc(c["name"])}</option>' for c in cities)
    agua_seed = ""
    if cities and cities[0]["kind"] == "madrid":
        agua_seed = (
            f"<b>{es_eur(18.94 + 20 * 1.0158)}</b>"
            f"<em>{esc(cities[0]['name'])} · 10 m³. {esc(cities[0]['note'])}</em>"
        )
    media = lookup(by_slug.get("agua-media-espana"), "Precio medio doméstico")
    script = r"""
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>[...r.querySelectorAll(s)];
function openPanel(name){
  const btn=$(`.tab[data-panel="${name}"]`);
  if(!btn) return;
  $$(".tab").forEach(b=>b.setAttribute("aria-selected", b===btn));
  $$(".panel").forEach(p=>{p.hidden=p.id!=="panel-"+name;});
}
$$(".tab").forEach(btn=>btn.addEventListener("click",()=>{
  openPanel(btn.dataset.panel);
  history.replaceState(null,"","#"+btn.dataset.panel);
}));
const start=(location.hash||"#luz").replace("#","");
if(["luz","gas","agua"].includes(start)) openPanel(start);
function setHour(btn){
  const box=btn.closest(".series");
  $$(".hour", box).forEach(h=>h.setAttribute("aria-pressed", h===btn));
  const mark=btn.dataset.best==="1"?"Entre las 6 más baratas":"Fuera de las 6 más baratas";
  $("#panel-luz h1").textContent=btn.dataset.h;
  $("#luz-out").innerHTML="<b>"+btn.dataset.t+"</b><em>"+mark+"</em>";
}
$$(".hour").forEach(h=>h.addEventListener("click",()=>setHour(h)));
$$(".seg button").forEach(b=>b.addEventListener("click",()=>{
  $$(".seg button").forEach(x=>x.setAttribute("aria-pressed", x===b));
  $$(".series").forEach(s=>{s.hidden=s.dataset.series!==b.dataset.series;});
  const on=$(".series:not([hidden]) .hour[aria-pressed='true']");
  if(on) setHour(on);
}));
const gas=JSON.parse($("#gas-data").textContent);
const eur=n=>n.toLocaleString("es-ES",{minimumFractionDigits:2,maximumFractionDigits:2})+" €";
function pickGas(kwh){
  return gas.find(g=>kwh<=g.max && kwh>g.min) || gas[0];
}
function gasUpdate(){
  const kwh=Math.max(0, Math.min(300000, Number($("#kwhn").value)||0));
  $("#kwhn").value=kwh; $("#kwh").value=Math.min(50000, kwh);
  const row=pickGas(kwh);
  $$(".tariff").forEach(el=>el.classList.toggle("on", el.dataset.id===row.id));
  const month=row.fijo+(kwh/12)*row.v;
  $("#gas-out").innerHTML="<b>"+eur(month)+"</b><em>"+row.id+" al mes, sin impuestos. Fijo "+eur(row.fijo)+" más el consumo.</em>";
}
$("#kwh").addEventListener("input",()=>{$("#kwhn").value=$("#kwh").value; gasUpdate();});
$("#kwhn").addEventListener("input", gasUpdate);
const agua=JSON.parse($("#agua-data").textContent);
function tiers(list,m3){
  let left=m3, prev=0, sum=0;
  for(const [up,price] of list){
    const room=up==null?left:Math.max(0, up-prev);
    const take=Math.min(left, room);
    sum+=take*price; left-=take; prev=up??prev;
    if(left<=1e-9) break;
  }
  return sum;
}
function aguaCost(c,m3){
  if(c.kind==="tiers") return c.fixed+tiers(c.tiers,m3);
  if(c.kind==="valencia"){
    const rate=m3*2<=12?0.477306:0.558360;
    return 6.024+3.403+m3*(rate+0.032579);
  }
  if(c.kind==="zaragoza"){
    const d=m3/30, t1=Math.min(d,0.2), t2=Math.min(Math.max(d-0.2,0),0.416), t3=Math.max(d-0.616,0);
    return 0.093264*30+(t1*0.287+t2*0.688+t3*1.720)*30;
  }
  if(c.kind==="sevilla"){
    const d=m3/30, t1=Math.min(d,0.11), t2=Math.min(Math.max(d-0.11,0),0.02), t3=Math.max(d-0.13,0);
    return 0.271*30+(t1*1.448+t2*2.798+t3*4.891)*30;
  }
  if(c.kind==="madrid"){
    const prices=[1.0158,1.5923,3.4745,3.9956];
    let left=m3*2, prev=0, v=0;
    for(let i=0;i<4;i++){
      const up=i<3?(i+1)*20:1e12, take=Math.min(left, up-prev);
      v+=take*prices[i]; left-=take; prev=up;
      if(left<=0) break;
    }
    return 18.94+v;
  }
  if(c.kind==="cordoba") return 9.01+tiers([[14,0.8668],[30,1.1268],[60,1.3435],[null,1.6036]], m3*2);
  return 0;
}
function aguaUpdate(){
  const m3=Math.max(1, Math.min(40, Number($("#m3n").value)||1));
  $("#m3").value=m3; $("#m3n").value=m3;
  const c=agua.find(x=>x.slug===$("#city").value)||agua[0];
  $("#agua-out").innerHTML="<b>"+eur(aguaCost(c,m3))+"</b><em>"+c.name+" · "+m3+" m³. "+c.note+"</em>";
}
$("#city").addEventListener("change", aguaUpdate);
$("#m3").addEventListener("input", ()=>{$("#m3n").value=$("#m3").value; aguaUpdate();});
$("#m3n").addEventListener("input", aguaUpdate);
gasUpdate(); aguaUpdate();
"""
    return f'''<div class="app">
<aside class="side"><a class="brand" href="{esc(base)}/">Tarifas</a>
<button class="tab" type="button" data-panel="luz" aria-selected="true">{ICON["luz"]}Luz</button>
<button class="tab" type="button" data-panel="gas" aria-selected="false">{ICON["gas"]}Gas</button>
<button class="tab" type="button" data-panel="agua" aria-selected="false">{ICON["agua"]}Agua</button>
</aside>
<div class="stage">
<section class="panel" id="panel-luz">
<p class="kicker">PVPC · península</p>
<h1>{esc(hour or "Luz")}</h1>
<p class="sub" id="luz-out"><b>{esc(price or "Sin dato")}</b><em>Entre las 6 más baratas. Pulsa otra hora.</em></p>
<div class="seg" role="group" aria-label="Periodo">
<button type="button" data-series="hoy" aria-pressed="true">Hoy</button>
<button type="button" data-series="semana" aria-pressed="false">Media 7 días</button>
</div>
{series}
<p class="fine">Tarifa regulada. No incluye el mercado libre ni Canarias y Baleares. <a href="{esc(base)}/luz-hoy/">Ficha de hoy</a></p>
</section>
<section class="panel" id="panel-gas" hidden>
<p class="kicker">BOE · sin impuestos</p>
<h1>Tu TUR</h1>
<p class="sub">Mueve el consumo anual. Se marca la tarifa regulada que corresponde, no una comercializadora.</p>
<div class="controls">
<label class="field">Consumo anual<input id="kwh" type="range" min="0" max="50000" step="100" value="9000"></label>
<label class="field">kWh al año<input id="kwhn" type="number" min="0" max="300000" step="100" value="9000"></label>
</div>
<div class="result" id="gas-out" aria-live="polite">{gas_seed}</div>
<div class="tariffs">{gas_html}</div>
<p class="fine">Por encima de 300.000 kWh hay otras TUR en la misma resolución. <a href="{esc(base)}/gas-tur1/">Ver TUR.1</a></p>
</section>
<section class="panel" id="panel-agua" hidden>
<p class="kicker">Ordenanza publicada</p>
<h1>Agua</h1>
<p class="sub">Elige ciudad y metros cúbicos. El importe usa solo los precios de esa ordenanza.</p>
<div class="controls">
<label class="field">Ciudad<select id="city">{options}</select></label>
<label class="field">m³ al mes<input id="m3" type="range" min="1" max="40" step="1" value="10"></label>
<label class="field">m³<input id="m3n" type="number" min="1" max="40" step="1" value="10"></label>
</div>
<div class="result" id="agua-out" aria-live="polite">{agua_seed}</div>
<p class="fine">Media España: {esc(media or "sin dato")}. Cada ciudad incluye conceptos distintos. <a href="{esc(base)}/agua-madrid/">Ficha de Madrid</a></p>
</section>
</div></div>
<script type="application/json" id="gas-data">{json.dumps(gas_rows, ensure_ascii=False)}</script>
<script type="application/json" id="agua-data">{json.dumps(cities, ensure_ascii=False)}</script>
<script>{script}</script>'''


def write(rel: str, content: str) -> None:
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build() -> int:
    cfg = json.loads((ROOT / "project.json").read_text("utf-8"))
    items = json.loads((ROOT / "data" / "items.json").read_text("utf-8"))
    errors = validate(items)
    if errors:
        print("\n".join(errors[:20]), file=sys.stderr)
        return 1

    base = cfg["site_url"].rstrip("/")
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    indexable = [it for it in items if len(it["facts"]) >= MIN_FACTS]
    if OUT.exists():
        shutil.rmtree(OUT)

    for it in items:
        updated = it.get("updated", today)
        shown = ordered_facts(it["facts"])
        facts = "".join(
            f'<div class="fact{" lead-fact" if i == 0 and str(k).startswith(("Hora más barata", "Término variable", "Total")) else ""}">'
            f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>"
            for i, (k, v) in enumerate(shown)
        )
        bars = bars_html(it)
        source = (
            f'<p class="src">Fuente: <a href="{esc(it["source"])}" rel="nofollow">documento oficial</a></p>'
            if it.get("source")
            else ""
        )
        crumb = f'<p class="crumb"><a href="{esc(base)}/">{esc(cfg["title"])}</a>'
        if it.get("group"):
            crumb += f' / <span>{esc(it["group"])}</span>'
        crumb += "</p>"
        body = (
            f"{crumb}<h1>{esc(it['title'])}</h1><p class=\"lead\">{esc(it['summary'])}</p>"
            f"<dl class=\"facts\">{facts}</dl>{bars}{source}"
            f"<p class=\"src\">Actualizado: {esc(updated)} · <a href=\"{esc(base)}/api/{esc(it['slug'])}.json\">JSON</a></p>"
        )
        ld = {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": it["title"],
            "description": it["summary"],
            "dateModified": updated,
            "url": f"{base}/{it['slug']}/",
        }
        if it.get("source"):
            ld["isBasedOn"] = it["source"]
        write(f"{it['slug']}/index.html", page(cfg, f"{it['title']} | {cfg['title']}", body, f"/{it['slug']}/", it["summary"], ld, len(it["facts"]) >= MIN_FACTS))
        write(f"api/{it['slug']}.json", json.dumps(it, ensure_ascii=False, indent=1))

    write("index.html", page(cfg, cfg["title"], dashboard(cfg, indexable, base), "/", cfg["description"], shell="app"))

    write("api/items.json", json.dumps(items, ensure_ascii=False, indent=1))
    write("health.json", json.dumps({"ok": True, "items": len(items), "indexable": len(indexable), "updated": now.isoformat()}))
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n")
    urls = [f"{base}/"] + [f"{base}/{it['slug']}/" for it in indexable]
    write(
        "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{esc(u)}</loc><lastmod>{today}</lastmod></url>" for u in urls)
        + "</urlset>",
    )
    llms = [f"# {cfg['title']}", "", f"> {cfg['description']}", "", "## Datos", "",
            f"- [items.json]({base}/api/items.json): todos los elementos, JSON",
            f"- [openapi.json]({base}/openapi.json): especificacion de la API",
            f"- [sitemap.xml]({base}/sitemap.xml)", "", "## Paginas", ""]
    llms += [f"- [{it['title']}]({base}/{it['slug']}/): {it['summary'][:100]}" for it in indexable[:50]]
    write("llms.txt", "\n".join(llms) + "\n")
    ok = {"200": {"description": "OK", "content": {"application/json": {}}}}
    write("openapi.json", json.dumps({
        "openapi": "3.0.3",
        "info": {"title": cfg["title"], "description": cfg["description"], "version": today},
        "servers": [{"url": base}],
        "paths": {
            "/api/items.json": {"get": {"summary": "Todos los elementos", "responses": ok}},
            "/api/{slug}.json": {"get": {"summary": "Un elemento", "parameters": [{"name": "slug", "in": "path", "required": True, "schema": {"type": "string"}}], "responses": ok}},
            "/health.json": {"get": {"summary": "Estado", "responses": ok}},
        },
    }, ensure_ascii=False, indent=1))
    print(f"ok: {len(items)} paginas, {len(indexable)} indexables -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(build())
