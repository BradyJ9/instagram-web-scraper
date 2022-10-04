from time import sleep
from datetime import datetime
from selenium import webdriver
from random import randrange
import sys
from pydub import AudioSegment
from pydub.playback import play

#Add in comments for the bot here
FAKE_COMMENTS_BACKUP = [

]

FAKE_COMMENTS = [

]

#support for multiple users, to prevent rate limiting
USERS = [

]

def login(username, password, headless):
    firefoxOptions = webdriver.FirefoxOptions()
    firefoxOptions.headless = headless
    browser = webdriver.Firefox(options=firefoxOptions) #new browser with no cookies/history
    browser.implicitly_wait(5)

    browser.get('https://www.instagram.com/') #login page if no cookies/cached data
    sleep(randrange(2,5))

    username_input = browser.find_element_by_css_selector("input[name='username']")
    password_input = browser.find_element_by_css_selector("input[name='password']")

    username_input.send_keys(username)
    password_input.send_keys(password)

    login_button = browser.find_element_by_xpath("//button[@type='submit']")
    login_button.click()

    sleep(randrange(2,5))

    return browser
    
def comment_on_last_x_posts(browser, x_posts):
    rand_comment = randrange(0, len(FAKE_COMMENTS) - 1)
    last_rand_comment = rand_comment
    for i in range(x_posts):
        try: 
            a_post = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/div[2]/article/div[1]/div/div[" + str(int((i / 3)) + 1) + "]/div[" + str(int((i % 3)) + 1) + "]")
            a_post.click()
            sleep(1)

            comment_section = browser.find_element_by_xpath("/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form/textarea")
            comment_section.click()

            while rand_comment == last_rand_comment: 
                rand_comment = randrange(0, len(FAKE_COMMENTS) - 1)
            comment_to_post = FAKE_COMMENTS[rand_comment]
            last_rand_comment = rand_comment

            browser.find_element_by_xpath("/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form/textarea").send_keys(comment_to_post)
            sleep(1)

            post_button = browser.find_element_by_xpath("/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form/button[2]")
            post_button.click()
            sleep(1)

            print("POSTED COMMENT: \'" + comment_to_post + "\' @ " + datetime.now().strftime("%H:%M:%S"))

        except Exception as e:
            print("ERROR: Couldn't find post or post page element at /html/body/div[1]/section/main/div/div[2]/article/div[1]/div/div[" + str(int((i / 3)) + 1) + "]/div[" + str(int((i % 3)) + 1) + "]\n")
            print(e)
        
        browser.get('https://www.instagram.com/goofed.goober/')
        sleep(randrange(2,5))


def monitor_for_new_posts(browser, sleep_time_seconds, headless):
    last_num_posts = 0
    user_index = 0
    last_hour = datetime.now().hour

    while (True):

        curr_hour = datetime.now().hour
        if curr_hour != last_hour: #change user every hour on the hour
            last_hour = curr_hour
            user_index = user_index + 1 if user_index < (len(USERS) - 1) else 0
            browser.close() #close or quit?

            browser = login(USERS[user_index][0], USERS[user_index][1], headless)
            print("****************\n******LOGGING IN NEW USER******\n****************")
            print ("****Now logged in as: " + USERS[user_index][0] + "****")

            browser.get('https://www.instagram.com/goofed.goober/')
            sleep(randrange(2,5))

        try:
            #num_posts_el = browser.find_element_by_class_name("g47SY ")
            #num_posts_el = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[1]/a/span") #xpath when user not logged in
            num_posts_el = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span") #xpath when user logged in
            sleep(1)
            num_posts = int(float(num_posts_el.text.replace(',',''))) #remove commas from string rep of posts

            print("Scanning for new posts..." + str(num_posts) + " posts at " + datetime.now().strftime("%H:%M:%S") + " as " + USERS[user_index][0] + "\n")
            #mp3_file = AudioSegment.from_file(file="rightAnswer.mp3", format="mp3")
            #play(mp3_file)

            if num_posts > last_num_posts and last_num_posts != 0:
                browser.close()
                print(str(num_posts - last_num_posts) + " New Posts...Total Posts Now: " + str(num_posts) + " " + datetime.now().strftime("%H:%M:%S"))

                comment_browser = login(USERS[0][0], USERS[0][1], headless) #all comments come from same user goobers_against_ads_r
                comment_browser.get('https://www.instagram.com/goofed.goober/')
                sleep(randrange(2,5))

                comment_on_last_x_posts(comment_browser, num_posts - last_num_posts) #there may be multiple new posts depending on how frequently we are checking
                comment_browser.close()

                browser = login(USERS[user_index][0], USERS[user_index][1], headless)
                browser.get('https://www.instagram.com/goofed.goober/')
                sleep(randrange(2,5))

            last_num_posts = num_posts

            browser.refresh()

        except Exception as e:
            print("ERROR")
            print(e)
            #mp3_file = AudioSegment.from_file(file="wrongAnswer.mp3", format="mp3")
            #play(mp3_file)
            browser.refresh()
        
        sleep(randrange(sleep_time_seconds - 5, sleep_time_seconds + 10))
        #sleep(sleep_time_seconds)

        
def main():
    if len(sys.argv) > 1 and int(sys.argv[1]) > 0:
        print("Starting in headless mode...")
        headless = True
    else:
        headless = False
    
    browser = login(USERS[0][0], USERS[0][1], headless)
    
    try:
        browser.get('https://www.instagram.com/goofed.goober/')
        sleep(randrange(2,5))

        monitor_for_new_posts(browser, 30, headless)
    except KeyboardInterrupt:
        print("Ending Session")
        browser.quit()
        sys.exit(0)




main()
