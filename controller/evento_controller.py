from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schema.erro_schema import ErroResponse
from schema.evento_schema import EventoCreate, EventoResponse, EventoUpdate
from service import evento_service

router = APIRouter(prefix="/eventos", tags=["Eventos"])

NAO_ENCONTRADO = {404: {"model": ErroResponse, "description": "Evento não encontrado."}}


@router.post("", response_model=EventoResponse, status_code=status.HTTP_201_CREATED,
             summary="Cadastrar evento")
def cadastrar_evento(dados: EventoCreate, db: Session = Depends(get_db)):
    return evento_service.criar(db, dados)


@router.get("", response_model=list[EventoResponse], summary="Listar eventos")
def listar_eventos(db: Session = Depends(get_db)):
    return evento_service.listar(db)


@router.get("/{evento_id}", response_model=EventoResponse, responses=NAO_ENCONTRADO,
            summary="Consultar evento")
def consultar_evento(evento_id: int, db: Session = Depends(get_db)):
    return evento_service.obter_ou_404(db, evento_id)


@router.put("/{evento_id}",
            response_model=EventoResponse,
            responses={**NAO_ENCONTRADO,
                       409: {"model": ErroResponse,
                             "description": "Capacidade menor que o número de inscritos."}},
            summary="Atualizar evento")
def atualizar_evento(evento_id: int, dados: EventoUpdate, db: Session = Depends(get_db)):
    return evento_service.atualizar(db, evento_id, dados)


@router.delete("/{evento_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               responses={**NAO_ENCONTRADO,
                          409: {"model": ErroResponse,
                                "description": "Evento possui inscrições."}},
               summary="Excluir evento")
def excluir_evento(evento_id: int, db: Session = Depends(get_db)):
    evento_service.excluir(db, evento_id)
