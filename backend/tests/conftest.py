"""Fixtures compartilhadas dos testes."""

import os
from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://agulhas:test@localhost/agulhas_test")
os.environ.setdefault("JWT_SECRET_KEY", "test-key-with-at-least-thirty-two-characters")

from app.api.v1.dependencies import get_db  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.security import (  # noqa: E402
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
)
from app.main import app  # noqa: E402
from app.models.audit_log import AuditLog  # noqa: E402
from app.models.estacao import EstacaoMonitoramento  # noqa: E402
from app.models.leitura import LeituraNivel, NivelRiscoEnum  # noqa: E402
from app.models.niveis_risco import NivelRisco  # noqa: E402
from app.models.ocorrencia import Ocorrencia  # noqa: E402
from app.models.refresh_token import RefreshToken  # noqa: E402
from app.models.usuario import PerfilUsuario, Usuario  # noqa: E402


class MockResult:
    """Simula o resultado de uma execução SQLAlchemy."""

    def __init__(self, items: list[Any]) -> None:
        self._items = items

    def scalar_one_or_none(self) -> Any:
        return self._items[0] if self._items else None

    def scalar_one(self) -> Any:
        if not self._items:
            msg = "Nenhum registro retornado"
            raise RuntimeError(msg)
        return self._items[0]

    def scalars(self) -> "MockResult":
        return self

    def mappings(self) -> "MockResult":
        return self

    def fetchall(self) -> list[Any]:
        return self._items

    def all(self) -> list[Any]:
        return self._items

    def first(self) -> Any:
        return self._items[0] if self._items else None


