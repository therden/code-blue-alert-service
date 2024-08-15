import requests
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

@anvil.server.callable

def get_one_coordinate_pair(district_record):
  # get data from record
  street = district_record["StreetLocation"]
  city = district_record["City"]
  state = "NY"
  zip = district_record["Zip"]

  # construct URL for Census Bureau query
  website = "https://geocoding.geo.census.gov/geocoder/locations/"
  address = f"{street}+{city},+{state}+{zip}"
  parameters = f"onelineaddress?address={address}&benchmark=4&format=json"
  URL = f"{website}{parameters}"

  # query Census Bureau
  response_dict = requests.get(URL).json()

  # extract and return coordinate pair
  longitude = response_dict['result']['addressMatches'][0]['coordinates']['x']
  latitude = response_dict['result']['addressMatches'][0]['coordinates']['y']
  return longitude, latitude
  
