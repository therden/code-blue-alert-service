from ._anvil_designer import xForecastTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import timedelta
from datetime import datetime
# from ..Footer import Footer


class xForecast(xForecastTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.record = properties["location_record"]
    self.location = self.record["NormalizedName"]
    # self.content_panel.add_component(Footer())
    self.updateForm()

  def set_alert_text_and_style(self):
    if self.record["CodeBlueQualified"]:
      in_effect = "IS"
      # self.rt_footer.content += f'\n### This Alert will remain in effect until **either** 7 AM on {(self.record["NOAAupdate"] + timedelta(days=1)):%b %d} **or** when Wind Chill temperatures exceed 32˚F -- whichever is *later*.'
      self.rt_header.content += f'\n### This Alert will remain in effect until **either** 7 AM on {(self.record["NOAAupdate"] + timedelta(days=1)):%b %d} **or** when Wind Chill temperatures exceed 32˚F -- whichever is *later*.'
      rt_background = "theme:Primary Container"
    else:
      in_effect = "IS NOT"
      rt_background = "lemonchiffon"
    self.rt_footer.data = {
      "forecast_datetime": f'{self.record["NOAAupdate"]:%I:%M %p on %b %d}',
      # "until_date": f'{(self.record["NOAAupdate"] + timedelta(days=1)):%b %d}',
    }
    self.rt_header.data = {
      "in_effect": in_effect,
      "for_date": f'{self.record["NOAAupdate"]:%b %d}',
    }
    self.rt_header.background = rt_background
    self.rt_footer.background = rt_background

  def updateForm(self):
    location = self.location
    record = self.record
    self.label_1.text = f"codeblue.info/for/{location}"
    self.image_1.source = record["LastGraph"]
    self.set_alert_text_and_style()

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    record = self.record
    anvil.server.call("updateForecast", record)
    anvil.server.call("updateForecastGraph", record)
    self.updateForm()
