import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
@anvil.server.route("/hello")
def hello(**p):
  return {"hello":"world"}

@anvil.server.route("/forecast/test")
def forecast_test(**p):
  return anvil.server.FormResponse("Forecast")

@anvil.server.route("/forecast/list")
def get_locations_list():
  # return [location['CountyName'] for location in app_tables.locations.search()]
  return '\n'.join([location['CountyName'] for location in app_tables.locations.search()])

@anvil.server.route("/forecast/:name")
def serve_location_page(name, **p):
  location = app_tables.locations.get(Name=name)
  if location:
    # return anvil.server.FormResponse('Forecast', location=location)
    return anvil.server.FormResponse('Forecast')
  else:
    return anvil.server.HttpResponse(404, f"Location '{name}' not supported")