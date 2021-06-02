from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, time
from pydantic.errors import DecimalIsNotFiniteError

from pydantic.types import Json
from transform_input_data import *
import pickle
from tensorflow import keras
import sklearn
import json
import csv


app = FastAPI()

class PredictionInput(BaseModel):
    client_id: int
    city_name: str
    company_id: int
    purchase_day: int
    purchase_time: time


class AdminRequest(BaseModel):
    username: str
    password: str
    first_model_path: str
    is_first_model_keras: int
    second_model_path: Optional[str]
    is_second_model_keras: Optional[int]

def open_model(filename, isKeras):
    if isKeras:
        model = keras.models.load_model(filename, compile=False)
    else:
        model = pickle.load(open(filename, 'rb'))
    return model

FIRST_MODEL_PATH = None
SECOND_MODEL_PATH = None
FIRST_MODEL = None
SECOND_MODEL = None
LOG = None
LOG_FILE = None
data_transformer = DataTransformer()


@app.on_event("startup")
def startup_event():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        global FIRST_MODEL
        global SECOND_MODEL
        global LOG
        global LOG_FILE
        FIRST_MODEL = open_model(config["first_model_path"], bool(config["is_first_model_keras"]))
        SECOND_MODEL = open_model(config["second_model_path"], bool(config["is_second_model_keras"]))
        LOG_FILE = open("logs/" + config["log_base_name"] + "_log.csv", "a", newline="")
        LOG = csv.writer(LOG_FILE)
        


@app.post("/predict")
def predict_time(prediction_input: PredictionInput):
    data = prediction_input.dict()

    # choose model based on id

    # transform data
    transformed_data = data_transformer.transform_input_data(data)
    print(transformed_data)

    # run the prediction
    prediction = np.float64(FIRST_MODEL.predict(transformed_data)[0][0])
    # prediction = np.float64(predict_from_file("base_model.pkl", transformed_data, False)[0][0])
    # prediction = np.float64(predict_from_file("full_model", transformed_data, True)[0][0])
    print(prediction)

    # log everything - to be implemented
    LOG.writerow([datetime.now(), data["client_id"], data["city_name"], data["company_id"], data["purchase_day"], data["purchase_time"], prediction])
    LOG_FILE.flush()
    
    # return result
    return {
        "prediction": prediction
    }
    
@app.post("/admin")
def manage_experiments(admin_request: AdminRequest):
    
    #very simple authentication
    USERNAME = "admin"
    PASSWORD = "admin"

    if(USERNAME != admin_request.username or PASSWORD != admin_request.password):
        return "Username and password do not match"

    config_data = {}
    config_data["first_model_path"] = admin_request.first_model_path
    config_data["is_first_model_keras"] = admin_request.is_first_model_keras
    
    if admin_request.second_model_path:
        config_data["second_model_path"] = admin_request.second_model_path
        config_data["is_second_model_keras"] = 0 # default to no
        if admin_request.is_second_model_keras:
            config_data["is_second_model_keras"] = admin_request.is_second_model_keras

    FIRST_MODEL_PATH = admin_request.first_model_path
    if(admin_request.second_model_path):
        SECOND_MODEL_PATH = admin_request.second_model_path
    else:
        SECOND_MODEL_PATH = ""

