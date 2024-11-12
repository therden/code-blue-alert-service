import anvil.email
import anvil.users
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.mpl_util
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.dates import ConciseDateFormatter
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np
import sys
from zoneinfo import ZoneInfo
import urllib.parse

APP_ORIGIN = anvil.server.get_app_origin()


@anvil.server.callable
def updateFields(rowObject, tupleList):
  for each in tupleList:
    rowObject[each[0]] = each[1]


@anvil.server.callable
def copyCurrentLocationsDataToDaily():
  location_rows = app_tables.locations.search()
  # each = location_rows[1]
  for each in location_rows:
    app_tables.daily_forecasts.add_row(
      NOAAupdate=each["NOAAupdate"],
      RawData=each["RawData"],
      DataRequested=each["DataRequested"],
      locality=each,
      DateOfForecast=each["DataRequested"].date(),
    )


@anvil.server.callable
def edit_locations():
  nextForecast = datetime.strptime("Oct 21 2024  5:00PM", "%b %d %Y %I:%M%p")
  listOfFieldValueTuples = [
    ("NextPMforecast", nextForecast),
    ("StrongForecastConsent", False),
    # ("Overnight", None),
    # ("NextDay", None),
  ]
  for location in app_tables.locations.search():
    updateFields(location, listOfFieldValueTuples)


@anvil.server.callable
def test_plot():
  # Make a nice wiggle
  x = [0, 1, 2, 3, 4]
  y = [3.3, 7.3, 2.7, 5, 3.7]

  # Plot it in the normal Matplotlib way
  fig, ax = plt.subplots()
  plt.xlabel("Hours")
  plt.ylabel("Fahrenheit")
  plt.title("Wind Chill Forecast")
  ax.vlines([0.75, 1.5, 2.25, 3], ymin=min(y), ymax=max(y), colors="blue", ls="-")
  plt.plot(x, y, "crimson")

  # Return this plot as a PNG image in a Media object
  return anvil.mpl_util.plot_image()


@anvil.server.callable
def get_sample_graph():
  # row = app_tables.locations.get(CountyName="Suffolk")
  row = app_tables.locations.get(CountyName="Tompkins")
  return graphForecast(row["RawData"], 1, 0)


@anvil.server.callable
def get_locations_links(**p):
  return [
    (f'{location["CountyName"]}', f'{APP_ORIGIN}/for/{location["NormalizedName"]}')
    for location in app_tables.locations.search()
  ]


@anvil.server.callable
def log_event(description='"log_event" called without a "Description"'):
  app_tables.event_log.add_row(event_datetime=datetime.now(), description=description)


@anvil.server.callable
@anvil.server.background_task
def getKeyForecastData(oneHourForecastDict, tempAdjustment):
  global lastPeriodEligible

  period = oneHourForecastDict
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


def tempModifierForCodeBlueFillBetween(temp):
  if temp > 32:
    temp = 32
  return temp


@anvil.server.callable
@anvil.server.background_task
def graphForecast(hourlyForecastJSON, daysToGraph=1, tempAdjustment=0):
  global lastPeriodEligible
  lastPeriodEligible = False

  DAYS = daysToGraph
  HOURS = 24 * daysToGraph
  LOCAL_TZ = ZoneInfo("America/New_York")

  raw_forecasts_by_hour = hourlyForecastJSON["properties"]["periods"]

  keyForecastData = [
    getKeyForecastData(single_forecast, tempAdjustment)
    for single_forecast in raw_forecasts_by_hour[:HOURS]
  ]
  graphData = {item["startTime"]: item["windChill"] for item in keyForecastData}
  minTemp = min(graphData.values())
  maxTemp = max(graphData.values())
  dateSet = [
    item["startTime"] for item in keyForecastData if item["startTime"].hour == 0
  ]

  fig, ax = plt.subplots()
  ax.set_title(f"Wind Chill Temperatures: {DAYS} day Forecast")
  ax.set_ylabel("°Fahrenheit")
  # ax.set_xlabel("Date | Hour")
  # plt.figure(figsize=(10,6))
  ax.plot(graphData.keys(), graphData.values(), color="darkgray", ls="--")
  plt.gca().xaxis.set_major_locator(mdates.DayLocator(tz=LOCAL_TZ))
  plt.gca().xaxis.set_minor_locator(mdates.HourLocator(tz=LOCAL_TZ))
  ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d", tz=LOCAL_TZ))
  ax.xaxis.set_minor_formatter(mdates.DateFormatter("%I %p", tz=LOCAL_TZ))
  ax.tick_params(
    axis="x",
    which="major",
    labelrotation=45,
    labelsize=7,
    color="black",
    labelcolor="black",
  )
  ax.tick_params(
    axis="x",
    which="minor",
    color="gray",
    labelcolor="gray",
    labelrotation=45,
    labelsize=8,
  )
  # add a vertical line at midnight(s)
  ax.vlines(x=dateSet, ymin=minTemp, ymax=maxTemp, colors="lightgray", ls="-")

  DataPoints1 = {item["startTime"]: item["windChill"] for item in keyForecastData}
  xs, ys = list(DataPoints1.keys()), list(DataPoints1.values())
  ax.plot(
    DataPoints1.keys(),
    DataPoints1.values(),
    color="#72B7F2",
    linewidth=0.5,
  )
  ax.fill_between(xs, ys, max(32, minTemp), interpolate=False, color="lemonchiffon")
  if minTemp <= 32:
    DataPoints2 = {
      item["startTime"]: tempModifierForCodeBlueFillBetween(item["windChill"])
      for item in keyForecastData
    }
    xs, ys = list(DataPoints2.keys()), list(DataPoints2.values())
    ax.fill_between(
      xs,
      ys,
      32,
      interpolate=False,
      color="#72B7F2",
    )
    # add a blue horizontal line at 32 degrees and color line below that blue
    ax.axhline(y=32, color="dodgerblue", linestyle="-", linewidth=2)
  return anvil.mpl_util.plot_image()


