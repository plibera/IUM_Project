from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, time

from transform_input_data import *
import pickle
from tensorflow import keras
import sklearn
import json
import csv
import random


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

def start_experiment():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        global FIRST_MODEL
        global SECOND_MODEL
        global LOG
        global LOG_FILE
        global GROUP_FILE
        FIRST_MODEL = open_model(config["first_model_path"], bool(config["is_first_model_keras"]))
        if config["second_model_path"]:
            SECOND_MODEL = open_model(config["second_model_path"], bool(config["is_second_model_keras"]))
        LOG_FILE = open("logs/" + config["log_base_name"] + "_log.csv", "a", newline="")
        with open("logs/" + config["log_base_name"] + "_group.csv", "a", newline=""):
            pass
        GROUP_FILE = open("logs/" + config["log_base_name"] + "_group.csv", "r+", newline="")
        LOG = csv.writer(LOG_FILE)
        
def get_group_id(client_id):
    global GROUP_FILE
    global SECOND_MODEL
    group_reader = csv.reader(GROUP_FILE)
    GROUP_FILE.seek(0)
    for row in group_reader:
        print(row)
        if(int(row[0]) == client_id):
            return int(row[1])
    if SECOND_MODEL is not None:
        group_id = random.randint(0, 1)
    else:
        group_id = 0
    group_writer = csv.writer(GROUP_FILE)
    group_writer.writerow([client_id, group_id])
    GROUP_FILE.flush()
    return group_id

FIRST_MODEL_PATH = None
SECOND_MODEL_PATH = None
FIRST_MODEL = None
SECOND_MODEL = None
LOG = None
LOG_FILE = None
GROUP_FILE = None
data_transformer = DataTransformer()


@app.on_event("startup")
def startup_event():
    start_experiment()    


@app.post("/predict")
def predict_time(prediction_input: PredictionInput):
    data = prediction_input.dict()

    # choose model based on id
    get_group_id(data["client_id"])

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
    config_data["log_base_name"] = str(datetime.now()).replace(" ", "").replace(".", "").replace(":", "")
    config_data["first_model_path"] = admin_request.first_model_path
    config_data["is_first_model_keras"] = admin_request.is_first_model_keras
    config_data["log_base_name"] += admin_request.first_model_path.replace(".", "")
    
    config_data["second_model_path"] = None
    if admin_request.second_model_path:
        config_data["second_model_path"] = admin_request.second_model_path
        config_data["log_base_name"] += admin_request.second_model_path.replace(".", "")
        config_data["is_second_model_keras"] = 0 # default to no
        if admin_request.is_second_model_keras:
            config_data["is_second_model_keras"] = admin_request.is_second_model_keras

    with open("config.json", "w") as config_file:
        json.dump(config_data, config_file)

    start_experiment()
    
    return "Successfully started new experiment"

