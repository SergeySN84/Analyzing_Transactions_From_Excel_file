import math
from typing import List, Dict, Any
import json
import re
from datetime import datetime
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


# 1. Анализ выгодных категорий повышенного кешбэка
def analyze_top_categories(data: List[Dict[str, Any]], year: int, month: int) -> str:

    logger.info("Анализ категорий за %s-%s", year, month)
    try:
        def parse_date(txx: Dict[str, Any]) -> datetime:
            return datetime.strptime(txx["Дата операции"], "%d.%m.%Y %H:%M:%S")

        def in_target_month(txx: Dict[str, Any]) -> bool:
            tx_date = parse_date(txx)
            return tx_date.year == year and tx_date.month == month

        filtered = list(filter(in_target_month, data))
        logger.debug("Найдено %d транзакций за указанный период", len(filtered))

        category_totals = {}
        for tx in filtered:
            category = tx.get("Категория", "Без категории")
            amount = abs(float(tx["Сумма операции"]))
            category_totals[category] = category_totals.get(category, 0) + amount

        result = json.dumps(category_totals, ensure_ascii=False, indent=4)
        logger.info("Успешно составлен отчет по категориям")
        return result

    except Exception as e:
        logger.error("Ошибка при анализе категорий: %s", e)
        raise


# 2. Инвесткопилка через округление
def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    logger.info("Рассчёт инвесткопилки для месяца %s с шагом округления %s", month, limit)
    try:
        target_year, target_month = map(int, month.split("-"))

        def is_in_target_month(txx: Dict[str, Any]) -> bool:
            try:
                tx_date = datetime.strptime(txx["Дата операции"], "%d.%m.%Y %H:%M:%S")
            except ValueError:
                return False
            return tx_date.year == target_year and tx_date.month == target_month

        filtered = list(filter(is_in_target_month, transactions))
        logger.debug("Найдено %d транзакций за месяц %s", len(filtered), month)

        amounts = []
        for tx in filtered:
            try:
                amount = float(tx["Сумма операции"])
            except (ValueError, KeyError):
                logger.warning("Не удалось преобразовать сумму: %s", tx.get("Сумма операции"))
                continue
            if amount < 0:
                amounts.append(abs(amount))

        logger.debug("Отрицательные суммы: %s", amounts)

        rounded = [math.ceil(amount / limit) * limit - amount for amount in amounts]
        total = round(sum(rounded), 2)

        logger.info("Общая сумма для инвесткопилки: %.2f", total)
        return total

    except Exception as e:
        logger.error("Ошибка в расчёте инвесткопилки: %s", e, exc_info=True)
        raise


# 3. Простой поиск по описанию или категории
def search_transactions(transactions: List[Dict[str, Any]], query: str) -> str:
    logger.info("Поиск по запросу '%s'", query)
    try:
        query = query.lower()
        result = []

        for tx in transactions:
            # Преобразуем в строку и приводим к нижнему регистру
            description = str(tx.get("Описание", "")).lower()
            category = str(tx.get("Категория", "")).lower()

            if query in description or query in category:
                result.append(tx)

        logger.debug("Найдено %d совпадений", len(result))
        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error("Ошибка при поиске: %s", e)
        raise


# 4. Поиск транзакций с номерами телефонов в описании
def find_phone_transactions(transactions: List[Dict[str, Any]]) -> str:
    logger.info("Поиск транзакций с телефонными номерами")
    try:
        # Обновлённое регулярное выражение для телефонных номеров
        phone_pattern = re.compile(
            r'\+7[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
            re.UNICODE
        )
        result = []

        for tx in transactions:
            description = tx.get("Описание", "")
            if phone_pattern.search(description):
                result.append(tx)

        logger.debug("Найдено %d транзакций с номерами телефонов", len(result))
        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error("Ошибка при поиске телефонов: %s", e)
        raise


# 5. Поиск переводов физическим лицам
def find_person_transfers(transactions: List[Dict[str, Any]]) -> str:
    logger.info("Поиск переводов физическим лицам")
    try:
        # Регулярное выражение для поиска имён и фамилий
        name_surname_pattern = re.compile(r"\b([А-Я][а-я]+ [А-Я]\.?|[А-Я][а-я]+\s+[А-Я][а-я]+)\b", re.UNICODE)
        result = []

        for tx in transactions:
            category = str(tx.get("Категория", "")).lower()  # Приводим категорию к нижнему регистру
            description = str(tx.get("Описание", ""))  # Получаем описание

            # Логируем каждую транзакцию для анализа
            logger.debug(f"Обрабатывается транзакция: Категория={category}, Описание={description}")

            # Проверяем, является ли категория "переводы" или аналогичной
            if category in {"переводы", "перевод физическому лицу"}:
                # Исключаем транзакции с описанием "Перевод Кредитная"
                if "Перевод Кредитная" in description:
                    logger.debug("Пропускаем транзакцию с описанием 'Перевод Кредитная'")
                    continue

                # Ищем имена и фамилии в описании
                match = name_surname_pattern.search(description)
                if match:
                    tx_copy = tx.copy()
                    tx_copy["Описание"] = match.group(1)  # Сохраняем только имя+фамилия
                    result.append(tx_copy)

        logger.debug("Найдено %d переводов физическим лицам", len(result))
        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error("Ошибка при поиске переводов физическим лицам: %s", e)
        raise
