from abc import ABC
from os import getenv
from typing import List, Dict, Tuple

from pyomo.core import Objective, maximize
from pyomo.opt import SolverFactory

from src.bills_of_materials import Bom
from src.constraints_builders.demand_constraints import DemandConstraintsBuilder
from src.constraints_builders.flow_constraints import FlowConstraintsBuilder
from src.constraints_builders.inventory_constraints import InventoryConstraintsBuilder
from src.constraints_builders.production_constraints import ProductionConstraintsBuilder
from src.optimizers.base_optimizer import BaseOptimizer
from src.utils import (
    build_material_time_indexes,
    build_single_material_equipment_formula_time_index,
    build_material_equipment_formula_time_indexes,
)
from src.variables import (
    ProductionVariable,
    InventoryVariable,
    FilledDemand,
    PurchasedQtyVariable,
)


class ManufacturingOptimizer(BaseOptimizer, ABC):
    def __init__(
        self,
        materials: List[str],
        all_equipment: List[str],
        formulas: List[str],
        simulation_duration: int,
        t0: int = 0,
        all_materials_all_time_indexes: List[Tuple[str, int]] = None,
        all_materials_t0_index: List[Tuple[str, int]] = None,
        material_equipment_formula_time_indexes: List[Tuple[str, str, str, int]] = None,
    ):
        # Simulation general info
        self.materials = materials
        self.all_equipment = all_equipment
        self.formulas = formulas
        self.tmax = simulation_duration
        self.t0 = t0

        # material time indexes
        self.all_materials_all_time_indexes = (
            all_materials_all_time_indexes
            if all_materials_all_time_indexes
            else build_material_time_indexes(
                materials=self.materials,
                t0=self.t0,
                tmax=self.tmax,
            )
        )
        self.all_materials_t0_index = (
            all_materials_t0_index
            if all_materials_t0_index
            else build_material_time_indexes(
                materials=self.materials,
                t0=self.t0,
                tmax=self.t0,
            )
        )
        self.material_equipment_formula_time_indexes = (
            material_equipment_formula_time_indexes
            if material_equipment_formula_time_indexes
            else build_material_equipment_formula_time_indexes(
                materials=self.materials,
                all_equipment=self.all_equipment,
                formulas=self.formulas,
                t0=self.t0,
                tmax=self.t0,
            )
        )

        # Variables
        self._production = None
        self._filled_demand = None
        self._inventory = None
        self._purchased_qty = None

        # Constraints
        self.initial_inventory = None
        self.inventory_tmax_goe_than_safety_stock = None

        self.no_production_at_t0 = None
        self.production_doesnt_exceed_capacity = None

        self.no_purchase_qty_at_t0 = None

        self.no_filled_demand_at_t0 = None
        self.filled_demand_loe_than_demand = None

        self.material_flow_balance = None

        # Objective Function
        self.objective = None

        # Optimizer Definition
        self.solver_path = getenv("SOLVER_PATH")
        self.solver_name = getenv("SOLVER_NAME")

    def build_model(
        self,
        initial_inventory: Dict[str, float],
        safety_stock: Dict[str, float],
        max_capacity: Dict[Tuple[str, str], int],
        demand: Dict[Tuple[str, int], int],
        bom: Bom,
        costs: Tuple[str, Dict[str, float]],
        selling_prices: Dict[str, float],
    ):
        self._create_variables()

        self._create_inventory_constraints(
            initial_inventory=initial_inventory, safety_stock=safety_stock
        )
        self._create_production_constraints(max_capacity=max_capacity)

        self._create_material_flow_balance_constraints(bom=bom)

        self._create_demand_constraints(demand=demand)

        self._build_objective_function(costs=costs, selling_prices=selling_prices)

    def _create_variables(self):
        self._production = ProductionVariable(self.material_equipment_formula_time_indexes)
        self._filled_demand = FilledDemand(self.all_materials_all_time_indexes)
        self._inventory = InventoryVariable(self.all_materials_all_time_indexes)
        self._purchased_qty = PurchasedQtyVariable(self.all_materials_all_time_indexes)

    def _create_inventory_constraints(
        self, initial_inventory: Dict[str, float], safety_stock: Dict[str, float]
    ):
        """
        TODO
        :param initial_inventory:
        :param safety_stock:
        :return:
        """
        inventory_constraints_builder = InventoryConstraintsBuilder(
            materials=self.materials,
            t0=self.t0,
            tmax=self.tmax,
        )

        self.initial_inventory = inventory_constraints_builder.set_initial_inventory(
            initial_inventory=initial_inventory
        )

        self.inventory_tmax_goe_than_safety_stock = (
            inventory_constraints_builder.inventory_tmax_goe_than_safety_stock(
                safety_stock=safety_stock
            )
        )

    def _create_production_constraints(
        self,
        max_capacity: Dict[Tuple[str, str], int],
    ):
        """
        TODO
        :param max_capacity:
        :return:
        """
        production_constraints_builder = ProductionConstraintsBuilder(
            materials=self.materials,
            t0=self.t0,
            tmax=self.tmax,
            all_equipment=self.all_equipment,
            formulas=self.formulas,
        )

        self.no_production_at_t0 = production_constraints_builder.no_production_at_t0()

        self.production_doesnt_exceed_capacity = (
            production_constraints_builder.production_doesnt_exceed_capacity(
                max_capacity=max_capacity
            )
        )

    def _create_material_flow_balance_constraints(
        self,
        bom: Bom,
    ):
        """

        :param bom:
        :return:
        """
        flow_constraints_builder = FlowConstraintsBuilder(
            materials=self.materials,
            t0=self.t0,
            tmax=self.tmax,
            all_equipment=self.all_equipment,
            formulas=self.formulas,
            bom=bom,
        )

        self.material_flow_balance = flow_constraints_builder.material_flow_balance()

    def _create_demand_constraints(self, demand: Dict[Tuple[str, int], int]):
        """
        TODO
        :param demand:
        :return:
        """
        demand_constraints_builder = DemandConstraintsBuilder(
            materials=self.materials,
            t0=self.t0,
            tmax=self.tmax,
            demand=demand,
        )

        self.no_filled_demand_at_t0 = (
            demand_constraints_builder.no_filled_demand_at_t0()
        )
        self.filled_demand_loe_than_demand = (
            demand_constraints_builder.filled_demand_loe_than_demand()
        )

    def _build_objective_function(
        self, costs: Tuple[str, Dict[str, float]], selling_prices: Dict[str, float]
    ):
        self.objective = Objective(
            expr=self.get_objective_function_expression(
                costs=costs, selling_prices=selling_prices
            ),
            sense=maximize,
        )

    def get_objective_function_expression(
        self, costs: Tuple[str, Dict[str, float]], selling_prices: Dict[str, float]
    ):
        return sum(
            selling_prices.get(material_time_index.material, 0.0)
            * self._filled_demand[material_time_index]
            - costs.stocking.get(material_time_index.material, 0.0)
            * self._inventory[material_time_index]
            - costs.purchasing.get(material_time_index.material, 0.0)
            * self._purchased_qty[material_time_index]
            - sum(
                costs.production.get((equipment, formula), 0.0)
                * self._production[
                    build_single_material_equipment_formula_time_index(
                        material=material_time_index.material,
                        equipment=equipment,
                        formula=formula,
                        time=material_time_index.time,
                    )
                ]
                for formula in self.formulas
                for equipment in self.all_equipment
            )
            for material_time_index in self.all_materials_all_time_indexes
        )

    def solve(self):
        solver = SolverFactory(self.solver_name, executable=self.solver_path)
        results = solver.solve(self, tee=False)

        self.check_feasibility(results)
