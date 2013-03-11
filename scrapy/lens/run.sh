#!/bin/bash

rm -f data.csv
scrapy crawl lens -o data.csv -t csv -L INFO
