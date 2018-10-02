# -*- coding: utf-8 -*-
# python2

import traceback
from driver import Driver
from bs4 import BeautifulSoup

"""
This script is used by update_users.
"""


class Users:
    def __init__(self, browser="", base_url="", username="", password="", users=""):
        self.doubles = []  # Storage for names occuring several times

        if users:
            self.collect_users_from_file(users)
            # self.check_doubles()

        else:
            self.base_url = base_url
            self.opendriver = Driver(browser=browser, base_url=base_url, username=username, password=password)
            self.driver = self.opendriver.driver

            self.get_userlist()
            self.check_doubles()

            self.opendriver.close()

    def get_userlist(self):
        """ """
        self.driver.get(self.base_url + "/users/adminlist")
        table = self.driver.find_element_by_xpath('//*[@id="left"]/div[3]/div[3]/table[2]').get_attribute('innerHTML')
        table = BeautifulSoup(table, "html.parser")

        self.userdict = {}
        for row in table.find_all("tr")[1:]:
            rowdata = [td.get_text().strip() for td in row.find_all("td")]
            rowdata[0] = int(rowdata[0])
            rowdata[4] = rowdata[4].split(", ")
            rowdata = tuple(rowdata)
            username = "%s %s" % (rowdata[1], rowdata[2])

            # Username already exists
            if self.userdict.get(username, None):
                data = self.userdict.get(username)
                if type(self.userdict.get(username)) == list:
                    data.append(rowdata)
                    self.userdict[username] = data
                else:
                    newentry = [data]
                    newentry.append(rowdata)
                    self.userdict[username] = newentry
                self.doubles.append((username, self.userdict[username]))

            else:
                self.userdict[username] = rowdata

    def collect_users_from_file(self, userlist):
        self.userdict = {}

        with open(userlist, "r") as f:
            for line in f:
                line = line.decode("UTF-8")
                line = line.strip()
                rowdata = line.split("\t")
                rowdata[0] = int(rowdata[0])
                if len(rowdata) > 4:
                    rowdata[4] = rowdata[4].split(", ")
                else:
                    rowdata.append("")
                rowdata = tuple(rowdata)
                username = "%s %s" % (rowdata[1], rowdata[2])

                # Username already exists
                if self.userdict.get(username, None):
                    data = self.userdict.get(username)
                    if type(self.userdict.get(username)) == list:
                        data.append(rowdata)
                        self.userdict[username] = data
                    else:
                        newentry = [data]
                        newentry.append(rowdata)
                        self.userdict[username] = newentry
                    self.doubles.append((username, self.userdict[username]))

                else:
                    self.userdict[username] = rowdata

    def get_user(self, user):
        """Get data for user."""
        return self.userdict.get(user, None)

    def check_doubles(self):
        """Check if any user names occur several times in data."""
        if self.doubles:
            print "%s names exist several times in the data base:" % len(self.doubles)
            for name, data in self.doubles:
                print "%s:" % name.encode("UTF-8")
                for i in data:
                    print "\t%s" % str(i)
            print
        else:
            print "All user names in the data base are unique!"

##############################################################################
if __name__ == "__main__":
    browser = "chrome"  # must be chrome or firefox
    base_url = "http://choir.chs.chalmers.se/choir_web/"
    username = ""
    password = ""
    users = "userlist.txt"

    Users(browser=browser, base_url=base_url, username=username, password=password, users=users)
