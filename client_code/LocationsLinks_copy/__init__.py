from ._anvil_designer import LocationsLinks_copyTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class LocationsLinks_copy(LocationsLinks_copyTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.rich_text_1.content = anvil.server.call("get_locations_list")

    # Any code you write here will run before the form opens.
