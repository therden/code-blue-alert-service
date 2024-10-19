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
    self.rt_content.data = {"html_error_code": '', "html_error_text": '', "additional_text": 'line 1\nline2'}

    # Any code you write here will run before the form opens.
