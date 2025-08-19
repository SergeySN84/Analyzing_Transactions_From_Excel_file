import pandas as pd
from datetime import datetime, timedelta
import logging

from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


def spending_by_category(transactions: pd.DataFrame, category: str, date: str = None) -> pd.DataFrame:
    """
    Формирует отчет по тратам за последние 3 месяца.
    """
    logger.info(f"Формирование отчета по категории '{category}'")

    # Проверяем, что дата задана корректно
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            logger.warning("Неверный формат даты, используется текущая.")
            target_date = datetime.today()
    else:
        target_date = datetime.today()

    # Рассчитываем начало периода — начало текущего месяца минус 3 месяца
    start_date = target_date - relativedelta(months=3)
    start_date = start_date.replace(day=1)
    end_date = target_date.replace(day=1) + relativedelta(months=1) - timedelta(seconds=1)

    logger.info(f"Фильтруем данные с {start_date.date()} по {target_date.date()}")

    # Убедимся, что категории очищены и соответствуют фильтру
    transactions["Категория"] = transactions["Категория"].fillna("Без категории").astype(str).str.strip().str.lower()

    # Убедимся, что даты в правильном формате
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], errors="coerce")

    # Фильтрация
    filtered = transactions[
        (transactions["Категория"] == category.strip().lower()) &
        (transactions["Дата платежа"] >= start_date) &
        (transactions["Дата платежа"] <= end_date)
        ]

    logger.info(f"Найдено {len(filtered)} записей по категории '{category}'")
    return filtered
