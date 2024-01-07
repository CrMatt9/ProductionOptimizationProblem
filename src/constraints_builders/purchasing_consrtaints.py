from typing import Set

from pyomo.core import Constraint

from src.constraints_builders.base_constraint import BaseConstraint


class PurchasingConstraintsBuilder(BaseConstraint):
    def only_components_can_be_purchased(self, all_parent_materials: Set[str]):
        def rule(model, material, time):
            if material in all_parent_materials:
                return model.purchased_quantity[material, time] == 0
            else:
                return Constraint.Skip

        return Constraint(
            self.all_materials_all_time_indexes,
            rule=rule,
            name="only_components_can_be_purchased",
        )
