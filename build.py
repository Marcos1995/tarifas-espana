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


def page(cfg: dict, title: str, body: str, path: str, desc: str, ld: dict | None = None, index: bool = True) -> str:
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
    return (
        f'<!doctype html><html lang="{esc(cfg.get("lang", "es"))}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>'
        f'<meta name="description" content="{esc(desc[:160])}"><link rel="canonical" href="{esc(base + path)}">'
        f'<meta name="theme-color" content="#FAFAF9"><link rel="icon" href="{icon}">'
        f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc[:160])}">'
        f'{robots}<style>{CSS}{tone}</style>{ld_tag}{cfg.get("head_html", "")}{analytics}</head><body>'
        f'<header class="top"><div class="wrap"><a class="brand" href="{esc(base)}/">Tarifas</a>'
        f'<nav aria-label="Secciones"><a href="{esc(base)}/#luz">Luz</a><a href="{esc(base)}/#gas">Gas</a><a href="{esc(base)}/#agua">Agua</a></nav></div></header>'
        f'<main class="wrap">{body}</main>'
        f'<footer><div class="wrap">{esc(cfg["title"])} · datos abiertos · <a href="{esc(base)}/api/items.json">JSON</a> · '
        f'<a href="{esc(base)}/openapi.json">OpenAPI</a> · <a href="{esc(base)}/llms.txt">llms.txt</a></div></footer></body></html>'
    )


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

    by_slug = {it["slug"]: it for it in indexable}
    luz = by_slug.get("luz-hoy")
    cheap = lookup(luz, "Hora más barata")
    hour = cheap.split(" ", 1)[0] if cheap else ""
    cheap_price = re.search(r"\(([^)]+)\)", cheap)
    hero = f"Más barata a las {hour}" if hour else cfg["title"]
    lead = (
        f"{esc(cheap_price.group(1) if cheap_price else lookup(luz, 'Precio medio'))} en la tarifa regulada PVPC de la península. "
        "Las horas en verde son las seis más baratas: ahí conviene la lavadora o el coche. "
        "No hay listado abierto de comercializadoras del mercado libre, así que no se nombra una marca ganadora."
    )
    kpis = ""
    if luz:
        kpis = '<div class="kpis">' + "".join(
            f"<div class=\"kpi\"><span>{esc(label)}</span><strong>{esc(lookup(luz, label).split(' (')[0])}</strong></div>"
            for label in ("Precio medio PVPC", "Hora más cara", "Diferencia con la media de 7 días", "Precio medio mercado spot")
            if lookup(luz, label)
        ) + "</div>"
    luz_block = (
        f'<section class="block" id="luz"><h2>Luz hoy</h2>'
        f"{kpis}{bars_html(luz) if luz else ''}"
        f'<p class="note"><a href="{esc(base)}/luz-hoy/">Detalle de hoy</a>'
        + (f' · <a href="{esc(base)}/luz-semana/">Media de 7 días</a>' if "luz-semana" in by_slug else "")
        + "</p></section>"
    )
    gas_cards = []
    for it in sorted((it for it in indexable if it.get("group") == "Gas"), key=lambda it: it["slug"]):
        variable = lookup(it, "Término variable").split(" (")[0]
        gas_cards.append(
            f'<a class="pick" data-find href="{esc(base)}/{esc(it["slug"])}/">'
            f'<span>{esc(it["title"])}</span><b>{esc(variable)}</b>'
            f'<small>{esc(lookup(it, "Término fijo"))} · {esc(lookup(it, "Consumo de la tarifa"))}</small></a>'
        )
    gas_block = (
        '<section class="block" id="gas"><h2>Gas regulado</h2>'
        '<p class="note">La TUR no se elige: depende de los kWh que consumes al año. Precios sin impuestos del BOE.</p>'
        f'<div class="picks">{"".join(gas_cards)}</div></section>'
        if gas_cards else ""
    )
    cities = []
    for it in indexable:
        if it.get("group") != "Agua" or it["slug"] == "agua-media-espana":
            continue
        total = lookup(it, "Total")
        amount = euro(total)
        if amount is None:
            continue
        scope = total.split("(", 1)[1].rstrip(")") if "(" in total else lookup(it, "Cuota fija")
        name = it["title"].replace("Tarifa del agua en ", "")
        cities.append((amount, name, total.split(" (", 1)[0], scope, it["slug"]))
    cities.sort()
    lowest = cities[0][0] if cities else None
    water_cards = "".join(
        f'<a class="pick{" best" if amount == lowest else ""}" data-find href="{esc(base)}/{esc(slug)}/">'
        f'<span>{esc(name)}</span><b>{esc(figure)}</b>'
        f'<small>{"Cifra más baja de la lista. " if amount == lowest else ""}{esc(scope)}</small></a>'
        for amount, name, figure, scope, slug in cities
    )
    media = by_slug.get("agua-media-espana")
    media_line = (
        f'<p class="note">Media nacional DAQUAS: {esc(lookup(media, "Precio medio doméstico"))} '
        f'(dato {esc(lookup(media, "Año"))}). <a href="{esc(base)}/agua-media-espana/">Ver el estudio</a></p>'
        if media else ""
    )
    agua_block = (
        '<section class="block" id="agua"><h2>Agua por ciudad</h2>'
        '<p class="note">Cifra de referencia de cada ordenanza para unos 10 m³. No son facturas iguales: cambian el periodo, el IVA y si incluyen saneamiento. No es un ranking de empresas.</p>'
        f'{media_line}<div class="picks">{water_cards}</div></section>'
        if water_cards else ""
    )
    search = (
        '<input class="search" id="q" type="search" aria-label="Buscar ciudad o tarifa" placeholder="Buscar ciudad o tarifa" oninput="'
        "const v=this.value.toLowerCase();"
        "for(const c of document.querySelectorAll('[data-find]'))c.hidden=!c.textContent.toLowerCase().includes(v);"
        "for(const s of document.querySelectorAll('section.block')){const p=[...s.querySelectorAll('[data-find]')];if(p.length)s.hidden=!p.some(c=>!c.hidden)}\">"
    )
    index_body = (
        f"<p class=\"kicker\">Península · datos oficiales</p><h1>{esc(hero)}</h1>"
        f"<p class=\"lead\">{lead}</p>{search}{luz_block}{gas_block}{agua_block}"
    )
    write("index.html", page(cfg, cfg["title"], index_body, "/", cfg["description"]))

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
