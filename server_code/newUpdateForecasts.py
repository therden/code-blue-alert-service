import anvil.email
import anvil.users
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import date, datetime, timedelta
import requests
import sys
from zoneinfo import ZoneInfo
from .Utilities import calculateWindchill
from .Utilities import log_event
from .Utilities import getCallingFunctionName as func_name
from .Utilities import graphForecast


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


@anvil.server.callable
def make_new_daily_forecast(location_row, raw_data=False):
  dailyForecastDict = dict()
  locationName = location_row["LocationName"]
  if not raw_data:
    raw_data = get_raw_data(location_row)
  print(raw_data)
  if not raw_data:
    log_event(f"Raw forecast data for {locationName} was not retrieved.")
    return False
  if not raw_data_contains_hourly_forecasts(raw_data):
    log_event(f"Raw data for {locationName} missing forecast data (periods).")
    return False
  forecastDates = get_forecast_dates(raw_data)
  overnight_status, morrow_status = extract_statuses(raw_data)
  dailyForecastDict["DateOfForecast"] = forecastDates[0].date()
  dailyForecastDict["locality"] = location_row
  dailyForecastDict["DataRequested"] = forecastDates[0]
  dailyForecastDict["NOAAupdate"] = forecastDates[1]
  dailyForecastDict["Graph"] = graphForecast(raw_data)
  dailyForecastDict["Overnight"] = overnight_status
  dailyForecastDict["NextDay"] = morrow_status
  dailyForecastDict["RawData"] = raw_data
  try:
    update_tables_with_daily_forecast_info(dailyForecastDict)
  except Exception:
    log_event(f"Table updates for {locationName} forecast unsuccessful.")


@anvil.server.callable
def get_raw_data(location_row):
  hourlyForecastURL = location_row["HourlyForecastURL"]
  try:
    ForecastJSON = requests.get(hourlyForecastURL).json()
  except:
    ForecastJSON = None
  finally:
    return ForecastJSON


def raw_data_contains_hourly_forecasts(raw_data):
  try:
    result = raw_data.get("properties", {}).get("periods")
  except:
    result = None
  return result


@anvil.server.callable
def get_forecast_dates(raw_data):
  UpdateRequestDT = getDatetimeObj(raw_data["properties"]["generatedAt"])
  NOAAforecastDT = getDatetimeObj(raw_data["properties"]["updateTime"])
  return UpdateRequestDT, NOAAforecastDT


@anvil.server.callable
def getDatetimeObj(datetime_str):
  formatStr = "%Y-%m-%dT%H:%M:%S%z"
  datetime_obj = datetime.strptime(datetime_str, formatStr)
  datetime_obj = make_date_offset_aware(datetime_obj)
  return datetime_obj


@anvil.server.callable
def extract_statuses(raw_data):
  transformedData = transform_data(raw_data)
  oneDay = timedelta(days=1)
  thisDate = datetime.combine(datetime.today(), datetime.min.time())
  tomorrow = thisDate + oneDay
  overnightStart = make_date_offset_aware(thisDate.replace(hour=17))
  overnightEnd = make_date_offset_aware(tomorrow.replace(hour=7))
  morrowStart = overnightEnd
  morrowEnd = overnightStart + oneDay
  qualfication_test = test_for_consecutive_hourly_windchill_forecasts
  overnight_status = qualfication_test(transformedData, overnightStart, overnightEnd)
  morrow_status = qualfication_test(transformedData, morrowStart, morrowEnd)
  return overnight_status, morrow_status
  # raise Exception(f"Function {func_name()} not yet implemented")


@anvil.server.callable
def make_date_offset_aware(datetime_obj):
  timezone = ZoneInfo("America/New_York")
  datetime_obj = datetime_obj.astimezone(timezone)
  return datetime_obj


@anvil.server.callable
def transform_data(raw_data):
  periods = raw_data["properties"]["periods"]
  return [transform_period(period) for period in periods]


@anvil.server.callable
def test_for_consecutive_hourly_windchill_forecasts(transformed_data, start_dt, end_dt):
  test_data = [
    dict
    for dict in transformed_data
    if dict["startTime"] >= start_dt and dict["startTime"] <= end_dt
  ]
  consecutive = False
  last_hour = False
  for each_hour in test_data:
    if each_hour["windChillF"] <= 32:
      if last_hour:
        consecutive = True
        break
      else:
        last_hour = True
    else:
      last_hour = False
  return consecutive
  # raise Exception(f"Function {func_name()} not yet implemented")


@anvil.server.callable
def transform_period(period):
  newPeriod = dict()
  newPeriod["startTime"] = datetime.strptime(period["startTime"], "%Y-%m-%dT%H:%M:%S%z")
  betterTemp = int(period["temperature"])
  betterWindSpeed = int(period["windSpeed"].split()[0])
  newPeriod["temperatureF"] = betterTemp
  newPeriod["windSpeedMPH"] = betterWindSpeed
  newPeriod["windChillF"] = calculateWindchill(betterTemp, betterWindSpeed)
  return newPeriod


@anvil.server.callable
def calculate_next_forecast_dt(this_forecast_dt):
  next_forecast = this_forecast_dt.replace(day=(datetime.now().day + 1))
  return next_forecast


@anvil.server.callable
@anvil.tables.in_transaction
def update_tables_with_daily_forecast_info(dailyForecastDict):
  app_tables.daily_forecasts.add_row(dailyForecastDict)
  location_row = dailyForecastDict["locality"]
  next_forecast_dt = location_row["NextForecastDue"]
  location_row["NextForecastDue"] = calculate_next_forecast_dt(next_forecast_dt)
  # print(f'For {location_row["CountyName"]}...')
  # print(
  #   f"  Next forecast datetime (to update Locations): {next_forecast_dt:%B %d, %I:%M %p}"
  # )
  # print("   Here's the dict that'll update 'daily_forecasts'")
  # print(dailyForecastDict)
  # raise Exception(f"Function {sys._getframe().f_code.co_name} not yet implemented")


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

# setupServerConsole():
# import anvil.email
# import anvil.users
# import anvil.files
# from anvil.files import data_files
# import anvil.tables as tables
# import anvil.tables.query as q
# from anvil.tables import app_tables
# import anvil.server
# from datetime import datetime, timedelta
# import requests
# import sys
# from zoneinfo import ZoneInfo
# from .Utilities import calculateWindchill
# from .Utilities import log_event
# from .Utilities import getCallingFunctionName as func_name
# from .Utilities import graphForecast
# locs = app_tables.locations.search()
# alb = locs[0]
# raw_data = alb["RawData"]
# p1 = raw_data["properties"]["periods"][0]
