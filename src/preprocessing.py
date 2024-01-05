from collections import namedtuple
from pathlib import Path
from typing import Union, Dict

import pandas as pd
from pandas import DataFrame, Series


def read_production_problem_excel_template(
    excel_file_path: Union[Path, str], sheets_names_mapping: Dict[str, str]
) -> Dict[str, DataFrame]:
    """
    TODO
    :param sheets_names_mapping:
    :param excel_file_path:
    :return:
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
    TODO
    :param df:
    :param column_key:
    :param column_value:
    :return:
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
    return tuple(zip(*args))


def create_costs(components_md: DataFrame, production_costs: DataFrame) -> namedtuple:
    """
    TODO
    :param components_md:
    :param production_costs:
    :return:
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
