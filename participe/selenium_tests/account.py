from splinter import Browser

def register_without_facebook():
    browser = Browser()
    browser.visit('localhost:8000/accounts/signup')



