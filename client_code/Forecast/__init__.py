from ._anvil_designer import ForecastTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Forecast(ForecastTemplate, location):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    ## Any code you write here will run before the form opens.
    # record = app_tables.locations.get(NormalizedName="tompkins")
    # self.image_1.source = record["LastGraph"]
    self.image_1.source = location["LastGraph"]

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    # record = app_tables.locations.get(NormalizedName="tompkins")
    # self.image_1.source = record["LastGraph"]
    self.image_1.source = location["LastGraph"]
    # self.image_1.source = anvil.server.call("test_plot")
