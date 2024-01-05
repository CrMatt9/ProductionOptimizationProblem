from typing import List, Tuple, Dict

from pyomo.core import Constraint

from src.constraints_builders.base_constraint import BaseConstraint
from src.utils import (
    build_single_material_equipment_formula_time_index,
    build_material_equipment_formula_time_indexes,
    build_equipment_formula_time_indexes,
    build_equipment_time_indexes,
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
        self.material_equipment_formula_time_indexes = (
            build_material_equipment_formula_time_indexes(
                materials=self.materials,
                all_equipment=self.all_equipment,
                formulas=self.formulas,
                t0=self.t0,
                tmax=self.tmax,
            )
        )

        self.equipment_formula_time_indexes = build_equipment_formula_time_indexes(
            all_equipment=self.all_equipment,
            formulas=self.formulas,
            t0=self.t0,
            tmax=self.tmax,
        )

        self.equipment_time_indexes = build_equipment_time_indexes(
            all_equipment=self.all_equipment,
            t0=self.t0,
            tmax=self.tmax,
        )

    def no_production_when_factory_is_closed(self):
        """
        TODO
        :return:
        """

        def rule(model, material: str, equipment: str, formula: str, time: int):
            hour_from_day = time % 24
            if hour_from_day < 8 or hour_from_day > 20:
                return model.production[(material, equipment, formula, time)] == 0
            return Constraint.Skip

        return Constraint(
            self.material_equipment_formula_time_indexes,
            rule=rule,
            name="no_production_when_factory_is_closed",
        )

    def production_doesnt_exceed_capacity(
        self, max_capacity: Dict[Tuple[str, str], int]
    ):
        """
        TODO
        :return:
        """

        def rule(model, equipment: str, formula: str, t: int):
            if (equipment, formula) in max_capacity:
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
                    )
                    <= max_capacity[
                        (
                            equipment,
                            formula,
                        )
                    ]
                )
            return Constraint.Skip

        return Constraint(
            self.equipment_formula_time_indexes,
            rule=rule,
            name="production_doesnt_exceed_capacity",
        )

    def max_continuous_production_time_limit(self, max_continuous_time: int):
        """
        TODO
        :return:
        """

        def rule(model, equipment: str, time: int):
            if time < self.tmax-max_continuous_time:
                return (
                    sum(
                        model.equipment_status[equipment, t]
                        for t in range(time, time + max_continuous_time + 1)
                    )
                    <= max_continuous_time
                )
            return Constraint.Skip

        return Constraint(
            self.equipment_time_indexes,
            rule=rule,
            name="max_continuous_production_time_limit",
        )
