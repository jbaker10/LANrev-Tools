#!/bin/bash

## Be sure to change the NODE_NAME and DOMAIN in line 9

findADAdminUsers(){
    ADAdminArray=()
    for e in `dscl . list /Users | grep -v "_" | grep -v "netboot"`;
        do
            if [ "`dscl . -read /Users/$e OriginalNodeName | tail -1 | sed 's/^[ \t]*//'`" == "/Active Directory/NODE_NAME/DOMAIN" ]; then
                admins=`dscl . -read /Groups/admin GroupMembership`
                if [[ $admins == *$e* ]]; then
                    ADAdminArray+=($e)
                fi
            fi
        done
}

findADAdminUsers;
echo $ADAdminArray;
