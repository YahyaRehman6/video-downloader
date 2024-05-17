
import re, io, base64
import ffmpeg
from urllib.parse import quote, unquote
import requests 
from pytube import YouTube
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)


def convert_bytes(byte_size):
    try:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if byte_size < 1024:
                return f"{byte_size:.2f} {unit}"
            byte_size /= 1024
    except:
        return ""


def encode_url(url):
    url_bytes = url.encode('utf-8')
    base64_bytes = base64.urlsafe_b64encode(url_bytes)
    base64_url = base64_bytes.decode('utf-8')
    return base64_url

def decode_url(encoded_url):
    base64_bytes = encoded_url.encode('utf-8')
    url_bytes = base64.urlsafe_b64decode(base64_bytes)
    url = url_bytes.decode('utf-8')
    return url
    



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


@app.route("/api/v1/download")
@cross_origin()
def download_video():
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({
                'status': False,
                'message': 'Url not found.'
            }), 400
        url = decode_url(url)
        response = requests.get(url)
        if response.status_code == 200:
            # Get the video content
            video_content = response.content
            
            video_stream = io.BytesIO(video_content)
            return send_file(video_stream, as_attachment=True, mimetype='video/mp4', download_name='video.mp4')
        else:
            return jsonify({
                'status': False,
                'message': 'Downloading failed'
            })    

    except Exception as e:
        print("E is : ", e)
        return jsonify({
            'status': False,
            'message': 'Something went wrong.'
        }), 400


@app.route("/api/v1/instagram")
@cross_origin()
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
    if not detail:
        return jsonify({
            'status': False,
            'message': 'Something went wrong.'
        })
    video_url = detail['video_url']
    encoded_url = encode_url(video_url)
    try:
        thumbnail_data, _ = (
            ffmpeg.input(video_url)
            .output("pipe:", format="image2", vframes=1)
            .run(capture_stdout=True, capture_stderr=True)
        )
        thumbnail_base64 = base64.b64encode(thumbnail_data).decode("utf-8")
        response_data = {
            'thumbnail': thumbnail_base64,
            'video_url': encoded_url
        }
        return response_data
    except Exception as e:
        return jsonify({
            'thumbnail': 'Failed to generate thumbnail',
            'video_url': encoded_url
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
                "url": quote(stream.url),
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
@cross_origin()
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

def get_facebook_video_detail(url):
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)

        # Sending the url and getting detail
        driver.get("https://snapsave.app/")
        url_input_tag = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='url']"))
        )
        url_input_tag.send_keys(url)
        submit_button = driver.find_element(By.XPATH, "//button[@id='send']")
        submit_button.click()

        try:        
            # getting title image and download url
            image = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//video[@id='vid']"))
            )
            download_url = image.get_attribute('src')
            image_url = image.get_attribute('poster')
        except:
            image_url = None    
            download_url = None
        video_details = {
            'thumbnail': image_url,
            'download_url': download_url
        }

        return video_details   
    except Exception as e:
        return {
            'message': str(e)
        }

    


@app.route("/api/v1/facebook")
def facebook():
    try:
        url = request.args.get("url")
        if not url:
            return jsonify({
                'status': False,
                'message': 'Url not found.'
            }), 400    

        detail = get_facebook_video_detail(url=url)
        detail['status'] = True
        return jsonify(detail)
    except Exception as e:
        print("Exception:", e)
        return jsonify({
            'status': False,
            'error': str(e) 
        }), 400
