from ._anvil_designer import About_fourfiftyeightTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class About_fourfiftyeight(About_fourfiftyeightTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # rt_data = {'logo': Image(source=BlobMedia("image/png", "_/theme/458-final-grayscale.png"))}
    # self.rich_text_1.content = rt_data
    # Any code you write here will run before the form opens.
