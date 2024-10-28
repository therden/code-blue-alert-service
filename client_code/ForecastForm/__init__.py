from ._anvil_designer import ForecastFormTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime
from datetime import timedelta


class ForecastForm(ForecastFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.record = properties["location_record"]
    self.location = self.record["NormalizedName"]
    self.forecast_for_date = f'{self.record["NOAAupdate"]:%b %d}'
    self.generated_datetime = f'{self.record["DataRequested"]:%B %d, %I:%M %p}'
    self.forecast_time = f'{self.record["NOAAupdate"]:%I:%M %p}'
    self.updateForm()

  def set_alert_text_and_style(self):
    if self.record["CodeBlueQualified"]:
      in_effect = "IS"
      self.rt_header.content += f'\n### This Alert will remain in effect until **either** 7 AM on {(self.record["NOAAupdate"] + timedelta(days=1)):%b %d} **or** when Wind Chill temperatures exceed 32˚F -- whichever is *later*.'
      rt_background = "theme:Primary Container"
    else:
      in_effect = "IS NOT"
      rt_background = "lemonchiffon"
    self.rt_header.data = {
      "in_effect": in_effect,
      "for_date": self.forecast_for_date,
    }
    self.rt_footer.content = f"Generated: {self.generated_datetime}\n  Source: {self.forecast_time} forecast, National Weather Service"
    self.rt_header.background = rt_background
    self.rt_footer.background = rt_background

  def updateForm(self):
    location = self.location
    record = self.record
    self.layout.rt_title.data.update({"site_title": f"codeblue.info/for/{location}"})
    self.image_1.source = record["LastGraph"]
    self.set_alert_text_and_style()
