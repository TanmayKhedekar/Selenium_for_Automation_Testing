from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- Setup ---
driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, 10)

# --- 1) Open YouTube ---
driver.get("https://www.youtube.com")
print("✅ Opened YouTube")

# --- 2) Search for a video ---
search_box = wait.until(EC.presence_of_element_located((By.NAME, "search_query")))
search_box.send_keys("Python Selenium tutorial")
search_box.send_keys(Keys.RETURN)
print("✅ Search done")

# --- 3) Click first video result ---
video = wait.until(EC.element_to_be_clickable((By.ID, "video-title")))
print("Opening video:", video.text)
video.click()

# --- 4) Wait while video plays ---
time.sleep(10)   # play for 10 seconds
driver.save_screenshot("youtube_video.png")
print("✅ Screenshot saved")

# --- 5) Finish ---
driver.quit()
print("🎉 YouTube automation complete!")