class InMemoryAsyncSession:
    """Sessão simulada de banco de dados em memória para testes rápidos e isolados."""

    def __init__(
        self,
        users_by_id: dict[UUID, Usuario],
        users_by_email: dict[str, Usuario],
        tokens_by_hash: dict[str, RefreshToken],
        tokens_by_id: dict[UUID, RefreshToken],
        estacoes_by_id: dict[UUID, EstacaoMonitoramento] | None = None,
        niveis_risco_by_estacao_id: dict[UUID, NivelRisco] | None = None,
        niveis_risco_by_id: dict[UUID, NivelRisco] | None = None,
        leituras: list[LeituraNivel] | None = None,
        ocorrencias: list[Ocorrencia] | None = None,
        audit_logs: list[AuditLog] | None = None,
    ) -> None:
        self.users_by_id = users_by_id
        self.users_by_email = users_by_email
        self.tokens_by_hash = tokens_by_hash
        self.tokens_by_id = tokens_by_id
        self.estacoes_by_id = estacoes_by_id if estacoes_by_id is not None else {}
        self.niveis_risco_by_estacao_id = (
            niveis_risco_by_estacao_id if niveis_risco_by_estacao_id is not None else {}
        )
        self.niveis_risco_by_id = niveis_risco_by_id if niveis_risco_by_id is not None else {}
        self.leituras = leituras if leituras is not None else []
        self.ocorrencias = ocorrencias if ocorrencias is not None else []
        self.audit_logs = audit_logs if audit_logs is not None else []

    def add(self, instance: Any) -> None:
        if isinstance(instance, RefreshToken):
            if getattr(instance, "id", None) is None:
                setattr(instance, "id", uuid4())  # noqa: B010
            self.tokens_by_hash[instance.token_hash] = instance
            self.tokens_by_id[instance.id] = instance
        elif isinstance(instance, Usuario):
            if getattr(instance, "id", None) is None:
                setattr(instance, "id", uuid4())  # noqa: B010
            self.users_by_id[instance.id] = instance
            self.users_by_email[instance.email] = instance
        elif isinstance(instance, EstacaoMonitoramento):
            if getattr(instance, "id", None) is None:
                setattr(instance, "id", uuid4())  # noqa: B010
            self.estacoes_by_id[instance.id] = instance
        elif isinstance(instance, NivelRisco):
            if getattr(instance, "id", None) is None:
                setattr(instance, "id", uuid4())  # noqa: B010
            self.niveis_risco_by_id[instance.id] = instance
            self.niveis_risco_by_estacao_id[instance.estacao_id] = instance
        elif isinstance(instance, LeituraNivel):
            if getattr(instance, "id", None) is None:
                setattr(instance, "id", uuid4())  # noqa: B010
            self.leituras.append(instance)
        elif isinstance(instance, Ocorrencia):
            if getattr(instance, "id", None) is None:
                setattr(instance, "id", uuid4())  # noqa: B010
            if getattr(instance, "criado_em", None) is None:
                setattr(instance, "criado_em", datetime.now(UTC))  # noqa: B010
            if getattr(instance, "atualizado_em", None) is None:
                setattr(instance, "atualizado_em", datetime.now(UTC))  # noqa: B010
            if instance.estacao_id in self.estacoes_by_id:
                instance.estacao = self.estacoes_by_id[instance.estacao_id]
            if instance.usuario_id in self.users_by_id:
                instance.usuario = self.users_by_id[instance.usuario_id]
            self.ocorrencias.append(instance)
        elif isinstance(instance, AuditLog):

            if getattr(instance, "id", None) is None:
                setattr(instance, "id", len(self.audit_logs) + 1)  # noqa: B010
            self.audit_logs.append(instance)

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def flush(self) -> None:
        pass

    async def refresh(self, instance: Any) -> None:
        pass

    async def execute(self, statement: Any) -> MockResult:
        params: dict[str, Any]
        if hasattr(statement, "compile"):
            compiled = statement.compile()
            sql = str(compiled)
            params = getattr(compiled, "params", {})
        else:
            sql = str(statement)
            params = {}

        # Consulta em usuarios
        if "FROM usuarios" in sql:
            for k, v in params.items():
                if k.startswith("email_") and isinstance(v, str):
                    user = self.users_by_email.get(v)
                    return MockResult([user] if user else [])
                if k.startswith("id_") and isinstance(v, UUID):
                    user = self.users_by_id.get(v)
                    return MockResult([user] if user else [])
            return MockResult([])

        # Consulta em refresh_tokens
        if "FROM refresh_tokens" in sql:
            token_val = None
            for k, v in params.items():
                if k.startswith("token_hash_") and isinstance(v, str):
                    token_val = self.tokens_by_hash.get(v)
                    break
            if token_val and not token_val.revogado:
                return MockResult([token_val])
            return MockResult([])

        # Atualização em refresh_tokens
        if "UPDATE refresh_tokens" in sql:
            revogado_val = params.get("revogado", True)
            for k, v in params.items():
                if k.startswith("id_") and isinstance(v, UUID):
                    tok = self.tokens_by_id.get(v)
                    if tok:
                        tok.revogado = bool(revogado_val)
                    return MockResult([])
                if k.startswith("token_hash_") and isinstance(v, str):
                    tok = self.tokens_by_hash.get(v)
                    if tok:
                        tok.revogado = bool(revogado_val)
                    return MockResult([])
            return MockResult([])

        # Consulta de status atual das estações (UC01)
        if "SELECT DISTINCT ON" in sql or ("FROM estacoes_monitoramento" in sql and "JOIN" in sql):
            rows: list[dict[str, Any]] = []
            now = datetime.now(UTC)
            for estacao_id, est in self.estacoes_by_id.items():
                if not est.ativa:
                    continue
                nr = self.niveis_risco_by_estacao_id.get(estacao_id)
                leituras_est = [lei for lei in self.leituras if lei.estacao_id == estacao_id]
                leituras_est.sort(key=lambda x: x.data_hora, reverse=True)
                latest = leituras_est[0] if leituras_est else None
                desatualizado = False
                if latest:
                    desatualizado = (now - latest.data_hora) > timedelta(hours=2)

                rows.append(
                    {
                        "estacao_id": str(est.id),
                        "codigo_externo": est.codigo_externo,
                        "nome": est.nome,
                        "rio": est.rio,
                        "nivel_atual_metros": latest.nivel_metros if latest else Decimal("0"),
                        "classificacao_risco": latest.classificacao.value if latest else "NORMAL",
                        "data_hora_leitura": latest.data_hora if latest else now,
                        "cota_atencao": nr.cota_atencao if nr else Decimal("2.00"),
                        "cota_alerta": nr.cota_alerta if nr else Decimal("2.50"),
                        "cota_emergencia": nr.cota_emergencia if nr else Decimal("3.20"),
                        "dados_desatualizados": desatualizado,
                    }
                )
            return MockResult(rows)

        # Consulta com JOIN em estacoes_monitoramento e niveis_risco
        if "FROM estacoes_monitoramento" in sql and "JOIN niveis_risco" in sql:
            result_tuples = []
            for e in self.estacoes_by_id.values():
                if e.ativa:
                    nr = self.niveis_risco_by_estacao_id.get(e.id)
                    result_tuples.append((e, nr))
            return MockResult(result_tuples)

        # Consulta simples em estacoes_monitoramento
        if "FROM estacoes_monitoramento" in sql:
            for v in params.values():
                if isinstance(v, UUID):
                    estacao_encontrada = self.estacoes_by_id.get(v)
                    is_ativa = estacao_encontrada and estacao_encontrada.ativa
                    return MockResult([estacao_encontrada] if is_ativa else [])
            return MockResult([e for e in self.estacoes_by_id.values() if e.ativa])


        # Consulta em niveis_risco
        if "FROM niveis_risco" in sql:
            for v in params.values():
                if isinstance(v, UUID):
                    nr = self.niveis_risco_by_estacao_id.get(v) or self.niveis_risco_by_id.get(v)
                    return MockResult([nr] if nr else [])
            return MockResult(list(self.niveis_risco_by_id.values()))

        # Consulta em leituras_nivel
        if "FROM leituras_nivel" in sql:
            est_id = None
            inicio = None
            for v in params.values():
                if isinstance(v, UUID):
                    est_id = v
                elif isinstance(v, datetime):
                    inicio = v
            matched: list[LeituraNivel] = []
            for item_leitura in self.leituras:
                if est_id and item_leitura.estacao_id != est_id:
                    continue
                if inicio and item_leitura.data_hora < inicio:
                    continue
                matched.append(item_leitura)
            matched.sort(key=lambda x: x.data_hora)
            return MockResult(matched)

        # Inserção em audit_log
        if "INSERT INTO audit_log" in sql:
            log_entry = AuditLog(
                id=len(self.audit_logs) + 1,
                usuario_id=params.get("usuario_id"),
                acao=params.get("acao", ""),
                entidade=params.get("entidade", ""),
                entidade_id=params.get("entidade_id", uuid4()),
                dados_anteriores=params.get("dados_anteriores"),
                dados_novos=params.get("dados_novos"),
                ip_address=params.get("ip_address"),
                request_id=params.get("request_id"),
                criado_em=datetime.now(UTC),
            )
            self.audit_logs.append(log_entry)
            return MockResult([log_entry])

        # Consulta em audit_log
        if "FROM audit_log" in sql:
            if "UPDATE_COTAS" in sql:
                return MockResult([log for log in self.audit_logs if log.acao == "UPDATE_COTAS"])
            if "CREATE_OCORRENCIA" in sql:
                matched_logs = [log for log in self.audit_logs if log.acao == "CREATE_OCORRENCIA"]
                return MockResult(matched_logs)
            return MockResult(list(self.audit_logs))

        # Consulta em ocorrencias
        if "FROM ocorrencias" in sql:
            target_id = None
            target_estacao = None
            for v in params.values():
                if isinstance(v, UUID):
                    if any(o.id == v for o in self.ocorrencias):
                        target_id = v
                    elif any(o.estacao_id == v for o in self.ocorrencias):
                        target_estacao = v
            if target_id:
                matched = [o for o in self.ocorrencias if o.id == target_id]
                return MockResult(matched)
            if target_estacao:
                matched = [o for o in self.ocorrencias if o.estacao_id == target_estacao]
                matched.sort(key=lambda x: x.criado_em, reverse=True)
                return MockResult(matched)
            matched = list(self.ocorrencias)
            matched.sort(key=lambda x: x.criado_em, reverse=True)
            return MockResult(matched)

        return MockResult([])



