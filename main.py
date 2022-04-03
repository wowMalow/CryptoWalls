import schedule
import threading
import time
from crypto.wallet import Wallet
import crypto.widgets as widgets
import walls.wallpaper as walls


def update() -> None:
    """
    Timer for thread with schedule module
    """
    while True:
        schedule.run_pending()
        time.sleep(60)


def wall_routine(wallet: Wallet) -> None:
    """
    Update values, generate and set new wallpaper
    """
    wallet.update()
    widgets.render_widgets(wallet)
    walls.make_wallpaper()
    walls.set_wallpaper()


def main() -> None:
    # Set wallet info from file
    wallet = Wallet()
    wallet.from_txt('coins.txt')
    # wallet.from_txt('binance.csv')

    # Set update rate and run schedule thread
    schedule.every(15).minutes.do(wall_routine, wallet=wallet)
    threading.Thread(target=update).start()


if __name__ == '__main__':
    main()

