"""
1. Read the GitHub API documentation, figure out
how to get user's list of repositories, and save it as JSON.
"""
import json

import requests

GIT_URL = 'https://api.github.com/users'
GIT_REPOS_RES = 'repos'


def get_user_repos(username: str) -> list:
    """Gets GitHub users list of
    repositories and their urls.

    :param username: GitHub user username.
    :return: list of objects with repos name and url.
    """
    response = requests.get(f'{GIT_URL}/{username}/{GIT_REPOS_RES}')
    response_dict = response.json()
    return [{'name': repo['full_name'], 'url': repo['html_url']} for repo in response_dict]


def main():
    repos = get_user_repos('dadika123')
    with open('task1.json', 'w') as file:
        json.dump(repos, file, indent=2)


if __name__ == '__main__':
    main()
