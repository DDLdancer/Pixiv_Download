import json
from time import sleep
import pixivpy3
import os
import sys
import random
import datetime

REFRESH_TOKEN_FILE="token.txt"
IMAGE_FOLDER="images/"

AUTH_SLEEPTIME_MIN=5
AUTH_SLEEPTIME_MAX=20

DOWNLOAD_SLEEPTIME_MIN=2
DOWNLOAD_SLEEPTIME_MAX=5

api = pixivpy3.AppPixivAPI()


def authorization():
    with open(REFRESH_TOKEN_FILE, 'r', encoding="utf-8") as f:
        refresh_token = f.readline()[:-1]
    while True:
        try:
            api.auth(refresh_token=refresh_token)
            print("Login success!")
            break
        except pixivpy3.utils.PixivError:
            print("Authorization failed, try again")
            sleep(random.randint(AUTH_SLEEPTIME_MIN, AUTH_SLEEPTIME_MAX))


def check_create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def download_url(url, path):
    api.download(url, path=path)
    print(datetime.datetime.now().strftime("%H:%M:%S"), "image downloaded to", path)
    sleep(random.randint(DOWNLOAD_SLEEPTIME_MIN, DOWNLOAD_SLEEPTIME_MAX))


def download_illust(illust_id):
    json_result = api.illust_detail(illust_id)
    title = IMAGE_FOLDER + json_result.illust.user.name + "/" + json_result.illust.title
    check_create_dir(title)

    single_page = json_result.illust.meta_single_page
    if single_page != {}:
        download_url(single_page.original_image_url , title)

    for meta_page in json_result.illust.meta_pages[:]:
        download_url(meta_page.image_urls['original'], title)

    print(title, "download complete!")


def download_author(author_id):
    json_result = api.user_illusts(author_id)
    for illust in json_result.illusts[:]:
        download_illust(illust.id)


if __name__ == "__main__":
    authorization()

    if len(sys.argv) >= 2:
        download_author(int(sys.argv[2]))

    else:
        while True:
            illust_id = int(input())
            if illust_id != 0:
                download_illust(illust_id)
            else:
                break
