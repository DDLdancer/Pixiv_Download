from time import sleep
import pixivpy3
import os
import sys
import random
import datetime
from tqdm import tqdm

REFRESH_TOKEN_FILE="token.txt"
IMAGE_FOLDER="images/"

AUTH_SLEEPTIME_MIN=5
AUTH_SLEEPTIME_MAX=20

DOWNLOAD_SLEEPTIME_MIN=1
DOWNLOAD_SLEEPTIME_MAX=2

api = pixivpy3.AppPixivAPI()


def info(s):
    print(datetime.datetime.now().strftime("%H:%M:%S"), s)


def authorization():
    with open(REFRESH_TOKEN_FILE, 'r', encoding="utf-8") as f:
        refresh_token = f.readline()[:-1]
    while True:
        try:
            api.auth(refresh_token=refresh_token)
            info("Login success!")
            break
        except pixivpy3.utils.PixivError:
            info("Authorization failed, try again")
            sleep(random.uniform(AUTH_SLEEPTIME_MIN, AUTH_SLEEPTIME_MAX))


def download_url(url, path):
    api.download(url, path=path)
    sleep(random.uniform(DOWNLOAD_SLEEPTIME_MIN, DOWNLOAD_SLEEPTIME_MAX))


def download_illust(illust_id):
    json_result = api.illust_detail(illust_id)
    title = IMAGE_FOLDER + json_result.illust.user.name + "/" + json_result.illust.title

    # Will not download again if the artwork already exists
    if os.path.exists(title):
        info(title + " already exists!")
        return
    else:
        os.makedirs(title)

    single_page = json_result.illust.meta_single_page
    if single_page != {}:
        download_url(single_page.original_image_url , title)

    meta_pages = json_result.illust.meta_pages
    for i in tqdm(range(len(meta_pages)),
                        desc = title + " downloading"):
        download_url(meta_pages[i].image_urls['original'], title)

    info(title + " download complete!")


def download_author(author_id):
    json_result = api.user_illusts(author_id)
    for illust in json_result.illusts[:]:
        download_illust(illust.id)


def download_bookmark(user_id):
    next_qs = {'user_id': user_id }
    while next_qs is not None:
        json_result = api.user_bookmarks_illust(**next_qs)
        for illust in json_result.illusts[:]:
            download_illust(illust.id)
        next_qs = api.parse_qs(json_result.next_url)


if __name__ == "__main__":
    authorization()

    if (len(sys.argv) >= 3) and (sys.argv[1] == "author"):
        download_author(int(sys.argv[2]))

    elif (len(sys.argv) >= 3) and (sys.argv[1] == "bookmark"):
        download_bookmark(int(sys.argv[2]))

    else:
        while True:
            illust_id = int(input("Please enter illust id:"))
            if illust_id != 0:
                download_illust(illust_id)
            else:
                break
