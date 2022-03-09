#!/bin/sh


sed -n -E 's/^.*ProgressBar-title">([^:]+).*$/\1/p;s/^.*ProgressBar-description">(.*)$/\1/p;
s/^.*data-category-id="(.*)".*$/\1/p;
s/^<div id="(.*)" data-js="career-category" data-mode=".*">.*$/|\1/p' $1
