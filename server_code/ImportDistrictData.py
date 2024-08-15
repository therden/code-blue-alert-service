import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import pandas as pd
import anvil.tables as tables
from anvil.tables import app_tables

def import_excel_data(file):
  with open(data_files[file], "rb") as f:
    df = pd.read_excel(f)
    for d in df.to_dict(orient="records"):
      # d is now a dict of {columnname -> value} for this row
      # We use Python's **kwargs syntax to pass the whole dict as
      # keyword arguments
      app_tables.local_districts.add_row(**d)      

# import_excel_data("SocialServicesDistricts.xlsx")