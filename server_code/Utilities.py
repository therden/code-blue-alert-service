
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def edit_locations():
  for location in app_tables.locations.search():
    location['NormalizedName'] = location['CountyName'].lower()
