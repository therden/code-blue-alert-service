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
    self.record = properties["location_record"]
    self.location = self.record["NormalizedName"]
    self.updateForm()

  def updateForm(self):
    location = self.location
    record = self.record
    self.label_1.text = f"codeblue.info/for/{location}"
    self.image_1.source = record["LastGraph"]
    lastDownload = record["DataRequested"].strftime("%Y-%m-%d %I:%M %p")
    lastNOAAupdate = record["NOAAupdate"].strftime("%I:%M %p")
    self.label_2.text = f"Updated {lastDownload} (from {lastNOAAupdate} NOAA update.)"

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    record = self.record
    anvil.server.call("updateForecast", record)
    anvil.server.call("updateForecastGraph", record)
    # anvil.server.call("updateForecast", record)
    self.updateForm()
