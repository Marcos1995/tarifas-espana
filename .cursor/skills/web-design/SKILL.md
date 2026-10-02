---
name: web-design
description: Any page, landing, dashboard or component (HTML/CSS/JSX), or "diseño", "web bonita", "UI", "landing". Designs and builds modern, minimal, fast, accessible UI directly, in one pass, no external design tool.
---

# Web design

You design and build in one pass: decide the system (tokens), write the page, check it. No external design service: it must take minutes, not a quarter of an hour.

## 0. Brief (30 s, don't ask the user)

Assume and state in one line: purpose, audience, main action (one CTA), tone. Real copy from the project (name, README, PROJECT.md); never lorem ipsum.

## 1. Style = `DESIGN.md`

The repo's `DESIGN.md` is the source of truth. Missing: create it (≤ 25 lines) with: palette (hex, light + dark), fonts, radius, spacing scale, tone, and the user's wishes on top. Existing design (Figma export, tokens, components, framework theme): follow it, don't restyle.

Default direction: **minimal, modern, calm**. Lots of air, one accent, strong type hierarchy, content first, flat surfaces with a 1px hairline instead of heavy shadows, one idea per section.

## 2. Tokens (pick, don't invent)

Neutrals (warm, never pure `#000`/`#fff` text):

| | bg | surface | ink | muted | line |
|---|---|---|---|---|---|
| light | `#FAFAF9` | `#FFFFFF` | `#1C1917` | `#57534E` | `#E7E5E4` |
| dark | `#0C0A09` | `#1C1917` | `#FAFAF9` | `#A8A29E` | `#292524` |

One accent (pick by tone; `on` = text on accent):

| tone | light accent | dark accent | on (light / dark) |
|---|---|---|---|
| tech, trust (default) | `#2457F5` | `#8AAAFF` | `#FFFFFF` / `#0C0A09` |
| nature, finance, health | `#0F7B5F` | `#4FD1A5` | `#FFFFFF` / `#0C0A09` |
| warm, creative, food | `#C2410C` | `#FB923C` | `#FFFFFF` / `#0C0A09` |
| editorial, luxury (mono) | `#1C1917` | `#FAFAF9` | `#FAFAF9` / `#1C1917` |

Rules: accent only on CTA, links, active state, one highlight per view. Status colors (ok/warn/error) only for status, with an icon or text too. No purple/blue gradients, no rainbow, no glassmorphism by default, no emojis as icons (inline SVG, 1.5px stroke, `currentColor`).

Type (no webfont download if you can avoid it; otherwise ≤ 2 families, `font-display: swap`, preload the main one):
- Sans UI/body: `"Inter", system-ui, -apple-system, "Segoe UI", sans-serif`. Character: pair with a display face for headings only when the tone asks for it (e.g. "Fraunces", "Space Grotesk", "DM Serif Display"). Static pages: system stack is faster and fine.
- Fluid scale: `--step-0: clamp(1rem, .96rem + .2vw, 1.125rem)`; h1 `clamp(2.25rem, 1.6rem + 3vw, 4rem)`, `line-height` 1.1, `letter-spacing: -0.02em`; body line-height 1.6; measure `max-width: 65ch`.
- Weights 400/500/600 only.

Space: 4px base → `4 8 12 16 24 32 48 64 96 128`. Section padding `clamp(3rem, 8vw, 8rem)`. Radius one value (`10px`) + pill for chips. Container `min(100% - 2rem, 72rem)`.

## 3. Layout recipes

- **Landing**: header (logo, 3-4 links, CTA) → hero (h1 ≤ 8 words, 1 sentence, 1 primary + 1 ghost CTA, proof/visual) → 3 feature blocks (icon, title, line) → proof (numbers, logos, quote) → pricing or steps (if relevant) → FAQ (`<details>`) → final CTA → footer. Skip any block that has no real content.
- **Dashboard/app**: sidebar (collapses to top bar < 768px) + header + content grid; stat cards (value large, label muted, delta), table with sticky header and row hover, empty/loading/error states always designed.
- **Forms**: label above input, helper text, inline error text (not color only), primary button right/full-width mobile, 44px min touch target.
- **Docs/portfolio/blog**: single column 65ch, sticky minimal nav, strong headings, code blocks with `--surface`.
- Mobile-first: write the 360px layout, then `@media (min-width: 768px)` and `(min-width: 1200px)` additions. Use CSS grid `repeat(auto-fit, minmax(16rem, 1fr))` before media queries.
- Avoid: everything centered, three identical cards with emoji, stock gradient hero, walls of text, carousels, auto-playing media, cookie/modal on load.

