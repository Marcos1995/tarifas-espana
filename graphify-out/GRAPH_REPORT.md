# Graph Report - tarifas-espana  (2026-10-02)

## Corpus Check
- 18 files · ~10,983 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: .mdc 2, (none) 1)

## Summary
- 96 nodes · 136 edges · 16 communities (14 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f7dd705b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- build.py
- Web design
- Debug
- Contexto del proyecto
- Verify (UI)
- Agent rules
- Build judgments with Laya
- Laya
- Review
- Project
- fetch.py
- gas_items
- main
- luz_items

## God Nodes (most connected - your core abstractions)
1. `luz_items()` - 13 edges
2. `gas_items()` - 10 edges
3. `Web design` - 8 edges
4. `main()` - 7 edges
5. `day_facts()` - 6 edges
6. `Debug` - 6 edges
7. `Contexto del proyecto` - 6 edges
8. `build()` - 5 edges
9. `load()` - 5 edges
10. `fetch_ree()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `today_madrid()` --references--> `date`  [EXTRACTED]
  fetch.py →   _Bridges community 14 → community 13_
- `luz_items()` --references--> `date`  [EXTRACTED]
  fetch.py →   _Bridges community 13 → community 15_
- `gas_items()` --calls--> `cent_to_eur()`  [EXTRACTED]
  fetch.py → fetch.py  _Bridges community 10 → community 13_
- `luz_items()` --calls--> `series()`  [EXTRACTED]
  fetch.py → fetch.py  _Bridges community 10 → community 15_
- `main()` --calls--> `luz_items()`  [EXTRACTED]
  fetch.py → fetch.py  _Bridges community 15 → community 14_

## Import Cycles
- None detected.

## Communities (16 total, 2 thin omitted)

### Community 0 - "build.py"
Cohesion: 0.20
Nodes (13): build(), esc(), page(), Genera el sitio estatico en _site/ desde project.json + data/items.json. Copia…, validate(), write(), datetime, html (+5 more)

### Community 1 - "Web design"
Cohesion: 0.22
Nodes (8): 0. Brief (30 s, don't ask the user), 1. Style = `DESIGN.md`, 2. Tokens (pick, don't invent), 3. Layout recipes, 4. Starter CSS (adapt; delete what you don't use), 5. Build rules, 6. Before HECHO, Web design

### Community 2 - "Debug"
Cohesion: 0.29
Nodes (6): 1. Root cause, 2. Compare, 3. Hypothesis, 4. Fix, Debug, Red flags → back to step 1

### Community 3 - "Contexto del proyecto"
Cohesion: 0.29
Nodes (6): Comandos utiles, Contexto del proyecto, Estado, Notas para el agente, Produccion, Stack

### Community 4 - "Verify (UI)"
Cohesion: 0.40
Nodes (4): 1. Screenshots, 2. Look, 3. Fix and repeat, Verify (UI)

### Community 5 - "Agent rules"
Cohesion: 0.50
Nodes (3): Agent rules, Flujo, Think → Simple → Surgical → Verify (Karpathy)

### Community 6 - "Build judgments with Laya"
Cohesion: 0.50
Nodes (3): Build judgments with Laya, Call, Design

### Community 7 - "Laya"
Cohesion: 0.50
Nodes (3): Laya, Reply (decision-only requests), Steps

### Community 8 - "Review"
Cohesion: 0.50
Nodes (3): Check, Do, Review

### Community 9 - "Project"
Cohesion: 0.50
Nodes (3): Docs, Project, Setup

### Community 10 - "fetch.py"
Cohesion: 0.24
Nodes (10): Decimal, by_day(), cent_to_eur(), dec(), money(), Escribe data/items.json. Es LO UNICO especifico de cada proyecto: reemplaza…, series(), urllib_error (+2 more)

### Community 13 - "gas_items"
Cohesion: 0.39
Nodes (8): date, es_date(), fetch_ree(), gas_items(), get(), next_quarter(), parse_boe(), ree_url()

### Community 14 - "main"
Cohesion: 0.38
Nodes (7): agua_items(), dump(), load(), main(), remember(), today_madrid(), Path

### Community 15 - "luz_items"
Cohesion: 0.53
Nodes (6): day_facts(), fmt_diff(), fmt_kwh(), kwh(), luz_items(), window()

## Knowledge Gaps
- **30 isolated node(s):** `1. Root cause`, `2. Compare`, `3. Hypothesis`, `4. Fix`, `Red flags → back to step 1` (+25 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 47 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `luz_items()` connect `luz_items` to `fetch.py`, `gas_items`, `main`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Why does `load()` connect `main` to `fetch.py`, `gas_items`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **What connects `1. Root cause`, `2. Compare`, `3. Hypothesis` to the rest of the system?**
  _30 weakly-connected nodes found - possible documentation gaps or missing edges._