from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Put your actual path here 👇
service = Service(r"C:\Users\Asus\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.google.com")
