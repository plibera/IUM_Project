from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import time
from transform_input_data import *
import pickle
from tensorflow import keras
import sklearn


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
    second_model_path: Optional[str]

def predict_from_file(filename, data, isKeras):
    if isKeras:
        model = keras.models.load_model(filename, compile=False)
    else:
        model = pickle.load(open(filename, 'rb'))
    return model.predict(data)

FIRST_MODEL_PATH = None
SECOND_MODEL_PATH = None
data_transformer = DataTransformer()


@app.post("/predict")
def predict_time(prediction_input: PredictionInput):
    data = prediction_input.dict()

    # choose model based on id
    data.pop("client_id")

    # transform data
    transformed_data = data_transformer.transform_input_data(data)
    print(transformed_data)

    # run the prediction
    prediction = np.float64(predict_from_file("base_model.pkl", transformed_data, False)[0][0])
    # prediction = np.float64(predict_from_file("full_model", transformed_data, True)[0][0])
    print(prediction)

    # log everything - to be implemented
    
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

    FIRST_MODEL_PATH = admin_request.first_model_path
    if(admin_request.second_model_path):
        SECOND_MODEL_PATH = admin_request.second_model_path
    else:
        SECOND_MODEL_PATH = ""

