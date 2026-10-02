<!-- managed-by-telegram-cursor-bot:agent-kit -->
# Contexto del proyecto

## Produccion
- URL: https://github.com/<owner>/<repo>
- Vista: https://<owner>.github.io/<repo>/ (repo público; Chrome)
- Vista local: `index.html`

## Estado
- Portada tipo tablero: hora barata de la luz, TUR según consumo y agua publicada por ciudad. Sin marcas del mercado libre (no hay precios abiertos).
- Una página solo existe si la fuente responde y se puede comprobar. El agua sin lectura de menos de un año no se publica.

## Stack
- Python 3.11, stdlib. `fetch.py` escribe `data/items.json`; `build.py` genera `_site/`.

## Comandos utiles
- Instalar: no hay dependencias
- Test: `python fetch.py && python build.py`
- Dev: abrir `_site/index.html`

## Notas para el agente
- Preferencias / arquitectura
- Cosas que NO tocar
- Lean kit (ver AGENTS.md)
