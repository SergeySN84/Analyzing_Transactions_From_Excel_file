import pandas as pd
from src.services import analyze_top_categories, investment_bank

# Загрузка данных из Excel
df = pd.read_excel("../data/operations.xlsx")
transactions = df.to_dict(orient="records")

# 1. Анализ выгодных категорий
categories_report = analyze_top_categories(transactions, year=2021, month=12)
print(categories_report)

# 2. Расчет инвесткопилки
invest_sum = investment_bank("2021-12", transactions, limit=50)
print(f"Сумма в инвесткопилке: {invest_sum:.2f} ₽")