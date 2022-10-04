from time import sleep
from datetime import datetime
from selenium import webdriver
from random import randrange
import sys

FAKE_COMMENTS = [

]

USERNAME = ""
PASSWORD = ""

def login(browser):
    browser.get('https://www.instagram.com/')
    sleep(randrange(4,7))

    username_input = browser.find_element_by_css_selector("input[name='username']")
    password_input = browser.find_element_by_css_selector("input[name='password']")

    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)

    login_button = browser.find_element_by_xpath("//button[@type='submit']")
    login_button.click()

    sleep(randrange(4,7))

def comment_on_last_x_posts(browser, x_posts):
    for i in range(x_posts):
        try: 
            a_post = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/div[2]/article/div[1]/div/div[" + str(int((i / 3)) + 1) + "]/div[" + str(int((i % 3)) + 1) + "]")
            a_post.click()
            sleep(randrange(2,5))

            comment_section = browser.find_element_by_xpath("/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form/textarea")
            comment_section.click()
            comment_to_post = FAKE_COMMENTS[randrange(0, len(FAKE_COMMENTS) - 1)]
            browser.find_element_by_xpath("/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form/textarea").send_keys(comment_to_post)
            sleep(randrange(2,5))

            post_button = browser.find_element_by_xpath("/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form/button[2]")
            post_button.click()
            sleep(randrange(2,5))

            print("POSTED COMMENT: \'" + comment_to_post + "\' @ " + datetime.now().strftime("%H:%M:%S"))

        except Exception as e:
            print("ERROR: Couldn't find post or post page element at /html/body/div[1]/section/main/div/div[2]/article/div[1]/div/div[" + str(int((i / 3)) + 1) + "]/div[" + str(int((i % 3)) + 1) + "]\n")
            print(e)
        
        browser.get('https://www.instagram.com/goofed.goober/')
        sleep(randrange(2,5))


def monitor_for_new_posts(browser, sleep_time_seconds):
    last_num_posts = 0;

    while (True):
        try:
            #num_posts_el = browser.find_element_by_class_name("g47SY ")
            num_posts_el = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span") #xpath when user logged in
            #num_posts_el = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[1]/a/span") #xpath when user not logged in
            sleep(1)
            num_posts = int(float(num_posts_el.text.replace(',',''))) #remove commas from string rep of posts

            print("Scanning for new posts..." + str(num_posts) + " posts at " + datetime.now().strftime("%H:%M:%S") + "\n")

            if num_posts > last_num_posts and last_num_posts != 0:
                print(str(num_posts - last_num_posts) + " New Posts...Total Posts Now: " + str(num_posts) + " " + datetime.now().strftime("%H:%M:%S"))
                #login(browser)
                comment_on_last_x_posts(browser, num_posts - last_num_posts) #there may be multiple new posts depending on how frequently we are checking

            last_num_posts = num_posts

            browser.refresh()

        except Exception as e:
            print("ERROR")
            print(e)
            browser.refresh()
        
        sleep(randrange(sleep_time_seconds - 10, sleep_time_seconds + 10))

        
def main():
    firefoxOptions = webdriver.FirefoxOptions()
    if len(sys.argv) > 1 and int(sys.argv[1]) > 0:
        print("Starting in headless mode...")
        headless = True
    else: 
        headless = False

    firefoxOptions.headless = headless
    browser = webdriver.Firefox(options=firefoxOptions)
    browser.implicitly_wait(5)

    login(browser)

    browser.get('https://www.instagram.com/goofed.goober/')
    sleep(randrange(2,7))

    monitor_for_new_posts(browser, 60)

main()

