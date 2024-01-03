from typing import Dict, Tuple, List

from pyomo.core import Constraint

from src.constraints_builders.base_constraint import BaseConstraint


class DemandConstraintsBuilder(BaseConstraint):
    def __init__(
        self,
        materials: List[str],
        t0: int,
        tmax: int,
        demand: Dict[Tuple[str, int], int],
    ):
        super().__init__(materials, t0, tmax)
        self.demand = demand

    def no_filled_demand_at_t0(self):
        """
        TODO
        :return:
        """

        def rule(model, material_t0_index):
            return model.filled_demand[material_t0_index] == 0

        return Constraint(
            self.all_materials_t0_index,
            rule=rule,
            name="no_filled_demand_at_t0",
        )

    def filled_demand_loe_than_demand(
        self,
    ):
        """
        TODO
        :return:
        """

        def rule(model, material_t_index):
            if material_t_index in self.demand:
                return (
                    model.filled_demand[material_t_index]
                    <= self.demand[material_t_index]
                )
            return Constraint.Skip

        return Constraint(
            self.all_materials_all_time_indexes,
            rule=rule,
            name="filled_demand_loe_than_demand",
        )
