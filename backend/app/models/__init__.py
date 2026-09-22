"""Modelos SQLAlchemy expostos em um único ponto para registro no metadata."""

from app.models.alerta import Alerta
from app.models.audit_log import AuditLog
from app.models.estacao import EstacaoMonitoramento
from app.models.leitura import LeituraNivel, NivelRiscoEnum
from app.models.niveis_risco import NivelRisco
from app.models.ocorrencia import Ocorrencia, StatusOcorrencia
from app.models.refresh_token import RefreshToken
from app.models.usuario import PerfilUsuario, Usuario

__all__ = [
    "Alerta",
    "AuditLog",
    "EstacaoMonitoramento",
    "LeituraNivel",
    "NivelRisco",
    "NivelRiscoEnum",
    "Ocorrencia",
    "PerfilUsuario",
    "RefreshToken",
    "StatusOcorrencia",
    "Usuario",
]
