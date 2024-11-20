import anvil.email
import anvil.users
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server



@anvil.server.callable
def say_hello(name):
  print("Hello, " + name + "!")
  return 42

async def get_server_data(cuid, collection_names:[]):
  pass

async def get_server_data2(cuid, collection_names=[]):
  pass
  