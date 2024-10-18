from ._anvil_designer import FooterTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime
import anvil.js


class Footer(FooterTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    current_year = datetime.datetime.today().year
    self.rt_footer_left.data = {"current_year": current_year}
    self.init_components(**properties)
    dom_node = anvil.js.get_dom_node(self.link_1)
    dom_node.addEventListener("mouseover", self.mouseover_event)
    dom_node.addEventListener("mouseout", self.mouseoff_event)
    # Any code you write here will run before the form opens.

  def mouseover_event(self, sender, **event_args):
    self.link_1.foreground = "whitesmoke"

  def mouseoff_event(self, sender, **event_args):
    self.link_1.foreground = "dimgray"
