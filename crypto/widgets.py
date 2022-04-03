"""
Widgets module generates images with info about
all cryptocurrencies in wallet as pie chart,
table of coins names with highlighted profits and module
created basic OHLC chart of BTC on different timeframes.
"""
import pandas as pd
import numpy as np
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from crypto.wallet import Wallet
from utils import PATH


def make_pie(wallet: Wallet) -> None:
    """
    Generate pie chart and save image to folder \images\widgets\
    """
    values = wallet.values()
    labels = wallet.symbols()

    quantile = np.cumsum(np.array(values)) / np.sum(np.array(values))
    i = np.where(quantile > 0.95)[0][0]
    other_usd = sum(values[i:])
    labels = labels[:i] + ['OTHER']
    values = values[:i] + [other_usd]

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=wallet.current_usd(),
        number={'prefix': "$", 'font.size': 54},
        delta={'position': "bottom", 'relative': True,
               'reference': wallet.get_invested_usd(),
               'valueformat': ".2%",
               'font.size': 20},
        domain={'x': [0, 1], 'y': [0, 1]}))

    fig.add_trace(go.Pie(labels=labels, values=values, sort=False,
                         insidetextfont_size=20, textposition='inside',
                         textinfo='label+percent', hole=.6, showlegend=False))

    fig.update_layout(paper_bgcolor="#161B22",
                      font_color='#DEE7E8',
                      plot_bgcolor='rgba(0,0,0,0)',
                      height=600,
                      width=600
                      )

    fig.write_image(rf'{PATH}\images\widgets\pie.png')


def make_table(wallet: Wallet) -> None:
    """
    Generate 2-column table with cryptocurrencies
    and it's profit and save image to folder \images\widgets\
    """
    coins = wallet.symbols()
    coins_num = len(coins)

    rows = math.ceil(coins_num / 2)
    col, row = 0, 0

    fig = go.Figure()

    for coin in coins:
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=wallet.coin_current(coin),
            number={'prefix': f"{coin} $", 'font.size': 28},
            delta={'position': "bottom", 'relative': True,
                   'reference': wallet.coin_invested(coin),
                   'valueformat': ".2%",
                   'font.size': 20},
            domain={'row': row, 'column': col}))

        row += 1
        if row == rows:
            row = 0
            col = 1

    fig.update_layout(paper_bgcolor="#161B22",
                      font_color='#DEE7E8',
                      plot_bgcolor='rgba(0,0,0,0)',
                      grid={'rows': rows, 'columns': 2,
                            'pattern': "independent"},
                      height=rows * 117,
                      width=600
                      )

    fig.write_image(rf'{PATH}\images\widgets\table.png')


def make_chart(wallet: Wallet, interval: str = '1d', outfile: str = 'chart') -> None:
    """
    Generate OHLC chart of BTC/USDT and save image to folder \images\widgets\.
    Choose timeframe with interval and filename of result image.
    """
    bars = wallet.exchange.fetch_ohlcv('BTC/USDT', timeframe=interval, limit=100)

    df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df.date = pd.to_datetime(df.date, unit='ms')

    df.loc[df.close >= df.open, 'volume_color'] = '#2EB872'
    df.loc[df.close < df.open, 'volume_color'] = '#E32636'

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.0, subplot_titles=('BTC', ''),
                        row_width=[0.2, 0.8])

    fig.add_trace(go.Candlestick(x=df.date, open=df.open, high=df.high,
                                 low=df.low, close=df.close, showlegend=False, name='Price',
                                 increasing_line_color='#2EB872', increasing_fillcolor='#2EB872',
                                 decreasing_line_color='#E32636', decreasing_fillcolor='#E32636'),
                  row=1, col=1)

    fig.add_trace(go.Bar(x=df.date, y=df.volume, marker_color=df.volume_color, marker_line_color=df.volume_color,
                         showlegend=False, name='Volume'),
                  row=2, col=1)

    fig.update(layout_xaxis_rangeslider_visible=False)

    fig.update_xaxes(zeroline=False, showline=True, linewidth=1, linecolor='#161B22', gridcolor='#202831')
    fig.update_yaxes(zeroline=False, showline=True, linewidth=1, linecolor='#161B22', gridcolor='#202831')

    fig.update_layout(
        xaxis_tickfont_size=12,
        font_color='#DEE7E8',
        autosize=False,
        width=700,
        height=500,
        margin=dict(l=10, r=10, b=10, t=30, pad=4),
        paper_bgcolor='#161B22',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False

    )

    fig.write_image(rf'{PATH}\images\widgets\{outfile}.png')


def render_widgets(wallet: Wallet) -> None:
    """
    Setup widgets and render them
    """
    try:
        make_pie(wallet)
        make_table(wallet)
        make_chart(wallet, interval='1d', outfile='chart1')
        make_chart(wallet, interval='15m', outfile='chart2')
    except Exception:
        pass


if __name__ == '__main__':
    wallet = Wallet()
    wallet.from_binance('binance.csv')
    wallet.update()

    render_widgets(wallet)