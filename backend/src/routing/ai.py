from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pathlib import Path
import json

from TotallySpies.backend.src.core.config import get_settings
from TotallySpies.backend.src.graph_processing.graph_builder import build_graph

router = APIRouter()

@router.post("/graph")
async def generate_graph():
    try:
        build_graph()  

        settings = get_settings()
        graph_file = Path(settings.JSON_PATH)
        if not graph_file.is_absolute():
            graph_file = Path.cwd() / graph_file

        with open(graph_file, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

        return JSONResponse(content=graph_data)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )