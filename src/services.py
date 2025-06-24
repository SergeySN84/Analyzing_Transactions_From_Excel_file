import json
from datetime import datetime
from typing import List, Dict, Any
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def analyze_top_categories(data: List[Dict[str, Any]], year: int, month: int) -> str:
    """Функция выгодные категории повышенного кешбэка"""
    logger.info(f"Анализ категорий за {year}-{month}")

    result = {}
    for tx in data:
        try:
            tx_date_str = tx.get("Дата операции", "")
            if isinstance(tx_date_str, pd.Timestamp):
                tx_date = tx_date_str.to_pydatetime()
            elif isinstance(tx_date_str, str):
                tx_date = datetime.strptime(tx_date_str, "%d.%m.%Y %H:%M:%S")
            else:
                continue

        except Exception:
            continue

        if tx_date.year != year or tx_date.month != month:
            continue

        category = tx.get("Категория", "Без категории").strip().lower()
        amount = abs(float(tx.get("Сумма операции", 0)))

        result[category] = int(result.get(category, 0) + amount)

    logger.info("Анализ завершен успешно.")
    return json.dumps(result, ensure_ascii=False, indent=4)
