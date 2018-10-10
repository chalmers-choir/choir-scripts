# -*- coding: utf-8 -*-

from selenium import webdriver


class Driver:

    def __init__(self, browser="", base_url="", username="", password=""):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.setUp(browser)
        self.login()
        # import time
        # time.sleep(30)

    def setUp(self, browser):
        """Set up the webdriver."""
        assert browser.lower() in ["chrome", "firefox"], "Browser must be firefox or chrome. %s is not valid." % browser
        if browser.lower() == "chrome":
            self.driver = webdriver.Chrome()
        elif browser.lower() == "firefox":
            self.driver = webdriver.Firefox()
        # self.driver.set_window_size(1400,1000)
        # self.driver.implicitly_wait(10)

    def login(self):
        """Log in the user."""
        driver = self.driver
        driver.get(self.base_url + "/user/")
        driver.find_element_by_id("edit-name").clear()
        driver.find_element_by_id("edit-name").send_keys(self.username)
        driver.find_element_by_id("edit-pass").clear()
        driver.find_element_by_id("edit-pass").send_keys(self.password)
        driver.find_element_by_id("edit-submit").click()

    def close(self):
        """Close connection to server."""
        self.logout()
        self.tearDown()

    def logout(self):
        """Logs out current user."""
        driver = self.driver
        driver.get(self.base_url + "/user/logout")

    def tearDown(self):
        """Shuts down webdriver."""
        self.driver.quit()
