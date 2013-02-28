#!/bin/bash

scrapy crawl jingdong -L INFO -o $1 -t CSV
