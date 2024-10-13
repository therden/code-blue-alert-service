from ._anvil_designer import ForecastTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import timedelta
from datetime import datetime


class Forecast(ForecastTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.record = properties["location_record"]
    self.location = self.record["NormalizedName"]
    self.updateForm()

  def set_rt_background(self):
    if not self.record["CodeBlueQualified"]:
      rt_background = "lemonchiffon"
    else:
      rt_background = "theme:Primary Container"
    self.rt_headline.background = rt_background
    self.rt_footer.background = rt_background

  def build_headline(self):
    if not self.record["CodeBlueQualified"]:
      in_effect = "IS NOT"
    else:
      in_effect = "IS"
    forecast_start = f'{self.record["NOAAupdate"]:%b %d}'
    forecast_end = f'{(self.record["NOAAupdate"] + timedelta(days=1)):%b %d}'
    # forecast_for = f"{forecast_start:%b %d} - {forecast_end:%b %d}"
    noaa_forecast_datetime = self.record["NOAAupdate"]
    forecast_time = f"{noaa_forecast_datetime:%I:%M %p}"
    self.rt_headline.data = {
      "in_effect": in_effect,
      # "forecast_for_date": forecast_for,
      "forecast_for_date": forecast_start,
    }
    self.rt_footer.data = {
      "forecast_datetime": f'{self.record["NOAAupdate"]:%b %d %I:%M %p}',
      "forecast_until": forecast_end,
    }
  
  def set_rt_text(self):
    

  def updateForm(self):
    location = self.location
    record = self.record
    self.label_1.text = f"codeblue.info/for/{location}"
    self.set_rt_background()
    self.build_headline()
    self.image_1.source = record["LastGraph"]
    # lastDownload = record["DataRequested"].strftime("%Y-%m-%d %I:%M %p")
    # lastNOAAupdate = record["NOAAupdate"].strftime("%I:%M %p")
    # self.label_2.text = (
    #   f"Updated {lastDownload} (from NOAA's {lastNOAAupdate} forecast.)"
    # )

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    record = self.record
    anvil.server.call("updateForecast", record)
    anvil.server.call("updateForecastGraph", record)
    # anvil.server.call("updateForecast", record)
    self.updateForm()
