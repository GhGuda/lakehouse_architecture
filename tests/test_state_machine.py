import json
from pathlib import Path


def test_state_machine_has_expected_flow() -> None:
    state_machine_path = Path("stepfunctions/state_machine.json")
    definition = json.loads(state_machine_path.read_text(encoding="utf-8"))
    states = definition["States"]

    assert definition["StartAt"] == "DetectNewRawFiles"
    assert states["HasNewFiles"]["Type"] == "Choice"
    assert states["RunProductsEtl"]["Next"] == "RunOrdersEtl"
    assert states["RunOrdersEtl"]["Next"] == "RunOrderItemsEtl"
    assert states["RunOrderItemsEtl"]["Next"] == "UpdateGlueCatalog"
    assert states["UpdateGlueCatalog"]["Next"] == "RunAthenaValidation"
    assert states["ValidationPassed"]["Type"] == "Choice"
    assert states["ArchiveProcessedRawFiles"]["Next"] == "Success"
    assert states["NotifyFailure"]["Next"] == "FailState"
