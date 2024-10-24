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


@anvil.server.route("/aboutfourfiftyeight")
@anvil.server.route("/about/fourfiftyeight")
def about_fourfiftyeight_form(**p):
  return anvil.server.FormResponse("About_fourfiftyeight")


@anvil.server.route("/aboutcodeblue")
@anvil.server.route("/about_code_blue")
@anvil.server.route("/about/codeblue")
@anvil.server.route("/about/code_blue")
def about_code_blue_form(**p):
  return anvil.server.FormResponse("About_Code_Blue")


@anvil.server.route("/aboutwindchill")
@anvil.server.route("/about_wind_chill")
@anvil.server.route("/about/windchill")
@anvil.server.route("/about/wind_chill")
def about_wind_chill_form(**p):
  return anvil.server.FormResponse("About_wind_chill")


@anvil.server.route("/aboutthissite")
@anvil.server.route("/about_this_site")
@anvil.server.route("/about/thissite")
@anvil.server.route("/about/this_site")
def about_this_site_form(**p):
  return anvil.server.FormResponse("About_this_site")


# @anvil.server.route("/locations")
# def locations_list_form(**p):
#   return anvil.server.FormResponse("LocationsLinksList")


@anvil.server.route("/for/test")
def forecast_test(**p):
  return anvil.server.FormResponse("ForecastTest")


@anvil.server.route("/for/:location_name")
def serve_location_page(location_name, **p):
  print(location_name)
  location_record = app_tables.locations.get(NormalizedName=location_name)
  if location_record:
    return anvil.server.FormResponse("ForecastForm", location_record=location_record)
  else:
    HTMLerrorCode = 404
    HTMLerrorText = "'Not Found'"
    additionalText = f'Location "{location_name}" not supported.'
    additionalText += "\nValid locations are listed at the following link."
    suggestedURL = f"{APP_ORIGIN}/locations"
    # return anvil.server.HttpResponse(responseCode, responseText)
    return anvil.server.FormResponse(
      "ErrorPage",
      HTMLerrorCode=HTMLerrorCode,  # required
      HTMLerrorText=HTMLerrorText,  # required
      additionalText=additionalText,  # optional
      suggestedURL=suggestedURL,  # optional
    )


@anvil.server.route("/locations")
@anvil.server.route("/for")
def locations_links_form(**p):
  return anvil.server.FormResponse("LocationsLinksFlow")


@anvil.server.route("/embed_test", cross_site_session=True)
def embed_test(**p):
  return anvil.server.FormResponse("test_embed_form")
