from ._anvil_designer import ForecastStateTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta


class ForecastState(ForecastStateTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.initial_display = True
    self.current_display = ""
    self.timer_1_tick()

  def update_is_needed(self):
    if 5 < datetime.now().hour < 17:
      if self.current_display != "Daytime":
        self.current_display = "Daytime"
        return True
    elif self.current_display != "Overnight":
      self.current_display = "Overnight"
      return True
    else:
      return False

  def update_form(self):
    if self.current_display == "Daytime":
      row_name = "NYS_day"
      days_delta = timedelta(days=1)
    else:
      row_name = "NYS_night"
      days_delta = timedelta(days=0)
    statemap = anvil.server.call("get_statemap", row_name)
    forecast_dt = statemap[1]
    forecast_for = forecast_dt + days_delta
    self.rich_text_1.data = {
      "forecast_for": f"{forecast_for:%B %d}",
      "which": self.current_display,
    }
    self.image_1.source = statemap[0]
    self.label_1.text = f"Forecast generated: {forecast_dt:%B %d, %I:%M %p}"
    if self.initial_display:
      self.initial_display = False
    else:
      alert(f"This page was updated at {datetime.now():%B %d, %I:%M:%S %p}")

  def timer_1_tick(self, **event_args):
    if self.update_is_needed():
      self.update_form()
