import csv
import json
import logging
import os
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

import settings
from utils import ChromeDriver

with open("settings.json", "r") as fp:
    SETTINGS = json.load(fp)

DRIVER = ChromeDriver(window_size=(1080, 720))


class element_is_gone(object):
    def __init__(self, element):
        self.element = element

    def __call__(self, driver):
        try:
            self.element.find_element_by_id("_________")
            return False
        except StaleElementReferenceException:
            return True


def login():
    logging.info("Login...")
    DRIVER.get("https://www.instagram.com/accounts/login")

    username = DRIVER.find_element_by_css_selector('#loginForm > div > div:nth-child(1) > div > label > input')
    password = DRIVER.find_element_by_css_selector('#loginForm > div > div:nth-child(2) > div > label > input')
    submit = DRIVER.find_element_by_css_selector('#loginForm > div > div:nth-child(3) > button')

    username.send_keys(SETTINGS["username"])
    password.send_keys(SETTINGS["password"])
    submit.click()

    WebDriverWait(DRIVER, 10).until(element_is_gone(submit))
    logging.info("Logged in.")


def load_user_info(username):
    logging.info(f"Loading info about {username}")
    html = DRIVER.get_html(f"https://www.instagram.com/{username}/")
    soup = BeautifulSoup(html, "html.parser")
    header = soup.find("header")
    ul = header.find("ul").find_all("li")
    result = {
        "username": username,
        "name": soup.find("h1").get_text(),
        "posts": ul[0].get_text().split(" ")[0].replace(",", ""),
        "followers": ul[1].get_text().split(" ")[0].replace(",", ""),
        "following": ul[2].get_text().split(" ")[0].replace(",", ""),
    }
    return result


def save_to_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8")as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "Name", "Posts", "Followers", "Following"])
        for user in data:
            writer.writerow([user["username"], user["name"], user["posts"], user["followers"], user["following"]])


def main():
    logging.basicConfig(format=settings.LOGGING_FORMAT, level=logging.INFO, datefmt="%H:%M:%S")
    login()
    for user in SETTINGS["accounts"]:
        username_ = user['username']
        logging.info(f"Parsing {username_}")
        DRIVER.get(f"https://www.instagram.com/{username_}/")

        element = DRIVER.find_element_by_css_selector('header > section > ul > li:nth-child(2) > a')
        element.click()

        logging.info("Scrolling to bottom...")

        old_element = None
        element = 0
        while old_element != element:
            old_element = element
            element = DRIVER.find_element_by_css_selector("body > div.RnEpo.Yx5HN > div > div > div.isgrP > ul > div > "
                                                          "li:last-child")
            ActionChains(DRIVER).move_to_element(element).perform()
            time.sleep(1)

        logging.info("Bottom reached")

        subscribers = DRIVER.find_elements_by_css_selector(
            "body > div.RnEpo.Yx5HN > div > div > div.isgrP > ul > div > li")
        result = []
        usernames = []
        for subscriber in subscribers:
            content = subscriber.text.split("\n")
            usernames.append(content[0])

        for username in usernames:
            result.append(load_user_info(username))

        save_to_csv(result, f"{username_}.csv")


if __name__ == '__main__':
    main()

os.system("Pause")
DRIVER.close()
