from ._anvil_designer import test_embed_formTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js.window import jQuery
from anvil.js import get_dom_node


class test_embed_form(test_embed_formTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    iframe = jQuery("<iframe width='100%' height='800px'>").attr(
      "src", "https://offbeat-hoarse-diet.anvil.app/"
    )
    iframe.appendTo(get_dom_node(self.content_panel))
