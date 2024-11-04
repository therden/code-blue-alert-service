from ._anvil_designer import LayoutTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .Footer import Footer

# import datetime
import anvil.js


class Layout(LayoutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    logo = Image(
      source="_/theme/codeblueinfo_512x512.png",
      height=44,
      spacing_above="None",
      spacing_below="None",
    )
    rt_title = RichText(
      content="# codeblue.info",
      spacing_above="None",
      spacing_below="None",
    )
    self.rt_title.data = {"site_logo": logo, "site_title": rt_title}
    self.add_component(Footer())
    # current_year = datetime.datetime.today().year
    # self.rt_form_footer_left.data = {"current_year": current_year}
    # change color of link on mouseover/mouseoff
    dom_node = anvil.js.get_dom_node(self.link_1)
    dom_node.addEventListener("mouseover", self.mouseover_event)
    dom_node.addEventListener("mouseout", self.mouseoff_event)

  def mouseover_event(self, sender, **event_args):
    self.link_1.foreground = "whitesmoke"

  def mouseoff_event(self, sender, **event_args):
    self.link_1.foreground = "dimgray"
