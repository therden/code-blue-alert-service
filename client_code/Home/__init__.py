from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..PlaceholderText import PlaceholderText
from ..Footer import Footer


class Home(HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.content_panel.add_component(PlaceholderText())
    self.content_panel.add_component(Footer())

    # populate locations dropdown
    item_list = []
    for row in app_tables.locations.search():
      item_list.append((row["CountyName"], row))
    self.drop_down_1.items = item_list

    # Any code you write here will run before the form opens.

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    # self.image_1.source = anvil.server.call('getForecastGraph')
    self.image_1.source = anvil.server.call("test_plot")
