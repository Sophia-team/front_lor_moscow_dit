import json
import os
import pathlib

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import geopandas as gpd
import cufflinks as cf

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

# geo_data = gpd.gpd.read_file('geo.json')

df_lat_lon = pd.read_csv(os.path.join(APP_PATH, os.path.join("data", "lon_lat_names.csv")))[["Latitude ", "Longitude", "Hover"]]
geo_data = gpd.gpd.read_file(os.path.join(APP_PATH, os.path.join("data", 'geo.json')))
df_full_data = pd.read_csv(os.path.join(APP_PATH, os.path.join("data", "graph_stats.csv")))

DATES = [
    1, 2,
    3, 4,
    5, 6,
    7, 8,
    9, 10,
    11, 12,
    13, 14,
    15, 16,
    17, 18,
    19, 20,
    21, 22,
    23, 24,
    25, 26,
    27, 28,
    29, 30,]

BINS = {
    "0-0.1%": (0, 0.1),
    "0.1-0.5%": (0.1, 0.5),
    "0.5-1%": (0.5, 1),
    "1-5%": (1, 5),
    "5-10%": (5, 10),
    "10-20%": (10, 20),
    "20-40%": (20, 40),
    "40-50%": (40, 50),
    "50-60%": (50, 60),
    "60-100%": (60, 100),
}

DEFAULT_COLORSCALE = [
    "#f2fffb",
    "#98ffe0",
    "#6df0c8",
    "#59dab2",
    "#31c194",
    "#25a27b",
    "#188463",
    "#157658",
    "#11684d",
    "#10523e",
]

DEFAULT_OPACITY = 0.8

mapbox_access_token = "pk.eyJ1IjoiZGVydHktZmxhbWUiLCJhIjoiY2tnZG9na3czMGxqNzJ6bnZraDhvNjdxcyJ9.UD6QkzNiy0aPOXqbUGdEgA"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

# App layout

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                # html.Img(id="logo", src=app.get_asset_url("dash-logo.png")),
                html.H4(children="SOPHIA: Очаги распространения инфекции"),
                html.P(
                    id="description",
                    children="Интеллектуальная система для мониторинга и прогнозирования эпидемиологической обстановки. Ai ядро, основанное на графе связей и моделях машинного обучения, позволяет проводить оценку влияния вводимых мер, моделирует различные сценарии развития событий. Система обладает широким набором интерфейсов, предназначенных для лёгкой интеграции с различными системами, включая системы информирования населения, и подключения новых источников данных. Архитектура решения позволяет легко масштабировать и внедрять предложенный подход.",
                ),
            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Используй слайдер для изменения дня:",
                                ),
                                html.P(
                                    id="slider-additional-text",
                                    children="Апрель",
                                ),
                                dcc.Slider(
                                    id="years-slider",
                                    min=min(DATES),
                                    max=max(DATES),
                                    value=max(DATES),
                                    marks={
                                        str(year): {
                                            "label": str(year),
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for year in DATES
                                    },
                                ),
                                dcc.Dropdown(
                                    options=[
                                        {
                                            "label": "Стандартный сценарий",
                                            "value": "sick",
                                        },
                                        {
                                            "label": "Сценарий 1",
                                            "value": "sick_1",
                                        },
                                        {
                                            "label": "Сценарий 2",
                                            "value": "sick_2",
                                        },
                                        {
                                            "label": "Сценарий 3",
                                            "value": "sick_3",
                                        },
                                        {
                                            "label": "Сценарий 4",
                                            "value": "sick_4",
                                        },
                                    ],
                                    value="sick",
                                    id="scenario-dropdown",
                                ),
                            ],
                        ),

                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Карта очагов распространения инфекций по г. Москва за {0} апр. 2020".format(max(DATES)),
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=dict(
                                        layout=dict(
                                            mapbox=dict(
                                                layers=[],
                                                accesstoken=mapbox_access_token,
                                                style=mapbox_style,
                                                center=dict(
                                                    lat=df_lat_lon["Latitude "].mean(),
                                                    lon=df_lat_lon["Longitude"].mean()),
                                                pitch=0,
                                                zoom=8,
                                            ),
                                            autosize=True,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Выберите график:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Гистограмм количества заболевших",
                                    "value": "show_absolute_deaths_single_year",
                                },
                                {
                                    "label": "Гистограмм количества заболевших (кумулятивно)",
                                    "value": "absolute_deaths_all_time",
                                },
                            ],
                            value="show_absolute_deaths_single_year",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("county-choropleth", "figure"),
    [Input("years-slider", "value")],
    [State("county-choropleth", "figure")],
)
def display_map(day, figure):
    cm = dict(zip(list(BINS.keys()), DEFAULT_COLORSCALE))

    data = [
        dict(
            lat=df_lat_lon["Latitude "],
            lon=df_lat_lon["Longitude"],
            text=df_lat_lon["Hover"],
            type="scattermapbox",
            hoverinfo="text",
            marker=dict(size=5, color="white", opacity=0),
        )
    ]

    annotations = [
        dict(
            showarrow=False,
            align="right",
            text="<b>Доля заразившихся",
            font=dict(color="#2cfec1"),
            bgcolor="#1f2630",
            x=0.95,
            y=0.95,
        )
    ]

    for i, bin in enumerate(reversed(list(BINS.keys()))):
        color = cm[bin]
        annotations.append(
            dict(
                arrowcolor=color,
                text=bin,
                x=0.95,
                y=0.85 - (i / 20),
                ax=-60,
                ay=0,
                arrowwidth=5,
                arrowhead=0,
                bgcolor="#1f2630",
                font=dict(color="#2cfec1"),
            )
        )

    if "layout" in figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
    else:
        lat = 55.751244
        lon = 37.618423
        zoom = 3.5

    layout = dict(
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            style=mapbox_style,
            center=dict(lat=lat, lon=lon),
            zoom=zoom,
        ),
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        annotations=annotations,
        dragmode="lasso",
    )

    # base_url = "https://raw.githubusercontent.com/jackparmer/mapbox-counties/master/"
    # if scenario == 0:
    #     col_name = 'rel'
    # else:
    #     col_name = 'rel_{}'.format(scenario)

    # answer = geo_data[(geo_data.date == day) & (geo_data[col_name] >= start) & (geo_data[col_name] < end)]
    # with open(os.path.join(APP_PATH, os.path.join("data", "mo.geojson")), "r") as read_file:
    #     geojson = json.load(read_file)
    for bin in BINS.keys():
        geo_layer = dict(
            sourcetype="geojson",
            source=json.loads(geo_data[(geo_data.date == day) & (geo_data['rel'] >= BINS[bin][0]) & (geo_data['rel'] < BINS[bin][1])].to_json()),
            type="fill",
            color=cm[bin],
            opacity=DEFAULT_OPACITY,
            # CHANGE THIS
            fill=dict(outlinecolor="#afafaf"),
        )
        layout["mapbox"]["layers"].append(geo_layer)

    fig = dict(data=data, layout=layout)
    return fig


