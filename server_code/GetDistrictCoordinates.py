import requests
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
def get_districts():
  # Get a list of entries from the Data Table, sorted by 'created' column, in descending order
  return app_tables.districts.search()


@anvil.server.callable
def get_coordinate_pair_from_census_bureau(district_record):
  STATE = "NY"
  # get data from record
  street = district_record["StreetLocation"]
  city = district_record["City"]
  zip = district_record["Zip"]

  # construct URL for Census Bureau query
  website = "https://geocoding.geo.census.gov/geocoder/locations/"
  address = f"{street}+{city},+{STATE}+{zip}"
  parameters = f"onelineaddress?address={address}&benchmark=4&format=json"
  URL = f"{website}{parameters}"

  # query Census Bureau
  response_dict = requests.get(URL).json()
  print(response_dict)

  # extract and return coordinate pair
  if response_dict["result"]["addressMatches"]:
    longitude = round(response_dict["result"]["addressMatches"][0]["coordinates"]["x"], 4)
    latitude = round(response_dict["result"]["addressMatches"][0]["coordinates"]["y"], 4)
    return longitude, latitude
  else:
    anvil.alert(f"Census Bureau API returned no coordinates for {address}")
    return False


@anvil.server.callable
def update_all_coordinates():
  for district_row in get_districts():
    coordinates = get_coordinate_pair_from_census_bureau(district_row)
    if coordinates:
      district_row["Longitude"], district_row["Latitude"] = coordinates[0], coordinates[1]
 
