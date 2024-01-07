from typing import Set

from pyomo.core import Constraint

from src.constraints_builders.base_constraint import BaseConstraint


class PurchasingConstraintsBuilder(BaseConstraint):
    def only_components_can_be_purchased(self, all_parent_materials: Set[str]):
        """
        Constraint to force only externally procured materials are being purchased externally.
        The other must be produced
        :param all_parent_materials: Set of all materials which are being produced in-house
        :return: Pyomo Constraint
        """
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

    def no_purchasing_when_factory_is_closed(self):
        """
        Constraint to assert nothing is purchased when factory is not operating
        :return: Pyomo Constraint
        """

        def rule(model, material: str, time: int):
            hour_from_day = time % 24
            if hour_from_day < 8 or hour_from_day > 20:
                return model.purchased_quantity[material, time] == 0
            return Constraint.Skip

        return Constraint(
            self.all_materials_all_time_indexes,
            rule=rule,
            name="no_purchasing_when_factory_is_closed",
        )
