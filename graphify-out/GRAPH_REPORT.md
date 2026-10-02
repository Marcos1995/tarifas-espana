# Graph Report - tarifas-espana  (2026-10-02)

## Corpus Check
- 19 files · ~11,602 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: .mdc 2, (none) 1)

## Summary
- 102 nodes · 146 edges · 15 communities (12 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1a38c8b3`
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
- DESIGN.md
- gas_items

## God Nodes (most connected - your core abstractions)
1. `luz_items()` - 13 edges
2. `gas_items()` - 10 edges
3. `build()` - 9 edges
4. `Web design` - 8 edges
5. `main()` - 7 edges
6. `day_facts()` - 6 edges
7. `Debug` - 6 edges
8. `Contexto del proyecto` - 6 edges
9. `load()` - 5 edges
10. `fetch_ree()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `fetch_ree()` --references--> `date`  [EXTRACTED]
  fetch.py →   _Bridges community 14 → community 10_

## Import Cycles
- None detected.

## Communities (15 total, 3 thin omitted)

### Community 0 - "build.py"
Cohesion: 0.18
Nodes (17): bars_html(), build(), esc(), euro(), lookup(), ordered_facts(), page(), Genera el sitio estatico en _site/ desde project.json + data/items.json. Copia… (+9 more)

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
Cohesion: 0.19
Nodes (19): Decimal, by_day(), cent_to_eur(), day_facts(), dec(), fetch_ree(), fmt_diff(), fmt_kwh() (+11 more)

### Community 14 - "gas_items"
Cohesion: 0.29
Nodes (12): date, agua_items(), dump(), es_date(), gas_items(), load(), main(), next_quarter() (+4 more)

## Knowledge Gaps
- **31 isolated node(s):** `1. Root cause`, `2. Compare`, `3. Hypothesis`, `4. Fix`, `Red flags → back to step 1` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 49 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `luz_items()` connect `fetch.py` to `gas_items`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Why does `load()` connect `gas_items` to `fetch.py`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **What connects `1. Root cause`, `2. Compare`, `3. Hypothesis` to the rest of the system?**
  _31 weakly-connected nodes found - possible documentation gaps or missing edges._