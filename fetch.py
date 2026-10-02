"""Escribe data/items.json. Es LO UNICO especifico de cada proyecto: reemplaza este fichero entero.

Contrato: lista de objetos
  {"slug": "kebab-case", "title": str, "summary": str,
   "facts": [["etiqueta", "valor"], ...],   # >=3 datos propios por pagina o se marca noindex
   "group": str (opcional), "updated": "YYYY-MM-DD" (opcional), "source": url (opcional)}

Reglas: solo fuentes publicas y estables, stdlib (urllib) salvo necesidad real, una peticion
ligera por recurso, sin claves de pago. Si una fuente falla: sys.exit(1) y NO tocar data/.
Historico (tendencias): lee el data/items.json anterior antes de sobrescribirlo.
Escribe con json.dumps(ensure_ascii=False, indent=1).

Luz: API publica de REE (PVPC). Si falta el PVPC de hoy, se aborta sin escribir.
Gas: resolucion del BOE; si no se puede leer, data/manual/gas.json y se omite si verified > 100 dias.
Agua: data/manual/agua.json (ordenanzas ya contrastadas); se omite si verified > 365 dias.
"""
import html
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).parent
DATA = ROOT / "data"
MANUAL = DATA / "manual"
ITEMS_PATH = DATA / "items.json"
HISTORY_PATH = DATA / "history.json"
GAS_PATH = MANUAL / "gas.json"
AGUA_PATH = MANUAL / "agua.json"
BOE_URL = "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20389"
REE = "https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real"
NOTE = (
    "PVPC es la tarifa regulada de la península; no incluye ofertas del mercado libre "
    "ni Canarias/Baleares."
)
MONTHS = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)
UA = {"User-Agent": "tarifas-espana/1.0", "Accept": "application/json,text/html;q=0.9,*/*;q=0.8"}


