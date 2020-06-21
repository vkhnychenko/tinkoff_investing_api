from openapi_client import openapi
from datetime import datetime
from pytz import timezone
from settings import TOKEN, SLEEP_TIME
import asyncio
from google_sheets import append_sheets, read_sheets
from asyncio import sleep

client = openapi.api_client(TOKEN)


async def main():

    """Получаем данные из таблиц для проверки"""
    buy = await read_sheets('Buy', 'ROWS')
    sell = await read_sheets('Sell', 'ROWS')
    dividend = await read_sheets('Dividend', 'ROWS')
    tax = await read_sheets('Tax', 'ROWS')
    pay_in_out = await read_sheets('Pay In/Out', 'ROWS')
    commission = await read_sheets('Commission', 'ROWS')
    buy_date = [item[0] for item in buy]
    sell_date = [item[0] for item in sell]
    dividend_date = [item[0] for item in dividend]
    tax_date = [item[0] for item in tax]
    pay_in_out_date = [item[0] for item in pay_in_out]
    commission_date = [item[0] for item in commission]

    """Скачиваем список сделок"""
    d1 = datetime(2019, 12, 3, 0, 0, 0, tzinfo=timezone('Europe/Moscow'))#дата начала
    d2 = datetime.now(tz=timezone('Europe/Moscow')) #по сегодняшний день
    ops = client.operations.operations_get(_from=d1.isoformat(), to=d2.isoformat())
    for op in ops.payload.operations:  # Перебираем операции
        data = {'operation_type': op.operation_type}
        try:
            instr = client.market.market_search_by_figi_get(op.figi)
            data.update({
                'ticker': instr.payload.ticker,
                'name': instr.payload.name})
        except:
            data.update({
                'ticker': '',
                'name': ''})
        if op.trades == None:  # Если биржевых сделок нет
            date = op.date.strftime("%d.%m.%Y %-H:%M:%S")
            data.update({
                'date': date,
                'price': op.price,
                'payment': op.payment,
                'quantity': op.quantity,
                'currency': op.currency})
        else:
            for t in op.trades:  # А если есть сделки - то перебираем их
                date = op.date.strftime("%d.%m.%Y %-H:%M:%S")
                data.update({
                    'date': date,
                    'price': t.price,
                    'payment': '',
                    'quantity': t.quantity,
                    'currency': op.currency})
        for key, value in data.items():
            if value == None:
                data.update({key: ''})

        """Сохраняем данные в таблицу"""
        if op.operation_type == 'Buy':
            if data['date'] not in buy_date:
                await sleep(SLEEP_TIME)
                await append_sheets('Buy', data)
        if op.operation_type == 'Sell':
            if data['date'] not in sell_date:
                await sleep(SLEEP_TIME)
                await append_sheets('Sell', data)
        if op.operation_type == 'Dividend':
            if data['date'] not in dividend_date:
                await sleep(SLEEP_TIME)
                await append_sheets('Dividend', data)
        if op.operation_type == 'Tax' or op.operation_type == 'TaxBack' or op.operation_type == 'TaxDividend':
            if data['date'] not in tax_date:
                await sleep(SLEEP_TIME)
                await append_sheets('Tax', data)
        if op.operation_type == 'PayIn' or op.operation_type == 'PayOut':
            if data['date'] not in pay_in_out_date:
                await sleep(SLEEP_TIME)
                await append_sheets('Pay In/Out', data)
        if op.operation_type == 'MarginCommission' or op.operation_type == 'BrokerCommission' or op.operation_type == 'ServiceCommission':
            if data['date'] not in commission_date:
                await sleep(SLEEP_TIME)
                await append_sheets('Commission', data)


if __name__ == '__main__':
    asyncio.run(main())