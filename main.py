import argparse
import os

from dotenv import load_dotenv
import requests
from requests.compat import urljoin, urlparse
from requests.exceptions import HTTPError

load_dotenv()

API_URL = "https://api-ssl.bitly.com/v4/"
USER_URL_PART = "user"
CREATE_URL_PART = "bitlinks"
CLICKS_URL_PART = "/clicks/summary"
bitly_token = os.getenv("TOKEN")


def is_bitlink(test_url="", token=""):
    parsed_obj = urlparse(test_url)
    bitly_url = parsed_obj.netloc + parsed_obj.path 
    url = urljoin(
      API_URL, CREATE_URL_PART + "/" + bitly_url
    )
    headers = {
      "Authorization": "Bearer " + token
    }
    response = requests.get(
      url=url,
      headers=headers,
    )
    if response.status_code not in (200, 404):
        response.raise_for_status()
    return response.status_code == 200


def create_bitlink(long_url="", token=""):
    url = urljoin(
      API_URL, CREATE_URL_PART
    )
    headers = {
      "Authorization": "Bearer " + token
    }
    payload = {
      "long_url": long_url
    }
    response = requests.post(
      url=url,
      headers=headers,
      json=payload
    )
    response.raise_for_status()
    return response.json()["link"]


def get_total_clicks(short_url="", token=""):
    parsed_obj = urlparse(short_url)
    bitly_url = parsed_obj.netloc + parsed_obj.path 
    path = "bitlinks/{bitlink}/clicks/summary".format(bitlink=bitly_url)
    url = urljoin(
      API_URL, path
    )
    headers = {
      "Authorization": "Bearer " + token
    }
    payload = {
        "units": -1,
        "unit": "day"
    }
    response = requests.get(
      url=url,
      headers=headers,
      params=payload
    )
    response.raise_for_status()
    return response.json()["total_clicks"]


def main():
    parser = argparse.ArgumentParser(
      description="Консольная утилита для работы с сервисом bit.ly"
    )
    parser.add_argument(
      "link", help="Ссылка на существующий битли, либо новая ссылка"
    )
    args = parser.parse_args()
    link = args.link
    try:
        test_is_bitlink = is_bitlink(test_url=link, token=bitly_token)
    except HTTPError as error:
        exit("Невозможно получить данные с сервера:\n{0}\n".format(error))

    if test_is_bitlink:
        try:
            res = get_total_clicks(link, bitly_token)
        except HTTPError as error:
            exit("Невозможно получить данные с сервера:\n{0}\n".format(error))
        print("Всего переходов по ссылке: {0}".format(res))
    else:
        try:
            res = create_bitlink(link, bitly_token)
        except HTTPError as error:
            exit("Невозможно получить данные с сервера:\n{0}\n".format(error))
        print(res)


if __name__ == '__main__':
    main()
