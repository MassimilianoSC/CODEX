"""
– se lanciato come script, rigenera order_map.json  
– se importato, espone la funzione `ordered` per ordinare i dict
"""
from __future__ import annotations
import json, pathlib, sys
from collections import OrderedDict
import re
from typing import Any

ORDER_FILE = pathlib.Path(__file__).with_name("order_map.json")

# ----------------------------------------------------------------------
# ✨ 1.  FUNZIONE USATA A RUN-TIME  ✨
# ----------------------------------------------------------------------
# carica la mappa (una sola volta)
try:
    _ORDER_MAP: dict[str, list[str]] = json.loads(ORDER_FILE.read_text(encoding="utf-8"))
except FileNotFoundError:
    _ORDER_MAP = {}

def ordered(data: dict, typename: str) -> dict:
    """
    Ritorna un nuovo dict con le chiavi nell’ordine richiesto dallo XSD.
    Se `typename` non è presente in _ORDER_MAP, restituisce il dict invariato.
    Gestisce in modo ricorsivo i sotto-diz. e mantiene eventuali chiavi extra.
    """
    seq = _ORDER_MAP.get(typename)
    if not seq:                       # nessuna regola → niente da fare
        return data

    out: OrderedDict[str, object] = OrderedDict()
    for key in seq:
        if key not in data:
            continue
        val = data[key]
        # prova a riordinare anche i sotto-elementi (solo se dict)
        if isinstance(val, dict):
            # per semplicità assumiamo che il nome del tipo coincida con la chiave
            val = ordered(val, key + "Type")
        elif isinstance(val, list):
            # riordina ogni dict dentro una lista
            val = [ordered(v, key + "Type") if isinstance(v, dict) else v for v in val]
        out[key] = val

    # append eventuali chiavi non previste
    for k, v in data.items():
        if k not in out:
            out[k] = v
    return out
# ----------------------------------------------------------------------
# ✨ 2.  PARTE “CLI”  ✨  (rigenera order_map.json se eseguito come script)
# ----------------------------------------------------------------------
def _dump_order_map():
    """rileggi XSD e rigenera order_map.json (come faceva il vecchio script)"""
    import xmlschema, re
    XSD = pathlib.Path(__file__).parent.parent / "schema" / "schemas" / "PraticaImpiantoCEMRL_v01.10.xsd"
    schema = xmlschema.XMLSchema(XSD)
    new_map: dict[str, list[str]] = {}
    for c in schema.types.values():
        if not c.name or not hasattr(c, "content") or not getattr(c, "content"):
            continue
        seq = [e.name for e in getattr(c.content, "iter_elements", lambda: [])()]
        if seq:
            new_map[c.name] = seq
    ORDER_FILE.write_text(json.dumps(new_map, indent=2, ensure_ascii=False))
    print("✅  order_map.json rigenerato")

if __name__ == "__main__":
    _dump_order_map()



import re
from typing import Any

_SPECIAL_XML_TAGS = {
    "quota_ce": "QuotaCE",
    "quotace": "QuotaCE",
    "alfa_pc": "AlfaPC",
    "alfapc": "AlfaPC",
    "alfa_dtx": "AlfaDTX",
    "alfadtx": "AlfaDTX",
    "fpr": "FPR",
    "ftc": "FTC",
    "num_portanti_attivabili": "NumPortantiAttivabili",
    "potenza_totale_connettore": "PotenzaTotaleConnettore",
    "potenza_irradiata_connettore": "PotenzaIrradiataConnettore",
}

_ACRONYMS = {
    "ce": "CE",
    "pc": "PC",
    "dtx": "DTX",
    "id": "ID",
    "gps": "GPS",
    "rf": "RF",
}

def snake_to_camel(name: str) -> str:
    """Convert a snake_case string to CamelCase handling special acronyms."""
    if name in _SPECIAL_XML_TAGS:
        return _SPECIAL_XML_TAGS[name]
    parts = name.split("_")
    first = parts[0].capitalize()
    rest = "".join(_ACRONYMS.get(p.lower(), p.capitalize()) for p in parts[1:])
    return first + rest


def camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def dict_snake_to_camel(obj: Any) -> Any:
    """Recursively convert dictionary keys from snake_case to CamelCase."""
    if isinstance(obj, dict):
        return {snake_to_camel(k): dict_snake_to_camel(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [dict_snake_to_camel(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(dict_snake_to_camel(v) for v in obj)
    if hasattr(obj, "__dict__"):
        return dict_snake_to_camel(vars(obj))
    return obj
