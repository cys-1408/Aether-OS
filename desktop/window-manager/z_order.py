"""Z-order helpers via sway stacking commands."""
from compositor_adapter import CompositorAdapter


def bring_to_front(wid: int) -> dict:
    return CompositorAdapter().run(f"[con_id={wid}] focus")


def make_floating(wid: int, floating: bool) -> dict:
    return CompositorAdapter().run(f"[con_id={wid}] floating {'enable' if floating else 'disable'}")
