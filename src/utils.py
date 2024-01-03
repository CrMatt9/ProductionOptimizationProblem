from collections import namedtuple
from typing import List, Tuple


def build_material_time_indexes(
    materials: List[str], t0: int, tmax: int
) -> List[Tuple[str, int]]:
    """
    Generates material time combination indexes in a standardized way
    :param materials: List of materials in scope for the desired index returned
    :param t0: First time period the indexes will contain
    :param tmax: Last time period on scope
    :return: Tuple with the string of the material and integer indicating time
    """
    material_time_index = namedtuple("MaterialTimeIndex", "material time")
    return [
        material_time_index(material=material, time=time)
        for material in materials
        for time in range(t0, tmax + 1)
    ]


def build_material_equipment_formula_time_indexes(
    materials: List[str],
    all_equipment: List[str],
    formulas: List[str],
    t0: int,
    tmax: int,
) -> List[Tuple[str, str, str, int]]:
    """
    TODO NOT USED YET CHECK IT
    Generates material time combination indexes in a standardized way
    :param materials: TODO
    :param all_equipment: TODO
    :param formulas: TODO
    :param t0: First time period the indexes will contain
    :param tmax: Last time period on scope
    :return: Tuple with the string of the material and integer indicating time
    """

    return [
        build_single_material_equipment_formula_time_index(
            material=material, equipment=machine, formula=formula, time=time
        )
        for material in materials
        for machine in all_equipment
        for formula in formulas
        for time in range(t0, tmax + 1)
    ]


def build_single_material_equipment_formula_time_index(
    material: str,
    equipment: str,
    formula: str,
    time: int,
):
    """
    TODO
    :param material:
    :param equipment:
    :param formula:
    :param time:
    :return:
    """
    material_equipment_formula_time_index = namedtuple(
        "MaterialEquipmentFormulaTimeIndex", "material equipment formula time"
    )

    return material_equipment_formula_time_index(
        material=material, equipment=equipment, formula=formula, time=time
    )
