from os import write
from time import sleep
from datetime import datetime
from selenium import webdriver
from random import randrange
import sys
import _thread
import pymongo

from selenium.webdriver.firefox.webdriver import WebDriver

GAA_USERNAME = ""
GAA_PASSWORD = ""
USER_HANDLE_TO_INSPECT = ""

CONNECTION_UNFOLLOW_THRESHOLD = 16 #after 16 unfollows it seems the connection becomes stale and any operations afterwards on the page is void
NUM_TO_UNFOLLOW = 32 
                     #TODO add logic to refresh page and restart unfollowing after 16 unfollows

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
    print("\n***New thread started: Logging followers in Database***\n")
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

def init_mongo_client():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")

    db = myclient["Followers"]

    col = db["followers"]    

    return col

def clear_followers(browser : WebDriver):
    followers = get_current_followers(browser)
    try:
        _thread.start_new_thread(log_followers_in_database, (followers, ))
    except Exception as e:
        print("Error starting up new thread")
        print(e)

    num_following = int(float(browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[3]/a/span").text.replace(",","")))
    print("Num Following: " + str(num_following))
    
    get_following_and_scroll_to_bottom(browser, num_following)

    print("Looping Following")
    non_friends = 0
    for f in range(num_following):
        try:
            following = browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/ul/div/li[" + str(f + 1) + "]/div/div[1]/div[2]/div[1]/span/a")
            following_text = following.text
            if not following_text in followers:
                print("\nYou follow " + following_text + " but they do not follow you")
                try:
                    unfollow_user(browser, following_text, f + 1)
                    non_friends += 1
                    if non_friends % CONNECTION_UNFOLLOW_THRESHOLD == 0 :
                        print("\n***REFRESHING PAGE***\n")
                        get_following_and_scroll_to_bottom(browser, num_following)
                    if (non_friends >= NUM_TO_UNFOLLOW):
                        break #prevent action limiting
                except Exception:
                    print("Error Unfollowing User at : " + str(f + 1))

                sleep(randrange(1,3))
        except Exception:
            print("Could not find element at /html/body/div[5]/div/div/div[2]/ul/div/li[" + str(f + 1) + "]/div/div[1]/div[2]/div[1]/span/a") 

    print("Num of people unfollowed: " + str(non_friends))
    sleep(10)

def get_following_and_scroll_to_bottom(browser : WebDriver, num_following : int):
    print("Getting Following...")
    browser.get("https://www.instagram.com/" + USER_HANDLE_TO_INSPECT + "/")
    sleep(randrange(2,5))

    browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[3]/a").click()
    sleep(1)

    sub_window = browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]")
    print("Scrolling to bottom")
    for i in range(int(num_following / 5)):
        # Scroll down to bottom
        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sub_window)

        # Wait to load page
        sleep(1.25)

def unfollow_user(browser: WebDriver, username : str, index : int):
    #print("/html/body/div[5]/div/div/div[2]/ul/div/li[" + str(index) + "]/div/div[2]/button")
    browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/ul/div/li[" + str(index) + "]/div/div[2]").click() #opens unfollow prompt
    sleep(randrange(2,4))

    browser.find_element_by_xpath("/html/body/div[6]/div/div/div/div[3]/button[1]").click() #unfollow button, confirm
    sleep(randrange(2,4))

    print("UNFOLLOWED " + username + "\n")

def get_current_followers(browser : WebDriver):
    num_followers_elem = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span")
    num_followers = int(float(num_followers_elem.text.replace(",","")))
    print("Num Followers: " + str(num_followers))

    browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[2]/a").click() #open up followers
    sleep(1)

    sub_window = browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]")
    print("Scrolling to bottom")
    for i in range(int(num_followers / 8)):
        # Scroll down to bottom
        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sub_window)

        # Wait to load page
        sleep(1.25)

    print("Looping followers")
    followers = []
    for f in range(num_followers):
        try:
            follower = browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/ul/div/li[" + str(f + 1) + "]/div/div[1]/div[2]/div[1]/span/a")  
            followers.append(follower.text)
        except Exception:
            print("Could not find element at /html/body/div[5]/div/div/div[2]/ul/div/li[" + str(f + 1) + "]/div/div[1]/div[2]/div[1]/span/a") 

    return followers

def main():
    if len(sys.argv) > 1 and int(sys.argv[1]) > 0:
        print("Starting in headless mode...")
        headless = True
    else:
        headless = False
    
    browser = login(GAA_USERNAME, GAA_PASSWORD, headless)
    
    try:
        browser.get('https://www.instagram.com/' + USER_HANDLE_TO_INSPECT + '/')
        sleep(randrange(2,5))

        clear_followers(browser)
    except KeyboardInterrupt:
        print("Ending Session")
    finally:
        browser.quit()
        sys.exit(0)

main()