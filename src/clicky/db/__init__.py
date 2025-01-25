from pathlib import Path

import clicky
from clicky.config import settings
from clicky.db.session import DBEngine

_SRC_PATH = Path(clicky.__file__).parent.parent

engine = DBEngine.from_dsn(
    dsn=settings.SQLITE_DB_URL,
    alembic_config_path=_SRC_PATH.parent / "alembic.ini",
)
