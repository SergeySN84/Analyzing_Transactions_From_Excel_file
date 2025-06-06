import pandas as pd
from src.services import (
    analyze_top_categories,
    investment_bank,
    search_transactions,
    find_phone_transactions,
    find_person_transfers,
)


def load_transactions(file_path: str = "../data/operations.xlsx") -> list:
    """Загрузка транзакций из Excel-файла"""
    print(f"[INFO] Загрузка данных из {file_path}...")
    df = pd.read_excel(file_path)
    return df.to_dict(orient="records")


def run_analyze_top_categories(transactions: list):
    print("\n[Функция] Анализ выгодных категорий кешбэка за декабрь 2021")
    result = analyze_top_categories(transactions, year=2021, month=12)
    print(result)


def run_investment_bank(transactions: list):
    print("\n[Функция] Расчёт инвесткопилки за 2021-12 с шагом округления 50")
    result = investment_bank("2021-12", transactions, limit=50)
    print(f"Сумма для инвесткопилки: {result:.2f} ₽")


def run_search_transactions(transactions: list):
    print("\n[Функция] Поиск транзакций по запросу 'Магнит'")
    result = search_transactions(transactions, query="Магнит")
    print(result)


def run_find_phone_transactions(transactions: list):
    print("\n[Функция] Поиск транзакций с телефонными номерами")
    result = find_phone_transactions(transactions)
    print(result)


def run_find_person_transfers(transactions: list):
    print("\n[Функция] Поиск переводов физическим лицам")
    result = find_person_transfers(transactions)
    print(result)


def main():
    # Загрузка транзакций
    transactions = load_transactions()

    # Запуск всех сервисов
    run_analyze_top_categories(transactions)
    run_investment_bank(transactions)
    run_search_transactions(transactions)
    run_find_phone_transactions(transactions)
    run_find_person_transfers(transactions)


if __name__ == "__main__":
    main()
