from ._anvil_designer import ForecastTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Forecast(ForecastTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    ## Any code you write here will run before the form opens.
    # location_record = app_tables.locations.get(NormalizedName="tompkins")
    # self.image_1.source = location_record["LastGraph"]
    location_record = properties["location_record"]
    self.image_1.source = location_record["LastGraph"]

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    location_record = app_tables.locations.get(NormalizedName="tompkins")
    self.image_1.source = location_record["LastGraph"]
    # self.image_1.source = location["LastGraph"]
    # self.image_1.source = anvil.server.call("test_plot")
