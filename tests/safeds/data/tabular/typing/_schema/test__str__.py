from safeds.data.tabular.containers import Table


def test__str__() -> None:
    table = Table.from_dict({"col1": ["col1_1"], "col2": [1]})
    assert str(table.schema) == "TableSchema:\nColumn Count: 2\nColumns:\n    col1: String\n    col2: Integer\n"