#!/bin/bash

dscl . -read /Users/$USER EMailAddress | awk '{print $2}'