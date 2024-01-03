from typing import List, Tuple

from src.utils import build_material_time_indexes


class BaseConstraint:
    def __init__(
        self,
        materials: List[str],
        t0: int,
        tmax: int,
        all_materials_all_time_indexes: List[Tuple[str, int]] = None,
        all_materials_t0_index: List[Tuple[str, int]] = None,
    ):
        self.materials = materials
        self.t0 = t0
        self.tmax = tmax

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
