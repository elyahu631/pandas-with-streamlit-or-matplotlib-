# /data_visualization.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import Dict


def create_horizontal_bar_chart(data: pd.Series, x_label: str, y_label: str, chart_title: str) -> go.Figure:
    """
    The function `create_horizontal_bar_chart` takes in a pandas Series, x and y labels, and a chart
    title, and returns a horizontal bar chart using Plotly.

    :param data: The data parameter is a pandas Series object that contains the data for the horizontal
    bar chart. The index of the Series represents the categories or labels for the bars, and the values
    represent the corresponding values or heights of the bars
    :param x_label: The x_label parameter is the label for the x-axis of the bar chart. It represents
    the variable or category being measured or compared
    :param y_label: The y_label parameter represents the label for the y-axis of the horizontal bar
    chart. It is the label that will be displayed on the y-axis to indicate the variable being measured
    or represented by the bars in the chart
    :param chart_title: The title of the horizontal bar chart. It is a string that describes the purpose
    or content of the chart
    :return: a horizontal bar chart as a `go.Figure` object.
    """
    chart_data = pd.DataFrame({x_label: data.index, y_label: data.values})
    print(chart_data)
    bar_chart_fig = px.bar(
        chart_data,
        x=y_label,
        y=x_label,
        orientation='h',
        labels={y_label: y_label, x_label: x_label},
        title=chart_title,
        text=y_label
    )

    return bar_chart_fig


def create_pie_chart(tremp_type_counts: Dict[str, int]) -> go.Figure:
    """
    The function `create_pie_chart` takes in a dictionary of tremp type counts and returns a pie chart
    visualization of the data.

    :param tremp_type_counts: The `tremp_type_counts` parameter is a dictionary that contains the counts
    of different types of tremps. The keys of the dictionary represent the tremp types, and the values
    represent the corresponding counts
    :return: a pie chart figure object.
    """
    labels = list(tremp_type_counts.keys())
    values = list(tremp_type_counts.values())
    pie_fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    pie_fig.update_layout(title_text="Tremp Type Counts")
    return pie_fig


def create_grouped_bar_chart(gender_month_grouped: pd.DataFrame) -> go.Figure:
    """
    The function creates a grouped bar chart to visualize the gender distribution of hitchhikers per
    month.

    :param gender_month_grouped: The parameter `gender_month_grouped` is a DataFrame that contains the
    data for the grouped bar chart. It should have the following columns:
    :return: a bar chart figure object.
    """
    grouped_fig = go.Figure()

    for gender in gender_month_grouped['gender'].unique():
        gender_data = gender_month_grouped[gender_month_grouped['gender'] == gender]
        grouped_fig.add_trace(go.Bar(name=gender, x=gender_data['date'].astype(str), y=gender_data['counts'],
                                     text=gender_data['counts'], textposition='auto'))

    grouped_fig.update_layout(barmode='group', title_text="Gender Distribution for Hitchhikers per Month")

    return grouped_fig


def render_html(content: str, font_size: int = 20, font_family: str = 'Arial') -> None:
    """
    Renders HTML with the specified content and style.

    Parameters:
    content (str): The content to be displayed
    font_size (int, optional): Font size for the content. Defaults to 20.
    font_family (str, optional): Font family for the content. Defaults to 'Arial'.
    """
    st.markdown(f'<div style="font-size: {font_size}px; font-family: {font_family};"> {content}</div>',
                unsafe_allow_html=True)


def display_general_statistics(total_hitchhikers: int, avg_people_per_tremp: str, total_tremps: int) -> None:
    """
    Display general statistics using Streamlit.

    Parameters:
    total_hitchhikers, avg_people_per_tremp, total_tremps (int): Integer values for display in general statistics
    """
    st.header("General Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Total Hitchhikers:")
        render_html(f'🙋‍♂️ {total_hitchhikers}')

    with col2:
        st.subheader("Avg People per Tremp:")
        render_html(f'👥 {avg_people_per_tremp}')

    with col3:
        st.subheader("Total Tremps:")
        render_html(f'🚗 {total_tremps}')


def display_top_statistics(top_drivers: pd.Series, top_routes: pd.Series, top_hours: pd.Series) -> None:
    """
    Display top statistics charts using Streamlit.

    Parameters:
    top_drivers, top_tracks, top_hours (DataFrames): DataFrames for displaying top statistics charts
    """
    st.header("Top Statistics")
    col1, col2 = st.columns(2)

    with col1:
        top_drivers_chart = create_horizontal_bar_chart(top_drivers, 'Driver', 'Total Rides', 'Top 5 Drivers')
        st.plotly_chart(top_drivers_chart)

    with col2:
        top_tracks_chart = create_horizontal_bar_chart(top_routes, 'Route', 'Total Rides', 'Top 5 Routes')
        st.plotly_chart(top_tracks_chart)

    top_hours_chart = create_horizontal_bar_chart(top_hours, 'Hour', 'Total Rides', 'Top 5 Hours')
    st.plotly_chart(top_hours_chart)


def display_tremp_and_gender(tremp_type_counts: Dict[str, int], gender_grouped: pd.DataFrame) -> None:
    """
    Display tremp types and gender distribution charts using Streamlit.

    Parameters:
    tremp_type_counts, gender_grouped (DataFrames): DataFrames for displaying pie and bar charts respectively
    """
    st.header("Tremp Types and Gender Distribution")
    col1, col2 = st.columns(2)

    with col1:
        tremp_type_counts_pie_chart = create_pie_chart(tremp_type_counts)
        st.plotly_chart(tremp_type_counts_pie_chart)

    with col2:
        fig = create_grouped_bar_chart(gender_grouped)
        st.plotly_chart(fig)


def display_data(
        df: pd.DataFrame,
        total_hitchhikers: int,
        avg_people_per_tremp: str,
        total_tremps: int,
        top_drivers: pd.Series,
        top_routes: pd.Series,
        top_hours: pd.Series,
        tremp_type_counts: Dict[str, int],
        gender_grouped: pd.DataFrame) -> None:
    """
    This function takes in several parameters and displays data using the Streamlit library.

    Parameters:
    df (DataFrame): The dataframe to display
    tremp_type, from_route, to_route, creator, user_in_tremp (list): Lists used for filtering the dataframe
    total_hitchhikers, avg_people_per_tremp, total_tremps (int): Integer values for display in general statistics
    top_drivers, top_tracks, top_hours (DataFrames): DataFrames for displaying top statistics charts
    tremp_type_counts, gender_grouped (DataFrames): DataFrames for displaying pie and bar charts respectively
    """
    # Set Streamlit configurations
    st.title(":car: TrempBoss Dashboard")

    # Display sections
    st.markdown("---")
    display_general_statistics(total_hitchhikers, avg_people_per_tremp, total_tremps)
    st.markdown("---")
    st.header("Tremp Data")
    st.dataframe(df)
    st.markdown("---")
    display_top_statistics(top_drivers, top_routes, top_hours)
    st.markdown("---")
    display_tremp_and_gender(tremp_type_counts, gender_grouped)

    # Hide Streamlit style
    hide_st_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                    </style>
                    """
    st.markdown(hide_st_style, unsafe_allow_html=True)
