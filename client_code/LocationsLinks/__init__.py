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

    # Any code you write here will run before the form opens.
    # self.rich_text_1.content = anvil.server.call('get_locations_list_links_string')
    links_data = anvil.server.call('get_locations_tuples')
    for this_link in links_data:
      # self.flow_panel_1.add_component(Label(text=thislink[1]))
      url = this_link[0]
      text = this_link[1]
      link = Link(url=url, text=text, foreground='white')
      self.flow_panel_1.add_component(link)
