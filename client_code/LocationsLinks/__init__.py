from ._anvil_designer import LocationsLinksTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class LocationsLinks(LocationsLinksTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # self.rich_text_1.content = anvil.server.call('get_locations_list_links_string')
    links = anvil.server.call('get_locations_links_list')
    for link in links:
      self.flow_panel_1.add_component(Label(text=link))
      self.flow_panel_1.add_component(Label(text=link))

    # Any code you write here will run before the form opens.

