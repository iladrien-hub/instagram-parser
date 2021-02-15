import pickle

import requests
from selenium import webdriver

import settings


class GetHtmlError(Exception):
    pass


class ChromeDriver(webdriver.Chrome):
    __COOKIES = "cookies.txt"

    def __init__(self, arguments=None, window_size=None):
        options = webdriver.ChromeOptions()
        if arguments is not None:
            for argument in arguments:
                # options.add_argument('headless')
                options.add_argument(argument)
        super(ChromeDriver, self).__init__(options=options)
        super(ChromeDriver, self).implicitly_wait(10)
        if window_size is not None:
            w, h = window_size
            self.set_window_size(w, h)

    def get_html(self, url, params=None):
        self.get(apply_params(url, params))
        return self.page_source

    def get(self, url, params=None):
        return super(ChromeDriver, self).get(apply_params(url, params))

    def save_cookie(self, path=__COOKIES):
        with open(path, 'wb') as fp:
            pickle.dump(self.get_cookies(), fp)

    def load_cookie(self, path=__COOKIES):
        with open(path, 'rb') as fp:
            cookies = pickle.load(fp)
            for cookie in cookies:
                self.add_cookie(cookie)


class Optional:
    def __init__(self, obj):
        self.obj = obj

    def orElse(self, else_obj):
        if self.obj is None:
            return else_obj
        return self.obj


def apply_params(url, params=None):
    if params is None:
        return url
    url += "?" + "&".join([f"{key}={params[key]}" for key in params.keys()])
    return url


def get_html(url, params=None):
    r = requests.get(url, params=params, headers=settings.HEADERS)
    if r.status_code == 200:
        return r.text
    else:
        raise GetHtmlError(f"Server response: {r}")
