import anvil.users
import pandas as pd
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
from anvil.tables import app_tables


def import_excel_data(file):
  with open(data_files[file], 'rb') as f:
    df = pd.read_excel(f)
    for d in df.to_dict(orient='records'):
      # d is now a dict of {columnname -> value} for this row
      # We use Python's **kwargs syntax to pass the whole dict as
      # keyword arguments
      app_tables.local_districts.add_row(**d)

      
# NOTE:  Had to 'pip install openpyxl' for the above to work
# NOTE:  SocialServicesDistricts.xlsx was previously uploaded as a 'data file'
# NOTE:  to run, uncomment the following line and re-start server
# import_excel_data('SocialServicesDistricts.xlsx')