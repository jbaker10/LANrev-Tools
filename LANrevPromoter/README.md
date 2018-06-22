# LANrev Promoter

## LANrev Promoter aims to automate the software promotion process within LANrev for you, so you can do better things.

----

### *** LANrev Promoter is more proof of concept at this point, and should be used with caution. ***
I have tested the functionality in a LANrev test environment and the script works as expected without doing anything to the LANrev database, but this again has not been extensively tested. The other caveat is that in order for the LANrev Admin Console to pick up on the change, you have to "Reload All Tables", as opposed to just "Sync[ing] All Tables".

### Things It _Will_ Do
* Automatically promote a package from your "Test" group to your "Production" group
* Alert you (during the script run) as to _which_ packages it is going to promote, before doing so
* Allow you to define a "DoNotPromote" list that it will never promote

### Things It _Won't_ Do
* Promote OS Software Updates
* Promote software that is defined in the "DoNotPromote" list
* Your dishes


### How to Use It:
* Download a copy of the LANrevPromoter.py script
* Run the script on your LANrev Server -- It cannot run on anything but the actual LANrev Server
	* Once better tested, the goal would be to have a LaunchDaemon run the script to truly automate the process
* If you want to exclude a piece of software from automatically being promoted, you need to append an array in the plist LANrevPromoter uses at `/Library/Preferences/com.github.jbaker10.lanrevpromoter.plist`. To do this, run the following command or use a text editor:
	* `sudo defaults write /Library/Preferences/com.github.jbaker10.lanrevpromoter.plist DoNotPromote -array-add "Name"`
	* Example: `sudo defaults write /Library/Preferences/com.github.jbaker10.lanrevpromoter.plist DoNotPromote -array-add "GoogleChrome"`

### What it Looks Like:
* Upon first run, you are prompted to choose which of your groups is your "Test" group, and which is your "Prod" group. This information is used for the promotion process.

![alt tag](https://github.com/jbaker10/images/blob/master/lanrevpromoter1.png)

* You are then shown the packages that LANrevPromoter found in the "test" group, and asked if you would like to promote those packages to "prod".

![alt tag](https://github.com/jbaker10/images/blob/master/lanrevpromoter2.png)

##License

Copyright 2016 Jeremiah Baker.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
