
import re
import requests 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, request, jsonify

app = Flask(__name__)


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
        return {'error': str(e)}


@app.route("/api/v1/instagram")
def instagram():
    url = request.args.get('url')
    if not url:
        return jsonify({
            'status': False,
            'message': 'Url not found.'
        }), 400
    if not "instagram" in url:
        return jsonify({
            'status': False,
            'message': 'Invalid url.'
        }), 400
    detail = get_instagram_detail(url)
    print("Instagram detail is : ", detail)
    if not detail:
        return jsonify({
            'status': False,
            'message': 'Something went wrong.'
        })

    return jsonify(detail)

@app.route("/api/v1/tiktok")
def tiktok():
    try:
        url = request.args.get("url")
        if not url:
            return jsonify({
                'status': False,
                'message': 'Url not found.'
            }), 400    
        scraping_url = "https://tikdownloader.io/api/ajaxSearch"

        headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
        data = {"q": url}
        response = requests.post(scraping_url, headers=headers, data=data)
        if response.status_code == 200:
            response_json = response.json()
            return jsonify({'data': str(response_json)})
        else:
            print("Error: Request failed with status code", response.status_code)
            print("request json is : ", response.text)
            return jsonify({'error': str(response.text)})
    except Exception as e:
        print("Exception:", e)
        return jsonify({
            'error': str(e) 
        })