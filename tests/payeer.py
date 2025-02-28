import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from ixbrowser_local_api import IxBrowserAPI  # если используете API ixbrowser
import requests  # для работы с API Payeer

# Настройки логирования
logging.basicConfig(level=logging.INFO, filename="bybit_p2p_trades.log",
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Параметры
PROFILE_PATH = ""  # Путь к профилю браузера
# Пример, замените на нужный endpoint
PAYEER_API_URL = "https://api.payeer.com/api/accounts"

# Инициализация браузера с использованием ixbrowser (или другого профиля)


def init_browser(profile_path):
    options = Options()
    options.add_argument(f"user-data-dir={profile_path}")
    browser = webdriver.Chrome(options=options)
    return browser

# Авторизация в Bybit (с ручным решением капчи)


def login_to_bybit(browser):
    browser.get(BYBIT_URL)
    logging.info("Ожидаем решения капчи вручную.")
    while True:
        try:
            # Подождите, пока капча не будет решена вручную
            if browser.find_element(By.ID, "user-profile-icon"):
                logging.info("Капча решена, заходим в P2P раздел.")
                break
        except Exception:
            time.sleep(1)

# Фильтрация сделок и выбор подходящих


def find_trade(browser, currency, amount):
    # Замените селектор на нужный
    trades = browser.find_elements(By.CSS_SELECTOR, ".trade-item")
    for trade in trades:
        price = trade.find_element(By.CSS_SELECTOR, ".price").text
        if currency in trade.text and float(price) >= amount:
            return trade
    return None

# Ожидание подтверждения оплаты через Payeer API


def check_payment(payeer_account, transaction_id):
    params = {
        'account': payeer_account,
        'transaction_id': transaction_id
    }
    response = requests.get(PAYEER_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "completed":  # или другой статус, в зависимости от API
            return True
    return False

# Подтверждение сделки


def confirm_trade(browser, twofa_code):
    # Введите код 2FA вручную или получите его из расширения
    twofa_input = browser.find_element(By.ID, "twofa-code-input")
    twofa_input.send_keys(twofa_code)
    confirm_button = browser.find_element(By.ID, "confirm-button")
    confirm_button.click()

# Основной цикл автоматизации


def automate_trades(profile_path):
    browser = init_browser(profile_path)
    login_to_bybit(browser)
    transaction_counter = 0

    while transaction_counter < 9:  # Переключаться между профилями после 5-9 сделок
        # Параметры фильтрации: валюта, сумма
        trade = find_trade(browser, "USD", 100)
        if trade:
            trade.click()
            logging.info("Сделка выбрана.")

            # Проводим сделку (например, вводим сумму и валюту)
            amount_input = browser.find_element(By.ID, "amount-input")
            amount_input.send_keys("100")  # Пример
            confirm_button = browser.find_element(By.ID, "confirm-button")
            confirm_button.click()

            # Ожидаем, пока оплата поступит на счет
            if check_payment("payeer_account", "transaction_id"):
                logging.info("Платеж подтвержден.")
                # Получаем 2FA код вручную
                confirm_trade(browser, "2fa_code_from_extension")
                logging.info("Сделка завершена.")
            else:
                logging.warning("Оплата не поступила. Прерывание сделки.")

            transaction_counter += 1
        else:
            logging.info("Подходящие сделки не найдены.")
            time.sleep(5)  # Пауза перед следующим поиском

        if transaction_counter % 5 == 0:
            logging.info("Смена профиля после 5 сделок.")
            browser.quit()
            # Инициализация нового профиля для следующей партии сделок
            browser = init_browser(profile_path)

    browser.quit()


# Запуск основного скрипта
if __name__ == "__main__":
    automate_trades(PROFILE_PATH)
