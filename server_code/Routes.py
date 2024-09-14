import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

APP_ORIGIN = anvil.server.get_app_origin()


def makeLink(URLstub, linkText):
  global APP_ORIGIN
  return f'<p><a href="{APP_ORIGIN}/for/{URLstub}">{linkText}</a></p>'


@anvil.server.callable
def get_locations_list_links_string():
  return "\n".join(
    get_locations_links_list()
    # [
    #   makeLink(location["NormalizedName"], location["CountyName"])
    #   for location in app_tables.locations.search()
    # ]
  )


@anvil.server.callable
def get_locations_links_list():
  # return [location['CountyName'] for location in app_tables.locations.search()]
  return [
    makeLink(location["NormalizedName"], location["CountyName"])
    for location in app_tables.locations.search()
  ]


@anvil.server.callable
def get_locations_tuples():
  # return [location['CountyName'] for location in app_tables.locations.search()]
  return [
    (f'{APP_ORIGIN}/for/{location["NormalizedName"]}', location["CountyName"])
    for location in app_tables.locations.search()
  ]


@anvil.server.route("/for")
def locations_list(**p):
  return anvil.server.FormResponse("LocationsLinks")


@anvil.server.route("/for/test")
def forecast_test(**p):
  return anvil.server.FormResponse("ForecastTest")


@anvil.server.route("/for/:location_name")
def serve_location_page(location_name, **p):
  print(location_name)
  location_record = app_tables.locations.get(NormalizedName=location_name)
  if location_record:
    return anvil.server.FormResponse("Forecast", location_record=location_record)
  else:
    return anvil.server.HttpResponse(404, f'Location "{location_name}" not supported')
