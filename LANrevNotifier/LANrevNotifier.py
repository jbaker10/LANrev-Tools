#!/usr/bin/python

import os,  \
       uuid, \
       time,  \
       shutil, \
       hashlib, \
       datetime, \
       sqlite3,   \
       plistlib,   \
       subprocess,  \
       datetime,     \
       sys

from Foundation import  NSArray,     \
                        NSDictionary, \
                        NSUserName,    \
                        NSHomeDirectory

from os.path import expanduser
from CoreFoundation import CFPreferencesCopyAppValue

from string import Template
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import urllib2
import smtplib


######################################
####### VARIABLES TO FILL IN #########

FROM_ADDRESS = "" ## Who should the email be sent FROM
TO_ADDRESS = "" ## Who should the email be sent TO
SMTP_SERVER = "" ## SMTP server to send email through. Can be a forwarding server

######################################
######################################

def get_id():
    '''Returns the current console user on this Mac'''
    ## Using SystemConfiguration:
    # return SCDynamicStoreCopyConsoleUser(None, None, None)[0]
    return os.getlogin()

open_exe = "/usr/bin/open"
BUNDLE_ID = "com.poleposition-sw.lanrev_admin"
CURRENT_USER = get_id()
LANrevPromoterPlist = "/Users/%s/Library/Preferences/com.github.jbaker10.lanrevpromoter.plist" % CURRENT_USER

