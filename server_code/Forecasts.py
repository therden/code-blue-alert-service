from datetime import date, datetime, timedelta
import json
import matplotlib.pyplot as plt
from matplotlib.dates import ConciseDateFormatter
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
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
  forecastURL = f"https://api.weather.gov/points/{latitude},{longitude}"
  result = requests.get(forecastURL).json()
  hourlyForecastURL = result.get("properties", {}).get("forecastHourly")
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
    # print(f"Counter: {counter}   Empty forecasts: {emptyForecastCount}")
    for each in emptyForecasts:
      result = anvil.server.call("updateForecast")
      #   result = getRawForecastData(
      #     each["locality"]["Latitude"], each["locality"]["Longitude"]
      #   )
      if not result:
        continue
        # periods = result.get("properties", {}).get("periods")
        # if periods:
        #   DataRequestDatetime = datetime.strptime(
        #     result["properties"]["generatedAt"], "%Y-%m-%dT%H:%M:%S%z"
        #   ) + timedelta(hours=-4)
        #   NOAAupdateDatetime = datetime.strptime(
        #     result["properties"]["updateTime"], "%Y-%m-%dT%H:%M:%S%z"
        #   ) + timedelta(hours=-4)
        # update fields in 'daily_forecasts' table
        each.update(
          DataRequested=each["locality"]["DataRequested"],
          NOAAupdate=each["locality"]["NOAAupdate"],
          RawData=each["locality"]["RawData"],
        )
        # # update equivalent fields in linked 'locations' table
        # each["locality"]["DataRequested"] = DataRequestDatetime
        # each["locality"]["NOAAupdate"] = NOAAupdateDatetime
        # each["locality"]["RawData"] = result


@anvil.server.callable
@anvil.server.background_task
def updateForecast(location_row):
  result = updateForecastData(location_row)
  if result:
    updateForecastGraph(location_row)
    return True
  else:
    return False


@anvil.server.callable
@anvil.server.background_task
def updateForecastData(location_row):
  lat, long = location_row["Latitude"], location_row["Longitude"]
  result = getRawForecastData(lat, long)
  if not result:
    return False
  periods = result.get("properties", {}).get("periods")
  if periods:
    DataRequestDatetime = datetime.strptime(
      result["properties"]["generatedAt"], "%Y-%m-%dT%H:%M:%S%z"
    ) + timedelta(hours=-4)
    NOAAupdateDatetime = datetime.strptime(
      result["properties"]["updateTime"], "%Y-%m-%dT%H:%M:%S%z"
    ) + timedelta(hours=-4)
    location_row.update(
      DataRequested=DataRequestDatetime,
      NOAAupdate=NOAAupdateDatetime,
      RawData=result,
    )
    return True


@anvil.server.callable
def calculateWindchill(temperature=80, windspeed=0):
  T, V = temperature, windspeed
  windchill = 35.74 + (0.6215 * T) - (35.75 * (V * 0.16)) + (0.4275 * (T * (V * 0.16)))
  return round(windchill, 1)


def getOneHourForecastData(oneHourlyForecastDict, tempAdjustment):
  global lastPeriodEligible

  period = oneHourlyForecastDict
  betterTemp = int(period["temperature"]) + tempAdjustment
  betterWindSpeed = int(period["windSpeed"].split()[0])

  newPeriod = dict()
  newPeriod["startTime"] = datetime.strptime(period["startTime"], "%Y-%m-%dT%H:%M:%S%z")
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


def tempModifier(temp):
  if temp > 32:
    temp = 32
  return temp


@anvil.server.callable
@anvil.server.background_task
def graphForecast(hourlyForecastJSON, daysToGraph=1, tempAdjustment=0):
  DAYS = daysToGraph
  HOURS = 24 * daysToGraph

  def getKeyForecastData(oneHourForecastDict):
    global lastPeriodEligible

    period = oneHourForecastDict
    betterTemp = int(period["temperature"]) + tempAdjustment
    betterWindSpeed = int(period["windSpeed"].split()[0])

    newPeriod = dict()
    newPeriod["startTime"] = datetime.strptime(
      period["startTime"], "%Y-%m-%dT%H:%M:%S%z"
    )
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

  # "2024-09-06T17:40:12+00:00"
  # NOAAforecastUpdated = datetime.strptime(
  #   hourlyForecastJSON["properties"]["updateTime"][:16], "%Y-%m-%dT%H:%M"
  # ) + timedelta(hours=-4)
  periods = hourlyForecastJSON["properties"]["periods"]
  keyForecastData = [getKeyForecastData(period) for period in periods[:HOURS]]
  graphData = {item["startTime"]: item["windChill"] for item in keyForecastData}
  minTemp = min(graphData.values())
  maxTemp = max(graphData.values())
  dateSet = list(
    set(item["startTime"].strftime("%Y-%m-%d") for item in keyForecastData)
  )
  dateSet.sort()

  fig, ax = plt.subplots()

  ax.plot(graphData.keys(), graphData.values(), color="darkgray", ls="--")
  plt.gca().xaxis.set_major_locator(mdates.DayLocator())
  plt.gca().xaxis.set_minor_locator(mdates.HourLocator())
  ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
  ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H"))
  # ax.tick_params(axis="x", which="major", labeltop=True, labelbottom=False)
  ax.tick_params(axis="x", which="major", labelrotation=90, labelsize=7)
  ax.tick_params(axis="x", which="minor", labelrotation=90, labelsize=8)

  ax.vlines(x=dateSet[1:], ymin=minTemp, ymax=maxTemp, colors="lightgray", ls="-")

  if minTemp <= 32:
    # add a red horizontal line at 32 degrees and color line below that blue
    coldDataPoints = {
      item["startTime"]: tempModifier(item["windChill"]) for item in keyForecastData
    }
    xs, ys = list(coldDataPoints.keys()), list(coldDataPoints.values())
    ax.plot(
      coldDataPoints.keys(),
      coldDataPoints.values(),
      color="cornflowerblue",
      linewidth=0.5,
    )
    ax.fill_between(xs, ys, 32, color="cornflowerblue", interpolate=False)
    ax.axhline(y=32, color="red", linestyle="-", linewidth=2)

  # plt.figure(figsize=(10,6))
  ax.set_xlabel("Date | Hour")
  ax.set_ylabel("Fahrenheit")
  ax.set_xlabel("Hourly Projections")
  ax.set_title(f"Wind Chill Temperatures: {DAYS} day Forecast")

  return anvil.mpl_util.plot_image()


@anvil.server.callable
@anvil.server.background_task
def updateForecastGraph(location_row, daysToGraph=1, tempAdjustment=0):
  location_row["LastGraph"] = anvil.server.call(
    "graphForecast", location_row["RawData"], daysToGraph, tempAdjustment
  )


@anvil.server.callable
@anvil.server.background_task
def updateGraphFromNormalizedName(normalized_name, daysToGraph=1, tempAdjustment=0):
  location = app_tables.locations.get(NormalizedName=normalized_name)
  updateForecastGraph(location, daysToGraph, tempAdjustment)


@anvil.server.callable
@anvil.server.background_task
def updateAllGraphs(daysToGraph=1, tempAdjustment=0):
  for row in app_tables.locations.search():
    anvil.server.call("updateForecastGraph", row, daysToGraph, tempAdjustment)


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
