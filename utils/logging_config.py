import os
import logging
import logging.config
from pathlib import Path

import yaml


def setup_logging() -> None:
    """
    Configura o logging a partir de um YAML.
    Usa LOGGING_CONFIG se setado; caso contrário, logging.yaml na raiz do projeto.
    Faz fallback para basicConfig se o arquivo não existir.
    """
    path_env = os.getenv("LOGGING_CONFIG", "logging.yaml")
    cfg_path = Path(path_env)
    if not cfg_path.is_absolute():
        cfg_path = Path(__file__).resolve().parents[1] / path_env

    if cfg_path.is_file():
        with cfg_path.open("rt", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )