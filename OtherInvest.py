#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 15:43:38 2019

@author: YoYo
"""

import pandas as pd
import Config
import openpyxl

def getBoerDetails():
    boer_net_value = pd.read_excel(Config.boer_net_value_doc_path,usecols=[2,4,5],index_col=0)
    boer_net_value.index = pd.to_datetime(boer_net_value.index, format='%Y%m%d')
    boer_net_value.index = boer_net_value.index.strftime("%Y-%m-%d")
    boer_net_value = boer_net_value.sort_index()
    principal = 2000
    transaction_cost = 10
    boer_net_value['资产市值'] = boer_net_value['单位净值'] * principal
    boer_net_value['目前收益'] = boer_net_value['资产市值'] - (principal + transaction_cost)
    boer_net_value['目前总收益%'] = (boer_net_value['单位净值'] - 1) * 100
    boer_net_value['目前净收益%'] = round((boer_net_value['目前收益'] / (principal + transaction_cost)) * 100, 2)
    
    return boer_net_value

def integrateOtherInvestment():
    #----------------删除旧表------------------#
    other_investment_workbook = openpyxl.load_workbook(Config.other_investment_doc_path)
    boer_worksheet = other_investment_workbook['波尔号']
    other_investment_workbook.remove(boer_worksheet)
    other_investment_workbook.save(Config.other_investment_doc_path)
    #----------------重新放入新表------------------#
    boer_net_value = getBoerDetails()
    writer = pd.ExcelWriter(Config.other_investment_doc_path,engine='openpyxl',mode='a') 
    boer_net_value.to_excel(writer,'波尔号')
    writer.save()


def getTotalAsset():
    boer_net_value = pd.read_excel(Config.other_investment_doc_path, sheet_name='波尔号', index_col=0)
    other_products = pd.read_excel(Config.other_investment_doc_path, sheet_name='理财产品', index_col=0)
    total_asset = pd.DataFrame()
    total_asset['总资产'] = boer_net_value['资产市值'].copy()
    for i in range(len(other_products)):
         total_asset += other_products.iloc[i,0]
    #----------------删除旧表------------------#
    other_investment_workbook = openpyxl.load_workbook(Config.other_investment_doc_path)
    total_asset_worksheet = other_investment_workbook['总资产']
    other_investment_workbook.remove(total_asset_worksheet)
    other_investment_workbook.save(Config.other_investment_doc_path)
    #----------------重新放入新表------------------#
    writer = pd.ExcelWriter(Config.other_investment_doc_path,engine='openpyxl',mode='a')
    total_asset.to_excel(writer,'总资产')
    writer.save()
    
    
    
integrateOtherInvestment()
getTotalAsset()



