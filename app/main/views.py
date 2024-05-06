import re
import requests
from . import bp
from .helpers import *
from flask import request, jsonify, send_file


@bp.route("/api/v1/instagram")
def instagram():
    url = request.args.get('url')
    if not url:
        return jsonify({
            'status': False,
            'message': 'Url not found.'
        }), 400
    # regex = r'^https?:\/\/(?:www\.)?instagram\.com\/reel\/[a-zA-Z0-9_-]+\/\?igsh=[a-zA-Z0-9_+-=]+$'
    # if not validate_url(url=url, regex=regex):
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

@bp.route("/api/v1/tiktok")
def tiktok():
    url = request.args.get("url")
    if not url:
        return jsonify({
            'status': False,
            'message': 'Url not found.'
        }), 400    
    scraping_url = "https://tikdownloader.io/api/ajaxSearch"

    headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
    data = {"q": url}

    try:
        response = requests.post(scraping_url, headers=headers, data=data)
        if response.status_code == 200:
            response_json = response.json()
            print("Response json is : ", response_json)
        else:
            print("Error: Request failed with status code", response.status_code)
            # Handle error case
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        # Handle error case
    return ""