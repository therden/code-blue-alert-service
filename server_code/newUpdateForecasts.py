import anvil.email
import anvil.users
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta
import requests
import sys
from zoneinfo import ZoneInfo
from .Utilities import log_event
from .Utilities import getCallingFunctionName as func_name


# background task to check Locations["NextForecastDue"] once each minute
@anvil.server.background_task
@anvil.server.callable
def checkForForecastsDue():
  now_dt = datetime.now().replace(second=0, microsecond=0)
  forecasts_due = app_tables.locations.search(
    NextForecastDue=q.less_than_or_equal_to(now_dt)
  )
  if len(forecasts_due):
    for location in forecasts_due:
      # launch background task for location
      anvil.server.launch_background_task("make_new_daily_forecast", location)
      # evaluate rawdata's suitability
      # transform rawdata for our purposes
      # generate forecast graph
      # save new forecast data to daily_forecasts
      # update location["NextForecastDue"]


def make_new_daily_forecast(location_row):
  dailyForecastDict = dict(RawData=None, DataRequested=None, NOAAupdate=None)
  locationName = location_row["LocationName"]
  raw_data = get_raw_data(location_row)
  if not raw_data:
    log_event(f"Raw forecast data for {locationName} was not retrieved.")
    return False
  if not raw_data_contains_hourly_forecasts(raw_data):
    log_event(f"Raw data for {locationName} missing forecast data (periods).")
    return False
  dailyForecastDict["RawData"] = raw_data
  forecastDates = get_forecast_dates(raw_data)
  dailyForecastDict["DataRequested"] = forecastDates[0]
  dailyForecastDict["NOAAupdate"] = forecastDates[1]

  transformed_data = transform_data(raw_data)
  dailyForecastDict["Graph"] = generate_forecast_graph(transformed_data)
  api_request_dt, noaa_forecast_dt, overnight_status, morrow_status = extract_values(
    transformed_data
  )
  next_forecast_dt = calculate_next_forecast_dt(location["NextForecastDue"])
  try:
    update_tables_with_daily_forecast_info(next_forecast_dt, dailyForecastDict)
  except Exception:
    log_event(f"Table updates for {locationName} forecast unsuccessful.")


def get_raw_data(location_row):
  hourlyForecastURL = location_row["HourlyForecastURL"]
  try:
    ForecastJSON = requests.get(hourlyForecastURL).json()
  except:
    ForecastJSON = None
  return ForecastJSON


def raw_data_contains_hourly_forecasts(raw_data, locationName):
  try:
    result = raw_data.get("properties", {}).get("periods")
  except:
    result = None
  return result


def get_forecast_dates(raw_data):
  UpdateRequestDT = getDatetimeObj(raw_data["properties"]["generatedAt"])
  NOAAforecastDT = getDatetimeObj(raw_data["properties"]["updateTime"])
  return UpdateRequestDT, NOAAforecastDT


def getDatetimeObj(datetime_str):
  formatStr = "%Y-%m-%dT%H:%M:%S%z"
  datetime_obj = datetime.strptime(datetime_str, formatStr)
  timezone = ZoneInfo("America/New_York")
  datetime_obj = datetime_obj.astimezone(timezone)
  return datetime_obj


def transform_data(raw_data):
  raise Exception(f"Function {func_name()} not yet implemented")


def generate_forecast_graph(transformed_data):
  raise Exception(f"Function {func_name()} not yet implemented")


def extract_values(transformed_data):
  # api_request_dt
  # noaa_forecast_dt
  # overnight_status
  # morrow_status
  raise Exception(f"Function {func_name()} not yet implemented")


def calculate_next_forecast_dt(this_forecast_dt):
  next_forecast = this_forecast_dt.replace(day=(datetime.now().day + 1))
  return next_forecast


@anvil.server.callable
@anvil.tables.in_transaction
def update_tables_with_daily_forecast_info():
  raise Exception(f"Function {sys._getframe().f_code.co_name} not yet implemented")


#     name = location["CountyName"]
#     this_forecast_dt = location["NextForecastDue"]
#     tomorrow_forecast_dt = location["NextForecastDue"].replace(day=(now_dt.day + 1))
#     print(
#       f"{name} due {this_forecast_dt}; done {datetime.now()}; next at {tomorrow_forecast_dt}"
#     )
# else:
#   print(f"No forecasts due at {now_dt}")


# @anvil.server.callable
# @anvil.tables.in_transaction
# def test_transactions():
#   for count in range(5):
#     app_tables.test.add_row(Column1=f"test entry #{count}")
