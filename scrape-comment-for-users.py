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
USER_HANDLE_TO_INSPECT = ""

COMMENT_PAGE_LENGTH = 12
COMMENT_PAGES_TO_SCAN = 1

DATABASE_NAME = ""
COLLECTION_NAME = ""

def init_mongo_client():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")

    db = myclient[DATABASE_NAME]    

    col = db[COLLECTION_NAME]

    return col

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

def scrape_comment_from_post(post_id : int, comment : str, browser : WebDriver, db_collection):
    browser.get('https://www.instagram.com/p/' + str(post_id))

    sleep(randrange(2, 5))
    
    sub_window = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/div[1]/article/div[3]/div[1]/ul")
    #/html/body/div[1]/section/main/div/div[1]/article/div[3]/div[1]/ul sub window

    #May not need to scroll if comment is high enough
    #for i in range(3):
        #browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sub_window)
        #click + button for more comments to load

    #/html/body/div[1]/section/main/div/div[1]/article/div[3]/div[1]/ul/div top pinned user comment
    #/html/body/div[1]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul[1]/div/li/div/div[1]/div[2]/span first comment
    #/html/body/div[1]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul[12]/div/li/div/div[1]/div[2]/span last comment

    #for now we are assuming comment is on the first page of comments
    for i in range(COMMENT_PAGES_TO_SCAN * COMMENT_PAGE_LENGTH):
        ith_comment = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul[" + str(i + 1) + "]/div/li/div/div[1]/div[2]/span").text
        print("Analyzing: \'" + ith_comment + "\'\n for phrase: " + comment)
        if ith_comment.find(comment) != -1:
            print("\n***Target Comment Found***: "+ ith_comment +" \n")
            scrape_users_from_comment(browser, i + 1, db_collection) #target comment found
            break

def scrape_users_from_comment(browser: WebDriver, index : int, db_collection):
    likes = int(float(browser.find_element_by_xpath("/html/body/div[1]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul["+ str(index) +"]/div/li/div/div[1]/div[2]/div/div/button[1]").text.split()[0]))
    print(str(likes) + " users to parse...")

    browser.find_element_by_xpath("/html/body/div[1]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul["+ str(index) +"]/div/li/div/div[1]/div[2]/div/div/button[1]").click()
    sleep(1)

    users_cache = []
    sub_window = browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/div")

    time_processed = time()
    users_inserted = 0
    for page in range(int(likes / 10)):

        for u in range(18):
            try:
                user = browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/div/div/div["+ str(u + 1) +"]/div[2]/div[1]/div/span/a").text
                if not user in users_cache: #user_cache to deal with scrolling inconsistencies in difficult to predict dynamic scroll flex, prevents duplicate entries
                    print(user + " liked this comment")
                    users_cache.append(user)
                    try:
                        insert_user_to_database(user, time_processed, db_collection)
                        users_inserted += 1
                    except Exception:
                        print("Something went wrong adding to the database")
                    
            except Exception:
                break #continue scrolling

        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sub_window)
        sleep(1)
    print("Inserted " + str(users_inserted) + " out of " + str(likes) + " into database")
    print("Exiting...")

def insert_user_to_database(user : str, time_processed : str, db_collection):
    try:
        new_entry = {"username": user, "time_processed": time_processed, "follow_request_sent":"f"}
        db_collection.insert_one(new_entry)
        print("\n*Successfully added user: " + user + " to the database*\n")
    except Exception as e:
        print(e)

def main():
    if len(sys.argv) == 4 and sys.argv[3] == "headless":
        headless = True
    else:
        headless = False

    if len(sys.argv) > 4:
        print("Usage incorrect: *Post ID* *Comment Text To Scrape From* //optional *headless*")
        sys.exit(0)
    
    try:
        post_id = sys.argv[1]
        comment = sys.argv[2]

        browser = login(GAA_USERNAME, GAA_PASSWORD, headless)

        sleep(randrange(2, 4))

        db_collection = init_mongo_client()

        sleep(1)

        scrape_comment_from_post(post_id, comment, browser, db_collection)

    except Exception as e:
        print("EXCEPTION THROWN DURING EXECUTION...EXITING")
        print(e)
    finally:
        browser.quit()

main() 
