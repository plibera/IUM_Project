import csv
from datetime import datetime
import json
import time
import requests

def main():
    test_data = open("testDataWithLabels.csv", "r", newline="")
    test_data_reader = csv.reader(test_data)
    client_id_counter = 0
    for row in test_data_reader:
        client_id = client_id_counter
        client_id_counter += 1

        city_name = row[0]
        company_id = row[1]
        purchase_weekday = time.strptime(row[2], "%A").tm_wday

        dt = row[3].split('.')[0] # get rid of ms
        purchase_time = str(datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").time())
        
        print(client_id, city_name, company_id, purchase_weekday, purchase_time)

        response = requests.post("http://127.0.0.1:8000/predict", json={
            "client_id": client_id, 
            "city_name": city_name, 
            "company_id": company_id, 
            "purchase_day": purchase_weekday, 
            "purchase_time": purchase_time})
        print(response, response.status_code, response.json())
        


if __name__ == "__main__":
    main()