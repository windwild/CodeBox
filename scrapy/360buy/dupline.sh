#!/bin/bash
wc $1 
sort $1 | uniq -d

