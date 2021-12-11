import requests
import json


use_openweather_API = False


#get the data by setting the api key
def which_city(city, use_API=False):

    if city == "paris":
        lat, lon = 48.8534, 2.3488
    if city == "bordeaux":
        lat, lon = 44.8404, -0.5805
    if city == "toulouse":
        lat, lon = 43.6043, 1.4437
        
    API_key = "921498f497b89988b95bb04c350702b0"
    openweather_url = "http://api.openweathermap.org/data/2.5/onecall?"
    Final_url = openweather_url + "appid=" + API_key + "&lat=" + str(lat) + "&lon=" + str(lon) + "&units=metric" + "&exclude=hourly,minutely,alerts"
    which_data = requests.get(Final_url).json()

    return which_data