@pytest.fixture
def mock_db() -> InMemoryAsyncSession:
    """Cria uma sessão em memória isolada para o teste."""
    users_by_id: dict[UUID, Usuario] = {}
    users_by_email: dict[str, Usuario] = {}
    tokens_by_hash: dict[str, RefreshToken] = {}
    tokens_by_id: dict[UUID, RefreshToken] = {}
    return InMemoryAsyncSession(users_by_id, users_by_email, tokens_by_hash, tokens_by_id)


@pytest.fixture(autouse=True)
def override_db(mock_db: InMemoryAsyncSession) -> Iterator[None]:
    """Sobrescreve a dependência get_db com a sessão em memória."""

    async def _get_test_db() -> AsyncIterator[InMemoryAsyncSession]:
        yield mock_db

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def db(mock_db: InMemoryAsyncSession) -> InMemoryAsyncSession:
    """Disponibiliza a sessão simulada de banco de dados para os testes."""
    return mock_db


@pytest.fixture
def usuario_seed(mock_db: InMemoryAsyncSession) -> Usuario:
    """Cria e persiste o usuário administrador padrão para testes."""
    user = Usuario(
        id=uuid4(),
        nome="Administrador Defesa Civil",
        email="admin@defesacivil.resende.rj.gov.br",
        senha_hash=hash_password("Admin@2026"),
        perfil=PerfilUsuario.ADMINISTRADOR,
        ativo=True,
    )
    mock_db.add(user)
    return user


