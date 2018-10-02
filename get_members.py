# -*- coding: utf-8 -*-

# python2.7

"""
This script defines the classes Member and Memberlist which are needed by
the script "create_accounts.py".

When run on its own this script will read a csv/tsv file given by the variable
"memberlist" and print all the members that were admitted in the term given
by the variable "current_term".

IMPORTANT! Before running create_accounts.py you must check that the indices
of the variable 'cells' in the 'fill_info' method of the class 'Member'
correspond to the correct columns in the csv/tsv file.
"""


class Member():
    def __init__(self, cells, term):
        self.fill_info(cells)
        self.new_member(term)

    def fill_info(self, cells):
        """Extract member info from table row."""
        self.firstname = cells[1].decode("UTF-8")
        self.lastname = cells[2].decode("UTF-8")
        self.username = cells[3].decode("UTF-8")
        self.union = "Yes" if cells[6] == "Ja" else "No"

        self.voice = cells[4]
        self.voice_kk = cells[5]
        self.choir = self.voice[:2]
        if len(self.voice) == 3:
            self.voice = self.choir + self.voice_kk
        self.cellphone = cells[10]
        self.email = cells[11].decode("UTF-8")
        self.adress = cells[12].decode("UTF-8")
        self.postcode = cells[13]
        self.city = cells[14].decode("UTF-8")

        birthdate = cells[19][:6]
        self.birthday = birthdate[-2:]
        self.birthmonth = birthdate[2:4]

        # Todo: This will be a problem next year when people born 2000 starts at Chalmers
        self.birthyear = "19" + birthdate[:2]

        self.entered = cells[22]  # Term of admittance to choir

    def new_member(self, term):
        """Check if this member is new."""
        if self.entered == term:
            self.new = True
        else:
            self.new = False

    def __str__(self):
        return "%s, %s (%s member)" % (self.username.encode("UTF-8"),
                                       self.voice,
                                       "new" if self.new else "old")


class Memberlist():
    def __init__(self, memberlist, term):
        self.members = []
        self.newmembers = []
        self.parse_list(memberlist, term)

    def parse_list(self, memberlist, term):
        """Parse input list and create list of all/new members."""
        with open(memberlist) as f:
            for n, line in enumerate(f):
                # Skip table header
                if n == 0:
                    self.sep = self.guess_separator(line)
                    continue
                # Skip empty lines
                if not line.strip():
                    continue
                line = line.strip("\n")
                cells = line.split(self.sep)
                # Create member
                m = Member(cells, term)
                self.members.append(m)
                if m.new:
                    self.newmembers.append(m)

    def guess_separator(self, line):
        """Check if the input is tab, comma or (Gud förbjude) semicolons separated.
        """
        return max(",", "\t", ";", key=line.count)


##############################################################################
if __name__ == '__main__':
    # For local testing
    memberlist = "Medlemsregistret.csv"
    current_term = "HT18"

    memberlist = Memberlist(memberlist, current_term)
    print "New members for this term (%s):\n" % current_term
    for member in memberlist.newmembers:
        print member
