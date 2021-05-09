import streamlit as st
import pandas as pd
from folium import plugins
import numpy as np
import matplotlib.pyplot as plt
import folium
import altair as alt
import pydeck as deck
import time
from streamlit_folium import folium_static

def doc(f):
    rl_vio = pd.read_csv("https://gist.githubusercontent.com/siyuduan6/19de7046dbc21673b8f927bb24ad1195/raw/655a655c5068d349e9fccb8a2abd54b59c6073af/crashes.csv")
    rl_vio1 = pd.read_csv("https://gist.githubusercontent.com/siyuduan6/4e46bffd955eb7d0fad85d03a7b25729/raw/4071e08a6521225856ac4ee837e71b1eb88ef7c1/red_light_violation.csv")
    rl_vio2 = pd.read_csv("https://gist.githubusercontent.com/siyuduan6/29203a998eda61848c67335d22846219/raw/557ceedb4d008752a3113a9455d4c525a1663920/Speed_Camera_Violations.csv", 
                          engine='python', encoding='utf-8', error_bad_lines=False)
    rl_lo = pd.read_csv("https://data.cityofchicago.org/api/views/7mgr-iety/rows.csv?accessType=DOWNLOAD")
    s_loc =pd.read_csv("https://data.cityofchicago.org/api/views/4i42-qv3h/rows.csv?accessType=DOWNLOAD")
    s_loc["ADDRESS"] = s_loc["ADDRESS"].str.split("(",expand=True).iloc[:,0]
    r_la = list(rl_lo["LATITUDE"])
    r_lo = list(rl_lo["LONGITUDE"])
    file_list = [rl_vio, rl_vio1, rl_vio2, rl_lo, s_loc, r_la, r_lo]
    return file_list[f]

def chicago_map():
    latitude = 41.8781
    longitude = -87.6298
    chi_m = folium.Map(location=[latitude, longitude], zoom_start=12, tiles='OpenStreetMap')
    return folium_static(chi_m)

def icon_adder(df, color, shape, info):
    latitude = 41.8781
    longitude = -87.6298
    chi_map = folium.Map(location=[latitude, longitude], zoom_start=12, tiles='OpenStreetMap')
    r_la = list(df["LATITUDE"])
    r_lo = list(df["LONGITUDE"])
    labels = list(info)
    incidents = folium.map.FeatureGroup(opacity=0.5)
    for la, lo, label in zip(r_la, r_lo, labels):
        folium.Marker([la, lo],popup =label,icon=folium.Icon(color = color, icon = shape), tooltip="Show me").add_to(incidents)
    chi_map.add_child(incidents)

    return folium_static(chi_map)

def icon_adder_re(map1, df2, color2, shape2, info2):
    r_la = list(df2["LATITUDE"])
    r_lo = list(df2["LONGITUDE"])
    labels = list(info2)
    incidents = folium.map.FeatureGroup(opacity=0.5)
    for la, lo, label in zip(r_la, r_lo, labels):
        folium.Marker([la, lo],popup =label,icon=folium.Icon(color = color2, icon = shape2), tooltip="Show me").add_to(incidents)
    map1.add_child(incidents)

    return folium_static(map1)
    

def point_adder(df, info):
    latitude = 41.8781
    longitude = -87.6298
    chi_map1 = folium.Map(location=[latitude, longitude], zoom_start=12,tiles='OpenStreetMap')
    r_la = list(df["LATITUDE"])
    r_lo = list(df["LONGITUDE"])
    labels = list(info)
    incidents = plugins.MarkerCluster().add_to(chi_map1)
    for la, lo, label in zip(r_la, r_lo, labels):
        folium.Marker([la, lo],popup =label,icon=None, tooltip="Show me").add_to(incidents)
    chi_map1.add_child(incidents)
    return folium_static(chi_map1)

def year_pick():
    rl_vio = doc(0)
    crash = rl_vio[rl_vio["YEAR"] > 2015]
    year_list = [2016, 2017, 2018, 2019, 2020, 2021]
    file = crash[crash["YEAR"]==2020].dropna(subset=["LOCATION"])
    options = st.sidebar.multiselect('View Car Crash by Year',year_list)
    if options:
        file = crash[crash["YEAR"]==options].dropna(subset=["LOCATION"])
    return point_adder(file, file["LOCATION"])


