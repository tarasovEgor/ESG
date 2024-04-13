import os
from pathlib import Path
from types import SimpleNamespace

from alembic.config import Config
from configargparse import Namespace

from app.settings import Settings

PROJECT_PATH = Path(__file__).parent.parent.resolve()


def make_alembic_config(cmd_opts: Namespace | SimpleNamespace, base_path: Path = PROJECT_PATH) -> Config:
    database_uri = Settings().database_uri_sync

    path_to_folder = cmd_opts.config
    # Change path to alembic.ini to absolute
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config + "alembic.ini")

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name, cmd_opts=cmd_opts)
    config.attributes["configure_logger"] = False

    # Change path to alembic folder to absolute
    alembic_location = "alembic"  # config.get_main_option("script_location")
    if not os.path.isabs(alembic_location):
        config.set_main_option("script_location", os.path.join(base_path, path_to_folder + alembic_location))
    if cmd_opts.pg_url:
        config.set_main_option("sqlalchemy.url", database_uri)

    return config
