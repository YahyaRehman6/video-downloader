
import re
import requests 
from pytube import YouTube
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

def get_youtube_detail(video_url):
    try:
        # Create a YouTube object with the given video URL
        yt = YouTube(video_url)

        # Get the highest resolution stream
        highest_resolution_url = yt.streams.get_highest_resolution().url
        highest_resolution_size = yt.streams.get_highest_resolution().filesize

        video_urls_and_sizes = [
            {
                "resolution": stream.resolution,
                "url": stream.url,
                "size": convert_bytes(stream.filesize)
            }
            # for stream in yt.streams.filter(progressive=True,file_extension="mp4") if stream.resolution is not None
            for stream in yt.streams.filter(progressive=True) if stream.resolution is not None
        ]

        video_details = {
            "title": yt.title,
            "duration": yt.length,
            "views": yt.views,
            "author": yt.author,
            "description": yt.description,
            "thumbnail_url": yt.thumbnail_url,
            "video_url": highest_resolution_url,
            "highest_resolution_size": convert_bytes(highest_resolution_size),
            "video_urls_by_resolution": video_urls_and_sizes,
        }

        return video_details

    except Exception as e:
        return {"error":str(e)}



@app.route("/api/v1/youtube")
def youtube_endpoint():
    try:
        url = request.args.get("url")
        if not url:
            return jsonify({
                'status': False,
                'message': 'Url not found.'
            }), 400    
        response = get_youtube_detail(url)
        return jsonify(response)

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 400