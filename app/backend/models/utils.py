import logging
import re

_logged_bad_values: set[tuple[str, str]] = set()

def _safe_enum(enum_cls, value, default=None):
    if value in (None, '', 'None'):
        return default

    try:
        return enum_cls(int(value))
    except (ValueError, TypeError):
        pass

    try:
        return enum_cls[str(value).strip().upper()]
    except (KeyError, ValueError, AttributeError):
        pass

    key = re.sub(r'[\s\-]+', '_', str(value).upper())
    try:
        return enum_cls[key]
    except (KeyError, ValueError):
        pass

    k = (enum_cls.__name__, str(value))
    if k not in _logged_bad_values:
        logging.warning("Valore %s non valido per %s: imposto %s",
                        value, enum_cls.__name__, default)
        _logged_bad_values.add(k)
    return default 

