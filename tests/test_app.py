import json
import os

import pytest

from app import total_cost


@pytest.mark.parametrize("items,discount,expected", [([10,20],0,30),([10,20],10,27),([],0,0),([10],100,0),([4.98],5,4.73)])
def test_total(items, discount, expected):
    assert total_cost(items, discount) == expected


@pytest.mark.parametrize("discount", [-1, 101])
def test_invalid_discount(discount):
    with pytest.raises(ValueError):
        total_cost([10], discount)


def test_negative_price():
    with pytest.raises(ValueError):
        total_cost([-1])


@pytest.mark.skipif(not os.environ.get("APPROVED_ASSET_PATH"), reason="Protected fixture is supplied by the chained pipeline")
def test_prepared_asset():
    with open(os.environ["APPROVED_ASSET_PATH"]) as f:
        asset = json.load(f)
    assert asset["currency"] == "USD"
    assert total_cost(asset["items"], asset["discount_percent"]) == 27


def test_contributor_cli_example():
    import subprocess
    import sys
    output = subprocess.check_output([sys.executable, "app.py"], text=True)
    assert json.loads(output)["total"] == 27
