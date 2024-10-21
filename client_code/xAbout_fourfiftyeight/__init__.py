from ._anvil_designer import xAbout_fourfiftyeightTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class xAbout_fourfiftyeight(xAbout_fourfiftyeightTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.rt_sidepanel_logo.data = {
      "458_logo": Image(source="_/theme/458-final-grayscale.png", height=150)
    }
    # Image(source=img, height=50), slot='slot0', width=50

    # self.rt_sidepanel.data = {"458_logo": "logo"}
    # Any code you write here will run before the form opens.
