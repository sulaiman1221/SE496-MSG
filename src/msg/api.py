import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from uuid import UUID


def _configure_msg_logger() -> None:
    logger = logging.getLogger("msg")
    if logger.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("INFO:     %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


_configure_msg_logger()

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI, OpenAI
from supabase import acreate_client

from msg.agents import PlannerAgent, TranslatorAgent, ValidatorAgent, VariantAgent
from msg.config import Settings, get_settings
from msg.domain import Difficulty, Mission, MissionType, Scenario
from msg.orchestrator import Orchestrator
from msg.rag import DoctrineRAG
from msg.storage import Repository, ScenarioFilters, ScenarioSummary

_log = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_WEB_DIST = _PROJECT_ROOT / "web" / "dist"
_RAG_CORPUS = _PROJECT_ROOT / "docs" / "corpus"
_RAG_INDEX = _PROJECT_ROOT / ".cache" / "rag_index.pkl"


def _load_rag(settings: Settings) -> DoctrineRAG | None:
    client = OpenAI(api_key=settings.openai_api_key)
    rag = DoctrineRAG(
        corpus_dir=_RAG_CORPUS, index_path=_RAG_INDEX, client=client
    )
    try:
        rag.load()
        return rag
    except Exception as exc:
        _log.warning(
            "RAG index missing or unreadable; agents will run without doctrine "
            "grounding. Run scripts/build_rag_index.py to enable RAG. (%s)",
            exc,
        )
        return None


def _build_orchestrator(
    settings: Settings,
    openai_client: AsyncOpenAI,
    repository: Repository,
    rag: DoctrineRAG | None,
) -> Orchestrator:
    return Orchestrator(
        planner=PlannerAgent(client=openai_client, settings=settings),
        variant_agent=VariantAgent(client=openai_client, settings=settings, rag=rag),
        translator=TranslatorAgent(client=openai_client, settings=settings),
        validator=ValidatorAgent(client=openai_client, settings=settings, rag=rag),
        repository=repository,
        settings=settings,
        openai_client=openai_client,
    )


@asynccontextmanager
async def _lifespan(app: FastAPI):
    settings = get_settings()
    openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    supabase_client = await acreate_client(
        settings.supabase_url, settings.supabase_service_key
    )
    repository = Repository(client=supabase_client)
    rag = _load_rag(settings)
    app.state.repository = repository
    app.state.orchestrator = _build_orchestrator(
        settings, openai_client, repository, rag
    )
    try:
        yield
    finally:
        await openai_client.close()


def get_orchestrator(request: Request) -> Orchestrator:
    return request.app.state.orchestrator


def get_repository(request: Request) -> Repository:
    return request.app.state.repository


def create_app() -> FastAPI:
    app = FastAPI(title="MSG API", lifespan=_lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/api/scenarios", response_model=Scenario)
    async def create_scenario(
        mission: Mission,
        orch: Orchestrator = Depends(get_orchestrator),
        repo: Repository = Depends(get_repository),
    ) -> Scenario:
        scenario_id = await orch.generate_and_persist(mission)
        scenario = await repo.get_scenario(scenario_id)
        if scenario is None:
            raise HTTPException(
                status_code=500, detail="scenario missing after persist"
            )
        return scenario

    @app.get("/api/scenarios", response_model=list[ScenarioSummary])
    async def list_scenarios(
        mission_type: MissionType | None = None,
        difficulty: Difficulty | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
        repo: Repository = Depends(get_repository),
    ) -> list[ScenarioSummary]:
        filters = ScenarioFilters(
            mission_type=mission_type,
            difficulty=difficulty,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        return await repo.list_scenarios(filters)

    @app.get("/api/scenarios/{scenario_id}", response_model=Scenario)
    async def get_scenario(
        scenario_id: UUID,
        repo: Repository = Depends(get_repository),
    ) -> Scenario:
        scenario = await repo.get_scenario(scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="scenario not found")
        return scenario

    if _WEB_DIST.exists():
        app.mount(
            "/assets",
            StaticFiles(directory=_WEB_DIST / "assets"),
            name="assets",
        )

        index_file = _WEB_DIST / "index.html"

        @app.get("/{full_path:path}", include_in_schema=False)
        async def spa_fallback(full_path: str) -> FileResponse:
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="not found")
            asset = _WEB_DIST / full_path
            if full_path and asset.is_file():
                return FileResponse(asset)
            return FileResponse(index_file)

    return app


app = create_app()
