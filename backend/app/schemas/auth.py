"""Schemas de entrada e saída para autenticação."""

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class LoginRequest(BaseModel):
    """Payload de entrada para autenticação de operador."""

    model_config = ConfigDict(strict=True)

    email: EmailStr
    senha: str

    @field_validator("senha")
    @classmethod
    def senha_nao_vazia(cls, v: str) -> str:
        """Valida que a senha possui comprimento mínimo de 6 caracteres."""
        if not v or len(v) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres.")
        return v


class LoginResponse(BaseModel):
    """Payload de resposta após login bem-sucedido."""

    model_config = ConfigDict(strict=True)

    nome: str
    perfil: str  # "ADMINISTRADOR" | "OPERADOR_DEFESA_CIVIL"
    mensagem: str = "Login realizado com sucesso."


class UsuarioAtualResponse(BaseModel):
    """Identidade do usuário autenticado (restaura a sessão após recarregar a página)."""

    model_config = ConfigDict(strict=True)

    nome: str
    perfil: str
