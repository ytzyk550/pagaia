from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import undetected_chromedriver.v2 as uc
from fake_useragent import UserAgent


def html_to_bs(html):
    return BeautifulSoup(html, 'html.parser')


def get_page_html(url):
    try:
        print('Initializes the Webdriver...')
        opts = uc.ChromeOptions()
        # Fake user-agent to ignore bot blocking
        ua = UserAgent()
        userAgent = ua.random
        opts.add_argument(f'user-agent={userAgent}')

        # Start scraping ...
        driver = uc.Chrome(options=opts)
        print('Scraping the page...')

        driver.get(url)
        WebDriverWait(driver, 3)
        sleep(2)
        print('Extracts data...')
        page = html_to_bs(driver.page_source)
        driver.quit()
        return page
    except Exception as e:
        print('get_page_html error: ' + str(e))
