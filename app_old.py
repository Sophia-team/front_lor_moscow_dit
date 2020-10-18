import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import State, Input, Output
from dash.exceptions import PreventUpdate

import pandas as pd
import os

app = dash.Dash(
    __name__,
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1, maximum-scale=1.0, user-scalable=no",
        }
    ],
)
server = app.server

app.config["suppress_callback_exceptions"] = True

# Plotly mapbox token
mapbox_access_token = "pk.eyJ1IjoiZGVydHktZmxhbWUiLCJhIjoiY2tnZG9na3czMGxqNzJ6bnZraDhvNjdxcyJ9.UD6QkzNiy0aPOXqbUGdEgA"

# Load data
csv_path = "demo_data.csv"
data = pd.read_csv(csv_path).sample(400).reset_index()

metrics = [
    ('Плотность заражения', 'total'),
    ('Количество жителей', 'total'),
    ('Количество заболевших', 'total')
]


def build_upper_left_panel():
    return html.Div(
        id="upper-left",
        className="six columns",
        children=[
            html.P(
                className="section-title",
                children="Выявление очагов распространения инфекций",
            ),
            html.Div(
                className="control-row-1",
                children=[
                    html.Div(
                        id="sector-select-outer",
                        children=[
                            html.Label("Выберите район"),
                            dcc.Dropdown(
                                id="sector-select",
                                options=[{"label": i, "value": i} for i in data.index],
                                value=data.index[0],
                            ),
                        ],
                    ),
                    html.Div(
                        id="select-metric-outer",
                        children=[
                            html.Label("Выберите метрику"),
                            dcc.Dropdown(
                                id="metric-select",
                                options=[{"label": i[0], "value": i[1]} for i in metrics],
                                value='total',
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                id="distinct-select-outer",
                className="control-row-2",
                children=[
                    html.Label('Выберите сектор'),
                    html.Div(
                        id="checklist-container",
                        children=dcc.Checklist(
                            id="distinct-select-all",
                            options=[{"label": "Выбрать все районы", "value": "All"}],
                            value=[],
                        ),
                    ),
                    html.Div(
                        id="distinct-select-dropdown-outer",
                        children=dcc.Dropdown(
                            id="distinct-select", multi=True, searchable=True,
                        ),
                    ),
                ],
            ),
            html.Div(
                id="table-container",
                className="table-container",
                children=[
                    html.Div(
                        id="table-upper",
                        children=[
                            html.P("Статистика"),
                            dcc.Loading(children=html.Div(id="cost-stats-container")),
                        ],
                    ),
                ],
            ),
        ],
    )


def generate_geo_map(geo_data, selected_metric, region_select):

    colors = ["#21c7ef", "#76f2ff", "#ff6969", "#ff1717"]

    hospitals = []

    lat = geo_data['y'].tolist()
    lon = geo_data['x'].tolist()

    metric_data = {
        "min": geo_data[selected_metric].min(),
        "max": geo_data[selected_metric].max()}
    metric_data["mid"] = (metric_data["min"] + metric_data["max"]) / 2
    metric_data["low_mid"] = (
        metric_data["min"] + metric_data["mid"]
    ) / 2
    metric_data["high_mid"] = (
        metric_data["mid"] + metric_data["max"]
    ) / 2

    for i in range(len(lat)):
        val = geo_data.loc[i, selected_metric]

        if val <= metric_data["low_mid"]:
            color = colors[0]
        elif metric_data["low_mid"] < val <= metric_data["mid"]:
            color = colors[1]
        elif metric_data["mid"] < val <= metric_data["high_mid"]:
            color = colors[2]
        else:
            color = colors[3]

        hospital = go.Scattermapbox(
            lat=[lat[i]],
            lon=[lon[i]],
            mode="markers",
            marker=dict(
                color=color,
                showscale=True,
                colorscale=[
                    [0, "#21c7ef"],
                    [0.33, "#76f2ff"],
                    [0.66, "#ff6969"],
                    [1, "#ff1717"],
                ],
                cmin=metric_data["min"],
                cmax=metric_data["max"],
                size=3 * (1 + (val + metric_data["min"]) / metric_data["mid"]),
                colorbar=dict(
                    x=0.9,
                    len=0.7,
                    title=dict(
                        text="Количество",
                        font={"color": "#737a8d", "family": "Open Sans"},
                    ),
                    titleside="top",
                    tickmode="array",
                    tickvals=[metric_data["min"], metric_data["max"]],
                    ticktext=[
                        "{}".format(metric_data["min"]),
                        "{}".format(metric_data["max"]),
                    ],
                    ticks="outside",
                    thickness=15,
                    tickfont={"family": "Open Sans", "color": "#737a8d"},
                ),
            ),
            opacity=0.8,
            # selectedpoints=[0],
            selected=dict(marker={"color": "#ffff00"}),
            # customdata=[('sdfsdf', 'sdfsdf')],
            hoverinfo="text",
            text='Количество заражённых'
            + "<br>"
            + 'Москва',
        )
        hospitals.append(hospital)

    layout = go.Layout(
        margin=dict(l=10, r=10, t=20, b=10, pad=5),
        plot_bgcolor="#171b26",
        paper_bgcolor="#171b26",
        clickmode="event+select",
        hovermode="closest",
        showlegend=False,
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=10,
            center=go.layout.mapbox.Center(
                lat=data['y'].mean(), lon=data['x'].mean()
            ),
            pitch=5,
            zoom=6,
            style="mapbox://styles/plotlymapbox/cjvppq1jl1ips1co3j12b9hex",
        ),
    )

    return {"data": hospitals, "layout": layout}


app.layout = html.Div(
    className="container scalable",
    children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.H6("SOPHIA: предсказение распространения заражения"),
            ],
        ),
        html.Div(
            id="upper-container",
            className="row",
            children=[
                build_upper_left_panel(),
                html.Div(
                    id="geo-map-outer",
                    className="six columns",
                    children=[
                        html.P(
                            id="map-title",
                            children="Уровень заражения",
                        ),
                        html.Div(
                            id="geo-map-loading-outer",
                            children=[
                                dcc.Loading(
                                    id="loading",
                                    children=dcc.Graph(
                                        id="geo-map",
                                        figure={
                                            "data": [],
                                            "layout": dict(
                                                plot_bgcolor="#171b26",
                                                paper_bgcolor="#171b26",
                                            ),
                                        },
                                    ),
                                )
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)

#
# @app.callback(
#     [
#         Output("map-title", "children"),
#     ],
#     [Input("distinct-select-all", "value"), Input("sector-select", "value"), ],
# )
# def update_region_dropdown(select_all, state_select):
#     state_raw_data = data
#     options = [{"label": i, "value": i} for i in state_raw_data.index]
#
#     ctx = dash.callback_context
#     if ctx.triggered[0]["prop_id"].split(".")[0] == "distinct-select-all":
#         if select_all == ["All"]:
#             value = [i["value"] for i in options]
#         else:
#             value = dash.no_update
#     else:
#         pass
#     return (
#         value,
#         options,
#     )


# @app.callback(
#     Output("checklist-container", "children"),
#     [Input("distinct-select", "value")],
#     [State("distinct-select", "options"), State("distinct-select-all", "value")],
# )
# def update_checklist(selected, select_options, checked):
#     if len(selected) < len(select_options) and len(checked) == 0:
#         raise PreventUpdate()
#
#     elif len(selected) < len(select_options) and len(checked) == 1:
#         return dcc.Checklist(
#             id="distinct-select-all",
#             options=[{"label": "Select All Regions", "value": "All"}],
#             value=[],
#         )
#
#     elif len(selected) == len(select_options) and len(checked) == 1:
#         raise PreventUpdate()
#
#     return dcc.Checklist(
#         id="distinct-select-all",
#         options=[{"label": "Select All Regions", "value": "All"}],
#         value=["All"],
#     )


# @app.callback(
#     Output("cost-stats-container", "children"),
#     [
#         Input("geo-map", "selectedData"),
#         Input("procedure-plot", "selectedData"),
#         Input("metric-select", "value"),
#         Input("sector-select", "value"),
#     ],
# )
# def update_hospital_datatable(geo_select, procedure_select, cost_select, state_select):
#     state_agg = generate_aggregation(data_dict[state_select], cost_metric)
#     # make table from geo-select
#     geo_data_dict = {
#         "Provider Name": [],
#         "City": [],
#         "Street Address": [],
#         "Maximum Cost ($)": [],
#         "Minimum Cost ($)": [],
#     }
#
#     ctx = dash.callback_context
#     if ctx.triggered:
#         prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
#
#         # make table from procedure-select
#         if prop_id == "procedure-plot" and procedure_select is not None:
#
#             for point in procedure_select["points"]:
#                 provider = point["customdata"]
#
#                 dff = state_agg[state_agg["Provider Name"] == provider]
#
#                 geo_data_dict["Provider Name"].append(point["customdata"])
#                 city = dff["Hospital Referral Region (HRR) Description"].tolist()[0]
#                 geo_data_dict["City"].append(city)
#
#                 address = dff["Provider Street Address"].tolist()[0]
#                 geo_data_dict["Street Address"].append(address)
#
#                 geo_data_dict["Maximum Cost ($)"].append(
#                     dff[cost_select]["max"].tolist()[0]
#                 )
#                 geo_data_dict["Minimum Cost ($)"].append(
#                     dff[cost_select]["min"].tolist()[0]
#                 )
#
#         if prop_id == "geo-map" and geo_select is not None:
#
#             for point in geo_select["points"]:
#                 provider = point["customdata"][0]
#                 dff = state_agg[state_agg["Provider Name"] == provider]
#
#                 geo_data_dict["Provider Name"].append(point["customdata"][0])
#                 geo_data_dict["City"].append(point["customdata"][1].split("- ")[1])
#
#                 address = dff["Provider Street Address"].tolist()[0]
#                 geo_data_dict["Street Address"].append(address)
#
#                 geo_data_dict["Maximum Cost ($)"].append(
#                     dff[cost_select]["max"].tolist()[0]
#                 )
#                 geo_data_dict["Minimum Cost ($)"].append(
#                     dff[cost_select]["min"].tolist()[0]
#                 )
#
#         geo_data_df = pd.DataFrame(data=geo_data_dict)
#         data = geo_data_df.to_dict("rows")
#
#     else:
#         data = [{}]
#
#     return dash_table.DataTable(
#         id="cost-stats-table",
#         columns=[{"name": i, "id": i} for i in geo_data_dict.keys()],
#         data=data,
#         filter_action="native",
#         page_size=5,
#         style_cell={"background-color": "#242a3b", "color": "#7b7d8d"},
#         style_as_list_view=False,
#         style_header={"background-color": "#1f2536", "padding": "0px 5px"},
#     )


# @app.callback(
#     Output("procedure-stats-container", "children"),
#     [
#         Input("procedure-plot", "selectedData"),
#         Input("geo-map", "selectedData"),
#         Input("metric-select", "value"),
#     ],
#     [State("sector-select", "value")],
# )
# def update_procedure_stats(procedure_select, geo_select, cost_select, state_select):
#     procedure_dict = {
#         "DRG": [],
#         "Procedure": [],
#         "Provider Name": [],
#         "Cost Summary": [],
#     }
#
#     ctx = dash.callback_context
#     prop_id = ""
#     if ctx.triggered:
#         prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
#
#     if prop_id == "procedure-plot" and procedure_select is not None:
#         for point in procedure_select["points"]:
#             procedure_dict["DRG"].append(point["y"].split(" - ")[0])
#             procedure_dict["Procedure"].append(point["y"].split(" - ")[1])
#
#             procedure_dict["Provider Name"].append(point["customdata"])
#             procedure_dict["Cost Summary"].append(("${:,.2f}".format(point["x"])))
#
#     # Display all procedures at selected hospital
#     provider_select = []
#
#     if prop_id == "geo-map" and geo_select is not None:
#         for point in geo_select["points"]:
#             provider = point["customdata"][0]
#             provider_select.append(provider)
#
#         state_raw_data = data_dict[state_select]
#         provider_filtered = state_raw_data[
#             state_raw_data["Provider Name"].isin(provider_select)
#         ]
#
#         for i in range(len(provider_filtered)):
#             procedure_dict["DRG"].append(
#                 provider_filtered.iloc[i]["DRG Definition"].split(" - ")[0]
#             )
#             procedure_dict["Procedure"].append(
#                 provider_filtered.iloc[i]["DRG Definition"].split(" - ")[1]
#             )
#             procedure_dict["Provider Name"].append(
#                 provider_filtered.iloc[i]["Provider Name"]
#             )
#             procedure_dict["Cost Summary"].append(
#                 "${:,.2f}".format(provider_filtered.iloc[0][cost_select])
#             )
#
#     procedure_data_df = pd.DataFrame(data=procedure_dict)
#
#     return dash_table.DataTable(
#         id="procedure-stats-table",
#         columns=[{"name": i, "id": i} for i in procedure_dict.keys()],
#         data=procedure_data_df.to_dict("rows"),
#         filter_action="native",
#         sort_action="native",
#         style_cell={
#             "textOverflow": "ellipsis",
#             "background-color": "#242a3b",
#             "color": "#7b7d8d",
#         },
#         sort_mode="multi",
#         page_size=5,
#         style_as_list_view=False,
#         style_header={"background-color": "#1f2536", "padding": "2px 12px 0px 12px"},
#     )


@app.callback(
    Output("geo-map", "figure"),
    [
        Input("metric-select", "value"),
        Input("distinct-select", "value"),
        Input("sector-select", "value"),
    ],
)
def update_geo_map(cost_select, region_select, state_select):

    return generate_geo_map(data, cost_select, region_select)


# @app.callback(
#     Output("procedure-plot", "figure"),
#     [
#         Input("metric-select", "value"),
#         Input("distinct-select", "value"),
#         Input("geo-map", "selectedData"),
#         Input("sector-select", "value"),
#     ],
# )
# def update_procedure_plot(cost_select, region_select, geo_select, state_select):
#     # generate procedure plot from selected provider
#     state_raw_data = data_dict[state_select]
#
#     provider_select = []
#     if geo_select is not None:
#         for point in geo_select["points"]:
#             provider_select.append(point["customdata"][0])
#     return generate_procedure_plot(
#         state_raw_data, cost_select, region_select, provider_select
#     )


if __name__ == "__main__":
    app.run_server(debug=True)
