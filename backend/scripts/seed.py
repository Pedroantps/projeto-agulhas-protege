"""Popula o banco com os dados mínimos do ambiente de desenvolvimento."""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.models.estacao import EstacaoMonitoramento  # noqa: E402
from app.models.usuario import PerfilUsuario, Usuario  # noqa: E402
from app.services.coleta.coletor import executar_coleta, garantir_estacao  # noqa: E402


async def _upsert_usuario(
    db: AsyncSession,
    *,
    nome: str,
    email: str,
    password: str,
    perfil: PerfilUsuario,
) -> Usuario:
    usuario = await db.scalar(select(Usuario).where(Usuario.email == email))
    if usuario is None:
        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=hash_password(password),
            perfil=perfil,
        )
        db.add(usuario)
    else:
        usuario.nome = nome
        usuario.senha_hash = hash_password(password)
        usuario.perfil = perfil
        usuario.ativo = True
    return usuario


async def _desativar_estacoes_legadas(db: AsyncSession) -> None:
    """Desativa estações simuladas de versões antigas (mantém o histórico de ocorrências)."""
    for codigo in ("SESMARIA-01", "ALAMBARI-01"):
        legada = await db.scalar(
            select(EstacaoMonitoramento).where(EstacaoMonitoramento.codigo_externo == codigo)
        )
        if legada is not None:
            legada.ativa = False


async def seed() -> None:
    """Cria usuários de teste e a estação real do CEMADEN, depois executa a primeira coleta."""
    async with AsyncSessionLocal() as db:
        async with db.begin():
            await _upsert_usuario(
                db,
                nome="Administrador de Teste",
                email="testeadmin@teste.com",
                password="Teste@2029",  # noqa: S106 - conta de teste exigida para avaliação
                perfil=PerfilUsuario.ADMINISTRADOR,
            )
            await _upsert_usuario(
                db,
                nome="Operador de Teste",
                email="testecomum@teste.com",
                password="Teste@2029",  # noqa: S106 - conta de teste exigida para avaliação
                perfil=PerfilUsuario.OPERADOR_DEFESA_CIVIL,
            )
            await _desativar_estacoes_legadas(db)
            await garantir_estacao(db)

    print("Usuários e estação do Rio Sesmaria (CEMADEN 330420118H) configurados.")
    if "--sem-coleta" in sys.argv:
        return
    resultado = await executar_coleta()
    print(
        f"Primeira coleta: {resultado.leituras_novas} leituras novas; "
        f"fontes ok: {', '.join(resultado.fontes_ok) or 'nenhuma'}; "
        f"erros: {resultado.erros or 'nenhum'}"
    )


if __name__ == "__main__":
    asyncio.run(seed())
