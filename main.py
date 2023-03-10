import asyncio

import ccxt.async_support as ccxt
import statsmodels.api as sm

exchange = ccxt.binance()
symbol = "ETH/USDT"
timeframe = "1m"
limit = 60
threshold = 0.01  # Для проверки работы можно выставить значение поменьше


async def get_prices(symbol: str, timeframe: str = timeframe, limit: int = limit) -> list[int]:
    """
    Функция получает исторические данные, соответствующие цене закрытия свечей
    :param str symbol: Единый символ рынка для получения данных OHLCV (open, high, low, close, volume)
    :param str timeframe: Продолжительность времени, которое представляет каждая свеча
    :param int|None limit: Максимальное количество свечей для извлечения
    :returns [[int]]: Список чисел, состоящий из цены закрытия свечей
    """
    prices = await exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    prices = [price[4] for price in prices]
    return prices


def r_squared_description(r_squared: float) -> str:
    """
    Функция выводит строковое представление коэффициента детерминации r-squared
    :param float r_squared: Коэффициент детерминации r-squared
    :returns str: Строковое представление коэффициента детерминации r-squared
    """
    if r_squared < 0.3:
        return "слабая"
    elif 0.3 <= r_squared < 0.5:
        return "умеренная"
    elif 0.5 <= r_squared < 0.7:
        return "заметная"
    elif 0.7 <= r_squared < 0.9:
        return "высокая"
    elif 0.9 <= r_squared:
        return "очень высокая"


async def analyze_futures_prices(symbol: str) -> str:
    btc_prices = await get_prices("BTC/USDT")
    futures_prices = await get_prices(symbol)

    # Получаем самую последнюю цену на фьючерс
    futures_current_price = futures_prices[-1]

    # Добавляем константу к массиву btc_price для модели линейной регрессии
    btc_price_with_const = sm.add_constant(btc_prices)

    # Обучаем модель линейной регрессии
    model = sm.OLS(futures_prices, btc_price_with_const).fit()
    r_squared = model.rsquared

    # Вычисляем максимальное изменение цены за час
    max_price = abs(futures_current_price / max(futures_prices) - 1)
    min_price = abs(min(futures_prices) / futures_current_price - 1)
    price_change = max(max_price, min_price)

    if price_change >= threshold:
        return f"Цена {symbol} изменилась на {price_change:.2%} за последний час. "\
            f"Зависимость от цены BTC/USDT {r_squared_description(r_squared)}. "\
            f"(r_squared = {r_squared:.2f})"


async def run():
    while True:
        result = await analyze_futures_prices(symbol)
        if result:
            print(result)
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(run())