@pytest.fixture
def operador_seed(mock_db: InMemoryAsyncSession) -> Usuario:
    """Cria e persiste um operador da Defesa Civil para testes de RBAC."""
    user = Usuario(
        id=uuid4(),
        nome="Operador Defesa Civil",
        email="operador@defesacivil.resende.rj.gov.br",
        senha_hash=hash_password("Operador@2026"),
        perfil=PerfilUsuario.OPERADOR_DEFESA_CIVIL,
        ativo=True,
    )
    mock_db.add(user)
    return user


@pytest.fixture
def auth_cookies(usuario_seed: Usuario, mock_db: InMemoryAsyncSession) -> dict[str, str]:
    """Emite cookies autenticados válidos para o usuário administrador."""
    access_token = create_access_token(
        data={"sub": str(usuario_seed.id), "role": usuario_seed.perfil.value}
    )
    refresh_token = create_refresh_token()
    token_db = RefreshToken(
        id=uuid4(),
        usuario_id=usuario_seed.id,
        token_hash=hash_refresh_token(refresh_token),
        expira_em=datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        revogado=False,
    )
    mock_db.add(token_db)
    return {"access_token": access_token, "refresh_token": refresh_token}


@pytest.fixture
def operador_cookies(operador_seed: Usuario, mock_db: InMemoryAsyncSession) -> dict[str, str]:
    """Emite cookies autenticados válidos para o operador da Defesa Civil."""
    access_token = create_access_token(
        data={"sub": str(operador_seed.id), "role": operador_seed.perfil.value}
    )
    refresh_token = create_refresh_token()
    token_db = RefreshToken(
        id=uuid4(),
        usuario_id=operador_seed.id,
        token_hash=hash_refresh_token(refresh_token),
        expira_em=datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        revogado=False,
    )
    mock_db.add(token_db)
    return {"access_token": access_token, "refresh_token": refresh_token}


@pytest.fixture
def admin_cookies(auth_cookies: dict[str, str]) -> dict[str, str]:
    """Alias para os cookies do administrador."""
    return auth_cookies


@pytest.fixture
def estacoes_seed(mock_db: InMemoryAsyncSession) -> list[EstacaoMonitoramento]:
    """Cria e persiste uma estação ativa com cotas e leitura inicial."""
    estacao_id = uuid4()
    estacao = EstacaoMonitoramento(
        id=estacao_id,
        codigo_externo="SESMARIA-01",
        nome="Estação Parque Ipiranga",
        rio="Rio Sesmaria",
        latitude=Decimal("-22.468000"),
        longitude=Decimal("-44.456000"),
        ativa=True,
    )
    mock_db.add(estacao)

    niveis_risco = NivelRisco(
        id=uuid4(),
        estacao_id=estacao_id,
        cota_atencao=Decimal("2.00"),
        cota_alerta=Decimal("2.50"),
        cota_emergencia=Decimal("3.20"),
    )
    mock_db.add(niveis_risco)

    leitura = LeituraNivel(
        id=uuid4(),
        estacao_id=estacao_id,
        data_hora=datetime.now(UTC),
        nivel_metros=Decimal("1.85"),
        classificacao=NivelRiscoEnum.NORMAL,
        fonte="SIMULADOR_TELEMETRIA",
    )
    mock_db.add(leitura)

    return [estacao]


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Cria um cliente HTTP isolado para cada teste usando HTTPS."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://test") as test_client:
        yield test_client
