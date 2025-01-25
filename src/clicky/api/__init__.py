from pathlib import Path

import clicky


def get_templates_dir() -> Path:
    return Path(clicky.__file__).parent.parent / "templates"
