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

def get_id():
    '''Returns the current console user on this Mac'''
    ## Using SystemConfiguration:
    # return SCDynamicStoreCopyConsoleUser(None, None, None)[0]
    return os.getlogin()

def bashCommand(script):
    try:
        return subprocess.check_output(script)
    except (subprocess.CalledProcessError, OSError), err:
        return "[* Error] **%s** [%s]" % (err, str(script))


open_exe = "/usr/bin/open"
BUNDLE_ID = "/Users/%s/Library/Preferences/com.poleposition-sw.lanrev_admin" % get_id()
CURRENT_USER = get_id()
LANrevPromoterPlist = "/Users/%s/Library/Preferences/com.github.jbaker10.lanrevpromoter.plist" % get_id()

def convertPlist():
    bashCommand(["/usr/bin/plutil", "-convert", "xml1", LANrevPromoterPlist])

class Promoter():

    def createPrefFile(self):
        pl = dict(
            TestingGroupID=0,
            TestingGroupName="",
            ProductionGroupID=0,
            ProductionGroupName="",
            LastRun="",
            DoNotPromote=()
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

    # def getDBInfo(self, fileStatus):
    #     global sd_packages_latest
    #     global sd_groups_latest
    #     global sd_groups_packages_latest
    #     global database_path
    #     database_path = "/Library/Application Support/LANrev Server/ServerDatabase.db"

    #     print "[+] Full path to database [%s]" % database_path

    #     conn = sqlite3.connect(database_path)
    #     conn.row_factory = self.dict_factory
    #     c = conn.cursor()
    #     sd_groups_latest = c.execute("select * from 'sd_groups'").fetchall()
    #     sd_packages_latest = c.execute("select * from 'sd_packages'").fetchall()
    #     if fileStatus is False:
    #         index = 0
    #         for group in sd_groups_latest:
    #             print "Group Name: %s  =====>  Group ID: %i" % (sd_groups_latest[index]["Name"], sd_groups_latest[index]["id"])
    #             index += 1
    #         # print "\n"
    #         index = 0
    #         packages_num = 0
    #         agent = "LANrev Agent"
    #         # for package in sd_packages_latest:
    #         #     if sd_packages_latest[index]["id"] <= 10000:
    #         #         print "Package Name: %s  =====>  Package ID: %i" % (sd_packages_latest[index]["Name"], sd_packages_latest[index]["id"])
    #         #         index += 1
    #         #         packages_num += 1
    #     global sd_groups_packages_latest
    #     sd_groups_packages_latest = c.execute("select * from 'sd_groups_packages'").fetchall()
    #     c.close()
    #     conn.close()

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
            # print "\n"
            index = 0
            packages_num = 0
            agent = "LANrev Agent"
            # for package in sd_packages_latest:
            #     if sd_packages_latest[index]["id"] <= 10000:
            #         print "Package Name: %s  =====>  Package ID: %i" % (sd_packages_latest[index]["Name"], sd_packages_latest[index]["id"])
            #         index += 1
            #         packages_num += 1
        global sd_groups_packages_latest
        sd_groups_packages_latest = c.execute("select * from 'sd_groups_packages_latest'").fetchall()
        c.close()
        conn.close()


    def setPrefs(self):
        global currentPrefsPlist
        today = datetime.date.today()
        currentPrefsPlist = plistlib.readPlist(LANrevPromoterPlist)
        if currentPrefsPlist["TestingGroupID"] == 0:
            testGID = raw_input("\nPlease enter the ID corresponding to your Test/Dev group: ")
            currentPrefsPlist["TestingGroupID"] = int(testGID)
            plistlib.writePlist(currentPrefsPlist, LANrevPromoterPlist)
            for group in sd_groups_latest:
                if group["id"] == testGID:
                    currentPrefsPlist["TestingGroupName"] = group["Name"]
            #currentPrefsPlist["TestingGroupID"] = sd_groups_latest[]["Name"]
            plistlib.writePlist(currentPrefsPlist, LANrevPromoterPlist)
        if currentPrefsPlist["ProductionGroupID"] == 0:
            prodGID = raw_input("Please enter the ID corresponding to your Production group: ")
            currentPrefsPlist["ProductionGroupID"] = int(prodGID)
            plistlib.writePlist(currentPrefsPlist, LANrevPromoterPlist)
        currentPrefsPlist["LastRun"] = str(today)
        plistlib.writePlist(currentPrefsPlist, LANrevPromoterPlist)

    def openDB(self, command):
        db = sqlite3.connect(database_path)
        db.row_factory = self.dict_factory
        cursor = db.cursor()
        cursor.execute(command)
        db.commit()
        cursor.close()
        db.close()
    
    def commitDB(self):
        self.openDB("conn.commit()")
        
    def closeDB(self):
        self.openDB("c.close()")
        self.openDB("conn.close()")

    def showDevPkgs(self):
        notPromoting = []
        if len(pkgsInDev) is 0:
            print "There are no packages that need promotion"
            sys.exit()
        elif len(currentPrefsPlist["DoNotPromote"]) is not 0:
            for name in currentPrefsPlist["DoNotPromote"]:
                for pkg in pkgsInDev[:]:
                    if name in pkg["Name"]:
                        pkgsInDev.remove(pkg)
                        notPromoting.append(pkg)
        print "\nThe following packages will be promoted from dev to prod:\n"
        for pkg in pkgsInDev:
            print "* " + pkg["Name"]
        if len(notPromoting) is not 0:
            print "\n[%i] package(s) will not be promoted as we were told not to:\n" % len(notPromoting)
            for pkg in notPromoting:
                print "* " + pkg["Name"]

    def makeDBChanges(self):
        print "\nPromoting [%i] packages..." % len(pkgsInDev)
        for pkg in pkgsInDev:
            if "PlanB" in pkg["Name"]:
                pass
            elif "MS" in pkg["Name"]:
                pass
            else:
                self.openDB("UPDATE sd_groups_packages_latest SET sd_groups_record_id={ProdGroupID} WHERE id={id}".format(ProdGroupID=currentPrefs["ProductionGroupID"], id=int(pkg["id"])))

    def makeLANrevChanges(self):
        bashCommand(["/usr/bin/open", "lanrevadmin://CommitSoftwarePackageChanges"])
        bashCommand(["/usr/bin/open", "lanrevadmin://committoserver"])

    def main(self):
        global pkgsInDev
        global currentPrefs
        pkgsInDev = []
        fileStatus = os.path.isfile(LANrevPromoterPlist)
        if fileStatus is False:
            self.createPrefFile()
            print "[+] The new LANrevPromoter preference file was created at %s" % LANrevPromoterPlist
        convertPlist()
        self.getDBInfo(fileStatus)
        self.setPrefs()
        currentPrefs = plistlib.readPlist(LANrevPromoterPlist)
        print "\nThe current prefereneces are:\n"
        print "[+] LastRun: %s" % currentPrefs["LastRun"]
        print "[+] TestingGroupID: %s" % currentPrefs["TestingGroupID"]
        print "[+] ProductionGroupID: %s" % currentPrefs["ProductionGroupID"]

        #sd_groups_packages_latest = self.openDB('''c.execute("select * from 'sd_groups_packages_latest'").fetchall()''')
        ## Spits out all of the machines that are in the currently defined test group
        index = 0
        for package in sd_groups_packages_latest:
            if sd_groups_packages_latest[index]["sd_package_record_id"] <= 10000:
                if sd_groups_packages_latest[index]["sd_groups_record_id"] == currentPrefs["TestingGroupID"]:
                    pkgsInDev.append(package)
            index += 1        

        for pkg in pkgsInDev:
            for package in sd_packages_latest:
                if pkg["sd_package_record_id"] == package["id"]:
                    pkg["Name"] = package["Name"]

        self.showDevPkgs()
        if len(pkgsInDev) is 0:
            print "\nThere are no packages that need promotion."
        else:
            decision = raw_input("\nDo you want to proceed? [y/n] ")
            if decision == "y":
                self.makeDBChanges()
                subprocess.check_output([open_exe, "lanrevadmin://importsoftwarepackage?packagepath=/var/tmp/fake.ampkgprops"])
                subprocess.check_output([open_exe, "lanrevadmin://CommitSoftwarePackageChanges"])

            else:
                sys.exit()


promoter = Promoter()
promoter.main()
