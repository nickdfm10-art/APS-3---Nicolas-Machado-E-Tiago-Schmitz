from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schema.relatorio_schema import (
    CategoriaRelatorioResponse,
    CursoRelatorioResponse,
    OcupacaoEventoResponse,
)
from service import relatorio_service

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


@router.get("/eventos/ocupacao", response_model=list[OcupacaoEventoResponse],
            summary="Relatório de ocupação dos eventos")
def relatorio_ocupacao(db: Session = Depends(get_db)):
    return relatorio_service.ocupacao_eventos(db)


@router.get("/eventos/categorias", response_model=list[CategoriaRelatorioResponse],
            summary="Relatório de eventos por categoria")
def relatorio_categorias(db: Session = Depends(get_db)):
    return relatorio_service.eventos_por_categoria(db)


@router.get("/participantes/cursos", response_model=list[CursoRelatorioResponse],
            summary="Relatório de participação por curso")
def relatorio_cursos(db: Session = Depends(get_db)):
    return relatorio_service.participacao_por_curso(db)
