"""Public entry points for the Kovalent rewrite.

The top-level package stays lightweight on purpose so pure-domain tests can
import `kovalent.*` without pulling in Pygame.
"""


def run() -> None:
    from .app import run as _run

    _run()


__all__ = ["run"]
