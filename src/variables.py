from pyomo.core import Var, NonNegativeReals


class InventoryVariable(Var):
    def __init__(self, all_materials_all_time_indexes):
        super().__init__(all_materials_all_time_indexes, name="inventory_quantity", domain=NonNegativeReals)
        self._id = "inventory_quantity"

    def __str__(self):
        return "InventoryVariable"

    def __eq__(self, other):
        return self.id == other.id

    @property
    def id(self):
        return self._id


class FilledDemand(Var):
    def __init__(self, all_materials_all_time_indexes):
        super().__init__(all_materials_all_time_indexes, name="filled_demand", domain=NonNegativeReals)
        self._id = "filled_demand"

    def __str__(self):
        return "FilledDemandVariable"

    def __eq__(self, other):
        return self.id == other.id

    @property
    def id(self):
        return self._id


class PurchasedQtyVariable(Var):
    def __init__(self, all_materials_all_time_indexes):
        super().__init__(
            all_materials_all_time_indexes,
            name="purchased_quantity",
            domain=NonNegativeReals,
        )
        self._id = "purchased_quantity"

    def __str__(self):
        return "PurchasedQtyVariable"

    def __eq__(self, other):
        return self.id == other.id

    @property
    def id(self):
        return self._id


class ProductionVariable(Var):
    def __init__(self, material_equipment_formula_time_indexes):
        super().__init__(material_equipment_formula_time_indexes, name="production", domain=NonNegativeReals)
        self._id = "production"

    def __str__(self):
        return "ProductionVariable"

    def __eq__(self, other):
        return self.id == other.id

    @property
    def id(self):
        return self._id
