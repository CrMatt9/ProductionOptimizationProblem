from typing import List, Tuple, Dict

from pyomo.core import Constraint

from src.constraints_builders.base_constraint import BaseConstraint
from src.utils import (
    build_single_material_equipment_formula_time_index,
)


class ProductionConstraintsBuilder(BaseConstraint):
    def __init__(
        self,
        materials: List[str],
        t0: int,
        tmax: int,
        all_equipment: List[str],
        formulas: List[str],
    ):
        super().__init__(materials, t0, tmax)
        self.all_equipment = all_equipment
        self.formulas = formulas

    def no_production_at_t0(self):
        """
        TODO
        :return:
        """

        def rule(model, material_t0_index):
            return model.production[material_t0_index] == 0

        return Constraint(
            self.all_materials_t0_index,
            rule=rule,
            name="no_production_at_t0",
        )

    def production_doesnt_exceed_capacity(
        self, max_capacity: Dict[Tuple[str, str], int]
    ):
        """
        TODO
        :return:
        """

        def rule(
            model,
            equipment: str,
            formula: str,
            max_capacity: Dict[Tuple[str, str], int],
        ):
            return (
                sum(
                    model.production[
                        build_single_material_equipment_formula_time_index(
                            material=material,
                            equipment=equipment,
                            formula=formula,
                            time=t,
                        )
                    ]
                    for material in self.materials
                    for t in range(self.t0, self.tmax + 1)
                )
                <= max_capacity[
                    (
                        equipment,
                        formula,
                    )
                ]
            )

        return Constraint(
            self.all_equipment,
            self.formulas,
            max_capacity,
            rule=rule,
            name="production_doesnt_exceed_capacity",
        )
