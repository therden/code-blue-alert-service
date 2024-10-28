from ._anvil_designer import LocationsLinksFlowTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class LocationsLinksFlow(LocationsLinksFlowTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    for thisLink in anvil.server.call("get_locations_links"):
      t, u = thisLink
      self.flow_panel_1.add_component(
        Link(text=thisLink[0], url=thisLink[1], foreground="#507C9E")
      )

  Link()

