import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def run_test():
    url = url_entry.get().strip()
    if not url.startswith("http"):
        url = "http://" + url

    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(url)

        results = []

        # 1. Title test
        title = driver.title
        results.append(f"Page title: {title}")

        # 2. Check at least one link exists
        links = driver.find_elements(By.TAG_NAME, "a")
        results.append(f"Found {len(links)} links on page")

        # 3. Screenshot
        driver.save_screenshot("screenshot.png")
        results.append("Screenshot saved as screenshot.png")

        # 4. Wait for body
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            results.append("Body loaded successfully ✅")
        except:
            results.append("❌ Body not found")

        # Show results
        messagebox.showinfo("Test Results", "\n".join(results))

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        try:
            driver.quit()
        except:
            pass


# ---------------- GUI ----------------
root = tk.Tk()
root.title("Universal Web Testing Tool")
root.geometry("400x200")

label = tk.Label(root, text="Enter Website URL:", font=("Arial", 12))
label.pack(pady=10)

url_entry = tk.Entry(root, width=40, font=("Arial", 12))
url_entry.pack(pady=5)

run_button = tk.Button(root, text="Run Test", font=("Arial", 12), command=run_test)
run_button.pack(pady=20)

root.mainloop()
