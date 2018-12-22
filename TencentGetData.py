#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  8 12:27:35 2018

@author: YoYo
"""
import pandas as pd
from bs4 import BeautifulSoup
import Fund
import re
import time
import openpyxl
import os
from datetime import timedelta
from copy import deepcopy

class TencentGetData():

    def __init__(self, specify_date=None):
        if specify_date == None:
            date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        else:
            date = specify_date
            
        self.date = (pd.to_datetime(date)-timedelta(0)).strftime('%Y-%m-%d')
        self.soup = BeautifulSoup(open("Tencent_data/%s.htm"%self.date),'lxml')
        print('Read %s data successful'%self.date)
        self.getAllFundsIDList()
        print('Get %s funds name successful'%self.date)
        self.getEachFundDetails()
        self.wrapUpFunds()
        self.identifyNewFund()
        if self.new_fund_list:
            self.createTable()
        if self.existing_fund_list:
            self.updateTable()
        print('Update %s data successful'%self.date)
    
    def getTotalAsset(self):
        search_ = self.soup.select('div [class="float-l"] > span')
    
    def getAllFundsIDList(self):
        search_fund_name_list = self.soup.select('div [class="float-l"] > span')
        self.fund_name_list = []
        self.fund_ID_list = []
        for i in range(0,len(search_fund_name_list)): 
            txt = search_fund_name_list[i].get_text()
            split_txt = txt.split(' ')
            self.fund_name_list.append(split_txt[0])
            self.fund_ID_list.append(split_txt[1])
    
    def getEachFundDetails(self):
        
        fund_repeat_factor = 0 # 用于有多个同样的基金持仓情况
        self.fund_list = []
        for i in range(0,len(self.fund_ID_list)):
            
            #----------------通过编号定位基金，并判断是否有多个同样的基金持仓------------------#
            if self.fund_ID_list[i] == self.fund_ID_list[i-1]:
                fund_repeat_factor += 1
                current_node = self.soup.find_all(text=self.fund_ID_list[i])[fund_repeat_factor]
            else:
                fund_repeat_factor = 0
                current_node = self.soup.find(text=self.fund_ID_list[i])
                
            #----------------拿到每个基金的总市值数据------------------#
            parent_node = current_node.find_parent('div','c-box') # 定位到这个基金的c-boxsection
            #self.fund_list[i].total_value = float(parent_node.find('p','num').get_text())
            
            #----------------根据不同基金种类，拿到每个基金的details数据------------------#
            names = locals()
            if current_node.find_parent('div','box-etf'):  
                names['fund%d'%(i+1)] = Fund.ETFFund(self.fund_name_list[i],self.fund_ID_list[i])
                self.fund_list.append(names['fund%d'%(i+1)])
                total_value_node = parent_node.find('div','col-div col-1')
                yest_profit_loss_node = parent_node.find('div','col-div col-2')
                cum_profit_loss_node = parent_node.find('div','col-div col-3')
                names['fund%d'%(i+1)].currentTotalValue(float(total_value_node.find('p','num').get_text()))
                try:
                    names['fund%d'%(i+1)].yesterdayPnL(float(yest_profit_loss_node.find('p','num f-red').get_text()))
                except AttributeError:
                    try:
                        names['fund%d'%(i+1)].yesterdayPnL(float(yest_profit_loss_node.find('p','num f-green').get_text()))
                    except:
                        names['fund%d'%(i+1)].yesterdayPnL(float(yest_profit_loss_node.find('p','num ').get_text()))
                try:
                    names['fund%d'%(i+1)].cumPnL(float(cum_profit_loss_node.find('p','num f-red').get_text()))
                except AttributeError:
                    try:
                        names['fund%d'%(i+1)].cumPnL(float(cum_profit_loss_node.find('p','num f-green').get_text()))
                    except:
                        names['fund%d'%(i+1)].cumPnL(float(cum_profit_loss_node.find('p','num ').get_text()))
                names['fund%d'%(i+1)].calculate_day = 252
            
            if current_node.find_parent('div','box-secure'):
                names['fund%d'%(i+1)] = Fund.SecureFund(self.fund_name_list[i],self.fund_ID_list[i])
                self.fund_list.append(names['fund%d'%(i+1)])
                total_value_node = parent_node.find('div','col-div col-1')
                yest_profit_loss_node = parent_node.find('div','col-div col-2')
                cum_profit_loss_node = parent_node.find('div','col-div col-3')
                names['fund%d'%(i+1)].currentTotalValue(float(total_value_node.find('p','num').get_text()))
                names['fund%d'%(i+1)].yesterdayPnL(float(parent_node.find('p','num ').get_text()))
                names['fund%d'%(i+1)].cumPnL(float(cum_profit_loss_node.find('p','num ').get_text()))
                names['fund%d'%(i+1)].calculate_day = 360
            
            if current_node.find_parent('div','box-stable'):
                names['fund%d'%(i+1)] = Fund.StableFund(self.fund_name_list[i],self.fund_ID_list[i])
                self.fund_list.append(names['fund%d'%(i+1)])
                total_value_node = parent_node.find('div','col-div col-1')
                current_period_pnl_node = parent_node.find('div','col-div col-2')
                names['fund%d'%(i+1)].currentTotalValue(float(total_value_node.find('p','num').get_text()))
                names['fund%d'%(i+1)].currentPeriodPnL(float(current_period_pnl_node.find('p','num ').get_text()))
                profitPer1w_string = re.findall(r'[0-9]+|[a-z]+',(total_value_node.find('p','m-tips').get_text().split(' '))[1])
                names['fund%d'%(i+1)].profitPer1w(float(profitPer1w_string[0]))
                names['fund%d'%(i+1)].maturityDate(total_value_node.find('p','m-tips').get_text().split(' ')[2])
                names['fund%d'%(i+1)].calculate_day = 360
        
        
        for i in self.fund_list:
            print('This is fund %d'%(self.fund_list.index(i)+1))
            i.displayKeyDetails()

    def wrapUpFunds(self):
        temp_fund_list = deepcopy(self.fund_list)
        self.organised_fund_list = []
        i = 0
        for j in range(1, len(temp_fund_list)):
            if temp_fund_list[i].name == temp_fund_list[j].name:
                temp_fund_list[i].total_value += temp_fund_list[j].total_value
                try:
                    temp_fund_list[i].yest_profit_loss += temp_fund_list[j].yest_profit_loss
                except:
                    pass #stable fund的昨日浮动盈亏由万份收益和总市值计算得到，所以不需要累加
                try:
                    temp_fund_list[i].cum_profit_loss += temp_fund_list[j].cum_profit_loss
                except:
                    temp_fund_list[i].current_period_pnl += temp_fund_list[j].current_period_pnl
                if j == len(temp_fund_list)-1:
                    self.organised_fund_list.append(temp_fund_list[i])
            else:
                self.organised_fund_list.append(temp_fund_list[i])
                i = j
                
        for i in self.organised_fund_list:
            print('This is fund %d'%(self.organised_fund_list.index(i)+1))
            i.displayKeyDetails()
        '''
        for i in range(1, len(temp_fund_list)):
            if temp_fund_list[i].name == temp_fund_list[i-1].name:
                temp_fund_list[i].total_value += temp_fund_list[i-1].total_value
                same_fund_factor += 1
                pass
            else:
                if same_fund_factor != 0:
                    wrap_up_fund = deepcopy(self.fund_list[i])
                    while same_fund_factor > 0:
                        wrap_up_fund.total_value += self.fund_list[i-same_fund_factor].total_value
                        #wrap_up_fund.
                        same_fund_factor -= 1
                    self.organised_fund_list
         
        '''
    
    def identifyNewFund(self):
        new_fund_No_str = input("新买入基金编号为(请填从1开始的数字): ") # input为类似 1,4,5
        if new_fund_No_str == '0': # 如果当天没有新的基金的话就填0
            self.new_fund_list = None
            self.existing_fund_list = self.organised_fund_list
        
        else:
            self.new_fund_list = []
            self.existing_fund_list = []
            
            try:
                new_fund_No = [int(x) for x in new_fund_No_str.split(',')]  # type = str
            except:
                new_fund_No = [int(new_fund_No_str)] 
            
            for i in new_fund_No:   
                new_fund = self.organised_fund_list[i - 1]
                self.new_fund_list.append(new_fund)
            
            all_fund_No = list(range(1, len(self.organised_fund_list)+1))
            existing_fund_No = list(set(all_fund_No).difference(set(new_fund_No)))
            
            for i in existing_fund_No:   
                existing_fund = self.organised_fund_list[i - 1]
                self.existing_fund_list.append(existing_fund)
        
    def createTable(self):
        try:
            writer = pd.ExcelWriter('/Users/YoYo/Desktop/智能记账/Tencent.xlsx',engine='openpyxl',mode='a') 
        except:
            writer = pd.ExcelWriter('/Users/YoYo/Desktop/智能记账/Tencent.xlsx')
            
        for i in range(0,len(self.new_fund_list)):
            fund_table = self.new_fund_list[i].createTable(self.date)
            fund_table.to_excel(writer,'%s'%self.new_fund_list[i].name)
        writer.save()
        
    def updateTable(self):
        existing_workbook = openpyxl.load_workbook('/Users/YoYo/Desktop/智能记账/Tencent.xlsx')
        updated_table_list = []
        sheet_name_list = []
        for i in range(0, len(self.existing_fund_list)):
            sheet_name = '%s'%self.existing_fund_list[i].name
            print(sheet_name)
            current_worksheet = existing_workbook[sheet_name]
            fund_table_old = pd.read_excel('/Users/YoYo/Desktop/智能记账/Tencent.xlsx', sheet_name=sheet_name, index_col=0)
            existing_workbook.remove(current_worksheet)
            fund_table_new = self.existing_fund_list[i].createTable(self.date)
            fund_table = pd.concat([fund_table_old,fund_table_new])
            updated_table_list.append(fund_table)
            sheet_name_list.append(sheet_name)
        try:
            existing_workbook.save('/Users/YoYo/Desktop/智能记账/Tencent.xlsx')
            writer = pd.ExcelWriter('/Users/YoYo/Desktop/智能记账/Tencent.xlsx',engine='openpyxl',mode='a') 
        except:
            os.remove('/Users/YoYo/Desktop/智能记账/Tencent.xlsx')
            writer = pd.ExcelWriter('/Users/YoYo/Desktop/智能记账/Tencent.xlsx')
        for i in range(0,len(updated_table_list)):
            updated_table_list[i].to_excel(writer, sheet_name_list[i])
        writer.save()
        
        
    
if __name__ == '__main__':
    
    start_date = '2018-12-07'
    while start_date != time.strftime('%Y-%m-%d',time.localtime(time.time())):
        try:
            TencentGetData(start_date)
        except:
            pass
        start_date = (pd.to_datetime(start_date)+timedelta(1)).strftime('%Y-%m-%d')

