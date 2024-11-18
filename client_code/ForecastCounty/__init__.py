from ._anvil_designer import ForecastCountyTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime
from datetime import timedelta


class ForecastCounty(ForecastCountyTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.record = properties["location_record"]
    # self.location = self.record["NormalizedName"]
    self.location = self.record["CountyName"]
    self.forecast_for_date = f'{self.record["NOAAupdate"]:%b %d}'
    self.generated_datetime = f'{self.record["DataRequested"]:%B %d, %I:%M %p}'
    self.forecast_time = f'{self.record["NOAAupdate"]:%I:%M %p}'
    self.updateForm()

  def set_alert_text_and_style(self):
    if self.record["CodeBlueQualified"]:
      rt_background = "theme:Primary Container"
      if self.record["StrongForecastConsent"]:
        self.rt_header.content = f"### Windchill temps for the {self.forecast_for_date} overnight WILL be low enough to trigger a Code Blue alert."
      else:
        self.rt_header.content = f"### A Code Blue Alert **IS** in effect for the {self.forecast_for_date} overnight."
        self.rt_header.content += f'\n### This Alert will remain in effect until **either** 7 AM on {(self.record["NOAAupdate"] + timedelta(days=1)):%b %d} **or** when Wind Chill temperatures exceed 32˚F -- whichever is *later*.'
    else:  # wind chill temps insufficient to trigger Code Blue Alert
      rt_background = "lemonchiffon"
      if self.record["StrongForecastConsent"]:
        self.rt_header.content = f"### A Code Blue Alert is **NOT** in effect for the {self.forecast_for_date} overnight."
      else:
        self.rt_header.content = f"### Windchill temps for the {self.forecast_for_date} overnight will **NOT** be sufficient to trigger a Code Blue alert."
    self.rt_header.content = (
      f"## **{self.location} County** status\n" + self.rt_header.content
    )
    self.rt_footer.content = f"Generated: {self.generated_datetime}\n  Source: {self.forecast_time} forecast, National Weather Service"
    self.rt_header.background = rt_background
    self.rt_footer.background = rt_background

  def updateForm(self):
    # location = self.location
    # self.layout.rt_title.data.update({"site_title": f"codeblue.info/for/{location}"})
    record = self.record
    self.image_1.source = record["LastGraph"]
    self.set_alert_text_and_style()
