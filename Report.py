#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 16:21:28 2019

@author: YoYo
"""

from pyecharts import Pie, Line
import pandas as pd
import Config

total_asset_df = pd.read_excel(Config.total_asset_doc_path, index_col=0)


total_asset_df.index
line = Line('总资产走势图')
line.add('实际总资产',total_asset_df.index,total_asset_df['总资产'],yaxis_min='dataMin',mark_point = ['max'],mark_point_textcolor='#01050C')    
line.add('前复权总资产',total_asset_df.index,total_asset_df['前复权总资产'],yaxis_min='dataMin',is_smooth = True,mark_line = ['average'])
line.render()

excel_list = [Config.tencent_doc_path, Config.bank_main_doc_path, Config.bank_small_doc_path, Config.other_investment_doc_path]
names = globals()
for i in excel_list:
    names[] = pd.read_excel(i, sheet_name=None, index_col=0)
attr = ['衬衫','羊毛衫','雪纺衫','裤子','高跟鞋','袜子']
v1 = [5,20,36,10,75,90]
pie = Pie('收益构成')
pie.add('',attr,v1,is_label_show = True)
pie.render('./html/pie01.html') 
