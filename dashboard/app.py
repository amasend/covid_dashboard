import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import json
import numpy as np
from postman_covid19_sdk.client import APIClient
from postman_covid19_sdk.utils.enums import StatusType

from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server
client = APIClient()

# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

# Dictionary of all countries with locations
with open("../location_list.json", 'r') as f:
    list_of_locations = json.loads(f.read())

data = client.get_by_country(country=client.Countries.POLAND, status=StatusType.CONFIRMED)

data_confirmed = None
data_recovered = None
data_deaths = None
prev_location = None


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
                        html.P(
                            """You can select different starting day here, also you can chose a country to show."""
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
                                                for i in list_of_locations
                                            ],
                                            placeholder="Select a location",
                                        ),
                                        dcc.Dropdown(
                                            id="type-dropdown",
                                            options=[
                                                {"label": 'linear', "value": 'linear'},
                                                {"label": 'log', "value": 'log'},
                                                {"label": 'percent', "value": 'percent'},
                                            ],
                                            placeholder="Select a location",
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
                        dcc.Graph(id="line-graph"),
                    ],
                ),
            ],
        )
    ]
)


def download_data(location):
    global data_confirmed
    global data_recovered
    global data_deaths

    if location:
        data_confirmed = remove_duplicated(client.get_by_country(country=client.Countries.__dict__[location]))
        data_recovered = remove_duplicated(client.get_by_country(country=client.Countries.__dict__[location],
                                                                 status=StatusType.RECOVERED))
        data_deaths = remove_duplicated(client.get_by_country(country=client.Countries.__dict__[location],
                                                              status=StatusType.DEATHS))

    else:
        data_confirmed = remove_duplicated(client.get_by_country(country=client.Countries.POLAND))
        data_recovered = remove_duplicated(
            client.get_by_country(country=client.Countries.POLAND, status=StatusType.RECOVERED))
        data_deaths = remove_duplicated(
            client.get_by_country(country=client.Countries.POLAND, status=StatusType.DEATHS))


def remove_duplicated(data: 'DataFrame') -> 'DataFrame':
    idx = data.groupby(level=0)['Cases'].transform(max) == data['Cases']
    return data[idx]


@app.callback(
    Output("middle-text", "children"),
    [
        Input("location-dropdown", "value"),
    ],
)
def update_middle_text(selectedLocation):
    return [
        f"{selectedLocation if selectedLocation else 'POLAND'} graph of the Confirmed/Recovered/Deaths/Active cases."
    ]


