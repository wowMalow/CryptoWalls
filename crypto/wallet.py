"""
Basic classes for monitoring your cryptocurrency profits.
Coin class describes each position in your wallet with name of coin,
amount, spent usd on it and current usd value.
Wallet summarizes info about all the coins.
"""
import pandas as pd
import ccxt
from typing import List

from utils import root_path
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class Coin:
    """
    Coin class describes each position in your wallet with
    name of coin (symbol), amount, spent usd on it (value_usd)
    and current usd value (current_value_usd)
    """
    def __init__(self, symbol: str, amount: float = 0.,
                 value_usd: float = 0., current_value_usd: float = 0.) -> None:
        self._symbol = symbol
        self._amount = amount
        self._value_usd = value_usd
        self._current_value_usd = current_value_usd

    def __str__(self) -> str:
        return f'{self._symbol} {self._amount}'

    def name(self) -> str:
        return self._symbol

    def amount(self) -> float:
        return self._amount

    def set_amount(self, amount: float) -> None:
        self._amount = amount

    def invested_value(self) -> float:
        return self._value_usd

    def set_invested_value(self, value: float) -> None:
        self._value_usd = value

    def current_value(self) -> float:
        return self._current_value_usd

    def set_current_value(self, value: float) -> None:
        self._current_value_usd = value

    def update_value(self, price: float) -> None:
        self._current_value_usd = self._amount * price


class Wallet:
    """
    Wallet collects Coins and gets actual prices
    on each cryptocurrency. Can be filled from binance
    trading history or from txt file with tabulated
    coin name, amount of coin and spent usd on it.
    """
    def __init__(self) -> None:
        self._coins = []
        self.exchange = ccxt.binance()

    def __str__(self) -> str:
        return f'{[(coin.name(), coin.amount()) for coin in self._coins]}'

    def add_coin(self, coin: Coin) -> None:
        self._coins.append(coin)

    def get_coin(self, symbol: str) -> Coin:
        for coin in self._coins:
            if coin.name() == symbol:
                return coin
        return None

    def sort(self) -> None:
        self._coins = sorted(self._coins, key=lambda coin: -coin.current_value())

    def symbols(self) -> List[str]:
        return [coin.name() for coin in self._coins]

    def values(self) -> List[float]:
        return [coin.current_value() for coin in self._coins]

    def current_usd(self) -> float:
        return sum(self.values())

    def get_invested_usd(self) -> float:
        usd = [coin.invested_value() for coin in self._coins]
        return sum(usd)

    def to_dict(self) -> dict:
        info = {}
        for coin in self._coins:
            info[coin.name()] = {'amount': coin.amount(),
                                  'old_value_usd': coin.invested_value(),
                                  'current_value_usd': coin.current_value()}
        return info

    def coin_current(self, symbol: str) -> float:
        """
        Returns current usd value of particular coin
        """
        for coin in self._coins:
            if coin.name() == symbol:
                return coin.current_value()
        return 0

    def coin_invested(self, symbol: str) -> float:
        """
        Returns invested usd value to particular coin
        """
        for coin in self._coins:
            if coin.name() == symbol:
                return coin.invested_value()
        return 0

    def get_prices(self) -> List[tuple]:
        request = []
        for symbol in self.symbols():
            request.append(f'{symbol}/USDT')
        response = self.exchange.fetchTickers(request)
        prices = []
        for symbol in response.keys():
            prices.append((symbol[:-5], response[symbol]['last']))
        return prices

    def update(self) -> None:
        try:
            new_prices = self.get_prices()
            for symbol, price in new_prices:
                coin = self.get_coin(symbol)
                coin.set_current_value(coin.amount() * price)
            self.sort()
        except Exception:
            print('Connection lost')

    def from_binance(self, filename: str) -> None:
        """
        Collect coins from your trading history csv file on binance.
        Fill the wallet with actual amount of each coin.

        :param filename: path to csv file (binance.csv)
        :return: Wallet object
        """

        path_filename = root_path(filename)
        df = pd.read_csv(path_filename)
        cols_name = list(df.columns)
        for col in cols_name:
            df[col] = df[col].str.replace(',', '')

        df = df.iloc[::-1]

        # Extract coins names and values in float
        for col in ['Price', 'Executed', 'Amount', 'Fee']:
            if col in ['Executed', 'Amount']:
                df[f'{col}_coin'] = df[col].str.replace(r'[\d\.]', '')
            df[col] = df[col].str.replace(r'[^\d\.]', '').astype(float)

        # Collects all trades from dataFrame grouped by coins
        coins = {}
        for coin in list(df.Executed_coin):
            coins[coin] = {'amount': 0, 'threshold': 0, 'price': 0, 'usd': 0}

        for idx in df.index:
            row = df.loc[idx]
            amount = coins[row.Executed_coin]['amount']
            if row.Side == 'BUY':
                coins[row.Executed_coin]['amount'] = amount + row.Executed - row.Fee
            else:
                coins[row.Executed_coin]['amount'] = amount - row.Executed

            # Filter coins with usd value less than 5$
            if row.Amount_coin in ['USDT', 'BUSD']:
                coins[row.Executed_coin]['threshold'] = 5 / row.Price
                coins[row.Executed_coin]['price'] = row.Price
                if row.Side == 'BUY':
                    coins[row.Executed_coin]['usd'] += row.Amount
                else:
                    coins[row.Executed_coin]['usd'] -= row.Amount

        # Add coins to a wallet
        for coin in coins.keys():
            if abs(coins[coin]['amount']) > coins[coin]['threshold']:
                self.add_coin(Coin(coin, amount=abs(coins[coin]['amount']),
                                   value_usd=abs(coins[coin]['usd'])))

    def from_txt(self, filename: str) -> None:
        """
        Collect coins from tabulated txt file (columns: symbols, amount, invested_usd).
        Fill the wallet with actual amount of each coin.

        :param filename: path to txt file (coins.txt)
        :return: Wallet object
        """
        path_filename = root_path(filename)
        with open(path_filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if i == 0: # skip table title
                    continue
                # Add coins to a wallet
                symbol, amount, usd = line.rstrip('\n').split('\t')
                self.add_coin(Coin(symbol, amount=float(amount), value_usd=float(usd)))


if __name__ == '__main__':
    wallet = Wallet()
    wallet.from_txt('coins.txt')
    # wallet.from_binance('binance.csv')
    wallet.update()
    print(wallet)
    print(wallet.to_dict())
