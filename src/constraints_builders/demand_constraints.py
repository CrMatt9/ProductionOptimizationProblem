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

    def demand_is_filled_only_at_concrete_time_in_a_day(self, demand_filling_time: int):
        """
        TODO
        :param demand_filling_time:
        :return:
        """

        def rule(model, material, t):
            if t % 24 != demand_filling_time:
                return model.filled_demand[(material, t)] == 0
            return Constraint.Skip

        return Constraint(
            set(self.all_materials_all_time_indexes),
            rule=rule,
            name="demand_is_filled_only_at_concrete_time_in_a_day",
        )

    def filled_demand_loe_than_demand(
        self,
    ):
        """
        TODO
        :return:
        """

        def rule(model, material, t):
            material_t_index = (material, t)
            return model.filled_demand[material_t_index] <= self.demand.get(
                material_t_index, 0
            )

        return Constraint(
            self.all_materials_all_time_indexes,
            rule=rule,
            name="filled_demand_loe_than_demand",
        )
