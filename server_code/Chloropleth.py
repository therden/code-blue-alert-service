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
from datetime import datetime


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
  svg = fig.to_image(format="png", width=900)
  return png


@anvil.server.callable
def convert_px_chloropleth_to_svg(fig):
  svg = fig.to_image(format="svg", width=900)
  return svg


@anvil.server.callable
def get_png_of_chloropleth():
  fig = make_nys_chloropleth()
  png = convert_px_chloropleth_to_png(fig)
  return png


@anvil.server.callable
def save_NYS_png_to_table(img=None, record_name=None):
  blob = anvil.BlobMedia(content_type="image/png", content=img)
  record = app_tables.media.get(Name=record_name)
  if record and blob:
    record["Blob"] = blob
  else:
    raise ("Borked!")


@anvil.server.callable
def make_and_save_NYS_chloropleth_to_table(rec_name=None):
  fig = make_nys_chloropleth()
  # map_image = fig.to_image(format="svg", width=900)
  # blob = anvil.BlobMedia(
  #   content_type="image/svg", content=map_image, name=f"{rec_name}.svg"
  # )
  map_image = fig.to_image(format="png", width=900)
  blob = anvil.BlobMedia(
    content_type="image/png", content=map_image, name=f"{rec_name}.png"
  )
  rec = app_tables.media.get(Name=rec_name)
  rec["Blob"] = blob


@anvil.server.callable
def write_text_to_file(text):
  with data_files.editing("my_text_file.txt") as path:
    # path is now a string path on the filesystem. We can write to it with normal Python tools.
    # For example:
    with open(path, "w+") as f:
      f.write(text)


# from anvil.files import data_files
# import anvil.server
# import json
# import pandas as pd
# import plotly.express as px
# df = pd.read_csv(data_files["fips_NYScounties_CodeBlue3.csv"], dtype={"fips": str})
