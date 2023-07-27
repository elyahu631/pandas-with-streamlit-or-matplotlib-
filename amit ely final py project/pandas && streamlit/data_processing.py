# /data_processing.py
import pandas as pd
import streamlit as st
from typing import Tuple, Optional
import constants_joined_cols_names as const

# col names in join-table / tremps / users_in_tremp
TREMP_ID_COLUMN = const.TREMP_ID_COLUMN

# col names in join-table (part of tremps-table)
USERS_IN_TREMP_COLUMN = const.USERS_IN_TREMP_COLUMN
TREMP_TYPE_COLUMN = const.TREMP_TYPE_COLUMN
SEATS_AMOUNT_COLUMN = const.SEATS_AMOUNT_COLUMN
TREMP_TIME_COLUMN = const.TREMP_TIME_COLUMN
FROM_ROUTE_COLUMN = const.FROM_ROUTE_COLUMN
TO_ROUTE_COLUMN = const.TO_ROUTE_COLUMN
CREATOR_COLUMN = const.CREATOR_COLUMN
DATE_COLUMN = const.DATE_COLUMN
TREMP_DATE_COLUMN = const.TREMP_DATE_COLUMN
ROUTES_COLUMN = const.ROUTES_COLUMN
# col names in users / users_in_tremp table
USER_ID_COLUMN = 'user_id'

# col names in users_in_tremp table
IS_TREMP_CREATOR_COLUMN = 'is_tremp_creator'

# col tremp_type data
TREMP_TYPES = ['driver', 'hitchhiker']

# col names in users table
GENDER_COLUMN = 'gender'
FULL_NAME_COLUMN = 'full_name'


