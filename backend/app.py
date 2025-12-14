from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .src.sqldb.models import Base
from .src.sqldb.db import engine
from .src.routing import auth
from .src.routing import ai

# kreira tabele ako ne postoje
Base.metadata.create_all(bind=engine)


origins = [
    "http://localhost:8080",  
    "http://127.0.0.1:8080",
    "*"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
