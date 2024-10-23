import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta


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
      # get rawdata from noaa's api
      # evaluate rawdata's suitability
      # transform rawdata for our purposes
      # generate forecast graph
      # save new forecast data to daily_forecasts
      # update location["NextForecastDue"]


def make_new_daily_forecast(location_row):
  raw_data = get_raw_data(location_row)
  if not raw_data:
    # log failure  #todo
    return False
  if not raw_data_usable(raw_data):
    # log failure  #todo
    return False
  transformed_data = transform_data(raw_data)
  graph_image = generate_forecast_graph(transformed_data)
  api_request_dt, noaa_forecast_dt, overnight_status, morrow_status = extract_values(
    transformed_data
  )
  next_forecast_dt = calculate_next_forecast_dt(location["NextForecastDue"])
  try:
    update_tables_with_daily_forecast_info()
  except Exception:
    pass
    # log failure  #todo


# @anvil.server.callable
# @anvil.tables.in_transaction
# def test_transactions():
#   for count in range(5):
#     app_tables.test.add_row(Column1=f"test entry #{count}")


def get_raw_data(location_row):
  pass


def raw_data_usable(raw_data):
  pass


def transform_data(raw_data):
  pass


def generate_forecast_graph(transformed_data):
  pass


def extract_values(transformed_data):
  # api_request_dt
  # noaa_forecast_dt
  # overnight_status
  # morrow_status
  pass


def calculate_next_forecast_dt(this_forecast_dt):
  return this_forecast_dt.replace(day=(now_dt.day + 1))


@anvil.server.callable
@anvil.tables.in_transaction
def update_tables_with_daily_forecast_info():
  pass


#     name = location["CountyName"]
#     this_forecast_dt = location["NextForecastDue"]
#     tomorrow_forecast_dt = location["NextForecastDue"].replace(day=(now_dt.day + 1))
#     print(
#       f"{name} due {this_forecast_dt}; done {datetime.now()}; next at {tomorrow_forecast_dt}"
#     )
# else:
#   print(f"No forecasts due at {now_dt}")
