#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python3

from selenium.webdriver.support.ui import Select
import re
import traceback
from datetime import datetime, time, timedelta
from driver import Driver

"""
This script is used to create auditions on the new web page
(http://chalmerssangkor.se).
Uses driver.py
"""


class Auditions:
    def __init__(self, browser, base_url="", username="", password="", audition_title="",
                 audition_published=False, audition_enabled=True, audition_capacity="",
                 audition_maximum_spaces="", audition_email="", audition_confirmation_message="",
                 from_time=time, to_time=time, length=timedelta, dates=[]):
        self.base_url = base_url
        self.audition_title = audition_title
        self.audition_published = audition_published
        self.audition_enabled = audition_enabled
        self.audition_capacity = audition_capacity
        self.audition_maximum_spaces = audition_maximum_spaces
        self.audition_email = audition_email
        self.audition_confirmation_message = audition_confirmation_message
        self.from_time = from_time
        self.to_time = to_time
        self.length = length
        self.dates = dates

        self.opendriver = Driver(browser=browser, base_url=base_url, username=username, password=password)
        self.driver = self.opendriver.driver

        self.create_auditions()
        self.opendriver.close()

    def create_auditions(self):
        """Takes dates and times to generate parameters to send to create_audition() for creating node and set
        registration settings.

        For each date we generate auditions with the specified length between 'from_time` and `to_time`.
        """
        for date in self.dates:
            # Constructing datetimes for when auditions for the day starts and ends.
            current_datetime = datetime.combine(datetime.strptime(date, '%Y-%m-%d'), self.from_time)
            day_end = datetime.combine(datetime.strptime(date, '%Y-%m-%d'), self.to_time)

            while current_datetime < day_end:
                audition_start = current_datetime.strftime('%Y-%m-%d %H:%M')
                audition_end = (current_datetime + self.length).strftime('%Y-%m-%d %H:%M')

                try:
                    self.create_audition(audition_start, audition_end)
                except Exception as e:
                    print('Could not create audition between dates:')
                    print(audition_start + ' and ' + audition_end)
                    print(e)
                    print(traceback.format_exc())
                    print
                else:
                    print('Audition created between dates:')
                    print(audition_start + ' and ' + audition_end)
                    print

                current_datetime = current_datetime + self.length

    def create_audition(self, start_time, end_time):
        """Creates a single audition node and sets registration settings.
        """
        driver = self.driver
        driver.get(self.base_url + "/node/add/audition")

        assert "Skapa Audition" == driver.find_element_by_xpath("//h1").text, "Could not load node creation page"

        driver.find_element_by_id("edit-title").clear()
        driver.find_element_by_id("edit-title").send_keys(self.audition_title)
        Select(driver.find_element_by_name("field_custom_auditions_registrat[und][0][registration_type]")).select_by_visible_text("Auditions")
        driver.find_element_by_id("edit-field-custom-auditions-time-und-0-value-date").clear()
        driver.find_element_by_id("edit-field-custom-auditions-time-und-0-value-date").send_keys(start_time)
        driver.find_element_by_id("edit-field-custom-auditions-time-und-0-value2-date").clear()
        driver.find_element_by_id("edit-field-custom-auditions-time-und-0-value2-date").send_keys(end_time)
        #driver.find_element_by_xpath("//li[6]/a/strong").click()
        driver.find_element_by_xpath('//*[@id="audition-node-form"]/div/div[6]/ul/li[5]').click()
        if driver.find_element_by_id("edit-status").is_selected() != self.audition_published:
            driver.find_element_by_id("edit-status").click()
        driver.find_element_by_id("edit-submit").click()

        assert re.compile(r"^[\s\S]*Audition \(Audition\) har skapats\.[\s\S]*$").search(driver.find_element_by_css_selector("div.messages.status").text), "Could not save node"

        driver.find_element_by_link_text("Manage Registrations").click()
        driver.find_element_by_link_text(u"Inställningar").click()
        if driver.find_element_by_id("edit-status").is_selected() != self.audition_enabled:
            driver.find_element_by_id("edit-status").click()
        driver.find_element_by_id("edit-capacity").clear()
        driver.find_element_by_id("edit-capacity").send_keys(self.audition_capacity)
        driver.find_element_by_id("edit-settings-maximum-spaces").clear()
        driver.find_element_by_id("edit-settings-maximum-spaces").send_keys(self.audition_maximum_spaces)
        if driver.find_element_by_id("edit-settings-multiple-registrations").is_selected():
            driver.find_element_by_id("edit-settings-multiple-registrations").click()
        driver.find_element_by_id("edit-settings-from-address").clear()
        driver.find_element_by_id("edit-settings-from-address").send_keys(self.audition_email)
        driver.find_element_by_id("edit-settings-confirmation").clear()
        driver.find_element_by_id("edit-settings-confirmation").send_keys(self.audition_confirmation_message)
        driver.find_element_by_id("edit-save").click()

        assert re.compile(r"^[\s\S]*Registration settings have been saved\.[\s\S]*$")\
            .search(driver.find_element_by_css_selector("div.messages.status").text),\
            "Could not save registration settings"


if __name__ == "__main__":
    browser = "chrome"  # must be chrome or firefox
    base_url = "http://chalmerssangkor.se"
    username = ""
    password = ""
    audition_title = "Audition"
    audition_published = False
    audition_enabled = True
    audition_capacity = "1"
    audition_maximum_spaces = "1"
    audition_email = "vice@choir.chs.chalmers.se"
    audition_confirmation_message = "Registration has been saved."

    from_time = time(19, 45)
    to_time = time(21, 00)
    length = timedelta(minutes=15)
    dates = ['2018-09-03', '2018-09-04', '2018-09-05', '2018-09-07', '2018-09-10', '2018-09-11', '2018-09-12']

    auditions = Auditions(browser, base_url, username, password, audition_title,
                          audition_published, audition_enabled, audition_capacity,
                          audition_maximum_spaces, audition_email, audition_confirmation_message,
                          from_time, to_time, length, dates)
