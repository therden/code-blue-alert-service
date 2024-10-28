from ._anvil_designer import LocationsLinksListTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class LocationsLinksList(LocationsLinksListTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.rich_text_1.content = anvil.server.call('get_locations_links_list')

