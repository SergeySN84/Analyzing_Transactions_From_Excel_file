from datetime import datetime
import json

import pandas as pd

from src.utils import (get_date_range, filter_data_by_date, aggregate_expenses,
                       prepare_main_section, fetch_currency_rates, fetch_stock_prices)


def generate_report(expenses_df: pd.DataFrame, income_df: pd.DataFrame, date_str: str = None,
                    range_type: str = "M") -> str:
    """Функция для создания JSON отчета из файла с транзакциями"""
    start_date, end_date = get_date_range(date_str or datetime.today().strftime("%Y-%m-%d"), range_type)

    filtered_expenses = filter_data_by_date(expenses_df, start_date, end_date)
    filtered_income = filter_data_by_date(income_df, start_date, end_date)

    expenses_total = round(filtered_expenses["Сумма операции"].sum())
    income_total = round(filtered_income["Сумма операции"].sum())

    report = {
        "period": f"{start_date.date()} - {end_date.date()}",
        "expenses": {"total_amount": abs(expenses_total),
                     "categories": prepare_main_section(aggregate_expenses(filtered_expenses))},
        "income": {"total_amount": income_total,
                   "categories": prepare_main_section(aggregate_expenses(filtered_income))},
        "currency_rates": fetch_currency_rates() or [],
        "stock_prices": fetch_stock_prices() or []
    }

    return json.dumps(report, ensure_ascii=False, indent=4)
