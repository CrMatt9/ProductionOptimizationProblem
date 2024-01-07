from typing import List

from pandas import DataFrame

from src.preprocessing import (
    unify_columns_into_tuple,
    create_mapping_dictionary_from_two_columns,
)


class Bom:
    def __init__(
        self,
        bom_data: DataFrame,
        formula_column_name="formula",
        parent_column_name="manufactured_good",
        children_column_name="component",
        children_to_parent_proportion_column_name="material_to_quantity",
    ):
        self._bom_data = bom_data
        self._bom_data["formula_parent_component"] = unify_columns_into_tuple(
            self._bom_data[formula_column_name],
            self._bom_data[parent_column_name],
            self._bom_data[children_column_name],
        )

        self._bom_raw = create_mapping_dictionary_from_two_columns(
            df=self._bom_data,
            column_key="formula_parent_component",
            column_value=children_to_parent_proportion_column_name,
        )

        # TODO check if required
        self.formula_column_name = formula_column_name
        self.parent_column_name = parent_column_name
        self.children_column_name = children_column_name
        self.children_to_parent_proportion_column_name = (
            children_to_parent_proportion_column_name
        )

    @property
    def all_parent_materials(self) -> List[str]:
        """
        TODO
        :return:
        """
        return self._bom_data[self.parent_column_name].unique().tolist()

    @property
    def all_component_materials(self) -> List[str]:
        """
        TODO
        :return:
        """
        return self._bom_data[self.children_column_name].unique().tolist()

    def get_required_quantity(
        self,
        formula: str,
        parent_material: str,
        children_material: str,
    ):
        """
        TODO
        :param formula:
        :param parent_material:
        :param children_material:
        :return:
        """
        return self._bom_raw.get((formula, parent_material, children_material), 0)
