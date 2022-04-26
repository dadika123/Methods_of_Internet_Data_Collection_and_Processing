"""
2. Check out list of open APIs, find the one that requires auth.
Make requests with auth and save responses to JSON.
"""
import os
import re
import json

import requests
from dotenv import load_dotenv

load_dotenv()

YT_URL = 'https://www.googleapis.com/youtube/v3'
YT_VIDEOS_RES = 'videos'
PARAMS = {
    'key': os.getenv('API_KEY'),
    'part': 'snippet,contentDetails,statistics,status'
}


def get_video_data(video_url: str) -> dict:
    """Gets data about a
    YouTube video via its URL.

    :param video_url: YouTube video URL.
    :return: YouTube video data dict.
    """
    match = re.search(r'watch\?v=(.+)', video_url)
    vid_id = match.group(1)
    params = {**PARAMS, 'id': vid_id}
    response = requests.get(f'{YT_URL}/{YT_VIDEOS_RES}', params=params)
    return response.json()


def main():
    video_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    video_data = get_video_data(video_url)
    with open('task2.json', 'w') as file:
        json.dump(video_data, file, indent=2)


if __name__ == '__main__':
    main()
