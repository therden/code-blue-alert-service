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
    # self.statemap_img.source = statemap[0]
    forecast_dt = statemap[1]
    self.rich_text_1.data = {
      "forecast_for": f"{forecast_dt + days_delta:%B %d}",
      "which": forecast_text,
    }
    self.layout.content_panel.add_component(
      Image(
        source=statemap[0],
        display_mode="original_size",
        border="black",
        spacing_above="small",
        spacing_below="small",
      )
    )
    self.layout.content_panel.add_component(
      Label(align="Left", text=f"Forecast generated: {forecast_dt:%B %d, %I:%M %p}")
    )
