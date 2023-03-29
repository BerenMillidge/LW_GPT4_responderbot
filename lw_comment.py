import openai
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import feedparser
from datetime import datetime, timedelta
import json

openai.api_key = "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"
API_KEY = "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"
API_ENDPOINT = "https://api.openai.com/v1/chat/completions"


LW_EMAIL = "gpt4responderbot"
LW_PASSWORD = "gpt4responder12345!"

def list_engines():
    engines = openai.Engine.list()
    return engines['data']


def generate_chat_completion(messages, model="gpt-4", temperature=1, max_tokens=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if max_tokens is not None:
        data["max_tokens"] = max_tokens

    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

def get_new_posts():
    feed = feedparser.parse("http://lesswrong.com/feed.xml")
    #print("FEED: ", feed)

    # Get the current time
    now = datetime.now()

    # Get the time 24 hours ago
    past_24_hours = now - timedelta(hours=24)

    # Filter entries published in the past 24 hours
    new_entries = []
    for entry in feed.entries:
        entry_time = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
        if entry_time > past_24_hours:
            new_entries.append(entry)

    return new_entries

def generate_comment(post_title, summary):

    prompt = f"Write a less wrong comment responding to the post '{post_title}' with summary '{summary}' in the style of Eliezer Yudkowsky"
    print("PROMPT: ", prompt)

    messages = [
    {"role": "system", "content": "You are Eliezer Yudkowsky, renowned AI safety researcher."},
    {"role": "user", "content": prompt}
    ]

    response = generate_chat_completion(messages, model = "gpt-4",temperature = 0.7, max_tokens = 200)
    return response

def login(driver, email, password):
    driver.get("https://www.lesswrong.com/login")
    time.sleep(2)

    email_input = driver.find_element(By.XPATH, "//input[@placeholder='username or email']")
    email_input.send_keys(email)

    password_input = driver.find_element(By.XPATH, "//input[@placeholder='password']")
    password_input.send_keys(password)

    password_input.submit()
    time.sleep(2)

def post_comment(driver, post_url, comment):
    print("in post comment")
    driver.get(post_url)
    print("get driver")
    time.sleep(2)

    comment_box_xpath = "//div[contains(@class, 'ck-editor__editable') and contains(@role, 'textbox')]"
    comment_box = driver.find_element(By.XPATH, comment_box_xpath)
    comment_box.send_keys(comment)
    time.sleep(5)

    #submit_button_xpath = "//button[contains(@class, 'MuiButton-root') and contains(@type, 'submit')]"
    #submit_button = driver.find_element(By.XPATH, submit_button_xpath)
    #submit_button.click()
    time.sleep(2)
    time.sleep(2)

def main():
    #driver = webdriver.Chrome("/usr/local/bin/chromedriver_mac_arm64")

    driver = webdriver.Chrome(ChromeDriverManager().install())
    email = LW_EMAIL
    password = LW_PASSWORD

    login(driver, email, password)

    seen_posts = set()
    while True:
        new_posts = get_new_posts()
        print("NEW POSTS: ", new_posts)
        #break
        for post in new_posts:
            print(post.keys())
            post_id = post["id"]
            post_summary = post["summary"]
            print("post id: ", post_id)
            print("post contet: ", post_summary)
            if post_id not in seen_posts:
                seen_posts.add(post_id)
                title = post["title"]
                print(f"New post: {title}")
                comment = "testing testing 123"
                comment = generate_comment(title, post_summary)
                print(f"Generated comment: {comment}")
                post_url = f"https://www.lesswrong.com/posts/{post_id}"
                print("POST URL: ", post_url)
                post_comment(driver, post_url, comment)
                break
                #time.sleep(10000)
        break

        time.sleep(60)  # Check for new posts every minute
    driver.quit()

if __name__ == "__main__":
    main()
    #new_posts = get_new_posts()
    #print("NEW POSTS: ", new_posts)
    #break
    ###for post in new_posts:
    #    print(post["summary"])
    ##    print(post.keys())
        #print(post[0])
    #    break
    #for engine in list_engines():
    #    print(engine.id)