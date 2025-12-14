from fastapi import FastAPI
from api.data_service import get_data
from machine_learning.random_forrest_practice_iris_flower import cm
from machine_learning.lasso import kfold_indices
from machine_learning.nm_vezba5 import pred

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Project B API is running"}

@app.get("/data")
def mock_data():
    return get_data()