@app.callback(
    Output("line-graph", "figure"),
    [
        Input("date-picker", "date"),
        Input("location-dropdown", "value"),
        Input("type-dropdown", "value")
    ],
)
def update_line_graph(datePicked, selectedLocation, selectedType):
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    global data_confirmed
    global data_recovered
    global data_deaths
    global prev_location

    if prev_location != selectedLocation or prev_location is None:
        download_data(location=selectedLocation)
        if prev_location is None:
            prev_location = 'POLAND'
        else:
            prev_location = selectedLocation

    data_active = data_confirmed.copy()
    data_active['Cases'] = data_confirmed['Cases'] - data_deaths['Cases'] - data_recovered['Cases']

    data_confirmed_tmp = data_confirmed.loc[date_picked:]
    data_recovered_tmp = data_recovered.loc[date_picked:]
    data_deaths_tmp = data_deaths.loc[date_picked:]
    data_active_tmp = data_active.loc[date_picked:]

    if selectedType == 'log':
        data_confirmed_tmp['Cases'] = np.log(data_confirmed['Cases'])
        data_confirmed_tmp['Cases'][np.isneginf(data_confirmed_tmp['Cases'])] = 0

        data_recovered_tmp['Cases'] = np.log(data_recovered['Cases'])
        data_recovered_tmp['Cases'][np.isneginf(data_recovered_tmp['Cases'])] = 0

        data_deaths_tmp['Cases'] = np.log(data_deaths['Cases'])
        data_deaths_tmp['Cases'][np.isneginf(data_deaths_tmp['Cases'])] = 0

        data_active_tmp['Cases'] = np.log(data_active['Cases'])
        data_active_tmp['Cases'][np.isneginf(data_active_tmp['Cases'])] = 0

    elif selectedType == 'percent':
        data_recovered_tmp['Cases'] = data_recovered['Cases'] / data_confirmed['Cases']
        data_deaths_tmp['Cases'] = data_deaths['Cases'] / data_confirmed['Cases']
        data_active_tmp['Cases'] = data_active['Cases'] / data_confirmed['Cases']
        data_confirmed_tmp['Cases'] = data_confirmed['Cases'] / data_confirmed['Cases']

    layout = go.Layout(
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=True,
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#1e1e1e",
        dragmode="select",
        font=dict(color="white"),
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
            showgrid=False
        ),
    )

    return go.Figure(
        data=[
            go.Scatter(
                x=data_active_tmp.index,
                y=data_active_tmp['Cases'],
                hovertemplate=
                '<br><b>Date</b>: %{x}</br>' +
                '<b>Cases</b>: %{y}',
                mode="lines+markers",
                marker=dict(color="white", symbol="circle", size=5),
                name='Active',
            ),
            go.Scatter(
                x=data_confirmed_tmp.index,
                y=data_confirmed_tmp['Cases'],
                hovertemplate=
                '<br><b>Date</b>: %{x}</br>' +
                '<b>Cases</b>: %{y}',
                mode="lines+markers",
                marker=dict(color="yellow", symbol="square", size=5),
                name='Confirmed',
            ),
            go.Scatter(
                x=data_recovered_tmp.index,
                y=data_recovered_tmp['Cases'],
                hovertemplate=
                '<br><b>Date</b>: %{x}</br>' +
                '<b>Cases</b>: %{y}',
                mode="lines+markers",
                marker=dict(color="green", symbol="circle", size=5),
                name='Recovered',
            ),
            go.Scatter(
                x=data_deaths_tmp.index,
                y=data_deaths_tmp['Cases'],
                hovertemplate=
                '<br><b>Date</b>: %{x}</br>' +
                '<b>Cases</b>: %{y}',
                mode="lines+markers",
                marker=dict(color="red", symbol="circle-x", size=5),
                name='Deaths',
            ),
        ],
        layout=layout,
    )


# Update Map Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    Output("map-graph", "figure"),
    [
        Input("date-picker", "date"),
        Input("location-dropdown", "value"),
    ],
)
def update_graph(datePicked, selectedLocation):
    zoom = 4.0
    bearing = 0

    if selectedLocation:
        latInitial = float(list_of_locations[selectedLocation]["lat"])
        lonInitial = float(list_of_locations[selectedLocation]["lon"])
        text_data = client.stream_live(country=client.Countries.__dict__[selectedLocation])
        text = (f"Confirmed: {text_data['Confirmed'].values[-1]} "
                f"Deaths: {text_data['Deaths'].values[-1]} "
                f"Recovered: {text_data['Recovered'].values[-1]} "
                f"Active: {text_data['Active'].values[-1]}")

    else:
        latInitial = float(list_of_locations['POLAND']["lat"])
        lonInitial = float(list_of_locations['POLAND']["lon"])
        text_data = client.stream_live(country=client.Countries.POLAND)
        text = (f"Confirmed: {text_data['Confirmed'].values[-1]} "
                f"Deaths: {text_data['Deaths'].values[-1]} "
                f"Recovered: {text_data['Recovered'].values[-1]} "
                f"Active: {text_data['Active'].values[-1]}")

    return go.Figure(
        data=[
            # Plot of important locations on the map
            Scattermapbox(
                lat=[list_of_locations[i]["lat"] for i in list_of_locations],
                lon=[list_of_locations[i]["lon"] for i in list_of_locations],
                mode="markers",
                hoverinfo="text",
                text=[i for i in list_of_locations],
                marker=dict(size=8, color="#ffa0a0"),
            ),
            # Data for all rides based on date and time
            Scattermapbox(
                lat=[latInitial],
                lon=[lonInitial],
                mode="markers",
                hoverinfo="lat+lon+text",
                text=text,
                marker=dict(
                    showscale=True,
                    color='red',
                    opacity=0.5,
                    size=30,
                ),
            ),
        ],
        layout=Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=35, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=latInitial, lon=lonInitial),
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
                                        "mapbox.center.lon": str(list_of_locations['POLAND']["lon"]),
                                        "mapbox.center.lat": str(list_of_locations['POLAND']["lat"]),
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
