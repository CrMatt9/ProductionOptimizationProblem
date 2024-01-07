from typing import List, Tuple, Dict, Set

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
        minimum_units_in_batch: int,
    ):
        super().__init__(materials, t0, tmax)
        self.all_equipment = all_equipment
        self.formulas = formulas
        self.minimum_units_in_batch = minimum_units_in_batch

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

    def components_cannot_be_produced(self, component_materials: Set[str]):
        """
        TODO
        :return:
        """

        def rule(model, material: str, equipment: str, formula: str, time: int):
            if material in component_materials:
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
            return sum(
                model.production[
                    build_single_material_equipment_formula_time_index(
                        material=material,
                        equipment=equipment,
                        formula=formula,
                        time=t,
                    )
                ]
                for material in self.materials
            ) * self.minimum_units_in_batch <= max_capacity.get(
                (
                    equipment,
                    formula,
                ),
                0,
            )

        return Constraint(
            self.equipment_formula_time_indexes,
            rule=rule,
            name="production_doesnt_exceed_capacity",
        )

    def equipment_status_loe_than_production(
        self,
    ):
        """
        TODO
        :return:
        """

        def rule(model, equipment: str, t: int):
            production_on_equipment_at_t = sum(
                model.production[
                    build_single_material_equipment_formula_time_index(
                        material=material,
                        equipment=equipment,
                        formula=formula,
                        time=t,
                    )
                ]
                for material in self.materials
                for formula in self.formulas
            )
            return model.equipment_status[equipment, t] <= production_on_equipment_at_t

        return Constraint(
            self.equipment_time_indexes,
            rule=rule,
            name="equipment_status_loe_than_production",
        )

    def equipment_status_is_active_when_producing(
        self,
    ):
        """
        TODO
        :return:
        """

        def rule(model, equipment: str, t: int):
            production_on_equipment_at_t = sum(
                model.production[
                    build_single_material_equipment_formula_time_index(
                        material=material,
                        equipment=equipment,
                        formula=formula,
                        time=t,
                    )
                ]
                for material in self.materials
                for formula in self.formulas
            )
            return (
                production_on_equipment_at_t
                <= model.equipment_status[equipment, t] * 1e8
            )

        return Constraint(
            self.equipment_time_indexes,
            rule=rule,
            name="equipment_status_is_active_when_producing",
        )

    def max_continuous_production_time_limit(self, max_continuous_time: int):
        """
        TODO
        :return:
        """

        def rule(model, equipment: str, time: int):
            if time < self.tmax - max_continuous_time:
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
