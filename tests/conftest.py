from typing import Dict

import pytest


@pytest.fixture
def sheets_names_mapping() -> Dict[str, str]:
    return {
        "bom": "Formulas",
        "finished_goods_md": "Products",
        "inventory": "Stock",
        "components_md": "Materials",
        "production_lines": "Equipment",
        "demand": "Demand",
    }
