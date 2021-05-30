import csv
import numpy as np

class DataTransformer:
    
    def __init__(self) -> None:
        self.city_names_database, self.city_coords_database = get_city_coords_database()

    def transform_input_data(self, data):
        
        # city coords
        city_coords_normalized = self.city_coords_database[self.city_names_database.index(data["city_name"])]
        
        # company
        company_one_hot = np.zeros(3)
        companies = [360, 516, 620]
        company_one_hot[companies.index(data["company_id"])] = 1

        # purchase day
        purchase_day_one_hot = np.zeros(7)
        purchase_day_one_hot[data["purchase_day"]] = 1
        
        # purchase time
        time = data["purchase_time"]
        time_normalized = (time.second + 60 * (time.minute + 60 * time.hour)) / (60 * 60 * 24)
        time_normalized = np.array([time_normalized])

        transformed_data = np.array([])
        transformed_data = np.concatenate((transformed_data, city_coords_normalized))
        transformed_data = np.concatenate((transformed_data, company_one_hot))
        transformed_data = np.concatenate((transformed_data, purchase_day_one_hot))
        transformed_data = np.concatenate((transformed_data, time_normalized))
        
        return transformed_data


def get_city_coords_database():
    # Convert cities to coordinates, and then normalize the coordinates based on min and max values for Poland

    # Read cities coordinates from csv file
    # Strip cities names of whitespaces and convert coordinates to floats [degrees] by dividing minutes by 60
    # City data contains few cities outside Poland, so we skip them using the following bounds
    minEastCoord = 14.11
    maxEastCoord = 24.15
    minNorthCoord = 49
    maxNorthCoord = 54.84
    citiesPath = 'cities.csv'

    cityDatabaseNames = []
    cityDatabaseCoords = []
    with open(citiesPath, newline='', encoding='utf8') as csvfile:
        citiesReader = csv.reader(csvfile)
        for row in citiesReader:
            coordRow = []
            for cell in row:
                cell = cell.strip()
                if len(cell) > 1:
                    if cell[-1] == 'E' or cell[-1] == 'N':
                        numericCoord = float(cell[0:2]) + float(cell[3:5])/60
                        coordRow.append(numericCoord)
                    else:
                        cityDatabaseNames.append(cell)
            if coordRow[0] >= minEastCoord and \
            coordRow[0] <= maxEastCoord and \
            coordRow[1] >= minNorthCoord and \
            coordRow[1] <= maxNorthCoord:
                cityDatabaseCoords.append(coordRow)
            else:
                del cityDatabaseNames[-1]
                
            
    #Convert to numpy
    citiesCoordinatesDataArray = np.array(cityDatabaseCoords)

    citiesCoordinatesDataArray[:, 0] = (citiesCoordinatesDataArray[:, 0]-minEastCoord)/(maxEastCoord-minEastCoord)
    citiesCoordinatesDataArray[:, 1] = (citiesCoordinatesDataArray[:, 1]-minNorthCoord)/(maxNorthCoord-minNorthCoord)

    return cityDatabaseNames, citiesCoordinatesDataArray