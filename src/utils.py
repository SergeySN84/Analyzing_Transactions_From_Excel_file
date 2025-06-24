import os
import pandas as pd
from datetime import datetime, timedelta
import logging
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

CURRATE_API_KEY = os.getenv("CURRATE_API_KEY")
# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_date_range(date_str: str, range_type: str = "M") -> (datetime, datetime):
    """Возвращает начальную и конечную дату в зависимости от типа диапазона."""
    date = datetime.strptime(date_str, "%Y-%m-%d")

    if range_type == "W":
        start_date = date - timedelta(days=date.weekday())
        end_date = start_date + timedelta(days=6)
    elif range_type == "M":
        start_date = date.replace(day=1)
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
    elif range_type == "Y":
        start_date = date.replace(month=1, day=1)
        end_date = date.replace(month=12, day=31)
    elif range_type == "ALL":
        start_date = datetime(2000, 1, 1)
        end_date = date
    else:
        raise ValueError(f"Неизвестный тип диапазона: {range_type}")

    logger.info(f"Диапазон дат: {start_date.date()} — {end_date.date()}")
    return start_date, end_date


def filter_data_by_date(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Фильтрует DataFrame по диапазону дат."""
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], errors="coerce")
    filtered_df = df[(df["Дата платежа"] >= start_date) & (df["Дата платежа"] <= end_date)]
    return filtered_df


def aggregate_expenses(expenses_df: pd.DataFrame) -> dict:
    """Агрегирует расходы по категориям."""
    category_totals = expenses_df.groupby("Категория")["Сумма операции"].sum().abs().to_dict()
    return category_totals


def prepare_main_section(aggregated_data: dict) -> list:
    """Подготавливает основной раздел с тратами по категориям."""
    sorted_data = sorted(aggregated_data.items(), key=lambda x: x[1], reverse=True)
    top_7 = [{"category": cat, "amount": round(amount)} for cat, amount in sorted_data[:7]]
    others_sum = sum(amount for _, amount in sorted_data[7:])

    if others_sum > 0:
        top_7.append({"category": "Остальное", "amount": round(others_sum)})

    return top_7


def prepare_transfers_and_cash(expenses_df: pd.DataFrame) -> list:
    """Подготавливает данные по переводам и наличным."""
    transfers = expenses_df[expenses_df["Категория"] == "Переводы"]["Сумма операции"].sum()
    cash = expenses_df[expenses_df["Категория"] == "Наличные"]["Сумма операции"].sum()

    result = []
    if abs(cash) > 0:
        result.append({"category": "Наличные", "amount": round(abs(cash))})
    if abs(transfers) > 0:
        result.append({"category": "Переводы", "amount": round(abs(transfers))})

    return result


def fetch_currency_rates():
    """Получает курсы валют через API."""
    url = f"https://currate.ru/api/?get=rates&pairs=USDRUB,EURRUB&key={CURRATE_API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return [{"currency": pair, "rate": float(data["data"][pair])} for pair in data["data"]]
        else:
            logging.warning("Ошибка получения курсов валют.")
            return []
    except Exception as e:
        logging.error("Ошибка получения курсов: %s", e)
        return []


def fetch_stock_prices():
    """Получает цены акций из S&P500."""
    try:
        # Пример с фиксированными данными (заменить на реальный API)
        sample_stocks = {
            "AAPL": 190.0,
            "AMZN": 180.0,
            "GOOGL": 2700.0,
            "MSFT": 300.0,
            "TSLA": 1000.0
        }
        return [{"stock": stock, "price": price} for stock, price in sample_stocks.items()]
    except Exception as e:
        logger.error("Ошибка получения цен акций: %s", e)
        return []
