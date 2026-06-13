import os
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    remote_url = os.environ.get("SELENIUM_REMOTE_URL")
    if remote_url:
        driver = webdriver.Remote(command_executor=remote_url, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    return driver

def test_frontend_sentiment():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    try:
        driver.get(f"{BASE_URL}/")
        text_input = wait.until(EC.presence_of_element_located((By.ID, "text-input")))
        text_input.clear()
        text_input.send_keys("This app is incredibly intuitive and has made my daily workflow dramatically more efficient.")
        submit_btn = driver.find_element(By.ID, "submit-btn")
        submit_btn.click()
        wait.until(EC.presence_of_element_located((By.ID, "result-output")))
        time.sleep(3)
        result_text = driver.find_element(By.ID, "result-output").text.strip()
        assert result_text, "result-output is empty"
        assert any(k in result_text for k in ["POSITIVE", "NEGATIVE", "Confidence"]), \
            f"Unexpected result: {result_text}"
    finally:
        driver.quit()
