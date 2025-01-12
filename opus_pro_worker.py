import json
import time
import tkinter as tk
import undetected_chromedriver as uc
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import math
import json
import os

def execute_opus_worker():
    def initiate_driver():
        opts = uc.ChromeOptions()
        opts.add_argument("--lang=en")
        opts.page_load_strategy = 'none'
        # opts.add_argument("--headless")
        opts.add_argument(r"--user-data-dir=C:\Users\space\AppData\Local\Google\Chrome\User Data")
        opts.add_argument("--profile-directory=Default")
        driver = uc.Chrome(options=opts, browser_executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                # 'Accept-Language': 'en-US,en;q=0.9',
                # 'Accept-Encoding': 'gzip, deflate, br',
                # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': 'https://www.google.com/'
            }
        }
                               )
        return driver
    initiate_driver()

execute_opus_worker()
