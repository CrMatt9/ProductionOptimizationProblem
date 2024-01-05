from typing import Dict

from pyomo.core import Constraint

from src.constraints_builders.base_constraint import BaseConstraint
from src.utils import build_material_time_indexes


class InventoryConstraintsBuilder(BaseConstraint):

    def set_initial_inventory(self, initial_inventory: Dict[str, float]):
        def rule(model, material):
            material_index = build_material_time_indexes(
                materials=[
                    material,
                ],
                t0=self.t0,
                tmax=self.t0,
            )[0]
            return (
                model.inventory_quantity[material_index] == initial_inventory[material]
            )

        return Constraint(
            self.materials,
            rule=rule,
            name="initial_inventory_constraint",
        )

    def inventory_tmax_goe_than_safety_stock(self, safety_stock: Dict[str, float]):
        def rule(model, material):
            material_tmax_index = build_material_time_indexes(
                materials=[
                    material,
                ],
                t0=self.tmax,
                tmax=self.tmax,
            )
            return (
                model.inventory_quantity[material_tmax_index] >= safety_stock[material]
            )

        return Constraint(
            self.materials,
            rule=rule,
            name="inventory_at_tmax_goe_than_safety_stock",
        )
