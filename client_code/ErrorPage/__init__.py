from ._anvil_designer import ErrorPageTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


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
      "suggeted_url": Link(text=suggested_url, url=suggested_url),
    }

    # Any code you write here will run before the form opens.
