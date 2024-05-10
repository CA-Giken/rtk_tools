#!/bin/bash
echo "ログ設定更新開始"
cd /home/ros/catkin_ws/src/rtk_tools
crontab cron.conf
crontab -l
echo "ログ設定更新終了"
read -p "エンターキーを押してください"

