#!/bin/bash

cd /ssd/YOODS/ROVI_LOG
cp rovi_log.csv rovi_log_$(date "+%Y%m%d_%H%M%S").csv
mv rovi_log.csv rovi_log_bak.csv
