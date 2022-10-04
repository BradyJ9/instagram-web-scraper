from os import write
from time import sleep, time
from datetime import datetime
from selenium import webdriver
from random import randrange
import sys
import pymongo

from selenium.webdriver.firefox.webdriver import WebDriver

GAA_USERNAME = ""
GAA_PASSWORD = ""

DATABASE_NAME = ""
COLLECTION_NAME = ""

FOLLOWER_DATABASE_NAME = ""
FOLLOWER_COLLECTION_NAME = ""

HISTORY_COLLECTION = "Followed"

NUMBER_TO_FOLLOW = 12 #too much will cause action limiting

DAY_IN_SECONDS = 86400
HOUR_IN_SECONDS = 3600

def init_mongo_client():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")

    return myclient

def login(username, password, headless):
    firefoxOptions = webdriver.FirefoxOptions()
    firefoxOptions.headless = headless
    browser = webdriver.Firefox(options=firefoxOptions) #new browser with no cookies/history
    browser.implicitly_wait(3)

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

#/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/button "Follow" button on private page
#/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/button

#/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button "Follow button on public page"
#/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button Text is "Follow"
#/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button

#/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button already following
#/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button/div/span

def follow_x_users(browser: WebDriver, db_client):
    users_followed = 0
    users = db_client[DATABASE_NAME][COLLECTION_NAME].find({"follow_request_sent": "f"}).sort("time_processed", -1)
    for i in range(NUMBER_TO_FOLLOW):
        user = users[i]
        print(user)
        username = user["username"]

        browser.get('https://www.instagram.com/' + username)
        sleep(randrange(2,5))

        db_client[DATABASE_NAME][COLLECTION_NAME].update_one({"username":username}, { "$set": { "follow_request_sent": "t" , "time_followed": time()} })

        if db_client[FOLLOWER_DATABASE_NAME][FOLLOWER_COLLECTION_NAME].find_one({"follower":username}): #already being followed by that user
            print(username + " is already following you...not following")
            db_client[DATABASE_NAME][COLLECTION_NAME].update_one({"username":username}, {"$set": { "already_followed_when_requested": "t" }})
        else:
            try:
                followButton = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button")
                if followButton.text == "Follow":
                    followButton.click()
                    users_followed += 1
                    print("\nFollow request sent to " + username + "\n")
            except Exception as e:
                print("Account may be private...")
                try:
                    followButton = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/button")
                    if followButton.text == "Follow":
                        followButton.click()
                        users_followed += 1 
                        print("\nFollow request sent to " + username + "\n")
                except Exception as e:
                    print(e)
                    print("Already following " + username + " or ERROR")  
            
            sleep(3)  
            
    print("***************************")
    print("********FINAL STATS********")
    print("***************************")

    print("FOLLOWED " + str(users_followed) + " USERS")

    last_hour = db_client[DATABASE_NAME][COLLECTION_NAME].count_documents({"time_followed": { "$gt": time() - HOUR_IN_SECONDS}})
    print("In last hour...Followed " + str(last_hour) + " by automation")

    last_day = db_client[DATABASE_NAME][COLLECTION_NAME].count_documents({"time_followed": { "$gt": time() - DAY_IN_SECONDS}})
    print("In last 24 hours...Followed " + str(last_day) + " by automation")

    last_two_days = db_client[DATABASE_NAME][COLLECTION_NAME].count_documents({"time_followed": { "$gt": time() - (DAY_IN_SECONDS * 2)}})
    print("In last 48 hours...Followed " + str(last_two_days) + " by automation")

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "headless":
        headless = True
    else:
        headless = False

    if len(sys.argv) > 2:
        print("Usage incorrect: //optional *headless*")
        sys.exit(0)

    try:
        browser = login(GAA_USERNAME, GAA_PASSWORD, headless)

        db_client = init_mongo_client()

        follow_x_users(browser, db_client)
    except Exception as e:
        print(e)
    finally:
        browser.quit()

main()