def today_madrid() -> date:
    try:
        return datetime.now(ZoneInfo("Europe/Madrid")).date()
    except Exception:
        return date.today()


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as res:
        return res.read()


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def load(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def dec(text: str) -> Decimal:
    return Decimal(str(text).replace(".", "").replace(",", "."))


def money(value: Decimal) -> str:
    q = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{q:.2f}".replace(".", ",") + " €"


def kwh(mwh: float) -> float:
    return mwh / 1000.0


def fmt_kwh(eur: float) -> str:
    return f"{eur:.3f}".replace(".", ",") + " €/kWh"


def fmt_diff(eur: float) -> str:
    sign = "+" if eur > 0 else ""
    return sign + f"{eur:.3f}".replace(".", ",") + " €/kWh"


def es_date(d: date) -> str:
    return f"{d.day} de {MONTHS[d.month - 1]} de {d.year}"


def cent_to_eur(cent: str) -> str:
    cent_d = dec(cent)
    places = max(2, -cent_d.as_tuple().exponent + 2)
    eur = (cent_d / Decimal(100)).quantize(Decimal(10) ** -places)
    return f"{eur:.{places}f}".replace(".", ",") + " €/kWh"


def ree_url(start: date, end: date) -> str:
    return (
        f"{REE}?start_date={start.isoformat()}T00:00"
        f"&end_date={end.isoformat()}T23:59&time_trunc=hour"
    )


def series(payload: dict, kind: str) -> list[dict]:
    out = []
    for inc in payload.get("included") or []:
        if inc.get("type") != kind:
            continue
        out.extend(inc.get("attributes", {}).get("values") or [])
    return out


def by_day(values: list[dict]) -> dict[str, list[tuple[str, float]]]:
    days: dict[str, list[tuple[str, float]]] = {}
    for row in values:
        stamp = str(row.get("datetime") or "")
        if len(stamp) < 16 or "value" not in row:
            continue
        days.setdefault(stamp[:10], []).append((stamp[11:16], float(row["value"])))
    for rows in days.values():
        rows.sort(key=lambda item: item[0])
    return days


def fetch_ree(start: date, end: date) -> dict:
    try:
        raw = get(ree_url(start, end))
        payload = json.loads(raw.decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        print(f"REE no responde ({start}..{end}): {exc}", file=sys.stderr)
        sys.exit(1)
    if "included" not in payload:
        print("REE no trae 'included'", file=sys.stderr)
        sys.exit(1)
    return payload


def window(hours: list[tuple[str, float]]) -> str:
    if len(hours) < 3:
        return "sin tres horas seguidas"
    best_i, best_s = 0, None
    for i in range(len(hours) - 2):
        total = hours[i][1] + hours[i + 1][1] + hours[i + 2][1]
        if best_s is None or total < best_s:
            best_s, best_i = total, i
    return f"{hours[best_i][0]}–{hours[best_i + 2][0]}"


def day_facts(hours: list[tuple[str, float]], week_mean_mwh: float, spot: list[float] | None) -> tuple[list, list]:
    prices = [v for _, v in hours]
    mean = sum(prices) / len(prices)
    cheap = min(hours, key=lambda item: (item[1], item[0]))
    dear = max(hours, key=lambda item: (item[1], item[0]))
    ranked = sorted(range(len(hours)), key=lambda i: (hours[i][1], hours[i][0]))
    best = set(ranked[:6])
    facts = [
        ["Precio medio PVPC", fmt_kwh(kwh(mean))],
        ["Hora más barata", f"{cheap[0]} ({fmt_kwh(kwh(cheap[1]))})"],
        ["Hora más cara", f"{dear[0]} ({fmt_kwh(kwh(dear[1]))})"],
        ["Mejores 3 horas seguidas", window(hours)],
        ["Diferencia con la media de 7 días", fmt_diff(kwh(mean - week_mean_mwh))],
    ]
    if spot:
        facts.append(["Precio medio mercado spot", fmt_kwh(kwh(sum(spot) / len(spot)))])
    bars = [
        [label, round(kwh(value), 6), fmt_kwh(kwh(value)), i in best]
        for i, (label, value) in enumerate(hours)
    ]
    return facts, bars


def luz_items(today: date) -> list[dict]:
    payload = fetch_ree(today - timedelta(days=6), today)
    pvpc = by_day(series(payload, "PVPC"))
    spot = by_day(series(payload, "Precio mercado spot"))
    if today.isoformat() not in pvpc or not pvpc[today.isoformat()]:
        print("REE no publica PVPC para hoy", file=sys.stderr)
        sys.exit(1)
    days = sorted(pvpc)
    all_values = [v for day in days for _, v in pvpc[day]]
    week_mean = sum(all_values) / len(all_values)
    daily = []
    for day in days:
        vals = [v for _, v in pvpc[day]]
        daily.append((day, sum(vals) / len(vals)))
    cheap_day = min(daily, key=lambda item: item[1])
    dear_day = max(daily, key=lambda item: item[1])

    profile: dict[str, list[float]] = {}
    for rows in pvpc.values():
        for label, value in rows:
            profile.setdefault(label, []).append(value)
    hours = [(label, sum(vals) / len(vals)) for label, vals in sorted(profile.items())]
    cheap = min(hours, key=lambda item: (item[1], item[0]))
    dear = max(hours, key=lambda item: (item[1], item[0]))
    ranked = sorted(range(len(hours)), key=lambda i: (hours[i][1], hours[i][0]))
    best = set(ranked[:6])
    n_days = len(days)
    week = {
        "slug": "luz-semana",
        "title": "Precio medio de la luz, últimos 7 días (PVPC)",
        "summary": (
            f"Media del PVPC peninsular en los {n_days} días con dato hasta el {es_date(today)}, "
            f"en €/kWh (EUR/MWh de REE partido por 1.000). {NOTE} "
            "Las barras son el perfil horario medio; las 6 horas más baratas van marcadas."
        ),
        "group": "Luz",
        "updated": today.isoformat(),
        "source": ree_url(today - timedelta(days=6), today),
        "facts": [
            ["Precio medio PVPC", fmt_kwh(kwh(week_mean))],
            ["Hora más barata", f"{cheap[0]} ({fmt_kwh(kwh(cheap[1]))})"],
            ["Hora más cara", f"{dear[0]} ({fmt_kwh(kwh(dear[1]))})"],
            ["Mejores 3 horas seguidas", window(hours)],
            ["Día más barato", f"{cheap_day[0]} ({fmt_kwh(kwh(cheap_day[1]))})"],
            ["Día más caro", f"{dear_day[0]} ({fmt_kwh(kwh(dear_day[1]))})"],
        ],
        "bars": [
            [label, round(kwh(value), 6), fmt_kwh(kwh(value)), i in best]
            for i, (label, value) in enumerate(hours)
        ],
    }
    hoy_hours = pvpc[today.isoformat()]
    facts, bars = day_facts(hoy_hours, week_mean, [v for _, v in spot.get(today.isoformat(), [])])
    hoy = {
        "slug": "luz-hoy",
        "title": "Precio de la luz hoy (PVPC)",
        "summary": (
            f"PVPC hora a hora del {es_date(today)} en la península, en €/kWh. {NOTE} "
            "Las 6 horas más baratas van marcadas: ahí se ve cuándo conviene poner la lavadora o cargar el coche."
        ),
        "group": "Luz",
        "updated": today.isoformat(),
        "source": ree_url(today, today),
        "facts": facts,
        "bars": bars,
    }
    items = [hoy, week]
    tomorrow = today + timedelta(days=1)
    try:
        nxt = json.loads(get(ree_url(tomorrow, tomorrow)).decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return items
    nxt_pvpc = by_day(series(nxt, "PVPC")).get(tomorrow.isoformat()) or []
    if len(nxt_pvpc) < 20:
        return items
    nxt_spot = [v for _, v in by_day(series(nxt, "Precio mercado spot")).get(tomorrow.isoformat(), [])]
    t_facts, t_bars = day_facts(nxt_pvpc, week_mean, nxt_spot)
    items.insert(1, {
        "slug": "luz-manana",
        "title": "Precio de la luz mañana (PVPC)",
        "summary": (
            f"PVPC hora a hora del {es_date(tomorrow)}, ya publicado por REE. {NOTE} "
            "Las 6 horas más baratas van marcadas."
        ),
        "group": "Luz",
        "updated": tomorrow.isoformat(),
        "source": ree_url(tomorrow, tomorrow),
        "facts": t_facts,
        "bars": t_bars,
    })
    return items


def next_quarter(effect: date) -> date:
    found = []
    for year in (effect.year, effect.year + 1):
        for month in (1, 4, 7, 10):
            candidate = date(year, month, 1)
            if candidate > effect:
                found.append(candidate)
    return min(found)


def parse_boe(page: str) -> dict | None:
    page = page.replace("\xa0", " ")
    if "TUR.1" not in page:
        return None
    pat = re.compile(
        r"TUR\.([1-4])</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>([\d.,]+)</td>\s*<td[^>]*>([\d.,]+)</td>",
        re.S,
    )
    found = {}
    for num, scope, fixed, variable in pat.findall(page):
        found.setdefault(num, {
            "scope": re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", scope))).strip(),
            "fixed": fixed.strip(),
            "variable_cent": variable.strip(),
        })
    if set(found) != {"1", "2", "3", "4"}:
        return None
    effect = re.search(r"surtirá efectos el\s+(\d{1,2} de [a-záéíóú]+ de \d{4})", page, re.I)
    effect_iso = None
    effect_label = effect.group(1) if effect else ""
    if effect:
        parts = effect.group(1).lower().split(" de ")
        if len(parts) == 3 and parts[1] in MONTHS:
            effect_iso = date(int(parts[2]), MONTHS.index(parts[1]) + 1, int(parts[0])).isoformat()
    return {"effect_label": effect_label, "effect": effect_iso, "tariffs": found}


def gas_items(today: date) -> list[dict]:
    parsed = None
    try:
        parsed = parse_boe(html.unescape(get(BOE_URL).decode("utf-8", errors="replace")))
    except (urllib.error.URLError, TimeoutError, OSError):
        parsed = None
    if parsed:
        record = {
            "source": BOE_URL,
            "verified": today.isoformat(),
            "effect": parsed["effect"],
            "effect_label": parsed["effect_label"],
            "tariffs": parsed["tariffs"],
        }
    else:
        record = load(GAS_PATH, None)
        if not record or "verified" not in record:
            print("BOE de la TUR ilegible y sin data/manual/gas.json", file=sys.stderr)
            return []
        verified = date.fromisoformat(record["verified"])
        if (today - verified).days > 100:
            print("TUR sin lectura fiable y verified > 100 días; se omiten las páginas de gas", file=sys.stderr)
            return []
    effect = date.fromisoformat(record["effect"]) if record.get("effect") else None
    nxt = es_date(next_quarter(effect)) if effect else ""
    items = []
    for num in ("1", "2", "3", "4"):
        row = record["tariffs"][num]
        facts = [
            ["Término fijo", f"{row['fixed']} €/mes"],
            ["Término variable", f"{cent_to_eur(row['variable_cent'])} ({row['variable_cent']} cént/kWh en el BOE)"],
            ["Entrada en vigor", record.get("effect_label") or ""],
            ["Próxima revisión trimestral", nxt],
            ["Consumo de la tarifa", row["scope"]],
            ["Impuestos", "No incluidos (precios sin impuestos del BOE)"],
            ["Verificado", record["verified"]],
        ]
        if not facts[2][1] or not facts[3][1]:
            return []
        items.append({
            "slug": f"gas-tur{num}",
            "title": f"TUR.{num} de gas natural",
            "summary": (
                f"Tarifa de último recurso TUR.{num}, precios sin impuestos de la resolución "
                f"de la Dirección General de Política Energética y Minas. {row['scope']} "
                "No incluye impuestos ni las ofertas del mercado libre."
            ),
            "group": "Gas",
            "updated": record.get("effect") or record["verified"],
            "source": record.get("source") or BOE_URL,
            "verified": record["verified"],
            "facts": facts,
        })
    if parsed:
        dump(GAS_PATH, record)
    return items


def agua_items(today: date) -> list[dict]:
    rows = load(AGUA_PATH, [])
    kept = []
    for item in rows:
        verified = date.fromisoformat(item["verified"])
        if (today - verified).days > 365:
            print(f"se omite {item.get('slug')}: verified {item['verified']} supera un año", file=sys.stderr)
            continue
        kept.append(item)
    return kept


def remember(items: list[dict]) -> dict:
    previous = load(ITEMS_PATH, [])
    history = load(HISTORY_PATH, {})
    if not isinstance(history, dict):
        history = {}
    known = {it.get("slug"): it for it in previous if isinstance(it, dict)}
    for item in items:
        slug = item["slug"]
        fingerprint = "|".join(v for k, v in item["facts"] if k != "Verificado")
        slot = history.setdefault(slug, [])
        if slot and slot[-1].get("value") == fingerprint:
            continue
        if not slot and slug in known:
            old = "|".join(v for k, v in known[slug].get("facts") or [] if k != "Verificado")
            if old and old != fingerprint:
                slot.append({"date": known[slug].get("updated", ""), "value": old})
        if not slot or slot[-1].get("value") != fingerprint:
            slot.append({"date": item.get("updated", ""), "value": fingerprint})
    return history


def main() -> int:
    today = today_madrid()
    # La luz es la fuente automática: si falla, no se toca data/.
    luz = luz_items(today)
    gas = gas_items(today)
    agua = agua_items(today)
    items = luz + gas + agua
    history = remember(items)
    dump(HISTORY_PATH, history)
    dump(ITEMS_PATH, items)
    print(f"ok: {len(items)} items ({sum(1 for it in items if it['group']=='Luz')} luz, "
          f"{sum(1 for it in items if it['group']=='Gas')} gas, "
          f"{sum(1 for it in items if it['group']=='Agua')} agua)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
