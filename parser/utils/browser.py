from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager  # type: ignore

from common.settings import get_settings


def get_browser() -> webdriver.Firefox | webdriver.Remote:
    docker = get_settings().docker
    if docker:
        browser = webdriver.Remote(get_settings().selenium_hub, DesiredCapabilities.FIREFOX)
    else:
        gecko = Service(GeckoDriverManager().install())
        browser = webdriver.Firefox(service=gecko)  # type: ignore
    browser.set_page_load_timeout(5)
    return browser
