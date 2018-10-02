# -*- coding: utf-8 -*-

from driver import Driver
import time
from get_members import Memberlist
from get_users import Users

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
    "ex-choir member": "29",
    "parent": "7",
    "lawful": "8",
    "concert master": "31",
    "board member": "3",
    "Archivist": "32",
    "tour participants": "30",
}

class Account:
    def __init__(self, browser="", base_url="", username="", password="",
                 active="", passive="", quit=""):

        self.base_url = base_url
        self.errors = []  # Storage for accounts that couldn't be updated
        self.success = []  # Storage for successfully updated accounts

        self.active = active
        self.passive = passive
        self.quit = quit

        self.get_members()
        self.get_users(browser, base_url, username, password)
        self.opendriver = Driver(browser=browser, base_url=base_url, username=username, password=password)
        self.driver = self.opendriver.driver

        # self.fix_active_members()
        self.fix_passive_members()
        # self.quit_members()
        # self.clean_all_old_members()
        # self.update_accounts()
        self.opendriver.close()

    def get_members(self):
        """
        Instatiate list with active, passive and ex choir members
        from the member registry.
        """
        self.memberlist = Memberlist(active=self.active, passive=self.passive, quit=self.quit)
        self.members = self.memberlist.memberdict
        # for member in self.memberlist.members:
        #     print member.username.encode("UTF-8"), ":", member.status
        # print

    def get_users(self, browser, base_url, username, password):
        """Instatiate dictionary of all users registered at the choir web page."""
        self.userbase = Users(browser, base_url, username, password)
        # self.userbase = Users(browser=browser, base_url=base_url, username=username, password=password, users="userlist.txt")
        self.users = self.userbase.userdict

    def fix_active_members(self):
        """Set checkboxes of members in active list."""
        # List of members to be set to "passive"
        self.active_members = [(x, y) for x, y in self.members.items() if y.status == "active"]
        edited_users = []

        for name, data in self.active_members:
            # print name.encode("UTF-8"), data.voice, data.choir
            properties = self.make_active(name, data)
            if properties:
                edited_users.append((name, properties))

        # Report result
        print "\nEdited %s accounts (made active members):" % (str(len(edited_users)))
        for i in edited_users:
            print i

    def fix_passive_members(self):
        """Set checkboxes of members in passive list."""
        # List of members to be set to "passive"
        self.passive_members = [(x, y) for x, y in self.members.items() if y.status == "passive"]
        edited_users = []

        for name, data in self.passive_members:
            print name.encode("UTF-8"), data.voice
            properties = self.make_passive(name)
            if properties:
                edited_users.append((name, properties))

        # Report result
        print "\nEdited %s accounts (made passive members):" % (str(len(edited_users)))
        for i in edited_users:
            print i

    def clean_all_old_members(self):
        """
        Set checkboxes of all users that do not appear on the active or passive
        list to correct value. Conductors won't be removed.
        """
        change_list = []
        edited_users = []
        for name, user in self.users.iteritems():
            if type(user) == list:
                for i in user:
                    if not any(x in i[4] for x in ["ex-choir member", 'MKD', 'KKD', "DKD"]):
                        change_list.append((name, i, i[0]))
            else:
                if name not in self.members:
                    if not any(x in user[4] for x in ["ex-choir member", 'MKD', 'KKD', "DKD"]):
                        change_list.append((name, user, None))

        print len(change_list)
        # for name, data, uid in sorted(change_list):
        #     print name.encode("UTF-8"), data
        # return
        for name, data, uid in sorted(change_list):
            # print name.encode("UTF-8"), data
            properties = self.make_ex(name, uid)
            if properties:
                edited_users.append((name, properties))

        # Report result
        print "\nEdited %s accounts (made ex-members):" % (str(len(edited_users)))
        for i in edited_users:
            print i

    def quit_members(self):
        """
        Set checkboxes of all members that quit the choir (according the
        "Slutat" document) to correct value.
        """
        # List of members to be set to "ex-choir member"
        self.quit_members = [(x, y) for x, y in self.members.items() if y.status == "quit"]
        edited_users = []

        for name, data in self.quit_members:
            properties = self.make_ex(name)
            if properties:
                edited_users.append((name, properties))

        # Report result
        print "\nEdited %s accounts (made ex-members):" % (str(len(edited_users)))
        for i in edited_users:
            print i

    def make_ex(self, name, uid=None):
        """Make user an ex-choir member on the homepage."""
        # List of check boxes to be unchecked
        remove_attrs = [attr for attr, val in ROLES.items() if attr not in ["ex-choir member", "lawful"]]

        quit_user = self.userbase.get_user(name)
        if type(quit_user) == list:
            for i in quit_user:
                if i[0] == uid:
                    quit_user = i
        if quit_user:  # Check if member has account on homepage
            user_id = quit_user[0]
            self.driver.get(self.base_url + "/user/" + str(user_id) + "/edit")
            assert "Kontoinformation" == self.driver.find_element_by_xpath("//*[@id='user-profile-form']/div/fieldset[1]/legend").text, "Could not load node creation page"
            # Set check boxes to correct values
            self.activate_checkbox("ex-choir member")
            for attr in remove_attrs:
                self.deactivate_checkbox(attr)
            # Save changes
            self.driver.find_element_by_id("edit-submit").click()
            return quit_user[4]
        else:  # User didn't exist, no changes applied
            return None

    def make_active(self, name, data, uid=None):
        """Make a user active on the homepage."""
        # List of check boxes to be checked
        add_attrs = [data.voice, data.choir, "lawful"]

        active_user = self.userbase.get_user(name)
        if type(active_user) == list:
            for i in active_user:
                if i[0] == uid:
                    active_user = i
        if active_user:  # Check if member has account on homepage
            user_id = active_user[0]
            self.driver.get(self.base_url + "/user/" + str(user_id) + "/edit")
            assert "Kontoinformation" == self.driver.find_element_by_xpath("//*[@id='user-profile-form']/div/fieldset[1]/legend").text, "Could not load node creation page"
            # Set check boxes to correct values
            self.deactivate_checkbox("passive")
            self.deactivate_checkbox("ex-choir member")
            for attr in add_attrs:
                self.activate_checkbox(attr)
            # Save changes
            self.driver.find_element_by_id("edit-submit").click()
            return active_user[4]
        else:  # User didn't exist, no changes applied
            return None

    def make_passive(self, name, uid=None):
        """Make user a passive member on the homepage."""
        # List of check boxes to be unchecked
        remove_attrs = [attr for attr, val in ROLES.items() if attr not in ["passive", "lawful", "Archivist", "admin"]]

        passive_user = self.userbase.get_user(name)
        if type(passive_user) == list:
            for i in passive_user:
                if i[0] == uid:
                    passive_user = i
        if passive_user:  # Check if member has account on homepage
            user_id = passive_user[0]
            self.driver.get(self.base_url + "/user/" + str(user_id) + "/edit")
            assert "Kontoinformation" == self.driver.find_element_by_xpath("//*[@id='user-profile-form']/div/fieldset[1]/legend").text, "Could not load node creation page"
            # Set check boxes to correct values
            self.activate_checkbox("passive")
            for attr in remove_attrs:
                self.deactivate_checkbox(attr)
            # Save changes
            self.driver.find_element_by_id("edit-submit").click()
            return passive_user[4]
        else:  # User didn't exist, no changes applied
            return None

    def activate_checkbox(self, boxname):
        elem = self.driver.find_element_by_id("edit-roles-%s" % ROLES[boxname])
        if not elem.get_attribute('checked'):
            elem.click()

    def deactivate_checkbox(self, boxname):
        elem = self.driver.find_element_by_id("edit-roles-%s" % ROLES[boxname])
        if elem.get_attribute('checked') == "true":
            elem.click()


##############################################################################
if __name__ == "__main__":
    browser = "chrome"  # must be chrome or firefox
    base_url = "http://choir.chs.chalmers.se/choir_web/"
    username = ""
    password = ""
    active = "Medlemsregistret.xlsx - Aktiv.tsv"
    passive = "Medlemsregistret.xlsx - Passiv.tsv"
    quit = "Medlemsregistret.xlsx - Slutat.tsv"

    Account(browser=browser, base_url=base_url, username=username,
            password=password, active=active, passive=passive,
            quit=quit)
