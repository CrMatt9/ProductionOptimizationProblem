from collections import namedtuple
from pathlib import Path
from typing import Union, Dict

import pandas as pd
from pandas import DataFrame, Series


def read_production_problem_excel_template(
    excel_file_path: Union[Path, str], sheets_names_mapping: Dict[str, str]
) -> Dict[str, DataFrame]:
    """
    Reads Excel file defined on data model (check doc folder to see it) and cleans it
    :param sheets_names_mapping: Mapping with the information of the tab names required with the actual names from
    the Excel provided.
    :param excel_file_path: Path where the data is read from.
    :return: Dictionary with table name as key and DataFrame as value
    """
    _required_data = [
        "bom",
        "finished_goods_md",
        "inventory",
        "components_md",
        "production_lines",
        "demand",
    ]
    _columns_renaming = {
        "material": "component",
        "product": "manufactured_good",
        "proportion": "material_to_quantity",
        "product_material": "material",
        "demand": "finished_good",
    }
    assert all(sheet in sheets_names_mapping for sheet in _required_data)
    data = {
        sheet: pd.read_excel(excel_file_path, sheet_name=sheets_names_mapping[sheet])
        for sheet in _required_data
    }

    for table_name, table_data in data.items():
        table_data.columns = (
            table_data.columns.str.replace(r"\([^()]*\)", "", regex=True)
            .str.replace("(?<=[a-z])(?=[A-Z])(?=[/])", "_", regex=True)
            .str.rstrip()
            .str.replace(" ", "_")
            .str.replace(".", "")
            .str.replace("/", "")
            .str.lower()
        )
        data[table_name] = table_data.rename(columns=_columns_renaming)
    return data


def create_mapping_dictionary_from_two_columns(df, column_key, column_value) -> dict:
    """
    From two columns of a DataFrame creates a dictionary which maps the values
    :param df: DataFrame
    :param column_key: Column data which will be converted to Dictionary keys
    :param column_value: Column data which will be converted to Dictionary values
    :return: In case data is 1:1 or *:1 returns a Dict of value:value,
     if it is 1:* the result will be value:tuple(values)
    """
    series = Series(
        df[column_value].values,
        index=df[column_key],
    )
    if any(series.index.duplicated()):
        return series.groupby(level=0).agg(list).to_dict()
    else:
        return series.to_dict()


def unify_columns_into_tuple(*args):
    """
    Unifies multiple columns in a tuple as (col1_value, col2_value, col3_value,...)
    :param args: DataFrame columns
    :return: Series
    """
    return tuple(zip(*args))


def create_costs(components_md: DataFrame, production_costs: DataFrame) -> namedtuple:
    """
    Based on given data generates a named tuple with all the costs mappings inside
    :param components_md: DataFrane with components data
    :param production_costs: DataFrane with production costs information
    :return: NamedTuple containing Dictionaries of all mappings
    """
    costs_builder = namedtuple("Costs", "inventory purchase production")

    inventory_costs_dict = create_mapping_dictionary_from_two_columns(
        df=components_md,
        column_key="component",
        column_value="inventory_cost",
    )
    purchase_costs_dict = create_mapping_dictionary_from_two_columns(
        df=components_md,
        column_key="component",
        column_value="purchase_cost",
    )
    production_costs_dict = create_mapping_dictionary_from_two_columns(
        df=production_costs,
        column_key="equipment_formula",
        column_value="operation_cost",
    )

    costs = costs_builder(
        inventory=inventory_costs_dict,
        purchase=purchase_costs_dict,
        production=production_costs_dict,
    )

    return costs
