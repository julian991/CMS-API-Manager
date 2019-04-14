from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as ureq
import pprint
import googlemaps
import json
import pyrebase
from datetime import datetime

class Dengue():
    def __init__(self):
        config = {
          "apiKey": "",
          "authDomain": "",
          "databaseURL": "https://data-storage-1205f.firebaseio.com/",
          "storageBucket": ""
        }
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

        data = self.db.child("Dengue_Data").get()
        self.j_data = dict(data.val())
        # pprint.pprint(self.j_data)

    @staticmethod
    def get_alphabets(s):
        special = ['(','/']
        for i in range(len(s)):
            if s[i] in special:
                i-=1
                return s[:i+1]



    def convert_to_json(self,li,date):
        api_key = 'AIzaSyCMwtsOxNlEec_9SI_FgkpSlpWwMtZUOKA'
        gm = googlemaps.Client(key = api_key)
        cluster_data = {"clusters":[]}
        cluster_data["updated_time"] = date

        for item in li:

            cluster = {}
            cluster["name"] = item[0][0]
            cluster["intensity"] = item[0][1]
            cluster["locations"] = []
            for address in item[1]:
                addr = {}
                addr["name"] = address[0]
                addr["coordinates"] = gm.geocode(address[0]+", Singapore")[0]["geometry"]["location"]
                addr["no_of_reports"] = address[1]

                cluster["locations"].append(addr)
            cluster_data["clusters"].append(cluster)

        return cluster_data

    @staticmethod
    def get_case(area_case):
        return area_case[1]

    def get_polygon_data(self):
        return {"data_dengue":self.j_data['polygon_data']}

    def write_json_file(self):

        my_url = 'https://www.nea.gov.sg/dengue-zika/dengue/dengue-clusters'
        uclient = ureq(my_url)
        page_html = uclient.read()
        uclient.close()

        page_soup = soup(page_html,"html.parser")
        table = page_soup.findAll("table",{"class":"table surveillance-table two-row-head"})[0]

        rows = table.findAll("tr")
        rows = rows[2:]

        parsed_row_data = []
        row_data=[]
        for i in range(len(rows)):


            if len(rows[i]['class'])!=0 and rows[i]['class'][0]=="hashlink":

                parsed_row_data.append(row_data)

                title = self.get_alphabets(rows[i]['id'])
                row_data = [[title],[[rows[i+1].findAll("td",{"style":"text-align:center"})[3].text,int(rows[i+1].findAll("td",{"style":"text-align:center"})[0].text)]]]

                colour = i+1

            elif i == colour:
                c= rows[i].findAll("td")[1].div['class'][0]
                row_data[0].append(c)

            else :
                row_data[1].append([rows[i].findAll("td",{"style":"text-align:center"})[0].text,int(rows[i].findAll("td",{"style":"text-align:center"})[1].text)])

                skip = 0

        self.date = page_soup.findAll("div",{"id":"mainContent_mainContent_TFA5CC790007_Col00"})[0].p.text.strip()

        self.parsed_row_data = parsed_row_data[1:]

        self.j_data = self.convert_to_json(self.parsed_row_data,self.date)

        now = datetime.now()
        h,m,s = str(now.hour),str(now.minute),str(now.second)
        self.j_data['time'] = ((h,m,s))



        clusters = self.j_data['clusters']
        polygons = []
        self.total_cases = 0
        self.area_cases = []
        for cluster in clusters:
            points = cluster['locations']
            points_data = []
            self.case = 0

            for point in points:
                points_data.append(point['coordinates'])
                self.total_cases+=point['no_of_reports']
                self.case+=point['no_of_reports']
            # print(cluster)
            try:
                area_case = [cluster['name'],self.case]
            except:
                area_case = [cluster['locations'][0]['name'],self.case]
            if area_case[0]==None:
                print(cluster)
            self.area_cases.append(area_case)
            polygons.append(points_data)

        self.area_cases.sort(key=self.get_case, reverse = True)
        self.j_data['polygon_data'] = polygons
        self.j_data['top5_data'] = self.area_cases[:5]
        self.j_data['total_cases'] = self.total_cases
        # print(self.area_cases[:5])

        self.db.child("Dengue_Data").update(self.j_data)

        #Json file in server
        title = "dengue_json_data"
        try:
            with open(title, 'w') as json_file:
                json.dump(self.j_data, json_file)
            return 'Json file saved successfully'
        except:
            return 'Json file not saved, an error has occurred'

if __name__=='__main__':
    dengue_api = Dengue()
    # pprint.pprint(dengue_api.j_data)
    dengue_api.write_json_file()
    print('Done!')
