#!/usr/bin/env python3

import numpy as np
import sys
import os
import time
import functools
import re
import socket
import roslib
import rospy
from std_msgs.msg import Bool
from std_msgs.msg import String
from std_msgs.msg import UInt8
import tkinter as tk
from tkinter import ttk
from rtk_tools import dictlib
from rtk_tools import timeout

# rospy.init_node("report",anonymous=True)
Config={
  "width":800,
  "rows":4,
  "altitude":-24,
  "font":{
    "family":"System",
    "size":10
  },
  "color":{
    "background": "#00FF00",
    "label": ("#FFFFFF","#555555"),
    "ok": ("#000000","#CCCCCC"),
    "ng": ("#FF0000","#CCCCCC")
  },
  "format":'{:.3g}',
  "delay": 1
}

Values_log={}#Added for writing log files
Reports=0    #Subscribed Report count
Snap_log={}  #Added for writing log files
Snap_list=[] #Added for writing log files
dir_path=os.getenv('ROVI_LOG_DIR')
file_path=os.getenv('ROVI_LOG_FILE')
file_name=os.path.join(dir_path,file_path)
if not os.path.exists(dir_path):
  os.makedirs(dir_path)
#file_name = "log.csv"
status = 0
recipe=""


def read_recipe():
  global recipe,Snap_log
  if "recipe" in Config:
    recipe=rospy.get_param(Config["recipe"])
    rospy.loginfo("recipe update : %s",recipe)
    if type(recipe) is str:
      Snap_log["__recipe__"]=recipe
    elif type(recipe) is dict:
      Snap_log["__recipe__"]=recipe["name"]
      recipe.pop("name")
      for key in recipe:
        Snap_log["__recipe__"]=Snap_log["__recipe__"]+":"+str(recipe[key])

def to_report(dat):
  global Values,Reports,Snap,Values_log,Snap_log
  if Reports>=1:    
    # rospy.loginfo("to_report : adding report")
    # rospy.loginfo("to_report : %s",dat.items())
    for k,v in dat.items():
      if k in Values_log:
        if(hasattr(v,"__iter__")):
          if type(v[0]) is str:
            Snap_log[k]=v
          else:
            Snap_log[k]=v[0]
        else:
          Snap_log[k]=v


def cb_report(s):
  dic=eval(s.data)
  to_report(dic)

def cb_update(s):
  rospy.loginfo("cb_update")# Snap の更新
  to_update()


def to_update():
  global Values,Reports,Values_log,flag_x1,count,Snap_log,recipe
  rospy.loginfo("Snap_log : %s", Snap_log)
  Reports=1
  return
  

def save_log():
  global Snap_log
  global file_name
  #パネル操作の場合は 1 s 待つ
  rospy.loginfo("start error check")
  for i in range(50):
    if 'error' in Snap_log:
      if Snap_log["error"] > 0:
        Snap_log["hantei"] = "NG"
      elif Snap_log["error"] == 0:
        Snap_log["hantei"] = "OK"
      break
    else:
      time.sleep(0.02)
  if not '__recipe__' in Snap_log:
    Snap_log["__recipe__"] = recipe
  rospy.loginfo("start snap_to_log")
  snap_to_log()
  flag = os.path.isfile(file_name)
  rospy.loginfo("**** : write logs")
  f=open(file_name, 'a',encoding="utf_8_sig") # Add
  if flag == False:
    f.write(str(Config["labels_log"]).lstrip('[').rstrip(']')+"\n") # 1 行目
  for x in Snap_list:
    ln=str(x).lstrip('[').rstrip(']')
    f.write(ln+"\n")
  f.close()
  rospy.loginfo("Snap_log : %s", Snap_log)
  Snap_log={}#ログリセット
  

def snap_to_log():
  global Reports
  global Snap_list
  if Reports>0:
    Snap_list=[]
    ldat=[]
    for k in Config["keys_log"]:
      if k in Snap_log:
        ldat.append(Snap_log[k])
      else:
        ldat.append(np.nan)
    Snap_list.append(ldat)


def cb_log_x0(s):
  global Reports
  global Snap_log
  global file_name
  global status
  if status != 0:
    for i in range(10):
      if status == 0:
        break
      else:
        time.sleep(0.1)
  status = 10
  Snap_log["rovi"] = "リセット"
  save_log()
  status = 0
  return


def cb_log_x1(s):
  global Reports
  global Snap_log
  global file_name
  global status
  if status != 0:
    for i in range(10):
      if status == 0:
        break
      else:
        time.sleep(0.1)
  status = 11
  Snap_log["rovi"] = "撮影"
  save_log()
  status = 0
  return


def cb_log_x2(s):
  global Reports
  global Snap_log
  global file_name
  global status
  if status != 0:
    for i in range(10):
      if status == 0:
        break
      else:
        time.sleep(0.1)
  status = 12
  Snap_log["rovi"] = "解析"
  save_log()
  status = 0
  return


def cb_log_x3(s):
  global Reports
  global Snap_log
  global file_name
  global status,recipe

  if status != 0:
    for i in range(10):
      if status == 0:
        break
      else:
        time.sleep(0.1)
  status = 13
  read_recipe()
  Snap_log["rovi"] = "レシピ変更"
  save_log()
  status = 0
  return


def cb_log_x4(s):
  global Reports
  global Snap_log
  global file_name
  global status
  if status != 0:
    for i in range(10):
      if status == 0:
        break
      else:
        time.sleep(0.1)
  status = 14
  Snap_log["rovi"] = "特徴検出"
  save_log()
  status = 0
  return

##############
def parse_argv(argv):
  args={}
  for arg in argv:
    tokens = arg.split(":=")
    if len(tokens) == 2:
      key = tokens[0]
      if re.match(r'\([ ]*([0-9.]+,[ ]*)*[0-9.]+[ ]*\)$',tokens[1]):
        # convert tuple-like-string to tuple
        args[key]=eval(tokens[1])
        continue
      args[key]=tokens[1]
  return args

####ROS Init####
rospy.init_node("log",anonymous=True)
# rospy.init_node("log",anonymous=True,disable_rosout=True)
try:
  conf=rospy.get_param("/config/report")
except:
  conf={}
try:
  dictlib.merge(Config,conf)
except Exception as e:
  print("get_param exception:",e.args)

dictlib.merge(Config,parse_argv(sys.argv))
if not "__recipe__" in Config["keys_log"]:
  Config["keys_log"].insert(1,"__recipe__")
  Config["labels_log"].insert(1,"Recipe")
####sub pub
rospy.Subscriber("/report",String,cb_report)
rospy.Subscriber("/request/clear",Bool,cb_update)
rospy.Subscriber("/request/capture",Bool,cb_update)
rospy.Subscriber("/request/solve",Bool,cb_update)
rospy.Subscriber("/request/recipe_load",String,cb_update)
rospy.Subscriber("/request/detect",String,cb_update)
rospy.Subscriber("/response/clear",Bool,cb_log_x0)
rospy.Subscriber("/response/capture",Bool,cb_log_x1)
rospy.Subscriber("/response/solve",Bool,cb_log_x2)
rospy.Subscriber("/response/recipe_load",Bool,cb_log_x3)
rospy.Subscriber("/response/detect",UInt8,cb_log_x4)
Values_log={}
for n,s in enumerate(Config["labels_log"]):
  k=Config["keys_log"][n]
  Values_log[k]=[]
read_recipe()

while not rospy.is_shutdown():
  timeout.update()
  rospy.sleep(0.1)
