# /initialize.py
import streamlit as st

from data_processing import (load_data, transform_data, calculate_total_statistics, calculate_top_drivers,
                             calculate_top_routes, calculate_top_hours, calculate_participation_counts_by_tremp_type,
                             group_by_gender_and_month)
from data_visualization import (display_data)
from sidebar import sidebar_upload, sidebar_filters, filter_data

import constants_joined_cols_names as const


def init_statistic_bord():
    """
    The function `init_statistic_bord()` initializes the statistic board by loading data, applying
    filters, calculating statistics, and displaying the data.
    """
    st.set_page_config(page_title="TrempBoss DashBoard", page_icon=":car:", layout="wide")
    uploaded_file = sidebar_upload()
    df_tremps, df_users, df_users_in_tremp = load_data(uploaded_file)

    # This code block checks if the variables `df_tremps`, `df_users`, and `df_users_in_tremp` are not
    # None. If all three variables are not None, it proceeds to perform data transformation,
    # filtering, and calculations on the data. It then displays the data using the `display_data`
    # function.
    if df_tremps is not None and df_users is not None and df_users_in_tremp is not None:
        df = transform_data(df_tremps, df_users, df_users_in_tremp)
        tremp_type, from_route, to_route, creator, user_in_tremp, start_date, end_date = sidebar_filters(df)
        df = filter_data(df, tremp_type, from_route, to_route, creator, user_in_tremp, start_date, end_date)

        total_hitchhikers, avg_people_per_tremp, total_tremps = calculate_total_statistics(df, df_users_in_tremp)
        top_drivers = calculate_top_drivers(df, df_users_in_tremp, df_users)
        top_tracks = calculate_top_routes(df)
        top_hours = calculate_top_hours(df)
        tremp_type_counts = calculate_participation_counts_by_tremp_type(df, df_users_in_tremp)
        gender_grouped = group_by_gender_and_month(df_users, df_users_in_tremp, df)

        # selecting specific columns from the DataFrame `df` and assigning the result back to `df`.
        df = df[[const.TREMP_ID_COLUMN, const.TREMP_TYPE_COLUMN, const.TREMP_DATE_COLUMN, const.TREMP_TIME_COLUMN,
                 const.SEATS_AMOUNT_COLUMN, const.FROM_ROUTE_COLUMN, const.TO_ROUTE_COLUMN,
                 const.USERS_IN_TREMP_COLUMN, const.CREATOR_COLUMN]]

        display_data(df, total_hitchhikers,
                     avg_people_per_tremp, total_tremps, top_drivers, top_tracks, top_hours, tremp_type_counts,
                     gender_grouped)
    else:
        st.error("Please upload an Excel file.")
