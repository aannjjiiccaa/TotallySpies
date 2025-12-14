from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from fastapi import HTTPException
from ..core.config import get_settings
from ..graph_processing.graph_builder import build_graph
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(ROOT_DIR)

from generate_summary import generate_summary
from chatbot import answer

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
    
@router.get("/summary")
def get_system_summary():
    try:
        summary = generate_summary()
        return {"status": "success", "summary": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate system summary: {str(e)}"
        )
    
@router.post("/ask")
async def ask(request: Request):
    try:
        body = await request.json()
        q = body.get("question")

        if not q:
            return {"status": "error", "answer": "", "detail": "Missing 'question' in JSON body"}

        ans = answer(q)
        return {"status": "success", "answer": ans}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))