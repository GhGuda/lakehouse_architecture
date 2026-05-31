from pathlib import Path


def test_iac_modules_exist() -> None:
    modules_root = Path("iac/modules")
    for module_name in ["s3", "iam", "glue", "stepfunctions"]:
        module_dir = modules_root / module_name
        assert module_dir.exists()
        assert (module_dir / "main.tf").exists()
        assert (module_dir / "variables.tf").exists()


def test_root_iac_files_exist() -> None:
    assert Path("iac/main.tf").exists()
    assert Path("iac/variables.tf").exists()
    assert Path("iac/outputs.tf").exists()
