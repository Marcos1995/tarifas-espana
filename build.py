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

CSS = """:root{--bg:#FAFAF9;--surface:#fff;--ink:#1C1917;--muted:#57534E;--line:#E7E5E4;--accent:#2457F5;--on:#fff;--radius:10px;color-scheme:light dark}
@media(prefers-color-scheme:dark){:root{--bg:#0C0A09;--surface:#1C1917;--ink:#FAFAF9;--muted:#A8A29E;--line:#292524;--accent:#8AAAFF;--on:#0C0A09}}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;font:400 clamp(1rem,.96rem + .2vw,1.125rem)/1.6 system-ui,-apple-system,"Segoe UI",Inter,sans-serif;color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-underline-offset:.2em}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
.wrap{width:min(100% - 2rem,64rem);margin-inline:auto}
.top{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:1rem;min-height:56px}
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
.facts{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(13rem,1fr));margin:2rem 0}
.fact{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:1rem 1.25rem}
.fact dt{font-size:.875rem;color:var(--muted);margin-bottom:.25rem}.fact dd{margin:0;font-size:1.25rem;font-weight:600;letter-spacing:-.01em;overflow-wrap:anywhere}
.bars{display:grid;gap:.4rem;margin:2rem 0}.bar{display:grid;grid-template-columns:3.5rem 1fr 6.5rem;align-items:center;gap:.75rem;font-size:.9375rem}
.bar i{display:block;height:.75rem;border-radius:99px;background:var(--line)}.bar.best i{background:var(--accent)}.bar span:last-child{text-align:right;color:var(--muted)}
.links{list-style:none;margin:0;padding:0;display:grid;gap:.5rem;grid-template-columns:repeat(auto-fill,minmax(14rem,1fr))}
.links a{display:block;padding:.6rem .9rem;color:var(--ink);text-decoration:none;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);transition:border-color .15s,transform .15s}
.links a:hover{border-color:var(--accent);transform:translateY(-1px)}
.src,footer{color:var(--muted);font-size:.9375rem}
footer{border-top:1px solid var(--line);padding-block:2rem}footer a{color:var(--muted)}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}"""


def esc(value) -> str:
    return html.escape(str(value), quote=True)


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
    icon = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='12' fill='%232457F5'/%3E%3C/svg%3E"
    return (
        f'<!doctype html><html lang="{esc(cfg.get("lang", "es"))}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>'
        f'<meta name="description" content="{esc(desc[:160])}"><link rel="canonical" href="{esc(base + path)}">'
        f'<meta name="theme-color" content="#FAFAF9"><link rel="icon" href="{icon}">'
        f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc[:160])}">'
        f'{robots}<style>{CSS}{tone}</style>{ld_tag}{cfg.get("head_html", "")}{analytics}</head><body>'
        f'<header class="top"><div class="wrap"><a class="brand" href="{esc(base)}/">{esc(cfg["title"])}</a>'
        f'<nav aria-label="Datos"><a href="{esc(base)}/api/items.json">JSON</a><a href="{esc(base)}/openapi.json">API</a></nav></div></header>'
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
        facts = "".join(f"<div class=\"fact\"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in it["facts"])
        top = max((b[1] for b in it.get("bars") or []), default=0) or 1
        bars = "".join(
            f'<div class="bar{" best" if len(b) > 3 and b[3] else ""}"><span>{esc(b[0])}</span>'
            f'<i aria-hidden="true" style="width:{max(2, round(b[1] / top * 100))}%"></i><span>{esc(b[2])}</span></div>'
            for b in it.get("bars") or []
        )
        bars = f'<div class="bars">{bars}</div>' if bars else ""
        source = (
            f'<p class="src">Fuente: <a href="{esc(it["source"])}" rel="nofollow">{esc(it["source"])}</a></p>'
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

    groups: dict[str, list] = {}
    for it in indexable:
        groups.setdefault(it.get("group", "Todos"), []).append(it)
    listing = "".join(
        f"<section><h2>{esc(g)}</h2><ul class=\"links\">"
        + "".join(f'<li><a href="{esc(base)}/{esc(i["slug"])}/">{esc(i["title"])}</a></li>' for i in its)
        + "</ul></section>"
        for g, its in sorted(groups.items())
    )
    search = (
        '<input class="search" id="q" type="search" aria-label="Filtrar" placeholder="Filtrar..." oninput="'
        "const v=this.value.toLowerCase();for(const l of document.querySelectorAll('.links li'))"
        "l.hidden=!l.textContent.toLowerCase().includes(v);"
        "for(const s of document.querySelectorAll('main section'))s.hidden=!s.querySelector('li:not([hidden])')\">"
    )
    meta = f'<div class="meta"><span class="chip">{len(indexable)} páginas</span><span class="chip">Actualizado {today}</span></div>'
    index_body = f"<h1>{esc(cfg['title'])}</h1><p class=\"lead\">{esc(cfg['description'])}</p>{search}{meta}{listing}"
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
