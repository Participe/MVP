from splinter import Browser

def account_confirmation():
    browser = Browser()
    browser.visit('localhost:8000/accounts/signup')



