from typing import Union
import math


def fmt_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def fmt_numeric(value: Union[int, float, None]) -> str:
    if value is None:
        return ""
    if isinstance(value, int):
        return f"{value:,}"
    if abs(value) < 0.001 and value != 0:
        return f"{value:.4e}"
    return f"{value:,.4f}"


def fmt_bytes(n: int) -> str:
    if n == 0:
        return "0 B"
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    i = int(math.floor(math.log(n, 1024)))
    p = math.pow(1024, i)
    s = round(n / p, 2)
    return f"{s} {units[i]}"


def fmt_color(value: float) -> str:
    """Standard ydata correlation coloring logic."""
    if value > 0.9:
        return "#d73027"
    if value > 0.7:
        return "#f46d43"
    if value > 0.5:
        return "#fdae61"
    return "#fee08b"
