from os import write
from time import sleep
from datetime import datetime
from selenium import webdriver
from random import randrange
import sys
import _thread
import pymongo

from selenium.webdriver.firefox.webdriver import WebDriver

GAA_USERNAME = "make_sportscenter_post_sports"
GAA_PASSWORD = "down_with_omar"
USER_HANDLE_TO_INSPECT = "make_sportscenter_post_sports"

def init_mongo_client():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")

    db = myclient["Followers"]

    col = db["followers"]    

    return col

def login(username, password, headless):
    firefoxOptions = webdriver.FirefoxOptions()
    firefoxOptions.headless = headless
    browser = webdriver.Firefox(options=firefoxOptions) #new browser with no cookies/history
    browser.implicitly_wait(5)

    browser.get('https://www.instagram.com/') #login page if no cookies/cached data
    sleep(randrange(4,7))

    username_input = browser.find_element_by_css_selector("input[name='username']")
    password_input = browser.find_element_by_css_selector("input[name='password']")

    username_input.send_keys(username)
    password_input.send_keys(password)

    login_button = browser.find_element_by_xpath("//button[@type='submit']")
    login_button.click()

    sleep(randrange(4,7))

    return browser

def log_followers_in_database(followers):
    db_collection = init_mongo_client()
    db_collection.drop()
    db_collection.create_index([("follower", pymongo.TEXT)], unique=True)
    
    added = 0
    for f in followers:
        try:
            db_collection.insert_one({"follower": f})
            added += 1
        except Exception as e:
            print(e)

    print("Added " + str(added) + " followers")

def update_current_followers(browser : WebDriver):
    num_followers_elem = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span")
    num_followers = int(float(num_followers_elem.text.replace(",","")))
    print("Num Followers: " + str(num_followers))

    browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[2]/a").click() #open up followers
    sleep(1)

    sub_window = browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]")
    print("Scrolling to bottom")
    for i in range(int(num_followers / 10)):
        # Scroll down to bottom
        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sub_window)

        # Wait to load page
        sleep(1.5)

    print("Looping followers")
    followers = []
    for f in range(num_followers):
        try:
            follower = browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/ul/div/li[" + str(f + 1) + "]/div/div[1]/div[2]/div[1]/span/a")  
            followers.append(follower.text)
        except Exception:
            print("Could not find element at /html/body/div[5]/div/div/div[2]/ul/div/li[" + str(f + 1) + "]/div/div[1]/div[2]/div[1]/span/a") 

    log_followers_in_database(followers)

def main():
    try:
        browser = login(GAA_USERNAME, GAA_PASSWORD, False)

        browser.get('https://www.instagram.com/' + USER_HANDLE_TO_INSPECT + '/')
        sleep(randrange(2,5))

        update_current_followers(browser)
    except Exception as e:
        print(e)
    finally:
        browser.quit()

main()