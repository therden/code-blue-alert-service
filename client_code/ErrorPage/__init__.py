from ._anvil_designer import ErrorPageTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js import window


class ErrorPage(ErrorPageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    html_error_code = properties["HTMLerrorCode"] or "unknown"
    html_error_message = properties["HTMLerrorText"] or "unknown"
    additional_text = properties["additionalText"] or ""
    suggested_url = properties["suggestedURL"] or ""
    # Link(text=suggested_url, url=suggested_url)
    self.rt_content.data = {
      "html_error_code": html_error_code,
      "html_error_message": html_error_message,
      "additional_text": additional_text,
      # "suggested_url": suggested_url,
      # "suggeted_url": Link(text=suggested_url, url=suggested_url),
    }
    self.link_1.text = suggested_url
    self.link_1.url = suggested_url
    dom_node = anvil.js.get_dom_node(self.link_1)
    dom_node.addEventListener("mouseover", self.mouseover_event)
    dom_node.addEventListener("mouseout", self.mouseoff_event)
    # Any code you write here will run before the form opens.

  def mouseover_event(self, sender, **event_args):
    self.link_1.foreground = "lightgray"

  def mouseoff_event(self, sender, **event_args):
    self.link_1.foreground = "dimgray"

  def link_1_click(self, **event_args):
    window.location = self.link_1.url