def vio_year():
    rl_vio1 = doc(1)
    rl_vio2 = doc(2)
    year = st.select_slider("Year", options=[2015, 2016, 2017, 2018, 2019, 2020], value=2020)
    vio1 = rl_vio1[rl_vio1["YEAR"] == year].groupby("MONTH")["VIOLATIONS"].sum()
    vio2 = rl_vio2[rl_vio2["YEAR"] == year].groupby("MONTH")["VIOLATIONS"].sum()
    vio = pd.DataFrame(vio1).merge(pd.DataFrame(vio2), left_index=True, right_index=True).rename(
        columns={"VIOLATIONS_x": "Red Light", "VIOLATIONS_y": "Speed"})
    fig = plt.figure(figsize=(8, 4))  # Create matplotlib figure
    ax = fig.add_subplot(111)  # Create matplotlib axes
    ax2 = ax.twinx()  # Create another axes that shares the same x-axis as ax.
    width = 0.8
    vio.plot(kind='bar', ax=ax, width=width, rot=0, cmap='tab10')
    ax.set_ylabel('Red Light Violation Cases')
    ax2.set_ylabel('Speed Violation Cases')
    ax.set_xlabel("Month")
    plt.grid(False)
    plt.xticks(rotation=45)
    return fig


def stack_bar_chart():
    rl_vio = doc(0)
    source = rl_vio[rl_vio["YEAR"] > 2015]
    crash_type = ["FAILING TO REDUCE SPEED TO AVOID CRASH",
                  "FAILING TO YIELD RIGHT-OF-WAY",
                  "FOLLOWING TOO CLOSELY",
                  "IMPROPER LANE USAGE", "IMPROPER OVERTAKING/PASSING"]
    cha = alt.Chart(source).mark_bar(size=20).encode(
        alt.Y('YEAR'),
        alt.X('count(CRASH_RECORD_ID)'),
        color="PRIM_CONTRIBUTORY_CAUSE",
        order=alt.Order(
            # Sort the segments of the bars by this field
            'PRIM_CONTRIBUTORY_CAUSE',
            sort='ascending'
        )).transform_filter(
        alt.FieldOneOfPredicate(field='PRIM_CONTRIBUTORY_CAUSE', oneOf=crash_type)
    ).interactive()

    select1 = st.sidebar.multiselect("Choose the crash type: ",crash_type)
    select2 = st.sidebar.multiselect("Choose the year: ",source["YEAR"].astype("int").unique())
    select3 = st.sidebar.multiselect("Choose the month:",source["MONTH"].astype("int").unique())
    if select1 in crash_type:
        cha = alt.Chart(source).mark_bar().encode(
            y='YEAR',
            x='count(CRASH_RECORD_ID)'
            ).transform_filter(
            alt.datum.PRIM_CONTRIBUTORY_CAUSE == select1
        )
        if select2:
            cha = alt.Chart(source).mark_bar().encode(
                y='MONTH',
                x='count(CRASH_RECORD_ID)'
            ).transform_filter(
                (alt.datum.PRIM_CONTRIBUTORY_CAUSE == select1) & (alt.datum.YEAR == select2)&
                (alt.FieldOneOfPredicate(field='MONTH', oneOf=select3))
            )
    return cha

def summary():
    rl_vio = doc(0)
    source = rl_vio[rl_vio["YEAR"] > 2015]
    crash_type = ["FAILING TO REDUCE SPEED TO AVOID CRASH",
                  "FAILING TO YIELD RIGHT-OF-WAY",
                  "FOLLOWING TOO CLOSELY",
                  "IMPROPER LANE USAGE", "IMPROPER OVERTAKING/PASSING"]
    cha = alt.Chart(source).mark_bar(size = 20).encode(
        alt.X('YEAR'),
        alt.Y('count(CRASH_RECORD_ID)'),
        row="PRIM_CONTRIBUTORY_CAUSE",
        column="DAMAGE"
    ).transform_filter(
        alt.FieldOneOfPredicate(field='PRIM_CONTRIBUTORY_CAUSE', oneOf=crash_type)
    ).interactive()

    alt.data_transformers.enable('default', max_rows=None)
    source1 = doc(1)
    source2 = doc(2)
    selection = alt.selection_interval()

    scale = alt.Scale(domain=[2015, 2016, 2017, 2018, 2019, 2020],
                      range=["#e7ba52", "#c7c7c7", "#aec7e8", "#659CCA", "#1f77b4", "#9467bd"])
    color = alt.condition(selection,
                          alt.Color('YEAR:O', scale=scale),
                          alt.value('darkgray'))
    rl = alt.Chart(source1).mark_bar(size=20).encode(
        alt.Tooltip(["YEAR:O", "MONTH:O", "sum(VIOLATIONS):Q"]),
        alt.X('MONTH',
              axis=alt.Axis(grid=False)),
        alt.Y('sum(VIOLATIONS):Q', title="Red Light Violation Number", axis=alt.Axis(grid=False)),
        color=color
    )

    speed = alt.Chart(source2).mark_bar(size=20).encode(
        alt.Tooltip(["YEAR:O", "MONTH:O", "sum(VIOLATIONS):Q"]),
        alt.X('MONTH', axis=alt.Axis(grid=False)),
        alt.Y('sum(VIOLATIONS):Q', title="Speed Violation Number", axis=alt.Axis(grid=False)),
        color=color
    )
    legend = alt.Chart(source1).mark_rect().encode(
        alt.Y('YEAR:O'),
        color=color
    ).add_selection(
        selection
    )
    vio = alt.hconcat(
        rl,
        speed, legend,
        title="Summary of Violations: Red Light Violations and Speed Violations"
    )
    sum = alt.vconcat(
        cha,
        vio,
        title="Summary of Car Crash Accidents"
    )
    return sum




