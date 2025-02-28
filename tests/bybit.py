
from ixBrowser import ixBrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Подключение к браузеру с нужным профилем

c = IXBrowserClient(port=54200)
browser = ixBrowser.connect(profile="profile_name")  # Замените на нужное имя профиля

# Открытие Bybit P2P страницы
browser.get("https://bybit.com/p2p")


def check_available_deals():
    # Подождите, пока страница загрузится
    time.sleep(5)
    
    # Получаем все доступные сделки
    deals = browser.find_elements(By.XPATH, "//div[@class='deal-item']")
    suitable_deals = []
    
    for deal in deals:
        # Фильтрация сделок по параметрам
        if "параметры" in deal.text:  # Настройте фильтрацию по вашим условиям
            suitable_deals.append(deal)
    
    return suitable_deals


def perform_deal(deal):
    # Нажимаем на сделку
    deal.click()
    
    # Пример, как ввести сумму и валюту (можно настроить)
    amount_field = browser.find_element(By.XPATH, "//input[@name='amount']")
    amount_field.send_keys("1000")  # Введите нужную сумму
    
    # Подтверждение сделки
    confirm_button = browser.find_element(By.XPATH, "//button[text()='Подтвердить']")
    confirm_button.click()

    # Добавьте ожидание загрузки страницы или выполнения действия
    time.sleep(3)


def get_2fa_code():
    # Получить 2FA код из расширения (по API или через DOM)
    # Пример получения кода из элемента (если расширение хранит его в DOM):
    twofa_code_element = browser.find_element(By.XPATH, "//div[@id='2fa-code']")
    return twofa_code_element.text


import requests

def check_payment(transaction_id):
    url = f"https://payeer.com/api/{transaction_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        payment_data = response.json()
        if payment_data["status"] == "completed":
            return True
    return False


def complete_deal():
    complete_button = browser.find_element(By.XPATH, "//button[text()='Завершить сделку']")
    complete_button.click()
    
    # Логирование завершения сделки
    with open("deal_log.txt", "a") as log_file:
        log_file.write("Сделка завершена\n")


def switch_profile():
    # Здесь можно переключить профиль (если профили в iXBrowser настроены как отдельные сессии)
    browser.quit()
    browser = ixBrowser.connect(profile="next_profile_name")
    return browser


def main():
    profile_count = 0
    deal_count = 0
    max_deals_per_profile = 5

    while True:
        # Подключаем браузер с нужным профилем
        browser = ixBrowser.connect(profile=f"profile_{profile_count}")
        
        # Проверяем доступные сделки
        deals = check_available_deals()
        
        for deal in deals:
            perform_deal(deal)
            
            # Получаем 2FA код (если нужно)
            twofa_code = get_2fa_code()
            
            # Проверяем оплату через Payeer API
            if check_payment(transaction_id="example_id"):
                complete_deal()
                deal_count += 1

            if deal_count >= max_deals_per_profile:
                # Переключаем профиль после 5 сделок
                profile_count += 1
                deal_count = 0
                break
