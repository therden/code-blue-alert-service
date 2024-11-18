from ._anvil_designer import About_fourfiftyeightTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js


class About_fourfiftyeight(About_fourfiftyeightTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    # self.layout.rt_title.data["site_title"].content += "/about/fourfiftyeight"
