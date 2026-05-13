"""Fair-use monthly quotas para features con costo variable (ej. AI).

Cada quota se declara en `JB_DRF_BILLING["MONTHLY_QUOTAS"]` con un `limit`
mensual y un `counter` (callable dotted-path) que sabe contar el uso del
user dentro de una ventana `[start, end)`.

La ventana es mes calendario en UTC (resetea día 1, 00:00 UTC).

El uso se expone en `/billing/status.quotas[key]` con shape:
    {used, limit, remaining, reset_at, reached}

Para enforcement server-side usar `enforce_quota(user, key)` que lanza
`QuotaExceeded` si ya se alcanzó el límite. El integrador decide cómo
traducirlo a HTTP (sugerido: 429 con `code='quota_exceeded'`).
"""
from __future__ import annotations

from django.utils import timezone
from django.utils.module_loading import import_string

from jb_drf_billing.conf import get_setting


class QuotaExceeded(Exception):
    """Lanzada por `enforce_quota` cuando el user alcanzó el límite mensual."""

    def __init__(self, key: str, usage: dict):
        self.key = key
        self.usage = usage
        super().__init__(f"Quota '{key}' exceeded: {usage}")


def get_month_window(now=None):
    """Retorna (start, end_exclusive) del mes actual en UTC."""
    now = now or timezone.now()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


def get_quota_config(key: str) -> dict | None:
    cfg = get_setting("MONTHLY_QUOTAS") or {}
    entry = cfg.get(key)
    if not isinstance(entry, dict):
        return None
    return entry


def get_quota_usage(user, key: str) -> dict | None:
    """Retorna usage dict o None si la quota no está configurada."""
    cfg = get_quota_config(key)
    if not cfg:
        return None
    counter_path = cfg.get("counter")
    if not counter_path:
        return None
    try:
        counter = import_string(counter_path)
    except ImportError:
        return None
    start, end = get_month_window()
    try:
        used = int(counter(user=user, start=start, end=end))
    except Exception:
        used = 0
    try:
        limit = int(cfg.get("limit", 0))
    except (TypeError, ValueError):
        limit = 0
    return {
        "used": used,
        "limit": limit,
        "remaining": max(0, limit - used),
        "reset_at": end.isoformat(),
        "reached": limit > 0 and used >= limit,
    }


def get_all_quota_usages(user) -> dict[str, dict]:
    cfg = get_setting("MONTHLY_QUOTAS") or {}
    result: dict[str, dict] = {}
    for key in cfg.keys():
        usage = get_quota_usage(user, key)
        if usage is not None:
            result[key] = usage
    return result


def enforce_quota(user, key: str) -> None:
    """No-op si la quota no está configurada. Lanza `QuotaExceeded` si reached."""
    usage = get_quota_usage(user, key)
    if usage and usage["reached"]:
        raise QuotaExceeded(key, usage)
