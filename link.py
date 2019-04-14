from flask import Flask, request
from Haze import Haze
import json

app = Flask(__name__)
haze_api = Haze.HazeAPI()

def readJson(jsonpath):
    with open(jsonpath) as json_file:
        return json.load(json_file)

#Insert data path here, please double check this portion
data_dengue_path = "./Dengue/dengue_json_data"
data_cd_path = "./Civil defence shelter locations"

@app.route('/',methods=['GET'])
def verify():
    json_data = {}
    try:
        json_data['data_dengue'] = readJson(data_dengue_path)
        json_data['data_cdshelter'] = readJson(data_cd_path)
        json_data['data_haze'] = haze_api.getHaze()
    except:
        print("JSON file is not found.")
    return str(json_data).replace("'",'"')
