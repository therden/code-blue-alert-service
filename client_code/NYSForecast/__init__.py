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
    self.display_appropriate_State_map()

  def display_appropriate_State_map(self, **event_args):
    if datetime.now().hour < 17:
      row_name = "NYS_nextday_graph"
    else:
      row_name = "NYS_overnight_graph"
    record = anvil.server.call("get_media_row", row_name)
    self.state_map_img.source = record["Blob"]
    # self.forecast_for_lbl.text = record["Updated"] + timedelta(days=1)
    # self.generated_at_lbl.text = record["Updated"]
