#!/bin/sh

# This sed command is a combination of 5 separate commands which are as following:
# 1 - Matches to competitive-rank-role-icon and captures the link to the role icon
# in a group, it then replaces the whole line with 'role-icon|' followed by the link.
# 2 - Matches to rank-tier-icon and performs the same operation as above.
# 3 - Matches ot rank-level and groups the trailing digits, printing them out as well.
# 4 - Matches any ProgressBar title and groups the title, printing it out.
# 5 - Matches any ProgressBar description, groups and prints the title.

# In all of these sed commands, | is used as a delimmiter for later usage with Python script.
# -n option prevents sed from echoing any lines, and /p terminating forces sed to print
# matches, resulting in sed printing ONLY the matches

# A specific note for the 4th command: since the name Soldier: 76 contains digits, and the
# C program format depends on only ProgressBar descriptions having digits, the
# sed to capture ProgressBar title captures everything in the title up to a colon if it exists,
# and letting the rest be captured outside of the group, meaning what is printed for all
# hero names is their name, except for SoldierL 76, whose name is cut off to print just Soldier

sed -n -E 's/^.*competitive-rank-role-icon["].*["](.*)["].*$/role-icon|\1/p;
s/^.*competitive-rank-level.*>([0-9]+)/rank|\1/p;
s/^.*ProgressBar-title["]>([^:]+).*$/\1/p;
s/^.*ProgressBar-description["]>(.*)$/\1/p' $1