def load_data(file_to_load: str) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    The function `load_data` loads data from an Excel file and returns three dataframes, or None if the
    file is not provided.
    
    :param file_to_load: The `file_to_load` parameter is a string that represents the file path of the
    Excel file to be loaded
    """

    if file_to_load:
        try:
            data_dict = pd.read_excel(file_to_load, sheet_name=None)
            return data_dict.get('tremps'), data_dict.get('users'), data_dict.get('users_in_tremps')  # same df[users]
        except Exception as e:
            st.error(f"Error loading data: {e}")
    return None, None, None


def transform_data(df_tremps: pd.DataFrame, df_users: pd.DataFrame, df_users_in_tremp: pd.DataFrame) -> pd.DataFrame:
    """
    Transform data from the tremps, users, and users_in_tremp dataframes for further processing and analysis.

    :param df_tremps: A DataFrame containing tremp data. Must include a 'date' column with date information. param
    :param df_users: A DataFrame containing user data. Must include 'user_id' and 'full_name' columns. param :param
    :param df_users_in_tremp: A DataFrame mapping users to tremps. Must include 'user_id' and 'is_tremp_creator'
    columns. :return: A DataFrame derived from df_tremps with additional columns for 'tremp_date', 'creator',
    and 'users_in_tremp'.
    """
    joined_df = df_tremps.copy()
    # df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])
    joined_df[TREMP_DATE_COLUMN] = joined_df[DATE_COLUMN].dt.date  # new column with only date component, no time

    df_users_in_tremp = merge_df(df_users_in_tremp, df_users[[USER_ID_COLUMN, FULL_NAME_COLUMN]], USER_ID_COLUMN)
    user_in_tremp = group_users_in_tremp(df_users_in_tremp)
    joined_df = merge_df(joined_df, user_in_tremp, TREMP_ID_COLUMN)

    # ensuring that every element in the USERS_IN_TREMP_COLUMN is a list.
    # If any element in that column is not a list, it gets replaced with an empty list
    joined_df[USERS_IN_TREMP_COLUMN] = joined_df[USERS_IN_TREMP_COLUMN]. \
        apply(lambda users_list: users_list if isinstance(users_list, list) else [])

    # Identify and add creator information to the dataframe
    creator = df_users_in_tremp[df_users_in_tremp[IS_TREMP_CREATOR_COLUMN]]
    joined_df = merge_df(joined_df, creator[[TREMP_ID_COLUMN, FULL_NAME_COLUMN]], TREMP_ID_COLUMN,
                         {FULL_NAME_COLUMN: CREATOR_COLUMN})

    joined_df[ROUTES_COLUMN] = df_tremps[FROM_ROUTE_COLUMN] + " to " + df_tremps[TO_ROUTE_COLUMN]

    return joined_df


def merge_df(df: pd.DataFrame, to_merge: pd.DataFrame, on: str,
             suffix_columns: Optional[dict[str, str]] = None) -> pd.DataFrame:
    """
    Merges two dataframes based on a specified column and optionally renames the merged columns.

    :param df: The main DataFrame that you want to merge with another DataFrame.
    :param to_merge: The DataFrame to merge with the main DataFrame.
    :param on: The column name(s) on which the two dataframes will be merged.
    :param suffix_columns: An optional dictionary that maps existing column names to their new names.
    :return: The merged DataFrame.
    """
    merged = df.merge(to_merge, on=on, how='left')

    if suffix_columns:
        merged = merged.rename(columns=suffix_columns)

    return merged


def group_users_in_tremp(df: pd.DataFrame) -> pd.DataFrame:
    """
    The function ` filters out the non-creator users from the input DataFrame df, groups them by tremp ID,
    and creates a list of names for each group. It then returns a new DataFrame where each row corresponds
    to a unique tremp ID and contains a list of non-creator usernames associated with that tremp ID.
    """
    # Filter out the creator users
    non_creator_users_df = df.loc[~df[IS_TREMP_CREATOR_COLUMN]]

    # Group by tremp ID and create a list of non-creator usernames for each tremp ID
    non_creator_users_grouped = non_creator_users_df.groupby(TREMP_ID_COLUMN)[FULL_NAME_COLUMN].apply(list)

    # Reset the index and assign a new column name to the list of names
    non_creator_users_grouped = non_creator_users_grouped.reset_index(name=USERS_IN_TREMP_COLUMN)

    return non_creator_users_grouped


def calculate_total_statistics(df_tremps: pd.DataFrame, df_users_in_tremp: pd.DataFrame) -> Tuple[int, str, int]:
    """
    The function calculates total statistics related to hitchhikers and tremps from two input
    dataframes.
    
    :param df_tremps: A pandas DataFrame containing information about tremps
    :param df_users_in_tremp: df_users_in_tremp is a pandas DataFrame that contains information about
    users participating in tremps. It likely includes columns such as user_id, tremp_id,
    and is_tremp_creator, among others
    :return: tuple containing three values:
    `total_hitchhikers`, `avg_people_per_tremp`, and `total_tremps`.
    """
    # Filter df_users_in_tremp dataframe
    tremp_ids = df_tremps[TREMP_ID_COLUMN].unique()
    df_users_in_tremp_filtered = df_users_in_tremp[df_users_in_tremp[TREMP_ID_COLUMN].isin(tremp_ids)]

    # Exclude rows where the user is the creator of the tremp
    non_creator_users_in_tremp = df_users_in_tremp_filtered[~df_users_in_tremp_filtered[IS_TREMP_CREATOR_COLUMN]]

    total_hitchhikers = calculate_total_hitchhikers(df_tremps, non_creator_users_in_tremp)
    total_tremps = non_creator_users_in_tremp[TREMP_ID_COLUMN].nunique()

    # Avoid division by zero and only format once
    avg_people_per_tremp = "{:.2f}".format(total_hitchhikers / total_tremps) if total_tremps != 0 else '0.00'

    return total_hitchhikers, avg_people_per_tremp, total_tremps


def calculate_total_hitchhikers(df_tremps: pd.DataFrame, non_creator_users_in_tremp: pd.DataFrame) -> int:
    """
    The function calculates the total number of hitchhikers by summing the number of non-creator users
    and the number of seats in hitchhiker tremps.
    """
    hitchhiker_tremps_with_non_creators = df_tremps[
        (df_tremps[TREMP_ID_COLUMN].isin(non_creator_users_in_tremp[TREMP_ID_COLUMN].unique())) &
        (df_tremps['tremp_type'] == 'hitchhiker')
        ]
    return non_creator_users_in_tremp.shape[0] + hitchhiker_tremps_with_non_creators['seats_amount'].sum()


def calculate_top(df: pd.DataFrame, column_name: str, top_count: int = 5) -> pd.Series:
    """
    The function calculates the top occurrences of a column in a DataFrame and returns the top items as
    a Series.
    """
    top_items = df[column_name].value_counts().nlargest(top_count).sort_values(ascending=True)
    return top_items


def filter_df_users_in_tremp(df_users_in_tremp, df_tremps, valid_driver_tremps, is_tremp_creator, tremp_type):
    """
    The function filters a DataFrame of users in tremps based on specified criteria.
    """
    tremps_of_type = df_tremps[df_tremps[TREMP_TYPE_COLUMN] == tremp_type][TREMP_ID_COLUMN]
    criteria = (
            (df_users_in_tremp[IS_TREMP_CREATOR_COLUMN] == is_tremp_creator) &
            df_users_in_tremp[TREMP_ID_COLUMN].isin(tremps_of_type) &
            df_users_in_tremp[TREMP_ID_COLUMN].isin(valid_driver_tremps)
    )
    return df_users_in_tremp[criteria]


def calculate_top_drivers(df_tremps: pd.DataFrame, df_users_in_tremp: pd.DataFrame,
                          df_users: pd.DataFrame) -> pd.Series:
    """
    The function `calculate_top_drivers` takes in three dataframes and returns a series of the top 5
    drivers based on the number of users they have in their tremps.    
    """
    # Find tremps that have more than one user
    valid_driver_tremps = df_users_in_tremp[TREMP_ID_COLUMN].value_counts()
    valid_driver_tremps = valid_driver_tremps[valid_driver_tremps > 1].index

    # Filter for 'driver' type tremps that have more than one user and is created by the driver
    df_users_in_tremp_drivers = filter_df_users_in_tremp(df_users_in_tremp, df_tremps, valid_driver_tremps, True,
                                                         TREMP_TYPES[0])
    # Filter for 'hitchhiker' type tremps that were not created by the user
    df_users_in_tremp_hitchhiker = filter_df_users_in_tremp(df_users_in_tremp, df_tremps, valid_driver_tremps, False,
                                                            TREMP_TYPES[1])
    # Combine driver and hitchhiker data
    df_all_drivers = pd.concat([df_users_in_tremp_drivers, df_users_in_tremp_hitchhiker])

    # Calculate top 5 drivers
    top_drivers = calculate_top(df_all_drivers, USER_ID_COLUMN)

    # Map user ID to full name
    user_map = df_users.set_index(USER_ID_COLUMN)[FULL_NAME_COLUMN]
    top_drivers.index = top_drivers.index.map(user_map)

    return top_drivers


def calculate_top_routes(df_tremps: pd.DataFrame) -> pd.Series:
    """
    The function calculates the top routes based on a DataFrame of tremps.
    :return: a pandas Series object, which contains the top routes calculated from the input DataFrame.
    """
    top_routes = calculate_top(df_tremps, ROUTES_COLUMN)
    return top_routes


def calculate_top_hours(df_tremps: pd.DataFrame) -> pd.Series:
    """
    The function calculates the top hours based on a DataFrame column   
    :param df_tremps: A pandas DataFrame containing data about tremps
    :return: a pandas Series object, which represents the top hours calculated from the input DataFrame.
    """
    rounded_hour_col = 'rounded_hour'

    df_tremps[rounded_hour_col] = df_tremps[TREMP_TIME_COLUMN].apply(
        lambda x: (x.hour + 1) if x.minute > 30 else x.hour)
    df_tremps[rounded_hour_col] %= 24
    top_hours = calculate_top(df_tremps, rounded_hour_col)
    df_tremps.drop(columns=[rounded_hour_col], inplace=True)

    # Convert the index to string type with specific format
    top_hours.index = top_hours.index.map(lambda x: '{:02d}:00'.format(x))

    return top_hours


def count_by_criteria(df: pd.DataFrame, is_creator: bool, tremp_ids_of_given_type: pd.Series) -> int:
    """
    The function counts the number of rows in a DataFrame that meet certain criteria based on whether
    the creator is specified and a given type of tremp ID.
    """
    criteria = (
            (df[IS_TREMP_CREATOR_COLUMN] == is_creator) &
            df[TREMP_ID_COLUMN].isin(tremp_ids_of_given_type)
    )
    return df[criteria].shape[0]


def count_by_tremp_type(df_tremps: pd.DataFrame, df_users_in_tremp: pd.DataFrame, tremp_type: str) -> Tuple[int, int]:
    """
    The function counts the number of creators and joiners in a given tremp type.
    """
    tremp_ids_of_given_type = df_tremps[df_tremps[TREMP_TYPE_COLUMN] == tremp_type][TREMP_ID_COLUMN]

    creators = count_by_criteria(df_users_in_tremp, True, tremp_ids_of_given_type)
    joiners = count_by_criteria(df_users_in_tremp, False, tremp_ids_of_given_type)

    return creators, joiners


def calculate_participation_counts_by_tremp_type(tremp_data: pd.DataFrame,
                                                 tremp_participation_data: pd.DataFrame) -> dict:
    """
    Calculates the number of tremp creators and joiners for each type of tremp.

    Parameters:
    tremp_data (pd.DataFrame): DataFrame containing information about each tremp.
    tremp_participation_data (pd.DataFrame): DataFrame containing information about user participation in each tremp.

    Returns:
    dict: A dictionary with counts of creators and joiners for each tremp type. Tremp types with zero counts are not
    included in the dictionary.
    """

    participation_counts_by_type = {}

    for tremp_type in TREMP_TYPES:
        creator_count, joiner_count = count_by_tremp_type(tremp_data, tremp_participation_data, tremp_type)
        participation_counts_by_type[f'{tremp_type.capitalize()} Creators'] = creator_count
        participation_counts_by_type[f'{tremp_type.capitalize()} Joiners'] = joiner_count

    # Remove entries where count is 0
    participation_counts_by_type = {tremp: count for tremp, count in participation_counts_by_type.items() if count != 0}

    return participation_counts_by_type


def group_by_gender_and_month(df_users: pd.DataFrame, df_users_in_tremp: pd.DataFrame,
                              df_tremps: pd.DataFrame) -> pd.DataFrame:
    """
    The function `group_by_gender_and_month` groups users by gender and month, based on their
    participation in tremps, and returns the counts for each gender-month combination for the last 12
    months.
    """

    merged = df_users_in_tremp.merge(df_tremps, on=TREMP_ID_COLUMN)
    merged = merged.merge(df_users, left_on=USER_ID_COLUMN, right_on=USER_ID_COLUMN)

    gender_month_grouped = merged.groupby([merged[DATE_COLUMN].dt.to_period('M'), GENDER_COLUMN]).size().reset_index(
        name='counts')

    # Filter the rows for the last 12 months
    last_month = gender_month_grouped[DATE_COLUMN].max()
    one_year_ago = last_month - 12
    filtered_gender_month_grouped = gender_month_grouped[gender_month_grouped[DATE_COLUMN] > one_year_ago]

    return filtered_gender_month_grouped
