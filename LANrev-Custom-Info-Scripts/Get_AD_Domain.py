#!/usr/bin/python

from Foundation import ODSession

mySession = ODSession.defaultSession()
nodes = mySession.nodeNamesAndReturnError_(None)

ret = False

for e in nodes:
    if "Active Directory" in e:
        ret = True
        print e

if not ret:
    print ret