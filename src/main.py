import os
import pandas as pd
import logging

# --- Импорты из src ---
from src.views import generate_report
from src.services import analyze_top_categories
from src.reports import spending_by_category

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_transactions(file_path: str = "data/operations.xlsx") -> pd.DataFrame:
    """Загружает транзакции из Excel как DataFrame."""
    logger.info(f"Загрузка транзакций из файла: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    try:
        df = pd.read_excel(file_path)

        # Парсим даты
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce", dayfirst=True)
        df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], errors="coerce", dayfirst=True)

        # Суммы
        df["Сумма операции"] = pd.to_numeric(df["Сумма операции"], errors="coerce")

        # Чистим данные
        df.dropna(subset=["Дата операции", "Сумма операции"], inplace=True)

        # Заполняем пропущенные категории
        df["Категория"] = df["Категория"].fillna("Без категории").astype(str).str.strip().str.lower()

        return df

    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        raise


def run_analysis():
    """Функция для запуска всех функциональностей проекта"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, "data", "operations.xlsx")

    print("Путь к файлу:", file_path)
    print("Файл существует?", os.path.exists(file_path))

    # Предварительная инициализация переменных
    df = pd.DataFrame()
    expenses_df = pd.DataFrame()
    income_df = pd.DataFrame()

    try:
        df = load_transactions(file_path)
        print("\nПервые 5 строк:")
        print(df.head(5))

        print("\nУникальные категории:")
        print(df["Категория"].unique())

        print("\nДанные за декабрь 2021:")
        print(df[df["Дата платежа"].dt.to_period("M") == "2021-12"][["Дата платежа", "Категория", "Сумма операции"]])

        # Разделение на доходы и расходы
        expenses_df = df[df["Сумма операции"] < 0].copy()
        income_df = df[df["Сумма операции"] > 0].copy()

        # --- Траты по категории 'Супермаркеты' ---
        print("\n[Функция] Траты по категории 'Супермаркеты'")
        try:
            res = spending_by_category(expenses_df, "Супермаркеты", date="2021-12-31")
            print(res.head())
            print("\nПример даты:", df["Дата платежа"].iloc[0])
            print("Тип даты:", type(df["Дата платежа"].iloc[0]))

            print("\nКоличество записей с 'супермаркеты':", len(df[df["Категория"] == "супермаркеты"]))
            print("Количество записей за декабрь 2021:", len(df[df["Дата платежа"].dt.to_period("M") == "2021-12"]))
            print("Количество записей за период с 2021-10-01 по 2021-12-31:", len(df[
              (df["Дата платежа"] >= "2021-10-01") & (df["Дата платежа"] <= "2021-12-31") &
              (df["Категория"] == "супермаркеты")]))
        except Exception as e:
            print(f"[ERROR] Не удалось выполнить отчет: {e}")

    except Exception as e:
        logger.error(f"Не удалось загрузить файл: {e}")
        return  # Останавливаем дальнейшее выполнение, если данные не загружены

    # Эти переменные используются только после успешной загрузки данных
    try:
        # --- Кешбэк за декабрь 2021 ---
        print("\n[Функция] Анализ выгодных категорий кешбэка за декабрь 2021")
        transactions_list = df.to_dict(orient="records")
        res = analyze_top_categories(transactions_list, year=2021, month=12)
        print(res)

        # --- Полный отчет за декабрь 2021 ---
        print("\n[Функция] Генерация полного отчета за декабрь 2021")
        full_report = generate_report(expenses_df, income_df, date_str="2021-12-31", range_type="M")
        print(full_report)

    except Exception as e:
        print(f"[ERROR] Ошибка анализа или генерации отчета: {e}")


if __name__ == "__main__":
    run_analysis()
