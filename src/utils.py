from typing import List

from src.indexes import Index


def build_material_time_indexes(
    materials: List[str], t0: int, tmax: int
) -> List[Index]:
    """
    Generates material time combination indexes in a standardized way
    :param materials: List of materials in scope for the desired index returned
    :param t0: First time period the indexes will contain
    :param tmax: Last time period on scope
    :return: List of Indexes containing all this information in a standardized order and format
    """
    return [
        Index([material, time], material=material, time=time)
        for material in materials
        for time in range(t0, tmax + 1)
    ]


def build_material_equipment_formula_time_indexes(
    materials: List[str],
    all_equipment: List[str],
    formulas: List[str],
    t0: int,
    tmax: int,
) -> List[Index]:
    """
    Generates all material time equipment and formula combination indexes in a standardized way
    :param materials: List of all material IDs
    :param all_equipment: List containing every equipment ID
    :param formulas: List of all formulas IDs
    :param t0: First time period the indexes will contain
    :param tmax: Last time period on scope
    :return: List of Indexes containing all this information in a standardized order and format
    """

    return [
        build_single_material_equipment_formula_time_index(
            material=material, equipment=equipment, formula=formula, time=time
        )
        for material in materials
        for equipment in all_equipment
        for formula in formulas
        for time in range(t0, tmax + 1)
    ]


def build_single_material_equipment_formula_time_index(
    material: str,
    equipment: str,
    formula: str,
    time: int,
) -> Index:
    """
    Generates one concrete material equipment formula time combination index in a standardized way
    :param material: material ID
    :param equipment: equipment ID
    :param formula: formula ID
    :param time: int representing the time
    :return: Index containing all this information in a standardized order and format
    """
    return Index(
        [material, equipment, formula, time],
        material=material,
        equipment=equipment,
        formula=formula,
        time=time,
    )


def build_equipment_formula_time_indexes(
    all_equipment: List[str],
    formulas: List[str],
    t0: int,
    tmax: int,
) -> List[Index]:
    """
     Generates all equipment formula and time combination indexes in a standardized way
    :param all_equipment: List containing every equipment ID
    :param formulas: List of all formulas IDs
    :param t0: First time period the indexes will contain
    :param tmax: Last time period on scope
    :return: List of Indexes containing all this information in a standardized order and format
    """

    return [
        Index(
            [equipment, formula, time],
            equipment=equipment,
            formula=formula,
            time=time,
        )
        for equipment in all_equipment
        for formula in formulas
        for time in range(t0, tmax + 1)
    ]


def build_equipment_time_indexes(
    all_equipment: List[str],
    t0: int,
    tmax: int,
) -> List[Index]:
    """
    Generates all equipment and time combination indexes in a standardized way
    :param all_equipment: List containing every equipment ID
    :param t0: First time period the indexes will contain
    :param tmax: Last time period on scope
    :return: List of Indexes containing all this information in a standardized order and format
    """

    return [
        Index(
            [equipment, time],
            equipment=equipment,
            time=time,
        )
        for equipment in all_equipment
        for time in range(t0, tmax + 1)
    ]
