from ._anvil_designer import Layout_copyTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .Footer import Footer
import anvil.js


class Layout_copy(Layout_copyTemplate):
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
    # self.content_panel.add_component(Footer)
    self.content_panel.add_component(Footer())
    # Any code you write here will run before the form opens.
