import pytest
import pandas as pd
from datetime import datetime
from src.reports import spending_by_category
from freezegun import freeze_time


@pytest.fixture
def sample_dataframe():
    """Фикстура с данными за август – декабрь"""
    data = {
        "Дата платежа": [
            datetime(2021, 12, 31),
            datetime(2021, 12, 15),
            datetime(2021, 11, 10),
            datetime(2021, 10, 5),
            datetime(2021, 9, 20),
            datetime(2021, 8, 25),
        ],
        "Категория": ["супермаркеты", "супермаркеты", "фастфуд", "фастфуд", "супермаркеты", "супермаркеты"],
        "Сумма операции": [-160.89, -64.00, -118.12, -200.00, -100.00, -90.00]
    }
    return pd.DataFrame(data)


@freeze_time("2021-11-15")
def test_spending_by_category_with_2021_11_15(sample_dataframe):
    result = spending_by_category(sample_dataframe, "супермаркеты", date="2021-11-15")
    print("\nРезультат фильтрации:")
    print(result[["Дата платежа", "Категория", "Сумма операции"]])
    assert len(result) == 2
    assert all(cat == "супермаркеты" for cat in result["Категория"])
    assert all(date >= datetime(2021, 8, 1) and date <= datetime(2021, 10, 31) for date in result["Дата платежа"])


@pytest.mark.parametrize("category, date_str, expected_count", [
    ("Супермаркеты", "2021-12-31", 3),     # Сентябрь – ноябрь
    ("Супермаркеты", "2021-11-15", 2),      # Август – октябрь
    ("Фастфуд", "2021-12-31", 2),           # Октябрь – ноябрь
])
def test_spending_by_category(sample_dataframe, category, date_str, expected_count):
    result = spending_by_category(sample_dataframe, category, date=date_str)
    print("\nРезультат фильтрации:")
    print(result[["Дата платежа", "Категория", "Сумма операции"]])
    print(f"\nДля {category} и даты {date_str}, найдено: {len(result)} записей")
    print(result[["Дата платежа", "Категория", "Сумма операции"]])
    assert len(result) == expected_count
