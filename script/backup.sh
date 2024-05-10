#!/bin/bash

#BAKDIR=/home/ros/.ros/YOODS/BAK
BAKDIR=/storage/YOODS/BAK

if [ -n "$BAK_DIR" ]; then
  BAKDIR="$BAK_DIR"
fi
BAKDIR="${BAKDIR%/}"

mkdir -p $BAKDIR
cd /home/ros

echo "バックアップ開始"
BAKFILE="catkin_ws_$(date "+%Y%m%d_%H%M%S").zip"
zip -y -r $BAKDIR/$BAKFILE catkin_ws
echo "バックアップ完了：$BAKDIR/$BAKNAME"
read -p "エンターキーを押してください"
