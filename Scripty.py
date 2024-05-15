from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
import html2text
import getpass

def init_driver():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver
    except Exception as e:
        print(f"Error initializing driver: {e}")
        raise

def login(driver, email, password):
    try:
        driver.get("https://www.linkedin.com/login")
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)
    except Exception as e:
        print(f"Error during login: {e}")
        driver.quit()
        raise

def navigate_to_post(driver, post_url):
    try:
        if post_url.startswith("https://www.linkedin.com/"):
            driver.get(post_url)
            time.sleep(5)
        else:
            print("Invalid post URL. Please provide a valid LinkedIn post URL.")
    except Exception as e:
        print(f"Error navigating to post: {e}")
        driver.quit()
        raise

def load_all_comments(driver, max_retries=10):
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        retries = 0
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            try:
                load_more_button = driver.find_element(By.CSS_SELECTOR, "button.comments-comments-list__load-more-comments-button")
                load_more_button.click()
                print("Clicked 'Load more comments' button.")
                time.sleep(3)
            except:
                try:
                    load_more_button = driver.find_element(By.XPATH, "//button[contains(@class, 'comments-comments-list__load-more-comments-button')]")
                    load_more_button.click()
                    print("Clicked 'Load more comments' button.")
                    time.sleep(3)
                except Exception as e:
                    print(f"No more 'Load more comments' button found: {e}")
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
            retries += 1
            if retries > max_retries:
                break
    except Exception as e:
        print(f"Error loading comments: {e}")
        driver.quit()
        raise

def extract_comments(driver):
    comments = []
    try:
        comment_elements = driver.find_elements(By.CLASS_NAME, "comments-comments-list__comment-item")
        print(f"Found {len(comment_elements)} initial comment elements.")
    
        for comment in comment_elements:
            try:
                # Extract the name and profile URL
                name_element = comment.find_element(By.CLASS_NAME, "comments-post-meta__name-text")
                profile_url = None
                try:
                    profile_url = name_element.find_element(By.XPATH, ".//a").get_attribute("href")
                except:
                    print("Profile URL not found.")
                name = name_element.text
                
                # Extract the position
                position = comment.find_element(By.CLASS_NAME, "comments-post-meta__headline").text
                
                # Extract the comment text
                comment_text_element = comment.find_element(By.CLASS_NAME, "comments-comment-item__main-content")
                html_content = comment_text_element.get_attribute("innerHTML")
                h = html2text.HTML2Text()
                h.ignore_links = True
                clean_comment_text = h.handle(html_content)

                comments.append({
                    "Name": name,
                    "LinkedIn URL": profile_url,
                    "Current Position": position,
                    "Comment Text": clean_comment_text.strip()
                })
                print(f"Extracted comment: {name}")
            except Exception as e:
                print(f"Error extracting comment: {e} - Skipping comment")
                continue
    except Exception as e:
        print(f"Error finding comment elements: {e}")
    return comments

def save_to_csv(comments, filename="linkedin_comments.csv"):
    try:
        if comments:
            df = pd.DataFrame(comments)
            filepath = os.path.join(os.getcwd(), filename)
            df.to_csv(filepath, index=False)
            print(f"Saved {len(comments)} comments to {filename}.")
        else:
            print("No comments found.")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def main():
    try:
        email = input("Enter your LinkedIn email: ")
        password = getpass.getpass("Enter your LinkedIn password: ")
        post_url = "https://www.linkedin.com/posts/aviral-bhatnagar-ajuniorvc_27k-luxury-homes-worth-15cr-were-sold-last-activity-7196394582807371779-Me4k?utm_source=share&utm_medium=member_desktop"

        driver = init_driver()
        login(driver, email, password)
        navigate_to_post(driver, post_url)
        load_all_comments(driver)
        comments = extract_comments(driver)
        save_to_csv(comments)
        driver.quit()

        print("Scraping completed. Data saved to linkedin_comments.csv")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
