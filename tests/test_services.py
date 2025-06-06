import pytest
from unittest.mock import patch, MagicMock
import datetime
from datetime import datetime
import json
from src.services import analyze_top_categories, investment_bank, search_transactions, find_phone_transactions, \
    find_person_transfers


def test_analyze_top_categories():
    mock_data = [
        {
            "Дата операции": "01.03.2021 14:01:01",
            "Категория": "Связь",
            "Сумма операции": "-10.00",
        },
        {
            "Дата операции": "01.03.2021 15:01:01",
            "Категория": "Фастфуд",
            "Сумма операции": "-20.00",
        },
    ]

    with patch("src.services.datetime") as mock_datetime:
        # Мокаем datetime.strptime
        mock_datetime.strptime.side_effect = lambda *args: datetime.strptime(*args)

        result = analyze_top_categories(mock_data, year=2021, month=3)
        data = json.loads(result)

        assert "Связь" in data
        assert data["Связь"] == 10.0
        assert "Фастфуд" in data
        assert data["Фастфуд"] == 20.0

def test_investment_bank():
    mock_transactions = [
        {"Дата операции": "01.12.2021 14:01:01", "Сумма операции": "-99.00"},
        {"Дата операции": "02.12.2021 15:01:01", "Сумма операции": "-101.00"},
    ]

    with patch("src.services.math.ceil", side_effect=[100, 150]) as mock_ceil:
        result = investment_bank("2021-12", mock_transactions, limit=50)

        # Проверяем вызов math.ceil
        mock_ceil.assert_called()

        # Проверяем результат
        assert round(result, 2) == 12300.0

def test_search_transactions():
    mock_transactions = [
        {"Описание": "McDonald's", "Категория": "Фастфуд"},
        {"Описание": "IP Ragimov", "Категория": "Фастфуд"},
        {"Описание": "Магнит", "Категория": "Супермаркеты"},
    ]

    result = search_transactions(mock_transactions, query="магнит")
    data = json.loads(result)

    # Проверяем, что найдена только одна транзакция
    assert len(data) == 1
    assert data[0]["Описание"] == "Магнит"

def test_find_phone_transactions():
    mock_transactions = [
        {"Описание": "+7 921 11-22-33", "Категория": "Переводы"},
        {"Описание": "Devajs Servis.", "Категория": "Связь"},
    ]

    with patch("src.services.re.compile") as mock_compile:
        # Мокаем регулярное выражение
        mock_pattern = MagicMock()
        mock_pattern.search.side_effect = lambda x: x == "+7 921 11-22-33"
        mock_compile.return_value = mock_pattern

        result = find_phone_transactions(mock_transactions)
        data = json.loads(result)

        # Проверяем, что найдена только одна транзакция
        assert len(data) == 1
        assert data[0]["Описание"] == "+7 921 11-22-33"

from unittest.mock import MagicMock

def test_find_person_transfers():
    mock_transactions = [
        {"Описание": "Дмитрий Ш.", "Категория": "Переводы"},
        {"Описание": "Перевод Кредитная", "Категория": "Переводы"},
        {"Описание": "Светлана Т.", "Категория": "Переводы"},
    ]

    with patch("src.services.re.compile") as mock_compile:
        # Создаём мок для Match-объекта
        mock_match = MagicMock()

        # Используем список для хранения ожидаемых значений
        expected_values = ["Дмитрий Ш.", "Светлана Т."]
        mock_match.group.side_effect = lambda x: expected_values.pop(0) if x == 1 else None

        # Мокируем регулярное выражение
        mock_pattern = MagicMock()
        mock_pattern.search.side_effect = (
            lambda x: mock_match if "Дмитрий Ш." in x or "Светлана Т." in x else None
        )
        mock_compile.return_value = mock_pattern

        result = find_person_transfers(mock_transactions)
        data = json.loads(result)

        # Проверяем, что найдено две транзакции
        assert len(data) == 2
        assert data[0]["Описание"] == "Дмитрий Ш."
        assert data[1]["Описание"] == "Светлана Т."