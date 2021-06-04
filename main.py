import pickle
from tensorflow import keras
import csv
import random
import sklearn
import json

from globals import *
from transform_input_data import *
from request_objects import *






# helper functions

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
        
        # reset models
        FIRST_MODEL = None
        SECOND_MODEL = None

        # open models
        FIRST_MODEL = open_model(config["first_model_path"], bool(config["is_first_model_keras"]))
        if config["second_model_path"]:
            SECOND_MODEL = open_model(config["second_model_path"], bool(config["is_second_model_keras"]))
        
        # open log and group file
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







# app requests

app = FastAPI()

@app.on_event("startup")
def startup_event():
    start_experiment()    


@app.post("/predict")
def predict_time(prediction_input: PredictionInput):
    data = prediction_input.dict()

    # choose model based on id
    group_id = get_group_id(data["client_id"])

    # transform data
    transformed_data = data_transformer.transform_input_data(data)

    # use defined models
    global FIRST_MODEL
    global SECOND_MODEL

    # run the prediction
    if 0 == group_id:
        prediction = np.float64(FIRST_MODEL.predict(transformed_data)[0][0])
    else:
        prediction = np.float64(SECOND_MODEL.predict(transformed_data)[0][0])

    # log everything
    LOG.writerow([datetime.now(), data["client_id"], data["city_name"], data["company_id"], data["purchase_day"], data["purchase_time"], group_id, prediction])
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
    config_data["is_second_model_keras"] = 0 # default to no
    if admin_request.second_model_path and admin_request.second_model_path != "":
        config_data["second_model_path"] = admin_request.second_model_path
        config_data["log_base_name"] += admin_request.second_model_path.replace(".", "")
        if admin_request.is_second_model_keras:
            config_data["is_second_model_keras"] = admin_request.is_second_model_keras

    with open("config.json", "w") as config_file:
        json.dump(config_data, config_file)

    start_experiment()
    
    return "Successfully started new experiment"

