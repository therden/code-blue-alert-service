from ._anvil_designer import FooterTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime


class Footer(FooterTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    current_year = datetime.datetime.today().year
    self.rt_footer_left.data = {"current_year": current_year}
    self.rt_footer_left.foreground = "white"
    self.link_1.foreground = "white"
    # self.link_1.add_component(
    #   Image(source="_/theme/458-final-grayscale.png", height=15)
    # )
    self.init_components(**properties)

  # Any code you write here will run before the form opens.