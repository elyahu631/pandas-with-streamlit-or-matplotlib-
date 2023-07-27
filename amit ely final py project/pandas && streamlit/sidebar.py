# /sidebar.py
from typing import Tuple
import pandas as pd
import datetime
import streamlit as st
import constants_joined_cols_names as const

DATE_COLUMN = const.DATE_COLUMN


def sidebar_upload():
    """
    The function `sidebar_upload` creates a sidebar in a Streamlit app where users can upload an Excel
    file.
    :return: The function `sidebar_upload` returns the uploaded file object.
    """
    st.sidebar.header("Please Upload Excel File Here:")
    uploaded_file = st.sidebar.file_uploader("Choose a XLSX file", type="xlsx")
    return uploaded_file


def sidebar_filters(df: pd.DataFrame) -> Tuple[str, str, str, str, str, datetime.date, datetime.date]:
    """
    The `sidebar_filters` function generates an interactive sidebar with various filter options 
    on a Streamlit application for a given dataframe `df`.

    It provides filter options based on unique values of 'tremp_type', and custom input options
    for 'from_route', 'to_route', 'creator', and 'user_in_tremp'. It also provides date range selection
    based on the minimum and maximum dates in the provided dataframe.
    """
     
    st.sidebar.header("Please Filter Here:")
    tremp_type = st.sidebar.selectbox(
        "Select Tremp Type:",
        options=['All'] + list(df["tremp_type"].unique()),
        index=0
    )
    from_route = st.sidebar.text_input("From Route:", "")
    to_route = st.sidebar.text_input("To Route:", "")
    creator = st.sidebar.text_input("Creator:", "")
    user_in_tremp = st.sidebar.text_input("User in Tremp:", "")

    # Date filter
    min_date = df[DATE_COLUMN].min().date()
    max_date = df[DATE_COLUMN].max().date()

    start_date = st.sidebar.date_input('Start date', min_date)
    end_date = st.sidebar.date_input('End date', max_date)

    return tremp_type, from_route, to_route, creator, user_in_tremp, start_date, end_date


def filter_data(df_filter, filter_tremp_type, filter_from_route, filter_to_route, filter_creator, filter_user_in_tremp,
                start_date, end_date):
    """
    The function `filter_data` filters a DataFrame based on various criteria such as tremp type, routes,
    creator, users in tremp, and date range.

    :return: the filtered dataframe, df_filter.
    """

    # only contain rows where the tremp_type is equal to filter_tremp_type.
    # If filter_tremp_type was "driver" for example, then df_filter will only
    # contain rows where the tremp_type is "driver".
    if filter_tremp_type != 'All':
        df_filter = df_filter[df_filter.tremp_type == filter_tremp_type]

    # where the 'from_route' column contains the 'filter_from_route' value.
    # The 'str.contains' method is used to check if 'filter_from_route' is in 'from_route' for each row.
    # The 'case=False' argument ensures the match is case-insensitive.
    # The 'na=False' argument ignores 'from_route' values that are NaN.
    if filter_from_route:
        df_filter = df_filter[df_filter.from_route.str.contains(filter_from_route, case=False, na=False)]

    if filter_to_route:
        df_filter = df_filter[df_filter.to_route.str.contains(filter_to_route, case=False, na=False)]

    if filter_creator:
        df_filter = df_filter[df_filter.creator.str.contains(filter_creator, case=False, na=False)]

    # The filtering process checks if the value of 'filter_user_in_tremp' exists
    # in the 'users_in_tremp' column for each row in the dataframe.
    if filter_user_in_tremp:
        user_in_tremp_condition = df_filter[const.USERS_IN_TREMP_COLUMN].apply(
            lambda users: filter_user_in_tremp in users)
        df_filter = df_filter[user_in_tremp_condition]

    # It selects rows where the 'date' column is greater than or equal to the `start_date` and
    # less than or equal to the `end_date`.
    start_date_mask = df_filter[DATE_COLUMN].dt.date >= start_date
    end_date_mask = df_filter[DATE_COLUMN].dt.date <= end_date
    df_filter = df_filter[start_date_mask & end_date_mask]

    df_filter = df_filter.reset_index(drop=True)

    return df_filter
