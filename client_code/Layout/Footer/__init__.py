from ._anvil_designer import FooterTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime
import anvil.js


class Footer(FooterTemplate):
  def __init__(self, **properties):
    current_year = datetime.datetime.today().year
    icon = anvil.Image(
      source="_/theme/458-final-grayscale.png",
      height=10,
    )
    # self.rt_footer_left.data = {"current_year": current_year, "spaces": "   "}
    self.rt_footer_left.data = {"current_year": current_year, "icon": icon}
    self.init_components(**properties)

    # change color of link on mouseover/mouseoff
    dom_node = anvil.js.get_dom_node(self.link_1)
    dom_node.addEventListener("mouseover", self.mouseover_event)
    dom_node.addEventListener("mouseout", self.mouseoff_event)

  def mouseover_event(self, sender, **event_args):
    self.link_1.foreground = "whitesmoke"

  def mouseoff_event(self, sender, **event_args):
    self.link_1.foreground = "black"
