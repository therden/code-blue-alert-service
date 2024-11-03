import anvil.email
import anvil.users
import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import json
import pandas as pd
import plotly.express as px


@anvil.server.callable
def make_nys_chloropleth():
  with open(data_files["fips_nys_counties.json"], "rt") as fileobject:
    counties = json.load(fileobject)
  # df = pd.read_csv("/Users/tomhe/Repos/codeblue/fips_NYScounties_CodeBlue2.csv",
  #                   dtype={"fips": str})
  df = pd.read_csv(data_files["fips_NYScounties_CodeBlue2.csv"], dtype={"fips": str})
  # df = df[(df["fips"]>"35999")&(df["fips"]<"37000")]

  fig = px.choropleth(
    df,
    geojson=counties,
    locations="fips",
    color="codeblue",
    color_discrete_sequence=["cornflowerblue", "lemonchiffon"],
    # category_orders={"continent": ["True", "False"]},
    hover_data={"fips": False, "county": True, "codeblue": True},
  )
  fig.update_geos(fitbounds="locations")
  fig.show()


# from anvil.files import data_files
# import anvil.server
# import json
# import pandas as pd
# import plotly.express as px
# df = pd.read_csv(data_files["fips_NYScounties_CodeBlue2.csv"], dtype={"fips": str})