@anvil.server.callable
def calculateWindchill(temperature=80, windspeed=0):
  T, V = temperature, windspeed
  windchill = 35.74 + (0.6215 * T) - (35.75 * (V * 0.16)) + (0.4275 * (T * (V * 0.16)))
  return round(windchill, 1)


def getCallingFunctionName():
  return sys._getframe().f_back.f_code.co_name


# @anvil.server.background_task
# @anvil.server.callable
# def findDuplicates():
#   def getDailies(prefix="START: "):
#     dailies = app_tables.daily_forecasts.search()
#     print(f"{prefix} daily forecast records: {len(dailies)}")
#     return dailies

#   def getLocations_and_ForecastDates():
#     dailies = getDailies()
#     locationrows = set()
#     forecastdates = set()
#     for daily in dailies:
#       locationrows.add(daily["locality"])
#       forecastdates.add(daily["DateOfForecast"])
#     return locationrows, forecastdates

#   locations, dates = getLocations_and_ForecastDates()
#   for adate in dates:
#     for aloc in locations:
#       found = app_tables.daily_forecasts.search(DateOfForecast=adate, locality=aloc)
#       if len(found) > 1:
#         found[0].delete()
#   getDailies(prefix="END:")


# @anvil.server.callable
# def import_fips_ids():
#   import pandas as pd

#   with open(data_files["fips_NYScounties_CodeBlue2.csv"]) as file:
#     records = pd.read_csv(file).to_dict(orient="records")
#     # print(records)
#   for rec in records:
#     # d is now a dict of {columnname -> value} for this row
#     loc_name = rec["county"]
#     row_to_update = app_tables.locations.get(CountyName=loc_name)
#     if row_to_update:
#       row_to_update.update(FIPS_id=rec["fips"])

# @anvil.server.callable
# def pop_locations_YorN():
#   import random
#   locs = app_tables.locations.search()
#   for loc in locs:
#     loc['NextDay']=random.choice([True, False])
#     loc["Overnight"]=random.choice([True, False])


def encode_svg(svg_image):
  bytes = svg_image.get_bytes()
  string = str(bytes)[2:-1]
  source = urllib.parse.quote(string)
  return f"data:image/svg+xml;utf8,{source}"


@anvil.server.callable
def get_statemap(row_name):
  row = app_tables.media.get(Name=row_name)
  updated_at = row["Updated"]
  svg_image = row["Blob"]
  encoded_img = encode_svg(svg_image)
  return encoded_img, updated_at


@anvil.server.background_task
@anvil.server.callable
def daily_forecast_update_durations():
  test_date = date(2024, 11, 9)
  delta = timedelta(days=-1)
  for x in range(30):
    try:
      test_date = test_date + delta
      rows = app_tables.daily_forecasts.search(
        tables.order_by("DataRequested"), DateOfForecast=test_date
      )
      print(f"{test_date}: {rows[56]['DataRequested']-rows[0]['DataRequested']}")
    except Exception:
      print(f"Error regarding date {test_date}")
