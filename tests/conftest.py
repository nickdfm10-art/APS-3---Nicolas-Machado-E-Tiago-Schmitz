"""Configuração dos testes: usa um banco SQLite temporário (nunca o eventos.db real)."""
import os
import tempfile
from pathlib import Path

# IMPORTANTE: definir a URL do banco ANTES de importar a aplicação.
_DIR_TEMP = tempfile.mkdtemp(prefix="aps3_testes_")
ARQUIVO_BANCO = Path(_DIR_TEMP) / "teste.db"
os.environ["EVENTOS_DATABASE_URL"] = f"sqlite:///{ARQUIVO_BANCO}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import model  # noqa: E402,F401
from database import Base, engine  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture(autouse=True)
def banco_limpo():
    """Cada teste começa com as tabelas recém-criadas e vazias."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
