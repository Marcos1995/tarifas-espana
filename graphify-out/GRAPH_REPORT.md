# Graph Report - tarifas-espana  (2026-10-02)

## Corpus Check
- 14 files · ~4,041 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: .mdc 2, (none) 1)

## Summary
- 66 nodes · 58 edges · 13 communities (10 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

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

## God Nodes (most connected - your core abstractions)
1. `Web design` - 8 edges
2. `Debug` - 6 edges
3. `Contexto del proyecto` - 6 edges
4. `build()` - 5 edges
5. `Verify (UI)` - 4 edges
6. `esc()` - 3 edges
7. `page()` - 3 edges
8. `Build judgments with Laya` - 3 edges
9. `Laya` - 3 edges
10. `Review` - 3 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (13 total, 3 thin omitted)

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

## Knowledge Gaps
- **30 isolated node(s):** `1. Root cause`, `2. Compare`, `3. Hypothesis`, `4. Fix`, `Red flags → back to step 1` (+25 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 51 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `1. Root cause`, `2. Compare`, `3. Hypothesis` to the rest of the system?**
  _30 weakly-connected nodes found - possible documentation gaps or missing edges._