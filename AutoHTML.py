#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 12:57:30 2019

@author: YoYo
"""

from selenium import webdriver
from time import sleep
from pykeyboard import PyKeyboard
from pymouse import PyMouse
import time
import tkinter.messagebox


execute_bool = False
while execute_bool == False:
    root = tkinter.Tk()
    root.withdraw()
    execute_bool = tkinter.messagebox.askokcancel('Money!Money!', 'Lets do it!')
    if execute_bool == False:
        sleep(10*60)

driver = webdriver.Chrome()
k = PyKeyboard()
m = PyMouse()
driver.get('https://qian.qq.com/web/v3/account/account.shtml')
sleep(30)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
driver.maximize_window()
sleep(5)
k.press_keys(['Command','s'])
sleep(5)
k.release_key('Command')
date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
k.type_string(date, interval=0.5)
sleep(3)
k.press_keys(['Command','d'])
sleep(3)
k.press_keys(['Command','1'])
sleep(3)
m.click(465, 195, button=1, n=1)
sleep(3)
m.click(488, 369, button=1, n=1)
sleep(3)
m.click(528, 288, button=1, n=1)
sleep(3)
k.press_keys(['Command','o'])
sleep(3)
m.click(528, 288, button=1, n=1) # tencent_data
sleep(3)
k.press_keys(['Command','o'])
sleep(3)
m.click(948, 723, button=1, n=1)
sleep(3)
driver.quit()


#e = tkinter.Entry(window)
#e.pack()
#window.mainloop()
#waiting_time = int(e.get())
#window.withdraw()
#sleep(waiting_time)
'''
def printentry():
    root.withdraw()
    

root = tkinter.Tk()
root.title('又又宝宝咱要等几分钟呢？')
root.geometry('300x50')
var = tkinter.StringVar()
tkinter.Entry(root, textvariable=var).pack() #设置输入框对应的文本变量为var
waiting_time = var.get()
tkinter.Button(root,text="ok",command=root.withdraw).pack()
root.mainloop()

print(2)
sleep(int(waiting_time))
print(3)

'''
