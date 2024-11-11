from ._anvil_designer import NYSForecastTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta


class NYSForecast(NYSForecastTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.update_form_data()

  def update_form_data(self, **event_args):
    current_hour = datetime.now().hour
    if 5 < current_hour < 17:
      row_name = "NYS_day"
      forecast_text = "Daytime"
      days_delta = timedelta(days=1)
    else:
      row_name = "NYS_night"
      forecast_text = "Overnight"
      days_delta = timedelta(days=0)
    # record = anvil.server.call("get_statemap_row", row_name)
    # self.statemap_img.source = record['Blob']
    statemap = anvil.server.call("get_statemap", row_name)
    self.statemap_img.source = statemap[0]
    forecast_dt = statemap[1]
    self.header_rt.data = {
      "forecast_for": f"{forecast_dt + days_delta:%B %d}",
      "which": forecast_text,
    }
    self.generated_at_lbl.text = f"Forecast generated: {forecast_dt:%B %d, %I:%M %p}"

  def timer_1_tick(self, **event_args):
    current_hour = datetime.now().hour
    current_min = datetime.now().minute
    if current_hour in (4, 16) and current_min >= 45:
      self.timer_1.interval = 0.75
    if current_hour in (5, 17) and current_min == 0:
      self.update_form_data()
      self.timer_1.interval = 15
