import json
import pytest
from src.services import analyze_top_categories


@pytest.fixture
def sample_transactions():
    """Тестовые транзакции за разные периоды"""
    return [
        {"Дата операции": "31.12.2021 16:44:00", "Категория": "Супермаркеты", "Сумма операции": "-160.89"},
        {"Дата операции": "31.12.2021 16:42:04", "Категория": "Супермаркеты", "Сумма операции": "-64.00"},
        {"Дата операции": "15.11.2021 13:11:51", "Категория": "Супермаркеты", "Сумма операции": "-273.90"},
        {"Дата операции": "10.11.2021 13:11:16", "Категория": "Фастфуд", "Сумма операции": "-118.12"},
        {"Дата операции": "01.03.2019 12:27:36", "Категория": "Различные товары", "Сумма операции": "-20.00"}
    ]


@pytest.mark.parametrize("year, month, expected_result", [
    (2021, 12, {"супермаркеты": 224}),
    (2021, 11, {"супермаркеты": 273, "фастфуд": 118}),
    (2021, 10, {}),
    (2021, 3, {"различные товары": 20})
])
def test_analyze_top_categories(sample_transactions, year, month, expected_result):
    result_json = analyze_top_categories(sample_transactions, year=year, month=month)
    result_dict = json.loads(result_json)

    for key in result_dict:
        assert key.lower() in expected_result or key in expected_result
        assert result_dict[key] == expected_result.get(key.lower(), 0)
