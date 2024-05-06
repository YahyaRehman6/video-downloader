import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def validate_url(url, regex) -> bool:
    pattern = re.compile(regex)
    if re.match(pattern, url):
        print("Matched....")
        return True
    else:
        print("Not matched....")
        return False


def get_instagram_detail(url):
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")

        browser = webdriver.Chrome(options=chrome_options)
        browser.get(url)
        video = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//video[@src]"))
        )
        video_url = video.get_attribute("src")
        return {
            "video_url": video_url,
        }
    except Exception as e:
        print("Exception is : ", e)
        return        