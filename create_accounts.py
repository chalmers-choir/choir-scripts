# -*- coding: utf-8 -*-

# python2.7

# from selenium import webdriver
import traceback
# import time
import random
import string
from get_members import Memberlist
from driver import Driver

"""
This script is used to automatically create user accounts from the exported member register.
The member register must be retrieved from a styret-member. It is exported from Google docs
as a csv/tsv-file (the "Aktiv" tab).

Running the script will do the following:
    - Extract member info from the provided csv/tsv file
    - Log onto the old choir web page
    - Create an account for every member admitted in the current term
    - Enter personal information, choir and voice affiliation
    - Send out an email with user name and password for every newly created account


IMPORTANT!!!

- Check the variables in the bottom of this script before you run it!
    memberfile = the name of the csv/tsv-file containing the active choir members (including the new ones)
    current_term = the current study term (e.g. "HT16"). Memebrs that were admitted in this term are
                   considered new and an account will be created for them.

- Check the messages that the script returns after running it. They will tell you which accounts
  have been created and which ones have not.

- This script assumes that the GUI language for the logged-in person is Swedish.
  It will crash if that's not the case. (This should not be a problem when using the admin account.)

- Check that the indices of the variable 'cells' in the 'fill_info' method of the class 'Member'
  in get_members.py correspond to the correct columns in the csv/tsv file.
"""

ROLES = {
    # The int refers to the "edit-roles-ID" in the HTML
    "DKA1": "11",
    "DKA2": "12",
    "DKS1": "9",
    "DKS2": "10",
    "KKA1": "15",
    "KKA2": "16",
    "KKB1": "19",
    "KKB2": "20",
    "KKS1": "13",
    "KKS2": "14",
    "KKT1": "17",
    "KKT2": "18",
    "MKB1": "23",
    "MKB2": "24",
    "MKT1": "21",
    "MKT2": "22",
    "DK": "4",
    "KK": "6",
    "MK": "5",
    "passive": "28",
    "parent": "7",
    "lawful": "8",
}

MONTHS = {
    "01": "jan",
    "02": "feb",
    "03": "mar",
    "04": "apr",
    "05": "maj",
    "06": "jun",
    "07": "jul",
    "08": "aug",
    "09": "sep",
    "10": "okt",
    "11": "nov",
    "12": "dec"
}


