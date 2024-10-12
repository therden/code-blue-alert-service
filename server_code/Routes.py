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
def makeMarkdownLink(linkText, URLstub):
  global APP_ORIGIN
  return f"[{linkText}]({APP_ORIGIN}/for/{URLstub})&nbsp;&nbsp;&nbsp; "


@anvil.server.callable
def get_locations_links_list():
  # return [location['CountyName'] for location in app_tables.locations.search()]
  return "\n".join(
    [
      makeLink(location["CountyName"], location["NormalizedName"])
      for location in app_tables.locations.search()
    ]
  )


@anvil.server.route("/locations")
def locations_list_form(**p):
  return anvil.server.FormResponse("LocationsLinksList")


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


@anvil.server.route("/for")
def locations_links_form(**p):
  return anvil.server.FormResponse("LocationsLinks")


@anvil.server.callable
def get_locations_links(**p):
  return [
    # makeMarkdownLink(location["CountyName"], location["NormalizedName"])
    # f'({location["CountyName"]}, {APP_ORIGIN}/for/{location["NormalizedName"]})'
    (f'{location["CountyName"]}', f'{APP_ORIGIN}/for/{location["NormalizedName"]}')
    for location in app_tables.locations.search()
  ]
