"""Configuração de logging técnico (arquivo rotativo)."""
import logging
import os
from logging.handlers import RotatingFileHandler

import config

_ROOT_NAME = "equip_control"
_configured = False


def _configure_root() -> None:
    global _configured
    if _configured:
        return
    os.makedirs(config.LOG_DIR, exist_ok=True)

    root = logging.getLogger(_ROOT_NAME)
    root.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler = RotatingFileHandler(
        config.LOG_FILE, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    _configured = True


def get_logger(name: str = _ROOT_NAME) -> logging.Logger:
    """Retorna um logger filho do logger raiz configurado (mesmos handlers)."""
    _configure_root()
    if name == _ROOT_NAME:
        return logging.getLogger(_ROOT_NAME)
    return logging.getLogger(_ROOT_NAME).getChild(name)