class Notifier():
    def bashCommand(self, script):
        try:
            return subprocess.check_output(script)
        except (subprocess.CalledProcessError, OSError), err:
            return "[* Error] **%s** [%s]" % (err, str(script))

    def createPrefFile(self):
        pl = dict(
            TestingGroupID=0,
            TestingGroupName="",
            LastRun="",
        )
        try:
            plistlib.writePlist(pl, LANrevPromoterPlist)
        except TypeError:
            print "Could not create plist"

    def get_pref(self, key, domain=BUNDLE_ID):
        """Return a single pref value (or None) for a domain."""
        value = CFPreferencesCopyAppValue(key, domain) or None
        # Casting NSArrays and NSDictionaries to native Python types.
        # This a workaround for 10.6, where PyObjC doesn't seem to
        # support as many common operations such as list concatenation
        # between Python and ObjC objects.
        if isinstance(value, NSArray):
            value = list(value)
        elif isinstance(value, NSDictionary):
            value = dict(value)
        return value

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def getDBInfo(self, fileStatus):
        global sd_packages_latest
        global sd_groups_latest
        global sd_groups_packages_latest
        lr_server = self.get_pref("ServerAddress")
        print "[+] Current LANrev Server [%s]" % lr_server
        global database_path
        database_path = None
        try:
            database_path = expanduser(self.get_pref("DatabaseDirectory"))
        except:
            pass
        if not database_path:
            database_path = NSHomeDirectory() + "/Library/Application Support/LANrev Admin/Database/"
            print "[+] Using default database path [%s]" % database_path
        else:
            if not database_path[-1] == "/":
                database_path = expanduser(database_path + "/")
            print "[+] Using override database path [%s]" % database_path
        servers_list = os.listdir(database_path)
        for e in servers_list:
            if lr_server in e:
                database_path = database_path + e + "/SDCaches.db"
                break
        print "[+] Full path to database [%s]" % database_path

        conn = sqlite3.connect(database_path)
        conn.row_factory = self.dict_factory
        c = conn.cursor()
        sd_groups_latest = c.execute("select * from 'sd_groups_latest'").fetchall()
        sd_packages_latest = c.execute("select * from 'sd_packages_latest'").fetchall()

        if fileStatus is False:
            index = 0
            for group in sd_groups_latest:
                print "Group Name: %s  =====>  Group ID: %i" % (sd_groups_latest[index]["Name"], sd_groups_latest[index]["id"])
                index += 1
            index = 0
            packages_num = 0
            agent = "LANrev Agent"
        global sd_groups_packages_latest
        sd_groups_packages_latest = c.execute("select * from 'sd_groups_packages_latest'").fetchall()
        c.close()
        conn.close()

    def setPrefs(self):
        today = datetime.date.today()
        currentPrefsPlist = plistlib.readPlist(LANrevPromoterPlist)
        ## Get the test group to check ID's for
        if currentPrefsPlist["TestingGroupID"] == 0:
            testGID = raw_input("\nPlease enter the ID corresponding to your Test/Dev group: ")
            currentPrefsPlist["TestingGroupID"] = int(testGID)
            plistlib.writePlist(currentPrefsPlist, LANrevPromoterPlist)
            for group in sd_groups_latest:
                if group["id"] == testGID:
                    currentPrefsPlist["TestingGroupName"] = group["Name"]
            plistlib.writePlist(currentPrefsPlist, LANrevPromoterPlist)
        
        currentPrefsPlist["LastRun"] = str(today)
        plistlib.writePlist(currentPrefsPlist, LANrevPromoterPlist)

    def notifyAdmins(self, addresses):

        htmlEmail = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <meta name="viewport" content="width=device-width" />
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>Really Simple HTML Email Template</title>
        <style>
        /* -------------------------------------
            GLOBAL
        ------------------------------------- */
        * {
          margin: 0;
          padding: 0;
          font-family: "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif;
          font-size: 100%;
          line-height: 1.6;
        }
        img {
          max-width: 100%;
        }
        body {
          -webkit-font-smoothing: antialiased;
          -webkit-text-size-adjust: none;
          width: 100%!important;
          height: 100%;
        }
        /* -------------------------------------
            ELEMENTS
        ------------------------------------- */
        a {
          color: #348eda;
        }
        .btn-primary {
          text-decoration: none;
          color: #FFF;
          background-color: #348eda;
          border: solid #348eda;
          border-width: 10px 20px;
          line-height: 2;
          font-weight: bold;
          margin-right: 10px;
          text-align: center;
          cursor: pointer;
          display: inline-block;
          border-radius: 25px;
        }
        .btn-secondary {
          text-decoration: none;
          color: #FFF;
          background-color: #aaa;
          border: solid #aaa;
          border-width: 10px 20px;
          line-height: 2;
          font-weight: bold;
          margin-right: 10px;
          text-align: center;
          cursor: pointer;
          display: inline-block;
          border-radius: 25px;
        }
        .last {
          margin-bottom: 0;
        }
        .first {
          margin-top: 0;
        }
        .padding {
          padding: 10px 0;
        }
        /* -------------------------------------
            BODY
        ------------------------------------- */
        table.body-wrap {
          width: 100%;
          padding: 20px;
        }
        table.body-wrap .container {
          border: 1px solid #f0f0f0;
        }
        /* -------------------------------------
            FOOTER
        ------------------------------------- */
        table.footer-wrap {
          width: 100%;  
          clear: both!important;
        }
        .footer-wrap .container p {
          font-size: 12px;
          color: #666;
          
        }
        table.footer-wrap a {
          color: #999;
        }
        /* -------------------------------------
            TYPOGRAPHY
        ------------------------------------- */
        h1, h2, h3 {
          font-family: "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif;
          color: #000;
          margin: 40px 0 10px;
          line-height: 1.2;
          font-weight: 200;
        }
        h1 {
          font-size: 36px;
        }
        h2 {
          font-size: 28px;
        }
        h3 {
          font-size: 22px;
        }
        p, ul, ol {
          margin-bottom: 10px;
          font-weight: normal;
          font-size: 14px;
        }
        ul li, ol li {
          margin-left: 5px;
          list-style-position: inside;
        }
        /* ---------------------------------------------------
            RESPONSIVENESS
            Nuke it from orbit. It's the only way to be sure.
        ------------------------------------------------------ */
        /* Set a max-width, and make it display as block so it will automatically stretch to that width, but will also shrink down on a phone or something */
        .container {
          display: block!important;
          max-width: 600px!important;
          margin: 0 auto!important; /* makes it centered */
          clear: both!important;
        }
        /* Set the padding on the td rather than the div for Outlook compatibility */
        .body-wrap .container {
          padding: 20px;
        }
        /* This should also be a block element, so that it will fill 100% of the .container */
        .content {
          max-width: 600px;
          margin: 0 auto;
          display: block;
        }
        /* Let's make sure tables in the content area are 100% wide */
        .content table {
          width: 100%;
        }
        /* Database Styles */
        .ToadExtensionTableContainer {
          padding: 0px;
          border: 6px solid #348eda;
          -moz-border-radius: 8px;
          -webkit-border-radius: 8px;
          -khtml-border-radius: 8px;
          border-radius: 8px;
          overflow: auto;
        }
        .ToadExtensionTable {
          width: 100%;
          border: 0px;
          border-collapse: collapse;
          font-family: Arial, Tahoma, Verdana, "Times New Roman", Georgia, Serif;
          font-size: 12px;
          padding: 1px;
          border: 1px solid #fff;
        }
        th {
          padding: 2px 4px;
          border: 1px solid #fff;
        }
        td {
          padding: 2px 4px;
          border: 1px solid #fff;
        }
        .HeaderColumnEven {
          background: #75b2e6;
          color: #fff;
        }
        .HeaderColumnOdd {
          background: #348eda;
          color: #fff;
        }
        .R0C0 {
          background: #F3FAFC;
        }
        .R0C1 {
          background: #E1EEFA;
        }
        .R1C0 {
          background: #CFE9F2;
        }
        .R1C1 {
          background: #B3DCEB;
        }
        .lft {
          text-align: left;
        }
        .rght {
          text-align: right;
        }
        .cntr {
          text-align: center;
        }
        .jstf {
          text-align: justify;
        }
        .nowrap {
          white-space: nowrap;
        }
        </style>
        </head>
        <body bgcolor="#f6f6f6">
        <!-- body -->
        <table class="body-wrap" bgcolor="#f6f6f6">
          <tr>
            <td class="container" bgcolor="#FFFFFF">
              <!-- content -->
              <div class="content">
              <table>
                <tr>
                  <td>
                    <h1>LANrev Packages assigned to <b>Test</b></h1>
                    <h3>Good Morning,</h3>
                    <br>
                    <p>The following packages are currently assigned to the Testing group:</p>
                    <br>
                  </td>
                </tr>
              </table>
              </div>
              <!-- /content -->
              <div class="ToadExtensionTableContainer">
              <table class="ToadExtensionTable">
                <tr>
                  <th class="HeaderColumnEven">Package Name</th>
                  <th class="HeaderColumnOdd">AvailabilityDate</th>
                  <th class="HeaderColumnEven">LastModified</th>
                </tr>'''
        index = 0
        values = ""
        for pkg in pkgsInDev:
            values += '''<tr>
            <td class="R0C0">%s</td>
            <td class="R0C1">%s</td>
            <td class="R0C0">%s</td>
            </tr>
          </td>
        </tr>\n''' % (pkgsInDev[index].get("Name"), \
                      pkgsInDev[index].get("AvailabilityDate"), \
                      pkgsInDev[index].get("LastModified"))
            index += 1

        htmlEmail2 = '''<!-- /content -->
              </table></div><br><div class="ToadExtensionTableContainer"><table class="ToadExtensionTable">
                <tr>
                  <th class="HeaderColumnEven">Patch Name</th>
                  <th class="HeaderColumnOdd">AvailabilityDate</th>
                  <th class="HeaderColumnEven">LastModified</th>
                </tr>'''
        index = 0
        values_2 = ""
        for patch in patchesInDev:
            values_2 += '''<tr>
            <td class="R0C0">%s</td>
            <td class="R0C1">%s</td>
            <td class="R0C0">%s</td>
            </tr>
          </td>
        </tr>\n''' % (patchesInDev[index].get("Name"), \
                      patchesInDev[index].get("AvailabilityDate"), \
                      patchesInDev[index].get("LastModified"))
            index += 1

        htmlEmail = htmlEmail + values + htmlEmail2 + values_2
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'LANrev Packages assigned to Test'
        msg['From'] = FROM_ADDRESS
        msg['To'] = addresses

        text = "LANrev Packages assigned to Test"

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(htmlEmail, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        s = smtplib.SMTP(SMTP_SERVER)
        s.sendmail(addresses, addresses, msg.as_string())
        s.quit()

    def main(self):
        global pkgsInDev
        global currentPrefs
        global patchesInDev
        pkgsInDev = []
        patchesInDev = []
        fileStatus = os.path.isfile(LANrevPromoterPlist)
        if fileStatus is False:
            self.createPrefFile()
        self.getDBInfo(fileStatus)
        self.setPrefs()

        currentPrefs = plistlib.readPlist(LANrevPromoterPlist)
        print "\nThe current preferences are:\n"
        print "[+] LastRun: %s" % currentPrefs["LastRun"]
        print "[+] TestingGroupID: %s" % currentPrefs["TestingGroupID"]

        index = 0
        for package in sd_groups_packages_latest:
            if sd_groups_packages_latest[index]["sd_package_record_id"] <= 10000:
                if sd_groups_packages_latest[index]["sd_groups_record_id"] == currentPrefs["TestingGroupID"]:
                    pkgsInDev.append(package)
            else:
                if sd_groups_packages_latest[index]["sd_groups_record_id"] == currentPrefs["TestingGroupID"]:
                    patchesInDev.append(package)
            index += 1        

        for pkg in pkgsInDev:
            for package in sd_packages_latest:
                if pkg["sd_package_record_id"] == package["id"]:
                    pkg["Name"] = package["Name"]
                    pkg["AvailabilityDate"] = package["AvailabilityDate"]
                    pkg["LastModified"] = package["last_modified"]
        for patch in patchesInDev:
            for package in sd_packages_latest:
                if patch["sd_package_record_id"] == package["id"]:
                    patch["Name"] = package["Name"]
                    patch["AvailabilityDate"] = package["AvailabilityDate"]
                    patch["LastModified"] = package["last_modified"]

        if len(pkgsInDev) is 0:
            if len(patchesInDev) is 0:
                print "\nThere are no packages in the test group."
                sys.exit(0)
        else:
            self.notifyAdmins(TO_ADDRESS)

notifier = Notifier()
notifier.main()