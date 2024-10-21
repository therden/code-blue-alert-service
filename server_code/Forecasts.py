from datetime import date, datetime, timedelta
import json

# import matplotlib.pyplot as plt
# from matplotlib.dates import ConciseDateFormatter
# import matplotlib.ticker as ticker
# import matplotlib.dates as mdates
import requests
from time import sleep
from zoneinfo import ZoneInfo
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .Utilities import log_event
from .Utilities import graphForecast
from .Utilities import calculateWindchill

lastPeriodEligible = False


@anvil.server.callable
def getHourlyForecastURL(locationRow):
  latitude = locationRow["Latitude"]
  longitude = locationRow["Longitude"]
  pointsURL = f"https://api.weather.gov/points/{latitude},{longitude}"
  pointsURLresult = requests.get(pointsURL).json()
  try:
    hourlyForecastURL = pointsURLresult.get("properties", {}).get("forecastHourly")
    return hourlyForecastURL
  except:
    graphForecast()


@anvil.server.callable
def updateHourlyForecastURLs():
  location_rows = app_tables.locations.search()
  for row in location_rows:
    currentForecastURL = getHourlyForecastURL(row)
    if row["HourlyForecastURL"] != currentForecastURL:
      description = f"Hourly Forecast URL for {row['LocationName']} updated from {row['HourlyForecastURL']} to {currentForecastURL}."
      log_event(description)
      row["HourlyForecastURL"] = currentForecastURL


@anvil.server.callable
def getRawForecastData(locations_row):
  hourlyForecastURL = locations_row["hourlyForecastURL"]
  try:
    ForecastJSON = requests.get(hourlyForecastURL).json()
    return ForecastJSON
  except:
    description = (
      f"Raw forecast data not retrieved for {locations_row['LocationName']}."
    )
    log_event(description)
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
  # with longer pauses between each try
  for counter in range(5):
    emptyForecasts = app_tables.daily_forecasts.search(
      DateOfForecast=thisDate, RawData=None
    )
    emptyForecastCount = len(emptyForecasts)
    if emptyForecastCount == 0:
      break
    sleep(5 * counter)
    for each in emptyForecasts:
      result = updateForecast(each["locality"])
      if not result:
        continue
      each.update(
        DataRequested=each["locality"]["DataRequested"],
        NOAAupdate=each["locality"]["NOAAupdate"],
        RawData=each["locality"]["RawData"],
      )


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
  # lat, long = location_row["Latitude"], location_row["Longitude"]
  result = getRawForecastData(location_row)
  if not result:
    return False
  periods = result.get("properties", {}).get("periods")
  if periods:
    # DataRequestDatetime = datetime.strptime(
    #   result["properties"]["generatedAt"], "%Y-%m-%dT%H:%M:%S%z"
    # ) + timedelta(hours=-4)
    # NOAAupdateDatetime = datetime.strptime(
    #   result["properties"]["updateTime"], "%Y-%m-%dT%H:%M:%S%z"
    # ) + timedelta(hours=-4)
    generated = result["properties"]["generatedAt"]
    updated = result["properties"]["updateTime"]
    formatStr = "%Y-%m-%dT%H:%M:%S%z"
    timezone = ZoneInfo("America/New_York")
    DataRequestDatetime = datetime.strptime(generated, formatStr).astimezone(timezone)
    # DataRequestDatetime = DataRequestDatetime.astimezone(timezone)
    NOAAupdateDatetime = datetime.strptime(updated, formatStr).astimezone(timezone)
    # NOAAupdateDatetime = NOAAupdateDatetime.astimezone(timezone)
    location_row.update(
      DataRequested=DataRequestDatetime,
      NOAAupdate=NOAAupdateDatetime,
      RawData=result,
    )
    return True


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





@anvil.server.callable
@anvil.server.background_task
def updateForecastGraph(location_row, daysToGraph=1, tempAdjustment=0):
  location_row["LastGraph"] = graphForecast(
    location_row["RawData"], daysToGraph, tempAdjustment
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
    # anvil.server.call("updateForecastGraph", row, daysToGraph, tempAdjustment)
    updateForecastGraph(row, daysToGraph, tempAdjustment)
