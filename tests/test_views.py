import json

import pytest

from src.views import generate_report
from unittest.mock import patch
import pandas as pd
from datetime import datetime


@pytest.fixture
def sample_expenses_df():
    """Траты за декабрь 2021"""
    data = {
        "Дата платежа": [datetime(2021, 12, 31), datetime(2021, 12, 15)],
        "Категория": ["Супермаркеты", "Переводы"],
        "Сумма операции": [-1000, -500]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_income_df():
    """Доходы за декабрь 2021"""
    data = {
        "Дата платежа": [datetime(2021, 12, 31)],
        "Категория": ["Пополнения"],
        "Сумма операции": [5000]
    }
    return pd.DataFrame(data)


@patch("src.utils.fetch_currency_rates")
@patch("src.utils.fetch_stock_prices")
def test_generate_report(mock_fetch_stock, mock_fetch_currency, sample_expenses_df, sample_income_df):
    """Тест генерации отчета за декабрь 2021"""
    mock_fetch_currency.return_value = [{"currency": "USDRUB", "rate": 75.0}]
    mock_fetch_stock.return_value = [{"stock": "AAPL", "price": 190.0}]

    report = generate_report(sample_expenses_df, sample_income_df, date_str="2021-12-31", range_type="M")
    report_data = json.loads(report)

    # Проверка сумм
    assert report_data["expenses"]["total_amount"] == 1500
    assert report_data["income"]["total_amount"] == 5000

    # Проверка валютных курсов
    if mock_fetch_currency.return_value:
        assert "currency_rates" in report_data
        assert len(report_data["currency_rates"]) > 0
        assert report_data["currency_rates"][0]["currency"] == "USDRUB"
        assert report_data["currency_rates"][0]["rate"] == 64.1824

    # Проверка акций
    if mock_fetch_stock.return_value:
        assert "stock_prices" in report_data
        assert len(report_data["stock_prices"]) > 0
        assert report_data["stock_prices"][0]["stock"] == "AAPL"
        assert report_data["stock_prices"][0]["price"] == 190.0
