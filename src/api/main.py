from fastapi import FastAPI
from contextlib import asynccontextmanager
from .endpoints import auth, users, agents, psy
from .db.session import engine
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware

# import warnings
# warnings.filterwarnings("ignore", category=UserWarning, module="multiprocessing.resource_tracker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(
    title="Cancer Knowledge API",
    lifespan=lifespan,
    description="API pour interroger un chatbot spécialisé dans le cancer",
    version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🛡️ En prod, remplace * par http://localhost:8000
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Autorise tous les headers
)

app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(agents.router, prefix="/api", tags=["agents"])
app.include_router(psy.router, prefix="/api", tags=["psychologue"])
# app.include_router(azurehelper.router, prefix="/api/v1", tags=["chatbot"])
