from datetime import date, datetime, timedelta
import json
import requests
from time import sleep
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


@anvil.server.callable
def getRawForecastData(latitude, longitude):
  forecastURL = f'https://api.weather.gov/points/{latitude},{longitude}'
  result = requests.get(forecastURL).json()
  hourlyForecastURL = result.get('properties', {}).get('forecastHourly')
  if hourlyForecastURL:
    ForecastJSON = requests.get(hourlyForecastURL).json()
    return ForecastJSON
  else:
    return None


@anvil.server.background_task
@anvil.server.callable
def updateDailyForecasts():
  thisDate = date.today()
  
  # create empty records for day's forecasts
  locations = app_tables.locations.search()
  for location in locations:
    app_tables.daily_forecasts.add_row(DateOfForecast=thisDate, locality=location)
  
  # iterate through empty records up to 5x
  for counter in range(5):
    # with longer pauses between each try
    emptyForecasts = app_tables.daily_forecasts.search(
      DateOfForecast=thisDate, RawData=None
    )
    emptyForecastCount = len(emptyForecasts)
    if emptyForecastCount == 0:
      break
    sleep(5 * counter)
    print(f'Counter: {counter}   Empty forecasts: {emptyForecastCount}')
    for each in emptyForecasts:
      result = getRawForecastData(
        each['locality']['Latitude'], each['locality']['Longitude']
      )
      if not result:
        continue
      periods = result.get('properties', {}).get('periods')
      if periods:
        DataRequestDatetime = datetime.strptime(
          result['properties']['generatedAt'], '%Y-%m-%dT%H:%M:%S%z'
        ) + timedelta(hours=-4)
        NOAAupdateDatetime = datetime.strptime(
          result['properties']['updateTime'], '%Y-%m-%dT%H:%M:%S%z'
        ) + timedelta(hours=-4)
        # update fields in 'daily_forecasts' table
        each.update(
          DataRequested=DataRequestDatetime,
          NOAAupdate=NOAAupdateDatetime,
          RawData=result,
        )
        # update equivalent fields in linked 'locations' table
        each['locality']['DataRequested'] = DataRequestDatetime
        each['locality']['NOAAupdate'] = NOAAupdateDatetime
        each['locality']['RawData'] = result

def calculateWindchill(temperature=80, windspeed=0):
    T, V = temperature, windspeed
    windchill = 35.74 + (0.6215*T) - (35.75*(V*0.16)) + (0.4275*(T*(V*0.16)))
    return round(windchill, 1)

def graphForecast(hourlyForecastJSON, tempAdjustment=0, daysToGraph=1):
  hours = daysToGraph * 24

# @anvil.server.background_task
# @anvil.server.callable
# def OLDupdateForecastData():
#   for row in app_tables.locations.search():
#     result = getRawForecastData(row['Latitude'], row['Longitude'])
#     if not result:
#       continue
#     periods = result.get('properties', {}).get('periods')
#     if periods:
#       DataRequestDatetime = datetime.strptime(
#         result['properties']['generatedAt'], '%Y-%m-%dT%H:%M:%S%z'
#       ) + timedelta(hours=-4)
#       NOAAupdateDatetime = datetime.strptime(
#         result['properties']['updateTime'], '%Y-%m-%dT%H:%M:%S%z'
#       ) + timedelta(hours=-4)
#       row.update(
#         DataRequested=DataRequestDatetime,
#         NOAAupdate=NOAAupdateDatetime,
#         RawData=result,
#       )

# latitude, longitude = (42.4395, -76.5022)

# days = 4
# tempAdjustment = -25  # used to test windchill calc with summertime data...
# hours = 24 * days
# lastPeriodEligible = False

# keyForecastData = [getOneHourForecastData(period) for period in periods[:hours]]

# def calculateWindchill(temperature=80, windspeed=0):
#     T, V = temperature, windspeed
#     windchill = 35.74 + (0.6215*T) - (35.75*(V*0.16)) + (0.4275*(T*(V*0.16)))
#     return round(windchill, 1)

# def getAllForecastData(latitude, longitude):
#   forecastURL = f'https://api.weather.gov/points/{latitude},{longitude}'
#   hourlyForecastURL = requests.get(forecastURL).json()['properties']['forecastHourly']
#   hourlyForecastJSON = requests.get(hourlyForecastURL).json()
#   periods = hourlyForecastJSON['properties']['periods']
#   return periods

# def getOneHourForecastData(oneHourlyForecastDict):
#     global lastPeriodEligible

#     period = oneHourlyForecastDict
#     betterTemp = int(period['temperature']) + tempAdjustment
#     betterWindSpeed = int(period['windSpeed'].split()[0])

#     newPeriod = dict()
#     newPeriod['startTime'] = datetime.strptime(period['startTime'], '%Y-%m-%dT%H:%M:%S%z')
#     newPeriod['temperatureF'] = betterTemp
#     newPeriod['windSpeedMPH'] = betterWindSpeed
#     newPeriod['windChill'] = calculateWindchill(betterTemp, betterWindSpeed)

#     newPeriod['consecutive'] = False
#     if newPeriod['windChill'] <= 32:
#         if lastPeriodEligible:
#             newPeriod['consecutive'] = True
#         else:
#             lastPeriodEligible = True
#     else:
#         lastPeriodEligible = False
#     return newPeriod

# @anvil.server.callable
# def getForecastGraph(keyForecastData, days):
#   graphData = {item['startTime']:item['windChill'] for item in keyForecastData}
#   minTemp = min(graphData.values())
#   maxTemp = max(graphData.values())
#   dateList = set(item['startTime'].strftime('%Y-%m-%d') for item in keyForecastData)

#   fig, ax = plt.subplots()
#   ax.plot(graphData.keys(), graphData.values(), color='darkgray')
#   ax.xaxis.set_major_formatter(ConciseDateFormatter(ax.xaxis.get_major_locator()))
#   ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(8))
#   plt.xlabel('Hours')
#   plt.ylabel('Fahrenheit')
#   plt.title(f'Wind Chill Temperature: {days} day Forecast')

#   ax.vlines(x=list(dateList)[1:], ymin=minTemp, ymax=maxTemp, colors='lightgray', ls='-')

#   if minTemp <= 32:
#       plt.axhline(y=32, color='red', linestyle='-')
#       coldDataPoints = {item['startTime']:item['windChill'] for item in keyForecastData if item['windChill'] <= 32}
#       xs, ys = list(coldDataPoints.keys()), list(coldDataPoints.values())
#       ax.plot(coldDataPoints.keys(), coldDataPoints.values(), color='cornflowerblue')
#       ax.fill_between(xs, ys, 32, color='cornflowerblue', interpolate=True)

#   # plt.show()
#   return anvil.mpl_util.plot_image()
