from typing import Dict

from src.bills_of_materials import Bom
from src.optimizers.manufacturing_optimizer import ManufacturingOptimizer
from src.preprocessing import (
    read_production_problem_excel_template,
    create_mapping_dictionary_from_two_columns,
    create_costs,
    unify_columns_into_tuple,
)


def test_e2e_production_problem(
    sheets_names_mapping: Dict[str, str],
    testing_data_path: str = "./e2e_test/input_data/production_problem.xlsx",
    minimum_units_in_batch: int = 10,
):
    raw_data = read_production_problem_excel_template(
        excel_file_path=testing_data_path,
        sheets_names_mapping=sheets_names_mapping,
    )

    production_lines = raw_data["production_lines"]
    demand = raw_data["demand"]
    # convert demand period to time (as demand is satisfied once in a day [at 8AM] the period refers to the day)
    demand["period"] = (demand["period"] - 1) * 24 + 8

    materials = (
        raw_data["components_md"].component.unique().tolist()
        + raw_data["finished_goods_md"].manufactured_good.unique().tolist()
    )
    all_equipment = production_lines.equipment.unique().tolist()
    formulas = raw_data["bom"].formula.unique().tolist()

    # calculate last working hour from last day on the plan
    simulation_duration = ((demand.period.max() // 24 + 1) * 24) - 4

    optimizer = ManufacturingOptimizer(
        materials=materials,
        all_equipment=all_equipment,
        formulas=formulas,
        simulation_duration=simulation_duration,
        minimum_units_in_batch=minimum_units_in_batch,
    )

    initial_inventory = create_mapping_dictionary_from_two_columns(
        df=raw_data.get("inventory"),
        column_key="productmaterial",
        column_value="initial_stock",
    )

    safety_stock = create_mapping_dictionary_from_two_columns(
        df=raw_data.get("inventory"),
        column_key="productmaterial",
        column_value="safety_stock",
    )

    production_lines["equipment_formula"] = unify_columns_into_tuple(
        production_lines.equipment, production_lines.formula
    )

    max_capacity = create_mapping_dictionary_from_two_columns(
        df=production_lines,
        column_key="equipment_formula",
        column_value="max_production_capacity",
    )

    demand["finished_good_time"] = unify_columns_into_tuple(
        demand.finished_good, demand.period
    )

    demand = create_mapping_dictionary_from_two_columns(
        df=demand,
        column_key="finished_good_time",
        column_value="amount",
    )

    selling_prices = create_mapping_dictionary_from_two_columns(
        df=raw_data["finished_goods_md"],
        column_key="manufactured_good",
        column_value="selling_price",
    )

    bom = Bom(raw_data["bom"])

    costs = create_costs(
        components_md=raw_data["components_md"], production_costs=production_lines
    )

    optimizer.build_model(
        initial_inventory=initial_inventory,
        safety_stock=safety_stock,
        max_capacity=max_capacity,
        demand=demand,
        bom=bom,
        costs=costs,
        selling_prices=selling_prices,
    )

    results = optimizer.solve()

    print(f"Optimal revenue from the production plan is: {optimizer.objective()}")

    for name, data in results._asdict().items():
        _qty_column_mapping = {
            "equipment_status": "status",
            "production": "batches",
        }

        data = data.loc[data[_qty_column_mapping.get(name, "quantity")] != 0]
        data.to_csv(f"./e2e_test/output_data/{name}.csv", index=False)

    assert int(optimizer.objective()) == 120125
