import csv
import json
import numpy as np
import math

def main():

    # get labels
    labels = []
    test_data = open("testDataWithLabels.csv", "r", newline="")
    test_data_reader = csv.reader(test_data)
    for row in test_data_reader:
        labels.append(np.float64(row[4]))
    
    # open log file
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        log_file = open("logs/" + config["log_base_name"] + "_log.csv", "r", newline="")
        log = csv.reader(log_file)

    # init variables
    row_id = 0
    model_0_total_loss = 0
    model_0_count = 0
    model_1_total_loss = 0
    model_1_count = 0

    # go through the log
    for row in log:
        # get data
        model_used = int(row[6])
        prediction = np.float64(row[7])
        label = labels[row_id]
        # update losses
        if model_used == 0:
            model_0_total_loss += (label - prediction) ** 2
            model_0_count += 1
        else:
            model_1_total_loss += (label - prediction) ** 2
            model_1_count += 1
        
        # increment coutner
        row_id += 1

    # print results
    average_model_0_rmse = math.sqrt(model_0_total_loss / model_0_count)
    average_model_1_rmse = math.sqrt(model_1_total_loss / model_1_count)
    print("First  model rmse: " + str(average_model_0_rmse))
    print("Second model rmse: " + str(average_model_1_rmse))
        
if __name__ == "__main__":
    main()