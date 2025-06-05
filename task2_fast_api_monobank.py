from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import httpx
from typing import Optional, List

app = FastAPI()

security = HTTPBasic()
PASSWORD = "supersecretpassword123"

def check_auth(creds: HTTPBasicCredentials = Depends(security)):
    if creds.password != PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

CURRENCY_CODES = {
    980: "UAH",
    840: "USD",
    978: "EUR",
    826: "GBP",
    985: "PLN",
}

@app.get("/rates")
async def get_rates(currencies: Optional[List[str]] = None, authorized: bool = Depends(check_auth)):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.monobank.ua/bank/currency")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Не вдалося отримати курси")
    data = response.json()
    results = []
    for rate in data:
        from_curr = CURRENCY_CODES.get(rate["currencyCodeA"])
        to_curr = CURRENCY_CODES.get(rate["currencyCodeB"])
        if not from_curr or not to_curr:
            continue
        if currencies and from_curr not in currencies and to_curr not in currencies:
            continue
        results.append({
            "from": from_curr,
            "to": to_curr,
            "buy": rate.get("rateBuy"),
            "sell": rate.get("rateSell"),
        })
    return {"rates": results}

@app.get("/purchase-check")
async def can_purchase(item: str, price_usd: float, saved_uah: float, authorized: bool = Depends(check_auth)):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.monobank.ua/bank/currency")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Не вдалося отримати курс долара")
    rates = response.json()
    usd_to_uah = next((r["rateSell"] for r in rates if r["currencyCodeA"] == 840 and r["currencyCodeB"] == 980), None)
    if not usd_to_uah:
        raise HTTPException(status_code=500, detail="Курс долара не знайдено")
    saved_usd = saved_uah / usd_to_uah
    shortage = price_usd - saved_usd
    if shortage <= 0:
        msg = f"летсго , ти можеш це купити {item}."
    elif shortage < 50:
        msg = f"от блін трішки не вистачило на {item}."
    elif shortage < 500:
        msg = f"давай трішки економніше і  {item} буде твоїм"
    else:
        msg = f"потірбно більше працювати {item} поки що недосяжний"
    return {
        "item": item,
        "price_usd": price_usd,
        "saved_uah": saved_uah,
        "usd_to_uah_rate": round(usd_to_uah, 2),
        "saved_usd": round(saved_usd, 2),
        "shortage_usd": round(max(shortage, 0), 2),
        "message": msg,
    }
