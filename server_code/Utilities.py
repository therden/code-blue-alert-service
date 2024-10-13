import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import matplotlib.pyplot as plt
from matplotlib.dates import ConciseDateFormatter
import matplotlib.ticker as ticker
import anvil.mpl_util
import numpy as np
import Forecasts


@anvil.server.callable
def updateFields(rowObject, tupleList):
  for each in tupleList:
    rowObject[each[0]] = each[1]


@anvil.server.callable
def copyCurrentLocationsDataToDaily():
  location_rows = app_tables.locations.search()
  # each = location_rows[1]
  for each in location_rows:
    app_tables.daily_forecasts.add_row(
      NOAAupdate=each["NOAAupdate"],
      RawData=each["RawData"],
      DataRequested=each["DataRequested"],
      locality=each,
      DateOfForecast=each["DataRequested"].date(),
    )


@anvil.server.callable
def edit_locations():
  listOfFieldValueTuples = [
    ("DataRequested", None),
    ("NOAAupdate", None),
    ("RawData", None),
  ]
  for location in app_tables.locations.search():
    updateFields(location, listOfFieldValueTuples)


@anvil.server.callable
def test_plot():
  # Make a nice wiggle
  x = [0, 1, 2, 3, 4]
  y = [3.3, 7.3, 2.7, 5, 3.7]

  # Plot it in the normal Matplotlib way
  fig, ax = plt.subplots()
  plt.xlabel("Hours")
  plt.ylabel("Fahrenheit")
  plt.title(f"Wind Chill Forecast")
  ax.vlines([0.75, 1.5, 2.25, 3], ymin=min(y), ymax=max(y), colors="blue", ls="-")
  plt.plot(x, y, "crimson")

  # Return this plot as a PNG image in a Media object
  return anvil.mpl_util.plot_image()


@anvil.server.callable
def get_sample_graph():
  row = app_tables.locations.search()[0]
  # Forecasts.graphForecast(row["RawData"], 1, 0)
  anvil.server.call("graphForecast", row["RawData"], 1, 0)