class Account:
    def __init__(self, browser="", base_url="", username="", password="", memberfile="", current_term=""):
        self.base_url = base_url
        self.errors = []  # Storage for accounts that couldn't be created
        self.success = []  # Storage for successfully created accounts

        self.memberfile = memberfile
        self.current_term = current_term

        self.get_new_members()
        self.opendriver = Driver(browser=browser, base_url=base_url, username=username, password=password)
        self.driver = self.opendriver.driver

        self.create_accounts()
        self.opendriver.close()

    def get_new_members(self):
        """Instatiate list with new choir members."""
        memberlist = Memberlist(self.memberfile, self.current_term)
        self.new_members = memberlist.newmembers

    def create_accounts(self):
        """Wrapper for create_account. Loops through list of new members."""
        for member in self.new_members:
            try:
                self.create_account(member)
            except Exception as e:
                print('Could not create account for %s' % member.username)
                print(e.message)
                print(traceback.format_exc())
                exit()

        # Print some messages about errors and success
        if self.success:
            print "The following %s accounts have been successfully created:" % str(len(self.success))
            for i in self.success:
                print i.encode("UTF-8")
        if self.errors:
            print "The following accounts could not be created:"
            for firstname, lastname, message in self.errors:
                print "%s %s: %s" % (firstname.encode("UTF-8"),
                                     lastname.encode("UTF-8"), message.encode("UTF-8"))

    def create_account(self, member):
        """Create an account for member and sets the given attributes (voice, adress etc.)."""
        driver = self.driver
        driver.get(self.base_url + "/admin/user/user/create")
        assert "Kontoinformation" == driver.find_element_by_xpath("//*[@id='user-register']/div/fieldset[1]/legend").text, "Could not load node creation page"

        # Generate random password for this account
        password = generate_password()

        # Basic account information
        driver.find_element_by_id("edit-name").clear()
        driver.find_element_by_id("edit-name").send_keys(member.username)
        driver.find_element_by_id("edit-mail").clear()
        driver.find_element_by_id("edit-mail").send_keys(member.email)
        driver.find_element_by_id("edit-pass-pass1").clear()
        driver.find_element_by_id("edit-pass-pass1").send_keys(password)
        driver.find_element_by_id("edit-pass-pass2").clear()
        driver.find_element_by_id("edit-pass-pass2").send_keys(password)

        # Select roles
        driver.find_element_by_id("edit-roles-%s" % ROLES[member.voice]).click()
        driver.find_element_by_id("edit-roles-%s" % ROLES[member.choir]).click()
        driver.find_element_by_id("edit-roles-%s" % ROLES["lawful"]).click()  # lawful must be checked
        driver.find_element_by_id("edit-notify").click()  # Send email with password to user

        # Personal information
        driver.find_element_by_id("edit-profile-email-address").clear()
        driver.find_element_by_id("edit-profile-email-address").send_keys(member.email)
        driver.find_element_by_id("edit-profile-first-name").clear()
        driver.find_element_by_id("edit-profile-first-name").send_keys(member.firstname)
        driver.find_element_by_id("edit-profile-last-name").clear()
        driver.find_element_by_id("edit-profile-last-name").send_keys(member.lastname)
        driver.find_element_by_id("edit-profile-phone-number").clear()
        driver.find_element_by_id("edit-profile-phone-number").send_keys(member.cellphone)

        # # Place (address, postcode and city has been removed from the account information)
        # driver.find_element_by_id("edit-locations-0-street").clear()
        # driver.find_element_by_id("edit-locations-0-street").send_keys(member.adress)
        # driver.find_element_by_id("edit-locations-0-postal-code").clear()
        # driver.find_element_by_id("edit-locations-0-postal-code").send_keys(member.postcode)
        # driver.find_element_by_id("edit-locations-0-city").clear()
        # driver.find_element_by_id("edit-locations-0-city").send_keys(member.city)

        # Birthday
        birthmonth = MONTHS[member.birthmonth]
        self.check_option('edit-profile-birthday-year', member.birthyear)
        self.check_option('edit-profile-birthday-month', birthmonth)
        self.check_option('edit-profile-birthday-day', member.birthday)

        # Is member in student union?
        self.check_option('edit-profile-chalmers-student-union-member', member.union)

        # Submit and check if account was created
        driver.find_element_by_id("edit-submit").click()
        message = driver.find_element_by_xpath('//*[@id="message"]/div').text
        if message.startswith(u"Skapade ett nytt användarkonto för") or \
           message.startswith(u"Lösenord och instruktioner har skickats per e-post till den nya användaren"):
            self.success.append("%s %s" % (member.firstname, member.lastname))
        else:
            self.errors.append((member.firstname, member.lastname, message))
        # time.sleep(30)

    def check_option(self, elem_ID, choice):
        """Chose option 'choice' from roll menu with 'elem_ID'."""
        for option in self.driver.find_element_by_id(elem_ID).find_elements_by_tag_name('option'):
            if option.text == choice:
                option.click()
                break


def generate_password(length=8):
    """Generate a random password with given character length."""
    pw = []
    chars = string.ascii_letters + string.digits + "!?-"
    for i in range(0, length):
        pw.append(random.choice(chars))
    return "".join(pw)

##############################################################################
if __name__ == "__main__":
    browser = "chrome"  # must be chrome or firefox
    base_url = "http://choir.chs.chalmers.se/choir_web/"
    # username = "anne.schumacher.up@gmail.com"
    username = ""
    password = ""
    memberfile = "Medlemsregistret.csv"
    current_term = "HT18"

    Account(browser=browser, base_url=base_url, username=username,
            password=password, memberfile=memberfile, current_term=current_term)
