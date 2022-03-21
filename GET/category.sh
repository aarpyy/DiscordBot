#!/bin/sh

curl -s 'https://playoverwatch.com/en-us/career/pc/Aarpyy-1975/' |
"$1" | sed -n -E 's/<option value=["](.*)["] option-id=["](.*)["]>.*$/\1|\2/p'
