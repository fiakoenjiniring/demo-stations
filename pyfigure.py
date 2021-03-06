"""MODULE FOR GENERATE FIGURE RELATED"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pyconfig import appConfig


def generate_watermark(n: int = 1, source: str = None) -> dict:
    """GENERATE DICT WATERMARK FOR SUBPLOTS"""

    n = "" if n == 1 else n
    return dict(
        source=appConfig.TEMPLATE.WATERMARK_SOURCE,
        xref=f"x{n} domain",
        yref=f"y{n} domain",
        x=0.5,
        y=0.5,
        sizex=0.5,
        sizey=0.5,
        xanchor="center",
        yanchor="middle",
        name="watermark",
        layer="below",
        opacity=0.2,
    )


def figure_empty(
    text: str = "", size: int = 40, margin_all: int = 0, height: int = 450
) -> go.Figure:
    """GENERATE FIGURE EMPTY"""

    data = [{"x": [], "y": []}]

    layout = go.Layout(
        title={"text": "", "x": 0.5},
        xaxis={
            "title": "",
            "showgrid": False,
            "showticklabels": False,
            "zeroline": False,
        },
        yaxis={
            "title": "",
            "showgrid": False,
            "showticklabels": False,
            "zeroline": False,
        },
        margin=dict(t=margin_all, l=margin_all, r=margin_all, b=margin_all),
        annotations=[
            dict(
                name="text",
                text=f"<i>{text}</i>",
                opacity=0.3,
                font_size=size,
                xref="x domain",
                yref="y domain",
                x=0.5,
                y=0.05,
                showarrow=False,
            )
        ],
        height=height,
    )

    return go.Figure(data, layout)


def figure_map_all_stations(combined_metadata: pd.DataFrame) -> go.Figure:
    """FIGURE OF ALL DATASET (STATIONS)"""

    data = []
    for dataset in combined_metadata["title"].unique():
        metadata_stations = combined_metadata.loc[combined_metadata["title"] == dataset]
        _scattermapbox = go.Scattermapbox(
            lat=metadata_stations.latitude,
            lon=metadata_stations.longitude,
            text=metadata_stations.station_name,
            customdata=metadata_stations.index,
            name=dataset,
            marker_size=12,
            marker_opacity=0.8,
        )
        data.append(_scattermapbox)

    layout = go.Layout(
        clickmode="event",
        title=None,
        margin=dict(t=0, l=0, b=0, r=0),
        mapbox=dict(
            center=dict(
                # ref: https://www.quora.com/Where-exactly-is-the-center-of-Indonesia-latitude-longitude-wise
                # 2??36'00.1"S 118??00'56.8"E (-2.600029, 118.015776)
                lat=-2.600029,
                lon=118.015776,
            ),
        ),
        dragmode=False,
        showlegend=True,
        legend_title="<b>Dataset</b>",
        legend=dict(
            yanchor="top", xanchor="left", x=0.01, y=0.99, bgcolor="rgba(0,0,0,0)"
        ),
        images=[
            dict(
                source=appConfig.TEMPLATE.WATERMARK_SOURCE,
                xref="x domain",
                yref="y domain",
                x=0.01,
                y=0.02,
                sizex=0.2,
                sizey=0.2,
                xanchor="left",
                yanchor="bottom",
                name="watermark-fiako",
                layer="above",
                opacity=0.7,
            )
        ],
    )

    return go.Figure(data, layout)


def figure_map_coordinate(
    point_coordinate: str,
    name_coordinate: str,
    df_with_distance: pd.DataFrame,
) -> go.Figure:
    """FIGURE MAP OF COORDINATE AND NEAREST STATIONS"""

    from geopy.point import Point

    point_coordinate = Point(point_coordinate)

    # ref: https://stats.stackexchange.com/questions/281162/scale-a-number-between-a-range
    def normalize(data: pd.Series, lower: float, upper: float):
        return lower + (upper - lower) * (
            (data - data.min()) / (data.max() - data.min())
        )

    LOWEST_OPACITY, HIGHEST_OPACITY = 0.4, 1
    opacity_stations = (
        normalize(df_with_distance.distance, LOWEST_OPACITY, HIGHEST_OPACITY)[::-1]
        if len(df_with_distance) > 1
        else [HIGHEST_OPACITY]
    )

    data = [
        go.Scattermapbox(
            lat=df_with_distance.latitude,
            lon=df_with_distance.longitude,
            text=df_with_distance.station_name,
            textposition="bottom right",
            texttemplate="%{customdata[0]}<br>%{text}<br>%{customdata[1]:.3f} km",
            customdata=np.stack(
                [
                    df_with_distance.index,
                    df_with_distance.distance,
                ],
                axis=-1,
            ),
            hovertemplate="%{customdata[0]} - %{text}<br>(%{lat:.5f}, %{lon:.5f})<br><b>%{customdata[1]:.3f} km</b><extra></extra>",
            name="Nearest Stations",
            marker_size=12,  # df_with_distance.distance,
            # marker_sizemin=5,
            # marker_sizeref=sizeref,
            marker_color="MidnightBlue",
            marker_opacity=opacity_stations,
            mode="markers+text",
        ),
        go.Scattermapbox(
            lat=[point_coordinate.latitude],
            lon=[point_coordinate.longitude],
            text=[name_coordinate],
            name=name_coordinate,
            textposition="bottom center",
            marker_size=15,
            marker_color="red",
            marker_opacity=1,
            mode="markers+text",
            hovertemplate="%{text}<br>(%{lat:.5f}, %{lon:.5f})<extra></extra>",
        ),
    ]

    layout = go.Layout(
        clickmode="event",
        title=None,
        margin=dict(t=0, l=0, b=0, r=0),
        mapbox_center_lat=point_coordinate.latitude,
        mapbox_center_lon=point_coordinate.longitude,
        dragmode=False,
        showlegend=True,
        mapbox=dict(
            zoom=9.5,
        ),
        images=[
            dict(
                source=appConfig.TEMPLATE.WATERMARK_SOURCE,
                xref="x domain",
                yref="y domain",
                x=0.5,
                y=0.02,
                sizex=0.3,
                sizey=0.3,
                xanchor="center",
                yanchor="bottom",
                name="watermark-fiako",
                layer="above",
                opacity=0.6,
            )
        ],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0,0,0,0)",
            itemsizing="constant",
        ),
    )

    return go.Figure(data, layout)


def figure_comp_heatmap(
    dataframe: pd.DataFrame, combined_metadata: pd.DataFrame = None
) -> go.Figure:
    """FIGURE HEATMAP COMPLETENESS ALL STATIONS"""

    table_percent = dataframe.T.iloc[::-1]
    table_percent_date = table_percent.copy()
    table_percent_date[:] = table_percent_date.columns.strftime("%B %Y")

    if combined_metadata is not None:
        y_label = [
            f"{stat_id} - {combined_metadata.loc[stat_id, 'station_name']}"
            for stat_id in table_percent.index
        ]
    else:
        y_label = table_percent.index

    data = go.Heatmap(
        z=table_percent.to_numpy(),
        x=table_percent.columns,
        y=y_label,
        zmin=0,
        zmax=100,
        customdata=table_percent_date.to_numpy(),
        # colorbar_title_text='Percentage'
        hovertemplate="%{y}<br>%{customdata}<br><b>%{z}%</b><extra></extra>",
    )

    layout = go.Layout(
        xaxis_title_text="<b>Date</b>",
        xaxis_showspikes=True,
        yaxis_title_text="<b>Station ID</b>",
        # yaxis_tickangle=-90,
        yaxis_fixedrange=True,
        yaxis={"tickvals": y_label, "ticktext": table_percent.index},
        margin=dict(t=45, l=0, r=0, b=0),
        dragmode="zoom",
        height=max(450, 45 * len(table_percent)),
        showlegend=True,
    )

    return go.Figure(data, layout)


def figure_comp_bar_single(
    series: pd.Series, combined_metadata: pd.DataFrame
) -> go.Figure:
    """FIGURE BAR COMPLETENESS SINGLE STATION"""

    border = 100 - series

    station_name = combined_metadata.loc[series.name, "station_name"]

    data = []
    _bar = go.Bar(
        x=series.index.strftime("%b %Y"),
        y=series,
        name=f"{station_name}",
        marker_line_width=0,
        hovertemplate=f"{series.name} - {station_name}<br>%{{x}}<br><b>%{{y}}%</b><extra></extra>",
    )
    data.append(_bar)
    _border = go.Bar(
        x=series.index.strftime("%b %Y"),
        y=border,
        name="<i>(border)</i>",
        hoverinfo="skip",
        marker_line_width=0,
        legendrank=500,
        visible="legendonly",
        marker_color="DarkGray",
    )
    data.append(_border)

    layout = go.Layout(
        barmode="stack",
        hovermode="x",
        bargap=0,
        dragmode="zoom",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
        ),
        xaxis_title="<b>Date</b>",
        yaxis={
            "fixedrange": True,
            "title": "<b>Percentage (%)</b>",
            "range": [0, 100],
        },
        margin=dict(t=45, l=0, r=0, b=0),
    )

    return go.Figure(data, layout)


def figure_scatter(
    dataframe: pd.DataFrame, combined_metadata_rr: pd.DataFrame
) -> go.Figure:
    """FIGURE LINE/SCATTER STATIONS"""

    data = [
        go.Scatter(
            x=series.index,
            y=series,
            mode="lines",
            name=f"{stat_id} - {combined_metadata_rr.loc[stat_id, 'station_name']}",
        )
        for stat_id, series in dataframe.items()
    ]
    layout = go.Layout(
        hovermode="closest",
        xaxis_title="<b>Date</b>",
        yaxis_title="<b>Rainfall (mm)</b>",
        legend_title="<b>Stations</b>",
        margin=dict(t=25, l=0, r=0, b=0),
    )

    return go.Figure(data, layout)