## 4. Starter CSS (adapt; delete what you don't use)

```css
:root{
  --bg:#FAFAF9; --surface:#fff; --ink:#1C1917; --muted:#57534E; --line:#E7E5E4;
  --accent:#2457F5; --on:#fff; --radius:10px; --shadow:0 1px 2px rgb(0 0 0/.06),0 8px 24px rgb(0 0 0/.06);
  --font:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;
  color-scheme:light dark;
}
@media (prefers-color-scheme:dark){:root{
  --bg:#0C0A09; --surface:#1C1917; --ink:#FAFAF9; --muted:#A8A29E; --line:#292524;
  --accent:#8AAAFF; --on:#0C0A09; --shadow:none;
}}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;font:400 clamp(1rem,.96rem + .2vw,1.125rem)/1.6 var(--font);color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
img,svg,video{max-width:100%;height:auto;display:block}
h1,h2,h3{line-height:1.15;letter-spacing:-.02em;margin:0 0 .5em;text-wrap:balance}
h1{font-size:clamp(2.25rem,1.6rem + 3vw,4rem)} h2{font-size:clamp(1.75rem,1.4rem + 1.5vw,2.5rem)}
p{margin:0 0 1em;max-width:65ch;text-wrap:pretty} .muted{color:var(--muted)}
a{color:var(--accent);text-underline-offset:.2em}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
.wrap{width:min(100% - 2rem,72rem);margin-inline:auto}
section{padding-block:clamp(3rem,8vw,8rem)}
.grid{display:grid;gap:1.5rem;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:1.5rem}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;min-height:44px;padding:0 1.25rem;border-radius:var(--radius);border:1px solid transparent;font:500 1rem var(--font);text-decoration:none;cursor:pointer;background:var(--accent);color:var(--on);transition:transform .15s,opacity .15s}
.btn:hover{opacity:.9;transform:translateY(-1px)} .btn:active{transform:none}
.btn.ghost{background:transparent;color:var(--ink);border-color:var(--line)}
.btn.ghost:hover{border-color:var(--ink)}
.chip{display:inline-block;padding:.2rem .7rem;border:1px solid var(--line);border-radius:99px;font-size:.875rem;color:var(--muted)}
input,select,textarea{width:100%;min-height:44px;padding:.6rem .8rem;font:inherit;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:var(--radius)}
label{display:block;margin-bottom:.35rem;font-weight:500}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
```

Motion: only `transform`/`opacity`, 150-250 ms, one subtle entrance (fade + 8px rise) at most. Nothing that blocks reading.

## 5. Build rules

- Static (default): one `index.html` + inline or one `styles.css`; no build, no framework, no CDN you can avoid. React repo: Tailwind v4 + shadcn/ui, map the tokens above to the theme, don't hand-write what shadcn has.
- Semantic HTML (`header nav main section footer`, one `h1`, ordered headings, `button` vs `a` correct), `<meta name="viewport">`, `lang`, `<title>`, meta description, `theme-color`, Open Graph tags, inline SVG favicon.
- Efficient: images `width`/`height`, `loading="lazy"` (not the hero), `fetchpriority="high"` on the hero image, AVIF/WebP, SVG for icons; no unused CSS/JS; target < 100 KB without images, no layout shift.
- Dark mode via `prefers-color-scheme` (+ a toggle only if the app needs it). Both themes must look intentional.
- Placeholder visuals: CSS shapes, SVG patterns or a soft tonal block; never broken images or stock URLs.
- Small tweaks (a color, spacing, a button): edit directly, don't redo the system.

## 6. Before HECHO

1. 360 / 768 / 1440 px: no horizontal scroll, no cramped or lost content.
2. WCAG AA: text 4.5:1, large text/UI 3:1 (both themes), visible focus, keyboard reachable, `alt` on images, labels on inputs, touch targets ≥ 44px.
3. `prefers-reduced-motion` respected; no console errors.
4. Look at it with skill `verify` (screenshots mobile + desktop, light + dark) and fix what looks off: weak hierarchy, orphan words, uneven spacing, low contrast, anything generic.
5. Write/update `DESIGN.md` if you chose or changed tokens.
