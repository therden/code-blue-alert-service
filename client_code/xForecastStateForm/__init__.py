from ._anvil_designer import xForecastStateFormTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta


class xForecastStateForm(xForecastStateFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.update_form_data()
    self.timer_1.interval = 720  # 12 minutes standard (changed for map updates)
    self.page_autorefreshed = False

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
    alert("testing color")
    if current_hour in (4, 16) and current_min >= 45:
      self.timer_1.interval = 60  # 1 minute -- exception (when map update is nearing)
      self.page_autorefreshed = False
    # if current_hour in (5, 17) and current_min >= 0 and not self.page_autorefreshed:
    if current_hour in (5, 17) and current_min >= 0 and not self.page_autorefreshed:
      self.timer_1.interval = 720  # 12 minutes standard (changed for map updates)
      self.update_form_data()
      self.page_autorefreshed = True
      Notification("This page has been updated!", title="Alert!", style="info")
    if current_hour in (6, 18):
      self.page_autorefreshed = False