@app.callback(Output("heatmap-title", "children"), [Input("years-slider", "value")])
def update_map_title(day):
    return "Карта очагов распространения инфекций по г. Москва за {0} апр. 2020".format(day)


@app.callback(
    Output("selected-data", "figure"),
    [
        Input("scenario-dropdown", "value"),
        Input("chart-dropdown", "value"),
        Input("years-slider", "value"),
    ],
)
def display_selected_data(scenario_dropdown, chart_dropdown, day):

    dff = df_full_data.copy()
    if scenario_dropdown == 'sick':
        chart_cols = ['date', scenario_dropdown]
    else:
        chart_cols = ['date', 'sick', scenario_dropdown]
    if "show_absolute_deaths_single_year" == chart_dropdown:
        dff = dff[dff['date'] <= day]
        title = "Абсолютное количество заразившихся, <b>{0} апр. 2020</b>".format(day)

        sick_cnt = dff[chart_cols]
        sick_cnt = sick_cnt.sort_values('date')
        sick_cnt = sick_cnt.groupby('date').sum()

    if 'absolute_deaths_all_time' == chart_dropdown:
        dff = dff[dff['date'] <= day]
        title = "Абсолютное количество заразившихся (кумулятивно), <b>{0} апр. 2020</b>".format(day)

        sick_cnt = dff[chart_cols]
        sick_cnt = sick_cnt.sort_values('date')
        sick_cnt = sick_cnt.groupby('date').sum().cumsum()

    if scenario_dropdown == 'sick':
        fig = sick_cnt.iplot(kind="bar", y=scenario_dropdown, title=title, asFigure=True)
    else:
        sick_cnt.rename(columns={scenario_dropdown: "Новый сценарий", "sick": "Стандартный сценарий"}, inplace=True)
        fig = sick_cnt.iplot(kind="bar", y=["Новый сценарий", "Стандартный сценарий", ], title=title, asFigure=True,)

    fig_layout = fig["layout"]
    fig_data = fig["data"]
    fig_layout['legend']['orientation'] = "h"
    fig_data[0]["text"] = sick_cnt.values.tolist()
    fig_data[0]["marker"]["color"] = "#2cfec1"
    fig_data[0]["marker"]["opacity"] = 1
    fig_data[0]["marker"]["line"]["width"] = 0
    fig_data[0]["textposition"] = "outside"
    fig_layout["paper_bgcolor"] = "#1f2630"
    fig_layout["plot_bgcolor"] = "#1f2630"
    fig_layout["font"]["color"] = "#2cfec1"
    fig_layout["title"]["font"]["color"] = "#2cfec1"
    fig_layout["xaxis"]["tickfont"]["color"] = "#2cfec1"
    fig_layout["yaxis"]["tickfont"]["color"] = "#2cfec1"
    fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
    fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"
    fig_layout["margin"]["t"] = 75
    fig_layout["margin"]["r"] = 50
    fig_layout["margin"]["b"] = 100
    fig_layout["margin"]["l"] = 50

    return fig


if __name__ == "__main__":
    app.run_server(debug=False)

