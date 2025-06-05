import requests

def get_usd_to_uah_rate():
    url = "https://api.monobank.ua/bank/currency"
    response = requests.get(url)
    if response.status_code != 200:
        print("Не вдалося отримати курси валют")
        return

    data = response.json()
    for rate in data:
        if rate["currencyCodeA"] == 840 and rate["currencyCodeB"] == 980:
            print(f"Курс USD to UAH (продаж): {rate.get('rateSell')}")
            print(f"Курс USD to UAH (купівля): {rate.get('rateBuy')}")
            return

    print("Курс USD to UAH не знайдено")

if __name__ == "__main__":
    get_usd_to_uah_rate()
