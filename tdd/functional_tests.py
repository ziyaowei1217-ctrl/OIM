from selenium import webdriver

browser = webdriver.Edge()

browser.get('http://localhost:8000')

assert 'Django' in browser.title

print("OK")

browser.quit()