def int_vega():
    rl_vio = doc(0)
    source = rl_vio[rl_vio["YEAR"] > 2015]
    source2 = source.dropna(subset=["INJURIES_TOTAL"])
    scale = alt.Scale(domain=[2016, 2017, 2018, 2019, 2020, 2021],
                      range=["#e7ba52", "#c7c7c7", "#aec7e8", "#659CCA", "#1f77b4", "#9467bd"])
    color = alt.Color('YEAR:O', scale=scale)
    click = alt.selection_multi(encodings=['color'])
    brush = alt.selection_interval()

    # Top panel is scatter plot of temperature vs time
    points = alt.Chart(source).mark_point().encode(
        alt.Tooltip(["YEAR:O", "MONTH:O", "count(CRASH_RECORD_ID):Q", "sum(INJURIES_TOTALL):Q"]),
        alt.X('MONTH:O', title='Month',
              axis=alt.Axis(
                  offset=10,
                  labelAngle=0,
                  ticks=True,
                  minExtent=30,
                  grid=False
              )
              ),
        alt.Y('count(CRASH_RECORD_ID):Q',
              scale=alt.Scale(domain=[0, 200]),
              axis=alt.Axis(
                  offset=10,
                  ticks=True,
                  minExtent=30,
                  grid=False,
              )),
        color=alt.condition(brush, color, alt.value('darkgray')),
        size=alt.SizeValue(75)

    ).properties(
        width=550,
        height=300,
    ).add_selection(
        brush
    ).transform_filter(
        click
    )

    lines = alt.Chart(source2).mark_circle().encode(
        alt.Tooltip(["YEAR:O", "MONTH:O", "count(CRASH_RECORD_ID):Q", "sum(INJURIES_TOTAL):Q"]),
        alt.X('MONTH:O',
              axis=alt.Axis(
                  offset=10,
                  ticks=True,
                  labelAngle=0,
                  minExtent=30,
                  grid=False
              )),
        alt.Y("sum(INJURIES_TOTAL):Q",
              title="Injured Number",
              axis=alt.Axis(
                  offset=10,
                  ticks=True,
                  minExtent=30,
                  grid=False,
              )), color=alt.condition(brush, color, alt.value('red')),
        size=alt.SizeValue(75)
    ).transform_filter(
        brush
    ).properties(
        width=550,
    ).add_selection(
        click
    )
    vega = alt.hconcat(
        points,
        lines,
        title="Cases VS Injured"
    )
    return vega

if __name__ == '__main__':
    st.title(" Welcome to Drive Safe in Chicago")
    st.header(" Locations of Traffic Cameras")
    rl = doc(3)
    s = doc(4)
    sc = st.sidebar.checkbox("Want to see the speed camera location?", True)
    rlc = st.sidebar.checkbox("Want to see the red light camera location?", True)
    if rlc and not sc:
        chi_m = icon_adder(rl,"red","info-sign", rl["INTERSECTION"])
    elif sc and not rlc:
        chi_m = icon_adder(s,"blue","glyphicon glyphicon-warning-sign",s["ADDRESS"])
    elif sc and rlc:
        chi_rl = icon_adder(rl,"red","info-sign", rl["INTERSECTION"])
        chi_m = icon_adder_re(chi_rl, s,"blue","glyphicon glyphicon-warning-sign",s["ADDRESS"])
    else:
        chi_m = chicago_map()  
    st.write(chi_m)
    st.header(" Car Crash Accidents in Chicago ")
    st.write(year_pick())
    st.header("*Summary*")
    st.write(summary())
    st.text("Violation Cases in Chicago Per Month")
    vio = vio_year()
    st.write(vio)
    st.text("Top 5 Causes of Car Crash Accident")
    st.write(stack_bar_chart())
    st.text("Crashes and Injures in the same period")
    st.write(int_vega())

