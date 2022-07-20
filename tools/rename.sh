#!/usr/bin/env bash

for folder in *
do
	(
	cd "$folder" || exit
	rename.ul -v "" "[$folder]" -- *
	mv ./* -t ..
	)
done
