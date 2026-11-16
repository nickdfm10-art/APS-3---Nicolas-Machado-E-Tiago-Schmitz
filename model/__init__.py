"""Models SQLAlchemy. Importar todos aqui garante o registro dos relacionamentos."""
from model.evento import Evento
from model.participante import Participante
from model.inscricao import Inscricao

__all__ = ["Evento", "Participante", "Inscricao"]
