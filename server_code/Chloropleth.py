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
import plotly.io as pio


@anvil.server.callable
def make_nys_chloropleth():
  with open(data_files["fips_nys_counties.json"], "rt") as fileobject:
    counties = json.load(fileobject)
  df = pd.read_csv(data_files["fips_NYScounties_CodeBlue3.csv"], dtype={"fips": str})
  fig = px.choropleth(
    df,
    geojson=counties,
    locations="fips",
    color="codeblue",
    color_discrete_sequence=["cornflowerblue", "lemonchiffon"],
    hover_data={"fips": False, "county": True, "codeblue": True},
  )
  fig.update_geos(
    fitbounds="locations",
    visible=False,
  )
  fig.update_layout(showlegend=False)
  return fig


@anvil.server.callable
def convert_px_chloropleth_to_png(fig):
  png = fig.to_image()
  return png


@anvil.server.callable
def get_png_of_chloropleth():
  fig = make_nys_chloropleth()
  return convert_px_chloropleth_to_png(fig)


@anvil.server.callable
def save_NYS_png_to_table(img=None, record_name=None):
  blob = anvil.BlobMedia(content_type="bytes", content=[img])
  record = app_tables.media.get(Name=record_name)
  if record and blob:
    record["Blob"] = blob
  else:
    raise ("Borked!")


# from anvil.files import data_files
# import anvil.server
# import json
# import pandas as pd
# import plotly.express as px
# df = pd.read_csv(data_files["fips_NYScounties_CodeBlue3.csv"], dtype={"fips": str})
