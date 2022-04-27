import os
import re

import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from urllib.parse import urlencode
from dotenv import load_dotenv

from instagram.items import InstagramUserItem

load_dotenv()


class ProfilesSpider(scrapy.Spider):
    name = 'profiles'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    login_form_data = {
        'username': os.getenv('INST_LOGIN'),
        'enc_password': os.getenv('INST_PASS_ENC')
    }
    common_headers = {
        'User-Agent': 'Instagram 155.0.0.37.107'
    }
    followers_link = 'https://i.instagram.com/api/v1/friendships/%s/followers/'
    followers_params = {
        'count': 12,
        'search_surface': 'follow_list_page'
    }
    following_link = 'https://i.instagram.com/api/v1/friendships/%s/following/'
    following_params = {
        'count': 12
    }

    def __init__(self, profiles: list or str, **kwargs):
        super(ProfilesSpider, self).__init__(*kwargs)
        if isinstance(profiles, str):
            profiles = profiles.split(',')
        self.profiles = profiles

    def parse(self, response: HtmlResponse, **kwargs):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata=self.login_form_data,
                                 headers={'X-CSRFToken': csrf})

    def login(self, response: HtmlResponse):
        data = response.json()
        if data.get('authenticated'):
            for profile in self.profiles:
                yield response.follow(
                    f'{self.start_urls[0]}{profile}/',
                    callback=self.parse_profile,
                    cb_kwargs={'profile': profile}
                )

    def parse_profile(self, response: HtmlResponse, profile):
        user_id = re.search(r'\"graphql\":{\"user\":.+?(?=\"id\")\"id\":\"(\d+)\"', response.text).group(1)
        base_url = f'{self.followers_link % user_id}'
        yield response.follow(
            f'{base_url}?{urlencode(self.followers_params, doseq=True)}',
            callback=self.parse_users,
            cb_kwargs={'base_url': base_url,
                       'profile': profile,
                       'params': self.followers_params,
                       'users_type': 'followers'},
            headers=self.common_headers
        )
        base_url = f'{self.following_link % user_id}'
        yield response.follow(
            f'{base_url}?{urlencode(self.following_params, doseq=True)}',
            callback=self.parse_users,
            cb_kwargs={'base_url': base_url,
                       'profile': profile,
                       'params': self.following_params,
                       'users_type': 'following'},
            headers=self.common_headers
        )

    def parse_users(self, response: HtmlResponse, base_url, profile, params, users_type):
        data = response.json()
        for user_data in data.get('users'):
            yield self.prepare_user(response, profile, user_data, users_type)
        if data.get('big_list'):
            next_params = {**params, 'max_id': data.get('next_max_id')}
            yield response.follow(
                f'{base_url}?{urlencode(next_params, doseq=True)}',
                callback=self.parse_users,
                cb_kwargs={'base_url': base_url,
                           'profile': profile,
                           'params': params,
                           'users_type': users_type},
                headers=self.common_headers
            )

    @staticmethod
    def prepare_user(response, profile, data, user_type):
        loader = ItemLoader(item=InstagramUserItem(), response=response)
        loader.add_value('caller_username', profile)
        loader.add_value('pk', data.get('pk'))
        loader.add_value('username', data.get('username'))
        loader.add_value('full_name', data.get('full_name'))
        loader.add_value('photo', data.get('profile_pic_url'))
        loader.add_value('is_private', data.get('is_private'))
        loader.add_value('type', user_type)
        return loader.load_item()

    @staticmethod
    def fetch_csrf_token(text):
        return re.search(r'\"csrf_token\":\"(\w+)\"', text).group(1)
