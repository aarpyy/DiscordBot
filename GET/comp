#!/bin/sh

sed -n -E 's/^.*competitive-rank-role-icon["].*["](.*)["].*$/\1/p;
s/^.*competitive-rank-level.*>([0-9]+)/\1/p' $1
