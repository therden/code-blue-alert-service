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
    # self.image_1.source = anvil.server.call("get_sample_graph")
    # self.plot_1.figure = anvil.server.call("make_nys_chloropleth")
    self.image_1.source = anvil.server.call("get_png_of_chloropleth")

  # def plot_1_click(self, points, **event_args):
  #   msg = f"Point: {points}"
  #   # alert(msg)

  # def plot_1_hover(self, points, **event_args):
  #   self.label_2.text = f"Point: {points}"

  # def plot_1_unhover(self, points, **event_args):
  #   self.label_2.text = f"Point: xxx\nxxx"
