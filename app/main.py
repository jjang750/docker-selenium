# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from tqdm.contrib.telegram import TelegramIO
from webdriver_manager.chrome import ChromeDriverManager

global driver


def landers():
    global driver
    print('-- start --')

    try:
        option = Options()
        option.add_argument('headless')
        option.add_argument('disable-gpu')
        option.add_argument('single-process')
        option.add_argument('disable-dev-shm-usage')
        option.add_argument('no-sandbox')

        s = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=s, options=option)
    except Exception as e:
        print(e)
        exit(0)

    yyyy = int('20'+datetime.now().strftime('%y'))
    mm = int(datetime.now().strftime('%m'))

    driver.get(f'https://www.ssglanders.com/game/schedule?year={yyyy}&month={mm}')
    driver.switch_to.default_content()
    driver.implicitly_wait(1000)

    # TODO
    calendar_dow = driver.find_elements(By.CLASS_NAME, 'day.home')

    message = f'Langers {yyyy}-{mm} \n'

    for calendar_row in calendar_dow:
        if calendar_row.text.endswith('인천'):
            s = calendar_row.text.split('\n')
            message += str(s[:1]) + str(s[2:])
            message += '\n'

    print(message)

    try:
        token = os.getenv('TELEGRAM_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        telegram = TelegramIO(token=token, chat_id=chat_id)
        telegram.write(message)
    except Exception as e:
        print(e)

    # TODO

    driver.quit()
    print('-- end --')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    landers()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
