from typing import Tuple, List

from pyomo.core import Constraint

from src.bills_of_materials import Bom
from src.constraints_builders.base_constraint import BaseConstraint
from src.utils import build_single_material_equipment_formula_time_index


class FlowConstraintsBuilder(BaseConstraint):
    def __init__(
        self,
        materials: List[str],
        t0: int,
        tmax: int,
        all_equipment: List[str],
        formulas: List[str],
        bom: Bom,
    ):
        super().__init__(materials, t0, tmax)
        self.all_equipment = all_equipment
        self.formulas = formulas
        self.bom = bom

    def material_flow_balance(
        self,
    ):
        def rule(
            model,
            material: str,
            t: int,
        ):
            if t == self.tmax:
                return Constraint.Skip

            material_time_index = (material, t)
            inventory_quantity_tip1 = model.inventory_quantity[(material, t + 1)]

            inventory_quantity_ti = model.inventory_quantity[material_time_index]

            production_ti = sum(
                model.production[
                    build_single_material_equipment_formula_time_index(
                        material=material,
                        equipment=equipment,
                        formula=formula,
                        time=t,
                    )
                ]
                for equipment in self.all_equipment
                for formula in self.formulas
            )
            parent_production_ti = sum(
                self.bom.get_required_quantity(
                    formula=formula,
                    parent_material=parent_material,
                    children_material=material,
                )
                * model.production[
                    build_single_material_equipment_formula_time_index(
                        material=parent_material,
                        equipment=equipment,
                        formula=formula,
                        time=t,
                    )
                ]
                for parent_material in self.bom.all_parent_materials
                for formula in self.formulas
                for equipment in self.all_equipment
            )

            filled_demand_ti = model.filled_demand[material_time_index]

            purchased_quantity = model.purchased_quantity[material_time_index]

            return (
                inventory_quantity_tip1
                == inventory_quantity_ti
                + purchased_quantity
                + production_ti
                - parent_production_ti
                - filled_demand_ti
            )

        return Constraint(
            self.all_materials_all_time_indexes,
            rule=rule,
            name="sc_main_equation_constraint",
        )
