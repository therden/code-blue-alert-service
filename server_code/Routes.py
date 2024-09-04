import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

APP_ORIGIN = anvil.server.get_app_origin()


@anvil.server.route('/forecast/test')
def forecast_test(**p):
  return anvil.server.FormResponse('ForecastTest')


def makeLink(URLstub, linkText):
  global APP_ORIGIN
  return f'<p><a href="{APP_ORIGIN}/forecast/{URLstub}">{linkText}</a></p>'


@anvil.server.callable
def get_locations_list():
  # return [location['CountyName'] for location in app_tables.locations.search()]
  return '\n'.join(
    [
      makeLink(location['NormalizedName'], location['CountyName'])
      for location in app_tables.locations.search()
    ]
  )


@anvil.server.route('/forecast/list')
def locations_list(**p):
  return anvil.server.FormResponse('LocationsLinks')


@anvil.server.route('/forecast/:location')
def serve_location_page(name, **p):
  location = app_tables.locations.get(NormalizedName=location)
  if location:
    return anvil.server.FormResponse('Forecast', location=location)
    # return anvil.server.FormResponse('Forecast')
  else:
    return anvil.server.HttpResponse(404, f'Location '{location}' not supported')
