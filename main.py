import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import SQLAlchemyError

from controller import (
    evento_controller,
    inscricao_controller,
    participante_controller,
    relatorio_controller,
)
from database import criar_tabelas
from exceptions import ServiceError

logger = logging.getLogger("eventos")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas no SQLite (se ainda não existirem) ao iniciar a aplicação.
    criar_tabelas()
    yield


app = FastAPI(
    title="API de Eventos Acadêmicos",
    description=(
        "API RESTful para gerenciar eventos, participantes e inscrições, com "
        "persistência em SQLite (SQLAlchemy) e relatórios consolidados."
    ),
    version="3.0.0",
    lifespan=lifespan,
)

app.include_router(evento_controller.router)
app.include_router(participante_controller.router)
app.include_router(inscricao_controller.router)
app.include_router(relatorio_controller.router)


@app.exception_handler(ServiceError)
async def tratar_erro_de_negocio(request: Request, exc: ServiceError):
    """404 / 409 levantados pelos services, no formato {"detail": "..."}."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(SQLAlchemyError)
async def tratar_erro_de_banco(request: Request, exc: SQLAlchemyError):
    """Falhas de persistência: detalhe técnico só no log, mensagem genérica ao cliente."""
    logger.exception("Falha de persistência em %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro ao acessar o banco de dados. Tente novamente mais tarde."},
    )


@app.get("/", include_in_schema=False)
def raiz():
    return RedirectResponse(url="/docs")
