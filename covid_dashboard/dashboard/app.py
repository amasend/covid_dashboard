from datetime import datetime as dt
from typing import List
import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *

sys.path.append('../..')
from covid_dashboard.managers.data_manager import DataManager

# initialize data manager
data_manager = DataManager()

# initialize dash server
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.Img(
                            className="logo", src=app.get_asset_url("covid.png")
                        ),
                        html.H2("COVID-19 DATA"),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        dcc.Dropdown(
                                            id="world-dropdown",
                                            options=[
                                                {"label": 'Total Confirmed', "value": 'TotalConfirmed'},
                                                {"label": 'New Confirmed', "value": 'NewConfirmed'},
                                                {"label": 'Total Recovered', "value": 'TotalRecovered'},
                                                {"label": 'New Recovered', "value": 'NewRecovered'},
                                                {"label": 'Total Deaths', "value": 'TotalDeaths'},
                                                {"label": 'New Deaths', "value": 'NewDeaths'},
                                            ],
                                            placeholder="Select world data for heat-map",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.P(
                            """
                            Select a start date.
                            """
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    min_date_allowed=dt(2020, 1, 22),
                                    max_date_allowed=dt.now(),
                                    initial_visible_month=dt(2020, 1, 22),
                                    date=dt(2020, 1, 22).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        html.P(
                            """
                            Select a country to show (default is POLAND).
                            """
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="location-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in data_manager.locations
                                            ],
                                            placeholder="Select a location",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.P(
                            """
                            Select a country to compare with.
                            """
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="location-dropdown2",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in data_manager.locations
                                            ],
                                            placeholder="Select a location to compare",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.P(
                            """
                            Select a data transformation type, logarithmic is 
                            better when you want to compare big and small countries together. 
                            Percent - 100% is always \"Confirmed Cases\" on that day.
                            """
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        dcc.Dropdown(
                                            id="type-dropdown",
                                            options=[
                                                {"label": 'linear', "value": 'linear'},
                                                {"label": 'log', "value": 'log'},
                                                {"label": 'percent', "value": 'percent'},
                                            ],
                                            placeholder="Select a graph type",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.P(
                            """
                            Select a type of the bar graph. 
                            \"diff\" - shows difference between particular day and one before, 
                            \"diff-in-%\" - shows the same, but in percentage
                            """
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        dcc.Dropdown(
                                            id="diff-type-dropdown",
                                            options=[
                                                {"label": 'diff', "value": 'diff'},
                                                {"label": 'diff-in-%', "value": 'diff-in-%'}
                                            ],
                                            placeholder="Daily difference type (bar graph)",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.P(
                            """
                            Select a number of cases to start plot with. This overrides the date property.
                            """
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        dcc.Input(
                                            id="number-of-cases",
                                            type="number",
                                            placeholder="Starting number of cases",
                                            min=100, max=1000, step=100,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        dcc.Markdown(
                            children=[
                                "Source: [covid19api.com](https://documenter.getpostman.com/view/10808728/SzS8rjbc?version=latest)"
                            ]
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="map-graph"),
                        html.Div(
                            id="middle-text",
                            className="text-padding",
                            children=[
                                f"Poland graph of the Confirmed/Recovered/Deaths cases."
                            ],
                        ),
                        dcc.Graph(id="line-graph")
                    ],
                ),
            ],
        )
    ]
)


@app.callback(
    Output("middle-text", "children"),
    [
        Input("location-dropdown", "value"),
        Input("location-dropdown2", "value"),
    ],
)
def update_middle_text(selected_location: str, selected_location2: str) -> List[str]:
    """
    Update text between map and graph.
    Only trigger when any of the locations are changed by the user.

    Parameters
    ----------
    selected_location: str, required
        Name of the first location.

    selected_location2: str, required
        Name of the second location.

    Returns
    -------
    List of the strings, updated text.
    """
    if selected_location2:
        data = [
            (f"{selected_location if selected_location else 'POLAND'} vs {selected_location2} "
             f"graph of the Confirmed/Recovered/Deaths/Active cases.")
        ]
    else:
        data = [
            (f"{selected_location if selected_location else 'POLAND'} "
             f"graph of the Confirmed/Recovered/Deaths/Active cases.")
        ]

    return data


@app.callback(
    Output("line-graph", "figure"),
    [
        Input("date-picker", "date"),
        Input("location-dropdown", "value"),
        Input("location-dropdown2", "value"),
        Input("type-dropdown", "value"),
        Input("number-of-cases", "value"),
        Input("diff-type-dropdown", "value"),
    ],
)
def update_line_graph(date_picked: str, selected_location: str, selected_location2: str, selected_type: str,
                      start_cases_num: str, diff_type: str) -> 'go.Figure':
    """
    Update the main line graph with countries data and comparison.

    Parameters
    ----------
    date_picked: str, required
        Date picked in the date picker panel.

    selected_location: str, required
        First selected location (default is None -> POLAND)

    selected_location2: str, required
        Second selected location (default is None)

    selected_type: str, required
        Type of the data transformation to show on the graph. OneOf: [linear, log, percent]

    start_cases_num: str, required
        Number of cases picked by the user on the panel. This indicates from where to start plotting a graph.
        Could be useful to compare situation in the countries.
    """
    # note: if user picked up a number of cases, we should turn off date filter
    if start_cases_num is not None:
        date_picked = dt.strptime(str(dt(2020, 1, 22).date()), "%Y-%m-%d")
    else:
        date_picked = dt.strptime(date_picked, "%Y-%m-%d")
    # --- end note

    # note: download data from API only if user picked a new location, otherwise operate on already downloaded data
    if data_manager.prev_location != selected_location:
        data_manager.download_data_for_location_one(location=selected_location)
        data_manager.prev_location = selected_location

    if data_manager.prev_location2 != selected_location2 and selected_location2 is not None:
        data_manager.download_data_for_location_two(location=selected_location2)
        data_manager.prev_location2 = selected_location2
    # --- end note

    # note: compute active cases (all cases - deaths - recovered)
    data_active = data_manager.data_confirmed.copy()
    data_active['Cases'] = (data_manager.data_confirmed['Cases'] - data_manager.data_deaths['Cases'] -
                            data_manager.data_recovered['Cases'])
    # --- end note

    # note: find date equivalent to number of cases that user picked,
    # we should move the beginning of our data to that date
    if start_cases_num is not None:
        try:
            date_picked = (data_manager.data_confirmed.loc[data_manager.data_confirmed['Cases'] >=
                                                           start_cases_num].index[0])
        except IndexError:
            date_picked = data_manager.data_confirmed.index[-1]
    # --- end note

    # note: filter data by the starting date
    data_manager.data_confirmed_tmp = data_manager.data_confirmed.loc[date_picked:]
    data_manager.data_recovered_tmp = data_manager.data_recovered.loc[date_picked:]
    data_manager.data_deaths_tmp = data_manager.data_deaths.loc[date_picked:]
    data_active_tmp = data_active.loc[date_picked:]
    # --- end note

    if diff_type == 'diff-in-%':
        # note: compute daily percentage change
        data_active_tmp_change = data_manager.compute_daily_growth_percentage(
            data=data_active_tmp['Cases'])
        data_confirmed_tmp_change = data_manager.compute_daily_growth_percentage(
            data=data_manager.data_confirmed_tmp['Cases'])
        data_recovered_tmp_change = data_manager.compute_daily_growth_percentage(
            data=data_manager.data_recovered_tmp['Cases'])
        data_deaths_tmp_change = data_manager.compute_daily_growth_percentage(
            data=data_manager.data_deaths_tmp['Cases'])
        # --- end note
    else:
        # note: compute daily change
        data_active_tmp_change = data_manager.compute_daily_growth(
            data=data_active_tmp['Cases'])
        data_confirmed_tmp_change = data_manager.compute_daily_growth(
            data=data_manager.data_confirmed_tmp['Cases'])
        data_recovered_tmp_change = data_manager.compute_daily_growth(
            data=data_manager.data_recovered_tmp['Cases'])
        data_deaths_tmp_change = data_manager.compute_daily_growth(
            data=data_manager.data_deaths_tmp['Cases'])
        # --- end note

    # to the same as above but for second location data
    if selected_location2:
        data_active2 = data_manager.data_confirmed2.copy()
        data_active2['Cases'] = (data_manager.data_confirmed2['Cases'] - data_manager.data_deaths2['Cases'] -
                                 data_manager.data_recovered2['Cases'])

        if start_cases_num is not None:
            try:
                date_picked = (data_manager.data_confirmed2.loc[data_manager.data_confirmed2['Cases'] >=
                                                                start_cases_num].index[0])
            except IndexError:
                date_picked = data_manager.data_confirmed2.index[-1]

        data_manager.data_confirmed_tmp2 = data_manager.data_confirmed2.loc[date_picked:]
        data_manager.data_recovered_tmp2 = data_manager.data_recovered2.loc[date_picked:]
        data_manager.data_deaths_tmp2 = data_manager.data_deaths2.loc[date_picked:]
        data_active_tmp2 = data_active2.loc[date_picked:]

        if diff_type == 'diff-in-%':
            # note: compute daily percentage change
            data_active_tmp_change2 = data_manager.compute_daily_growth_percentage(
                data=data_active_tmp2['Cases'])
            data_confirmed_tmp_change2 = data_manager.compute_daily_growth_percentage(
                data=data_manager.data_confirmed_tmp2['Cases'])
            data_recovered_tmp_change2 = data_manager.compute_daily_growth_percentage(
                data=data_manager.data_recovered_tmp2['Cases'])
            data_deaths_tmp_change2 = data_manager.compute_daily_growth_percentage(
                data=data_manager.data_deaths_tmp2['Cases'])
            # --- end note
        else:
            # note: compute daily change
            data_active_tmp_change2 = data_manager.compute_daily_growth(
                data=data_active_tmp2['Cases'])
            data_confirmed_tmp_change2 = data_manager.compute_daily_growth(
                data=data_manager.data_confirmed_tmp2['Cases'])
            data_recovered_tmp_change2 = data_manager.compute_daily_growth(
                data=data_manager.data_recovered_tmp2['Cases'])
            data_deaths_tmp_change2 = data_manager.compute_daily_growth(
                data=data_manager.data_deaths_tmp2['Cases'])
            # --- end note
    # --- end note

    # note: data transformation part per user choice
    if selected_type == 'log':
        data_manager.data_confirmed_tmp['Cases'] = np.log(data_manager.data_confirmed['Cases'])
        data_manager.data_confirmed_tmp['Cases'].loc[np.isneginf(data_manager.data_confirmed_tmp['Cases'])] = 0

        data_manager.data_recovered_tmp['Cases'] = np.log(data_manager.data_recovered['Cases'])
        data_manager.data_recovered_tmp['Cases'].loc[np.isneginf(data_manager.data_recovered_tmp['Cases'])] = 0

        data_manager.data_deaths_tmp['Cases'] = np.log(data_manager.data_deaths['Cases'])
        data_manager.data_deaths_tmp['Cases'].loc[np.isneginf(data_manager.data_deaths_tmp['Cases'])] = 0

        data_active_tmp['Cases'] = np.log(data_active['Cases'])
        data_active_tmp['Cases'].loc[np.isneginf(data_active_tmp['Cases'])] = 0

        if selected_location2:
            data_manager.data_confirmed_tmp2['Cases'] = np.log(data_manager.data_confirmed2['Cases'])
            data_manager.data_confirmed_tmp2['Cases'].loc[np.isneginf(data_manager.data_confirmed_tmp2['Cases'])] = 0

            data_manager.data_recovered_tmp2['Cases'] = np.log(data_manager.data_recovered2['Cases'])
            data_manager.data_recovered_tmp2['Cases'].loc[np.isneginf(data_manager.data_recovered_tmp2['Cases'])] = 0

            data_manager.data_deaths_tmp2['Cases'] = np.log(data_manager.data_deaths2['Cases'])
            data_manager.data_deaths_tmp2['Cases'].loc[np.isneginf(data_manager.data_deaths_tmp2['Cases'])] = 0

            data_active_tmp2['Cases'] = np.log(data_active2['Cases'])
            data_active_tmp2['Cases'].loc[np.isneginf(data_active_tmp2['Cases'])] = 0

    elif selected_type == 'percent':
        data_manager.data_recovered_tmp['Cases'] = data_manager.data_recovered['Cases'] / data_manager.data_confirmed[
            'Cases']
        data_manager.data_recovered_tmp['Cases'].loc[np.isnan(data_manager.data_recovered_tmp['Cases'])] = 0

        data_manager.data_deaths_tmp['Cases'] = data_manager.data_deaths['Cases'] / data_manager.data_confirmed['Cases']
        data_manager.data_deaths_tmp['Cases'].loc[np.isnan(data_manager.data_deaths_tmp['Cases'])] = 0

        data_active_tmp['Cases'] = data_active['Cases'] / data_manager.data_confirmed['Cases']
        data_active_tmp['Cases'].loc[np.isnan(data_active_tmp['Cases'])] = 0

        data_manager.data_confirmed_tmp['Cases'] = data_manager.data_confirmed['Cases'] / data_manager.data_confirmed[
            'Cases']
        data_manager.data_confirmed_tmp['Cases'].loc[np.isnan(data_manager.data_confirmed_tmp['Cases'])] = 0

        if selected_location2:
            data_manager.data_recovered_tmp2['Cases'] = (data_manager.data_recovered2['Cases'] /
                                                         data_manager.data_confirmed2['Cases'])
            data_manager.data_recovered_tmp2['Cases'].loc[np.isnan(data_manager.data_recovered_tmp2['Cases'])] = 0

            data_manager.data_deaths_tmp2['Cases'] = data_manager.data_deaths2['Cases'] / data_manager.data_confirmed2[
                'Cases']
            data_manager.data_deaths_tmp2['Cases'].loc[np.isnan(data_manager.data_deaths_tmp2['Cases'])] = 0

            data_active_tmp2['Cases'] = data_active2['Cases'] / data_manager.data_confirmed2['Cases']
            data_active_tmp2['Cases'].loc[np.isnan(data_active_tmp2['Cases'])] = 0

            data_manager.data_confirmed_tmp2['Cases'] = (data_manager.data_confirmed2['Cases'] /
                                                         data_manager.data_confirmed2['Cases'])
            data_manager.data_confirmed_tmp2['Cases'].loc[np.isnan(data_manager.data_confirmed_tmp2['Cases'])] = 0
    # --- end note

    # note: reset date index to numerical only if user specified starting number of cases
    if start_cases_num is not None:
        data_manager.data_recovered_tmp = data_manager.data_recovered_tmp.reset_index(drop=True)
        data_manager.data_deaths_tmp = data_manager.data_deaths_tmp.reset_index(drop=True)
        data_active_tmp = data_active_tmp.reset_index(drop=True)
        data_manager.data_confirmed_tmp = data_manager.data_confirmed_tmp.reset_index(drop=True)

        if selected_location2:
            data_manager.data_recovered_tmp2 = data_manager.data_recovered_tmp2.reset_index(drop=True)
            data_manager.data_deaths_tmp2 = data_manager.data_deaths_tmp2.reset_index(drop=True)
            data_active_tmp2 = data_active_tmp2.reset_index(drop=True)
            data_manager.data_confirmed_tmp2 = data_manager.data_confirmed_tmp2.reset_index(drop=True)
    # --- end note

    # create updated graph layout
    layout = go.Layout(
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=True,
        legend=dict(y=0.9),
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#1e1e1e",
        dragmode="select",
        font=dict(color="white"),
        barmode='group',
        uirevision=True,
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
            title=f'Number of Cases in {"linear" if selected_type is None else selected_type} scale',
            position=0.04,
            type='log' if selected_type == 'log' else 'linear',
            title_standoff=25,
            showgrid=False,
            overlaying='y2',
            rangemode='tozero',
        ),
        yaxis2=dict(
            title=f'Daily {"%" if diff_type == "diff-in-%" else ""} change',
            side='right',
            showgrid=False,
            position=0.96,
            rangemode='tozero',
        )
    )

    # prepare each graph layer
    data = [
        go.Scatter(
            x=data_active_tmp.index,
            y=data_active_tmp['Cases'],
            hovertemplate=
            '<br><b>Date</b>: %{x}</br>' +
            '<b>Cases</b>: %{y}',
            mode="lines+markers",
            marker=dict(color="white", symbol="circle", size=5),
            name=f'Active {selected_location if selected_location else "POLAND"}',
        ),
        go.Scatter(
            x=data_manager.data_confirmed_tmp.index,
            y=data_manager.data_confirmed_tmp['Cases'],
            hovertemplate=
            '<br><b>Date</b>: %{x}</br>' +
            '<b>Cases</b>: %{y}',
            mode="lines+markers",
            marker=dict(color="yellow", symbol="square", size=5),
            name=f'Confirmed {selected_location if selected_location else "POLAND"}',
        ),
        go.Scatter(
            x=data_manager.data_recovered_tmp.index,
            y=data_manager.data_recovered_tmp['Cases'],
            hovertemplate=
            '<br><b>Date</b>: %{x}</br>' +
            '<b>Cases</b>: %{y}',
            mode="lines+markers",
            marker=dict(color="green", symbol="circle", size=5),
            name=f'Recovered {selected_location if selected_location else "POLAND"}',
        ),
        go.Scatter(
            x=data_manager.data_deaths_tmp.index,
            y=data_manager.data_deaths_tmp['Cases'],
            hovertemplate=
            '<br><b>Date</b>: %{x}</br>' +
            '<b>Cases</b>: %{y}',
            mode="lines+markers",
            marker=dict(color="red", symbol="circle-x", size=5),
            name=f'Deaths {selected_location if selected_location else "POLAND"}',
        ),
        go.Bar(
            name=f'Active daily {"%" if diff_type == "diff-in-%" else ""} change {selected_location if selected_location else "POLAND"}',
            x=data_active_tmp.index,
            y=data_active_tmp_change,
            hovertemplate=
            '<br><b>Date</b>: %{x}</br>' +
            '<b>Change</b>: %{y}' + f'{"%" if diff_type == "diff-in-%" else ""}',
            opacity=1,
            yaxis='y2',
            offsetgroup=0,
            marker_color='rgb(56, 30, 24)',
        ),
        go.Bar(
            name=f'Confirmed daily {"%" if diff_type == "diff-in-%" else ""} change {selected_location if selected_location else "POLAND"}',
            x=data_manager.data_confirmed_tmp.index,
            y=data_confirmed_tmp_change,
            hovertemplate=
            '<br><b>Date</b>: %{x}</br>' +
            '<b>Change</b>: %{y}' + f'{"%" if diff_type == "diff-in-%" else ""}',
            opacity=1,
            yaxis='y2',
            offsetgroup=1,
            marker_color='rgb(196, 171, 38)',
        ),
        go.Bar(
            name=f'Recovered daily {"%" if diff_type != "diff" else ""} change {selected_location if selected_location else "POLAND"}',
            x=data_manager.data_recovered_tmp.index,
            y=data_recovered_tmp_change,
            hovertemplate=
            '<br><b>Date</b>: %{x}</br>' +
            '<b>Change</b>: %{y}' + f'{"%" if diff_type == "diff-in-%" else ""}',
            opacity=1,
            yaxis='y2',
            offsetgroup=2,
            marker_color='rgb(0, 66, 0)',
        ),
        go.Bar(
            name=f'Deaths daily {"%" if diff_type == "diff-in-%" else ""} change {selected_location if selected_location else "POLAND"}',
            x=data_manager.data_deaths_tmp.index,
            y=data_deaths_tmp_change,
            hovertemplate=
            '<br><b>Date</b>: %{x}</br>' +
            '<b>Change</b>: %{y}' + f'{"%" if diff_type == "diff-in-%" else ""}',
            opacity=1,
            yaxis='y2',
            offsetgroup=3,
            marker_color='rgb(96, 0, 0)',
        ),
    ]

    # prepare each graph layer for second location
    if selected_location2:
        data.extend(
            [
                go.Scatter(
                    x=data_active_tmp2.index,
                    y=data_active_tmp2['Cases'],
                    hovertemplate=
                    '<br><b>Date</b>: %{x}</br>' +
                    '<b>Cases</b>: %{y}',
                    mode="lines+markers",
                    marker=dict(color="rgb(203,213,232)", symbol="circle", size=5, opacity=0.5),
                    line=dict(dash='dash'),
                    name=f'Active {selected_location2}',
                ),
                go.Scatter(
                    x=data_manager.data_confirmed_tmp2.index,
                    y=data_manager.data_confirmed_tmp2['Cases'],
                    hovertemplate=
                    '<br><b>Date</b>: %{x}</br>' +
                    '<b>Cases</b>: %{y}',
                    mode="lines+markers",
                    marker=dict(color="goldenrod", symbol="square", size=5, opacity=0.5),
                    line=dict(dash='dash'),
                    name=f'Confirmed {selected_location2}',
                ),
                go.Scatter(
                    x=data_manager.data_recovered_tmp2.index,
                    y=data_manager.data_recovered_tmp2['Cases'],
                    hovertemplate=
                    '<br><b>Date</b>: %{x}</br>' +
                    '<b>Cases</b>: %{y}',
                    mode="lines+markers",
                    marker=dict(color="#B6E880", symbol="circle", size=5, opacity=0.5),
                    line=dict(dash='dash'),
                    name=f'Recovered {selected_location2}',
                ),
                go.Scatter(
                    x=data_manager.data_deaths_tmp2.index,
                    y=data_manager.data_deaths_tmp2['Cases'],
                    hovertemplate=
                    '<br><b>Date</b>: %{x}</br>' +
                    '<b>Cases</b>: %{y}',
                    mode="lines+markers",
                    marker=dict(color="magenta", symbol="circle-x", size=5, opacity=0.5),
                    line=dict(dash='dash'),
                    name=f'Deaths {selected_location2}',
                ),
                go.Bar(
                    name=f'Active daily {"%" if diff_type == "diff-in-%" else ""} change {selected_location2}',
                    x=data_active_tmp2.index,
                    y=data_active_tmp_change2,
                    hovertemplate=
                    '<br><b>Date</b>: %{x}</br>' +
                    '<b>Change</b>: %{y}' + f'{"%" if diff_type == "diff-in-%" else ""}',
                    opacity=1,
                    yaxis='y2',
                    offsetgroup=1,
                    marker_color='rgb(91, 6, 155)',
                ),
                go.Bar(
                    name=f'Confirmed daily {"%" if diff_type == "diff-in-%" else ""} change {selected_location2}',
                    x=data_manager.data_confirmed_tmp2.index,
                    y=data_confirmed_tmp_change2,
                    hovertemplate=
                    '<br><b>Date</b>: %{x}</br>' +
                    '<b>Change</b>: %{y}' + f'{"%" if diff_type == "diff-in-%" else ""}',
                    opacity=1,
                    yaxis='y2',
                    offsetgroup=2,
                    marker_color='rgb(91, 130, 155)',
                ),
                go.Bar(
                    name=f'Recovered daily {"%" if diff_type == "diff-in-%" else ""} change {selected_location2}',
                    x=data_manager.data_recovered_tmp2.index,
                    y=data_recovered_tmp_change2,
                    hovertemplate=
                    '<br><b>Date</b>: %{x}</br>' +
                    '<b>Change</b>: %{y}' + f'{"%" if diff_type == "diff-in-%" else ""}',
                    opacity=1,
                    yaxis='y2',
                    offsetgroup=3,
                    marker_color='rgb(196, 183, 189)',
                ),
                go.Bar(
                    name=f'Deaths daily {"%" if diff_type == "diff-in-%" else ""} change {selected_location2}',
                    x=data_manager.data_deaths_tmp2.index,
                    y=data_deaths_tmp_change2,
                    hovertemplate=
                    '<br><b>Date</b>: %{x}</br>' +
                    '<b>Change</b>: %{y}' + f'{"%" if diff_type == "diff-in-%" else ""}',
                    opacity=1,
                    yaxis='y2',
                    offsetgroup=4,
                    marker_color='rgb(107, 130, 118)',
                ),
            ]
        )

    return go.Figure(
        data=data,
        layout=layout,
    )


# Update Map Graph based on date-picker and location dropdown
@app.callback(
    Output("map-graph", "figure"),
    [
        Input("location-dropdown", "value"),
        Input("world-dropdown", "value"),
    ],
)
def update_map_graph(selected_location, selected_world_data_type) -> 'go.Figure':
    """
    Update a map graph with selected main location data and position.

    Parameters
    ----------
    selected_location: str, required
        Main selected location, default is None -> POLAND.

    selected_world_data_type: str, required
        Type of the world data to display in the map (heat map).

    Returns
    -------
    go.Figure with updated data.
    """
    zoom = 4.0
    bearing = 0

    # note: update information of the selected location (text on the map)
    if selected_location:
        initial_lat = float(data_manager.locations[selected_location]["lat"])
        initial_lon = float(data_manager.locations[selected_location]["lon"])
        text_data = data_manager.client.stream_live(country=data_manager.client.Countries.__dict__[selected_location])
        text = (f"Confirmed: {text_data['Confirmed'].values[-1]} "
                f"Deaths: {text_data['Deaths'].values[-1]} "
                f"Recovered: {text_data['Recovered'].values[-1]} "
                f"Active: {text_data['Active'].values[-1]}")
    # --- end note

    # note: if main location is empty, take default one -> POLAND
    else:
        initial_lat = float(data_manager.locations['POLAND']["lat"])
        initial_lon = float(data_manager.locations['POLAND']["lon"])
        text_data = data_manager.client.stream_live(country=data_manager.client.Countries.POLAND)
        text = (f"Confirmed: {text_data['Confirmed'].values[-1]} "
                f"Deaths: {text_data['Deaths'].values[-1]} "
                f"Recovered: {text_data['Recovered'].values[-1]} "
                f"Active: {text_data['Active'].values[-1]}")
    # --- end note

    data = [
        # Plot of important locations on the map
        Scattermapbox(
            lat=[data_manager.locations[i]["lat"] for i in data_manager.locations],
            lon=[data_manager.locations[i]["lon"] for i in data_manager.locations],
            mode="markers",
            hoverinfo="text",
            text=[i for i in data_manager.locations],
            marker=dict(size=8, color="#ffa0a0", showscale=False),
        ),
        # Data for all rides based on date and time
        Scattermapbox(
            lat=[initial_lat],
            lon=[initial_lon],
            mode="markers",
            hoverinfo="lat+lon+text",
            text=text,
            marker=dict(
                showscale=False,
                color='red',
                opacity=0.5,
                size=30,
            ),
        ),
    ]

    if selected_world_data_type:
        data.append(Densitymapbox(
            hovertemplate=
            f'<br><b>{selected_world_data_type}</b>:' + ' %{z}</br>',
            name=selected_world_data_type,
            lat=data_manager.world_data['Lat'],
            lon=data_manager.world_data['Lon'],
            z=data_manager.world_data[selected_world_data_type],
            radius=50,
            colorbar=dict(
                title=selected_world_data_type,
                x=0.93,
                xpad=0,
                nticks=24,
                tickfont=dict(color="#d8d8d8"),
                titlefont=dict(color="#d8d8d8"),
                thicknessmode="pixels",
            ),
        ))

    return go.Figure(
        data=data,
        layout=Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=35, t=0, b=0),
            showlegend=False,
            uirevision=True,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=initial_lat, lon=initial_lon),
                style="dark",
                bearing=bearing,
                zoom=zoom,
            ),
            updatemenus=[
                dict(
                    buttons=(
                        [
                            dict(
                                args=[
                                    {
                                        "mapbox.zoom": 4,
                                        "mapbox.center.lon": str(data_manager.locations['POLAND']["lon"]),
                                        "mapbox.center.lat": str(data_manager.locations['POLAND']["lat"]),
                                        "mapbox.bearing": 0,
                                        "mapbox.style": "dark",
                                    }
                                ],
                                label="Reset Zoom",
                                method="relayout",
                            )
                        ]
                    ),
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
        ),
    )


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')
