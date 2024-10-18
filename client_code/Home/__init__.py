from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js

class Home(HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # # Any code you write here will run before the form opens.
    # populate locations dropdown
    # item_list = []
    # for row in app_tables.locations.search():
    #   item_list.append((row["CountyName"], row))
    # item_list = [(row["CountyName"], row) for row in app_tables.locations.search()]
    # self.drop_down_1.items = item_list
