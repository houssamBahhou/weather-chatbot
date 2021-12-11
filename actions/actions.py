# load some libraries
from typing import Any, Text, Dict, List
from rasa_sdk import Action,FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
from wx import which_city



class Weather(Action):

    def name(self) -> Text:
        return "action_wx"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # get the current slot values from rasa
        city = tracker.get_slot('city')
        which_type = tracker.get_slot('which_type')
        forecast_period = tracker.get_slot('forecast_period')

        # set values for empty slots
        if forecast_period is None:
            forecast_period  = "current"
        if which_type is None:
            which_type = "weather"

        # set the forecast steps for OpenWeather forecast json format 
        drow = 0
        if forecast_period.lower() == "tomorrow":
           drow = 1
        # Default answer if better answer cannot be found
        response="Sorry, got no idea - but I hope it's going to be sunny and warm."


            
        # get the weather information from function defined in wx.py
        open_which_msg = which_city(city,True)
        # set values to current weather variables from open_which_msg json
        temp=round(open_which_msg['current']['temp'])
        pressure=round(open_which_msg['current']['pressure'])
        humidity=round(open_which_msg['current']['humidity'])
        wind=round(open_which_msg['current']['wind_speed'])
        wind_deg=round(open_which_msg['current']['wind_deg'])
        cond=(open_which_msg['current']['weather'][0]["description"])
        uvi=(open_which_msg['current']['uvi'])
            
        # set values to forecasted weather variables from open_which_msg json
        temp_min_predict = round(open_which_msg['daily'][drow]['temp']['min'])
        temp_max_predict = round(open_which_msg['daily'][drow]['temp']['max'])
        pressure_predict = round(open_which_msg['daily'][drow]['pressure'])
        humidity_predict=round(open_which_msg['daily'][drow]['humidity'])
        wind_speed_predict=round(open_which_msg['daily'][drow]['wind_speed'])
        wind_deg_predict=round(open_which_msg['daily'][drow]['wind_deg'])
        cond_predict=(open_which_msg['daily'][drow]['weather'][0]["description"])
        uvi_predict=round(open_which_msg['daily'][drow]['uvi'])

        # set predicted rainfall to 0 if field missing - OpenWeather API seems to not return it at all if 0
        try: 
            rain_predict=round(open_which_msg['daily'][drow]['rain'],1)
        except:
            rain_predict=0

        # answers to queries about current weather    
        if forecast_period.lower() == 'current': 
            # generic query
            if which_type=='weather': 
                response = "The current temperature in {} is {}C. It is {} and the wind speed is {}m/s".format(city, temp, cond, wind)
            # specific information
            if which_type=='wind':
                response = "The current wind speed in {} is {} metres per second from {} degrees. ".format(city, wind, wind_deg)
            if which_type=='temperature':
                response = "The current temperature in {} is {}degrees Celsius. ".format(city,temp)
            if which_type=='pressure':
                response="The current air pressure in {} is {} millibars. ".format(city,pressure)
            if which_type=='humid':
                response="The current humidity in {} is {}%. ".format(city,humidity)
            if which_type=='uvi':
                response="The current UV index in {} is {}. ".format(city,uvi)
            if which_type=='cloud_conditions':
                response="The current conditions in {} is {}.".format(city,cond)

        # answers to forecasts for today and tomorrow   
        if forecast_period.lower() == 'today' or forecast_period.lower() == 'tomorrow':
            # generic forecast
            if which_type=='weather':
                response = "The forecast high for {} {} is {}C. It is expected to be {} and the wind speed is {}m/s".format(city, forecast_period, temp_max_predict, cond_predict, wind_speed_predict)
            # more specific forecasts
            if which_type=='wind':
                response = "The forecasted wind speed for {} {} is {} metres per second from {} degrees. ".format(city, forecast_period, wind_speed_predict, wind_deg_predict)
            if which_type=='temperature':
                response = "The forecasted maximum temperature for {} {} is {}C while the minimum is {}C. ".format(city, forecast_period,temp_max_predict, temp_min_predict)
            if which_type=='pressure':
                response="The forecasted air pressure for {} {} is {} millibars. ".format(city, forecast_period,pressure_predict)
            if which_type=='humid':
                response="The forecasted humidity for {} {} is {}%. ".format(city, forecast_period,humidity_predict)
            if which_type=='uvi':
                response="The forecasted UV index for {} {} is {}. ".format(city, forecast_period,uvi_predict)
            if which_type=='cloud_conditions':
                response="The predicted conditions for {} {} is {} and 24hrs rain fall is expected to be {}mm".format(city, forecast_period,cond_predict, rain_predict)
            


        # send the response back to rasa
        dispatcher.utter_message(response)

#validate the slots "city" and "forecast_period"
ALLOWED_CITIES = ["paris","bordeaux","toulouse"]
ALLOWED_FORECASTS = ["current","tomorrow","today"]

class ValidateWeatherForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_weather_form"

    def validate_city(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `city` value."""

        if slot_value.lower() not in ALLOWED_CITIES:
            dispatcher.utter_message(text=f"Sorry, currently I am limited to information from Paris, Toulouse and Bordeaux only.")
            return {"city": None}
        dispatcher.utter_message(text=f"OK! You want to have the weather in '{slot_value}'.")
        return {"city": slot_value}

    def validate_forecast_period(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `forecast_period` value."""

        if slot_value.lower() not in ALLOWED_FORECASTS:
            dispatcher.utter_message(text=f"I don't recognize that forecast. We provide only {'/'.join(ALLOWED_FORECASTS)}.")
            return {"forecast_period": None}
        dispatcher.utter_message(text=f"OK! You chose the '{slot_value}' forcast.")
        return {"forecast_period": slot_value}