from fastapi import FastAPI
from api.data_service import get_mock_data

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Project B API is running"}

@app.get("/mock_data")
def mock_data():
    return get_mock_data()
