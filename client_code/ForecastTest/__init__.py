from ._anvil_designer import ForecastTestTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ForecastTest(ForecastTestTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.button_1_click()

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    # self.image_1.source = anvil.server.call("test_plot")
    self.image_1.source = anvil.server.call("get_sample_graph")
