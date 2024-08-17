from datetime import datetime
from pprint import pprint
import requests
import matplotlib.pyplot as plt
from matplotlib.dates import ConciseDateFormatter
import matplotlib.ticker as ticker
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.mpl_util
import numpy as np

latitude, longitude = (42.4395, -76.5022)
days = 4
tempAdjustment = -25  # used to test windchill calc with summertime data...
hours = 24 * days
lastPeriodEligible = False

keyForecastData = [getOneHourForecastData(period) for period in periods[:hours]]

def calculateWindchill(temperature=80, windspeed=0):
    T, V = temperature, windspeed
    windchill = 35.74 + (0.6215*T) - (35.75*(V*0.16)) + (0.4275*(T*(V*0.16)))
    return round(windchill, 1)

def getAllForecastData(latitude, longitude):
  forecastURL = f"https://api.weather.gov/points/{latitude},{longitude}"
  hourlyForecastURL = requests.get(forecastURL).json()["properties"]["forecastHourly"]
  hourlyForecastJSON = requests.get(hourlyForecastURL).json() 
  periods = hourlyForecastJSON["properties"]["periods"]
  return periods

def getOneHourForecastData(oneHourlyForecastDict):
    global lastPeriodEligible
    
    period = oneHourlyForecastDict
    betterTemp = int(period['temperature']) + tempAdjustment
    betterWindSpeed = int(period['windSpeed'].split()[0])
    
    newPeriod = dict()
    newPeriod["startTime"] = datetime.strptime(period['startTime'], '%Y-%m-%dT%H:%M:%S%z')
    newPeriod["temperatureF"] = betterTemp
    newPeriod["windSpeedMPH"] = betterWindSpeed
    newPeriod["windChill"] = calculateWindchill(betterTemp, betterWindSpeed)
    
    newPeriod["consecutive"] = False
    if newPeriod["windChill"] <= 32:
        if lastPeriodEligible:
            newPeriod["consecutive"] = True
        else:
            lastPeriodEligible = True
    else:
        lastPeriodEligible = False
    return newPeriod
  
def getForecastGraph(keyForecastData, days):
  graphData = {item['startTime']:item['windChill'] for item in keyForecastData}
  minTemp = min(graphData.values())
  maxTemp = max(graphData.values())
  dateList = set(item['startTime'].strftime('%Y-%m-%d') for item in keyForecastData)
  
  fig, ax = plt.subplots()
  ax.plot(graphData.keys(), graphData.values(), color='darkgray')
  ax.xaxis.set_major_formatter(ConciseDateFormatter(ax.xaxis.get_major_locator())) 
  ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(8))
  plt.xlabel('Hours')
  plt.ylabel('Fahrenheit')
  plt.xlabel('Hourly Projections')
  plt.title(f'Wind Chill Temperature: {days} day Forecast')
  
  ax.vlines(x=list(dateList)[1:], ymin=minTemp, ymax=maxTemp, colors='lightgray', ls='-')
  
  if minTemp <= 32:
      plt.axhline(y=32, color='red', linestyle='-')
      coldDataPoints = {item['startTime']:item['windChill'] for item in keyForecastData if item['windChill'] <= 32}
      xs, ys = list(coldDataPoints.keys()), list(coldDataPoints.values())
      ax.plot(coldDataPoints.keys(), coldDataPoints.values(), color='cornflowerblue')
      ax.fill_between(xs, ys, 32, color='cornflowerblue', interpolate=True)
    
  # plt.show()
  return anvil.mpl_util.plot_image()

