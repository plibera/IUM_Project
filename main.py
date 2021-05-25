from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class PredictionInput(BaseModel):
    client_id: int
    city_name: str
    company_id: int
    purchase_day: int
    purchase_time: datetime


class AdminRequest(BaseModel):
    username: str
    password: str
    first_model_path: str
    second_model_path: Optional[str]

FIRST_MODEL_PATH = None
SECOND_MODEL_PATH = None


@app.post("/predict")
def predict_time(prediction_input: PredictionInput):
    data = prediction_input.dict()

    # choose model based on id
    data.pop("client_id")

    # transform data - to be implemented

    # run the prediction - this is a stub
    prediction = 44
    probability = 0.75


    # log everything - to be implemented
    
    # return result
    return {
        "prediction": prediction,
        "probability": probability
    }
    
@app.post("/admin")
def manage_experiments(admin_request: AdminRequest):
    
    #very simple authentication
    USERNAME = "admin"
    PASSWORD = "admin"

    if(USERNAME != admin_request.username or PASSWORD != admin_request.password):
        return "Username and password do not match"

    FIRST_MODEL_PATH = admin_request.first_model_path
    if(admin_request.second_model_path):
        SECOND_MODEL_PATH = admin_request.second_model_path
    else:
        SECOND_MODEL_PATH = ""

