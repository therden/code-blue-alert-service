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
from datetime import datetime
from .Forecasts import graphForecast

APP_ORIGIN = anvil.server.get_app_origin()


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
  nextForecast = datetime.strptime("Oct 21 2024  5:00PM", "%b %d %Y %I:%M%p")
  listOfFieldValueTuples = [
    ("NextPMforecast", nextForecast),
    ("StrongForecastConsent", False),
    # ("Overnight", None),
    # ("NextDay", None),
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
  plt.title("Wind Chill Forecast")
  ax.vlines([0.75, 1.5, 2.25, 3], ymin=min(y), ymax=max(y), colors="blue", ls="-")
  plt.plot(x, y, "crimson")

  # Return this plot as a PNG image in a Media object
  return anvil.mpl_util.plot_image()


@anvil.server.callable
def get_sample_graph():
  # row = app_tables.locations.get(CountyName="Suffolk")
  row = app_tables.locations.get(CountyName="Tompkins")
  return graphForecast(row["RawData"], 1, 0)


@anvil.server.callable
def get_locations_links(**p):
  return [
    (f'{location["CountyName"]}', f'{APP_ORIGIN}/for/{location["NormalizedName"]}')
    for location in app_tables.locations.search()
  ]


@anvil.server.callable
def log_event(description='"log_event" called without a "Description"'):
  app_tables.event_log.add_row(event_datetime=datetime.now(), description=description)
