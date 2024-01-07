from abc import ABC
from collections import namedtuple
from typing import List, Dict, Tuple, Set

from pyomo.core import Objective, maximize

from src.bills_of_materials import Bom
from src.constraints_builders.demand_constraints import DemandConstraintsBuilder
from src.constraints_builders.flow_constraints import FlowConstraintsBuilder
from src.constraints_builders.inventory_constraints import InventoryConstraintsBuilder
from src.constraints_builders.production_constraints import ProductionConstraintsBuilder
from src.constraints_builders.purchasing_consrtaints import PurchasingConstraintsBuilder
from src.optimizers.base_optimizer import BaseOptimizer
from src.utils import (
    build_material_time_indexes,
    build_single_material_equipment_formula_time_index,
    build_material_equipment_formula_time_indexes,
    build_equipment_time_indexes,
)
from src.variables import (
    ProductionVariable,
    InventoryVariable,
    FilledDemand,
    PurchasedQtyVariable,
    EquipmentStatusVariable,
)


class ManufacturingOptimizer(BaseOptimizer, ABC):
    def __init__(
        self,
        materials: List[str],
        all_equipment: List[str],
        formulas: List[str],
        minimum_units_in_batch: int,
        simulation_duration: int,
        t0: int = 0,
        all_materials_all_time_indexes: List[Tuple[str, int]] = None,
        all_materials_t0_index: List[Tuple[str, int]] = None,
        material_equipment_formula_time_indexes: List[Tuple[str, str, str, int]] = None,
        equipment_time_indexes: List[Tuple[str, int]] = None,
    ):
        super().__init__(name="ManufacturingOptimizer")

        # Simulation general info
        self.materials = materials
        self.all_equipment = all_equipment
        self.formulas = formulas
        self.minimum_units_in_batch = minimum_units_in_batch
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
                tmax=self.tmax,
            )
        )
        self.equipment_time_indexes = (
            equipment_time_indexes
            if equipment_time_indexes
            else build_equipment_time_indexes(
                all_equipment=self.all_equipment,
                t0=self.t0,
                tmax=self.tmax,
            )
        )

        # Variables
        self.production = None
        self.filled_demand = None
        self.inventory_quantity = None
        self.purchased_quantity = None
        self.equipment_status = None

        # Constraints
        self.initial_inventory = None
        self.inventory_tmax_goe_than_safety_stock = None

        self.no_production_at_t0 = None
        self.components_cannot_be_produced = None
        self.production_doesnt_exceed_capacity = None
        self.equipment_status_is_active_when_producing = None
        self.equipment_status_loe_than_production = None
        self.max_continuous_production_time_limit = None

        self.no_purchase_qty_at_t0 = None

        self.no_filled_demand_at_t0 = None
        self.filled_demand_loe_than_demand = None

        self.material_flow_balance = None

        self.only_components_can_be_purchased = None
        self.no_purchasing_when_factory_is_closed = None

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
        """
        Creates the optimization model by instantiating all variables, constraints and objective function.
        :param initial_inventory: Dictionary which maps the material with the initial inventory on hand
        at beginning of the simulation
        :param safety_stock: Dictionary which maps the material with its safety stock
        :param max_capacity: Dict which maps Equipment and formula combination with its capacity
        :param demand: Dictionary which maps the finished_good and time to the quantity demanded to factory
        :param bom: Bom object which contains all related bills of materials information
        :param costs: Named tuple with all cost types and a dict which maps the cost to its generator
        :param selling_prices: Dictionary which maps finished_goods to its selling price
        :return: None
        """
        self._create_variables()

        self._create_inventory_constraints(
            initial_inventory=initial_inventory, safety_stock=safety_stock
        )
        self._create_production_constraints(
            component_materials=set(bom.all_component_materials),
            max_capacity=max_capacity,
        )

        self._create_material_flow_balance_constraints(bom=bom)

        self._create_demand_constraints(demand=demand)

        self._create_purchasing_constraints(
            all_parent_materials=set(bom.all_parent_materials)
        )

        self._build_objective_function(costs=costs, selling_prices=selling_prices)

    def _create_variables(self):
        """
        Creates all variables from model
        :return: None
        """
        self.production = ProductionVariable(
            self.material_equipment_formula_time_indexes
        )
        self.filled_demand = FilledDemand(self.all_materials_all_time_indexes)
        self.inventory_quantity = InventoryVariable(self.all_materials_all_time_indexes)
        self.purchased_quantity = PurchasedQtyVariable(
            self.all_materials_all_time_indexes
        )
        self.equipment_status = EquipmentStatusVariable(self.equipment_time_indexes)

    def _create_inventory_constraints(
        self, initial_inventory: Dict[str, float], safety_stock: Dict[str, float]
    ):
        """
        Creates all inventory related constraints
        :param initial_inventory: Dictionary which maps the material with the initial inventory on hand
        at beginning of the simulation
        :param safety_stock: Dictionary which maps the material with its safety stock
        :return: None
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
        component_materials: Set[str],
        max_capacity: Dict[Tuple[str, str], int],
        max_equipment_production_continuous_time: int = 4,
    ):
        """
        Creates all production related constraints
        :param component_materials: Set of all materials which are externally procured
        :param max_capacity: Dict which maps Equipment and formula combination with its capacity
        :param max_equipment_production_continuous_time: Periods of time which an equipment could be operating in a row
        :return: None
        """
        production_constraints_builder = ProductionConstraintsBuilder(
            materials=self.materials,
            t0=self.t0,
            tmax=self.tmax,
            all_equipment=self.all_equipment,
            formulas=self.formulas,
            minimum_units_in_batch=self.minimum_units_in_batch,
        )

        self.no_production_at_t0 = (
            production_constraints_builder.no_production_when_factory_is_closed()
        )

        self.components_cannot_be_produced = (
            production_constraints_builder.components_cannot_be_produced(
                component_materials=component_materials
            )
        )

        self.production_doesnt_exceed_capacity = (
            production_constraints_builder.production_doesnt_exceed_capacity(
                max_capacity=max_capacity
            )
        )

        self.equipment_status_is_active_when_producing = (
            production_constraints_builder.equipment_status_is_active_when_producing()
        )

        self.equipment_status_loe_than_production = (
            production_constraints_builder.equipment_status_loe_than_production()
        )

        self.max_continuous_production_time_limit = (
            production_constraints_builder.max_continuous_production_time_limit(
                max_continuous_time=max_equipment_production_continuous_time
            )
        )

    def _create_material_flow_balance_constraints(
        self,
        bom: Bom,
    ):
        """
        Creates all flow balance related constraints
        :param bom: Bom object which contains all related bills of materials information
        :return: None
        """
        flow_constraints_builder = FlowConstraintsBuilder(
            materials=self.materials,
            t0=self.t0,
            tmax=self.tmax,
            all_equipment=self.all_equipment,
            formulas=self.formulas,
            bom=bom,
        )

        self.material_flow_balance = flow_constraints_builder.material_flow_balance(
            minimum_units_in_batch=self.minimum_units_in_batch
        )

    def _create_demand_constraints(
        self, demand: Dict[Tuple[str, int], int], demand_filling_time: int = 8
    ):
        """
        Creates all demand related constraints
        :param demand: Dictionary which maps the finished_good and time to the quantity demanded to factory
        :param demand_filling_time: The hour when the demand is getting out from stock
        :return: None
        """
        demand_constraints_builder = DemandConstraintsBuilder(
            materials=self.materials,
            t0=self.t0,
            tmax=self.tmax,
            demand=demand,
        )

        self.no_filled_demand_at_t0 = (
            demand_constraints_builder.demand_is_filled_only_at_concrete_time_in_a_day(
                demand_filling_time
            )
        )
        self.filled_demand_loe_than_demand = (
            demand_constraints_builder.filled_demand_loe_than_demand()
        )

    def _create_purchasing_constraints(self, all_parent_materials: Set[str]):
        """
        Creates all purchasing related constraints
        :param all_parent_materials: Set of all materials which are being produced in-house
        :return: None
        """
        purchasing_constraints_builder = PurchasingConstraintsBuilder(
            materials=self.materials,
            t0=self.t0,
            tmax=self.tmax,
        )

        self.only_components_can_be_purchased = (
            purchasing_constraints_builder.only_components_can_be_purchased(
                all_parent_materials=all_parent_materials
            )
        )

        self.no_purchasing_when_factory_is_closed = (
            purchasing_constraints_builder.no_purchasing_when_factory_is_closed()
        )

    def _build_objective_function(
        self, costs: Tuple[str, Dict[str, float]], selling_prices: Dict[str, float]
    ):
        """
        Builds the objective function from this model
        :param costs: Named tuple with all cost types and a dict which maps the cost to its generator
        :param selling_prices: Dictionary which maps finished_goods to its selling price
        :return: None
        """
        self.objective = Objective(
            expr=self.get_objective_function_expression(
                costs=costs, selling_prices=selling_prices
            ),
            sense=maximize,
        )

    def get_objective_function_expression(
        self, costs: Tuple[str, Dict[str, float]], selling_prices: Dict[str, float]
    ):
        """
        Generated the objective function from this model
        :param costs: Named tuple with all cost types and a dict which maps the cost to its generator
        :param selling_prices: Dictionary which maps finished_goods to its selling price
        :return: Objective function expression
        """
        return sum(
            selling_prices.get(material_time_index.material, 0.0)
            * self.filled_demand[material_time_index]
            - costs.inventory.get(material_time_index.material, 0.0)
            * self.inventory_quantity[material_time_index]
            - costs.purchase.get(material_time_index.material, 0.0)
            * self.purchased_quantity[material_time_index]
            - sum(
                costs.production.get((equipment, formula), 0.0)
                * self.production[
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
            * self.minimum_units_in_batch
            for material_time_index in self.all_materials_all_time_indexes
        )

    def generate_results(
        self,
    ):
        """
        Generates results from the optimization. All its variables' status.
        :return: Namedtuple containing all variables status in DataFrames
        """

        results_container = namedtuple(
            "OptimizationResults",
            "production filled_demand inventory_quantity purchased_quantity equipment_status",
        )

        model_variables = [
            self.production,
            self.filled_demand,
            self.inventory_quantity,
            self.purchased_quantity,
            self.equipment_status,
        ]

        col_headers = {
            "production": [
                "material",
                "equipment",
                "formula",
                "time",
                "batches",
            ],
            "filled_demand": [
                "material",
                "time",
                "quantity",
            ],
            "inventory_quantity": [
                "material",
                "time",
                "quantity",
            ],
            "purchased_quantity": [
                "material",
                "time",
                "quantity",
            ],
            "equipment_status": [
                "equipment",
                "time",
                "status",
            ],
        }

        results = {
            model_variable.id: self.get_variable_results_on_dataframe_format(
                model_variable, col_headers
            )
            for model_variable in model_variables
        }

        self.results = results_container(
            production=results["production"],
            filled_demand=results["filled_demand"],
            inventory_quantity=results["inventory_quantity"],
            purchased_quantity=results["purchased_quantity"],
            equipment_status=results["equipment_status"],
        )

        return self.results
