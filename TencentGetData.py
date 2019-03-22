#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 12:54:04 2019

@author: YoYo
"""


# -*- coding: utf-8 -*-
"""
Created on Sat Dec  8 12:27:35 2018

@author: YoYo
"""
import pandas as pd
from bs4 import BeautifulSoup
import Fund_new
import re
import time
import openpyxl
import os
import Config
from datetime import timedelta
from copy import deepcopy
import tkinter.messagebox


class TencentGetData():

    def __init__(self, specify_date=None):
        if specify_date == None:
            date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        else:
            date = specify_date
            
        self.soup = BeautifulSoup(open(Config.tencent_soup_path + "/%s.htm"%date),'lxml')
        self.date = (pd.to_datetime(date)-timedelta(0)).strftime('%Y-%m-%d')
        print('Read %s data successful'%self.date)
        self.getAllFundsIDList()
        print('Get %s funds name successful'%self.date)
        self.getEachFundDetails()
        self.wrapUpFunds()
        self.getSubTotalPnL()
        self.identifyNewFund()
        if self.new_fund_list:
            self.createTable()
        if self.existing_fund_list:
            self.updateTable()
        print('Update %s data successful'%self.date)
    
    def getAssetDetails(self):
        assest_box_node = self.soup.find('div',"assets-box-t")
        total_assest_node = assest_box_node.find('var', 'js-data-product_balance')
        self.total_asset = float(total_assest_node.get_text().replace(',', ''))
#        asset_income_node = self.soup.find('div',"assets-sort clearfix")
#        self.fix_income_yes_pnl = float(asset_income_node.find('var', "js-data-html_fixed_profit").get_text())
#        self.fix_income_sum_pnl = float(asset_income_node.find('var',"js-data-html_sum_fixed_profit").get_text())
#        self.float_income_yes_pnl = float(asset_income_node.find('var',"js-data-html_float_profit").get_text())
#        self.float_income_sum_pnl = float(asset_income_node.find('var',"js-data-html_sum_float_profit").get_text())
    
    def createAssetTable(self):
        self.getAssetDetails()
        asset_table = pd.DataFrame(index=['总资产','昨日固定收益','昨日浮动收益','实时年化收益%'])
        roa = (self.fix_income_yes_pnl + self.float_income_yes_pnl) / self.total_asset * 300 * 100
        asset_table[self.date] = [self.total_asset, self.fix_income_yes_pnl, self.float_income_yes_pnl, round(roa,2)]
        
        return asset_table.T
    
    def getAllFundsIDList(self):
        search_fund_name_list = self.soup.select('div [class="f-l"] > span')
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
                names['fund%d'%(i+1)] = Fund_new.ETFFund(self.fund_name_list[i],self.fund_ID_list[i])
                self.fund_list.append(names['fund%d'%(i+1)])
                total_value_node = parent_node.find('div','col-div col-1')
                yest_profit_loss_node = parent_node.find('div','col-div col-2')
                cum_profit_loss_node = parent_node.find('div','col-div col-3')
                names['fund%d'%(i+1)].currentTotalValue(float(total_value_node.find('p','num').get_text().replace(',', '')))
                try:
                    names['fund%d'%(i+1)].yesterdayPnL(float(yest_profit_loss_node.find('p','num f-red').get_text().replace(',', '')))
                except AttributeError:
                    try:
                        names['fund%d'%(i+1)].yesterdayPnL(float(yest_profit_loss_node.find('p','num f-green').get_text().replace(',', '')))
                    except:
                        names['fund%d'%(i+1)].yesterdayPnL(float(yest_profit_loss_node.find('p','num ').get_text().replace(',', '')))
                try:
                    names['fund%d'%(i+1)].cumPnL(float(cum_profit_loss_node.find('p','num f-red').get_text().replace(',', '')))
                except AttributeError:
                    try:
                        names['fund%d'%(i+1)].cumPnL(float(cum_profit_loss_node.find('p','num f-green').get_text().replace(',', '')))
                    except:
                        names['fund%d'%(i+1)].cumPnL(float(cum_profit_loss_node.find('p','num ').get_text().replace(',', '')))
                names['fund%d'%(i+1)].calculate_day = 252
            
            if current_node.find_parent(id='fixed_fund_list'): #保险理财产品
                names['fund%d'%(i+1)] = Fund_new.SecureFund(self.fund_name_list[i],self.fund_ID_list[i])
                self.fund_list.append(names['fund%d'%(i+1)])
                total_value_node = parent_node.find('div','col-div col-1')
#                yest_profit_loss_node = parent_node.find('div','col-div col-2')
#                cum_profit_loss_node = parent_node.find('div','col-div col-3')
                current_period_pnl_node = parent_node.find('div','col-div col-2')
                day_to_maturity_node = parent_node.find('div','col-div col-3')
                names['fund%d'%(i+1)].currentTotalValue(float(total_value_node.find('p','num').get_text().replace(',', '')))
                names['fund%d'%(i+1)].currentPeriodPnL(float(current_period_pnl_node.find('p','num ').get_text().replace(',', '')))
                names['fund%d'%(i+1)].maturityDate(total_value_node.find('p','m-tips').get_text().split(' ')[1])
                try:
                    names['fund%d'%(i+1)].day2maturity(float(re.sub("\D", "", day_to_maturity_node.find('p', 'm-tips').get_text())))
                except ValueError:
                    names['fund%d'%(i+1)].day2maturity(0)
                names['fund%d'%(i+1)].duration(int(re.sub('\D','',self.fund_name_list[i])))
                
#                names['fund%d'%(i+1)].yesterdayPnL(float(parent_node.find('p','num ').get_text()))
#                names['fund%d'%(i+1)].cumPnL(float(cum_profit_loss_node.find('p','num ').get_text()))
                names['fund%d'%(i+1)].calculate_day = 360
            
            if current_node.find_parent(id='coin_fund_list'): #货币基金
                names['fund%d'%(i+1)] = Fund_new.StableFund(self.fund_name_list[i],self.fund_ID_list[i])
                self.fund_list.append(names['fund%d'%(i+1)])
                total_value_node = parent_node.find('div','col-div col-1')
                yest_profit_loss_node = parent_node.find('div','col-div col-2')
                cum_profit_loss_node = parent_node.find('div','col-div col-3')
#                current_period_pnl_node = parent_node.find('div','col-div col-2')
                names['fund%d'%(i+1)].currentTotalValue(float(total_value_node.find('p','num').get_text().replace(',', '')))
                names['fund%d'%(i+1)].yesterdayPnL(float(parent_node.find('p','num ').get_text().replace(',', '')))
                names['fund%d'%(i+1)].cumPnL(float(cum_profit_loss_node.find('p','num ').get_text().replace(',', '')))
#                names['fund%d'%(i+1)].currentPeriodPnL(float(current_period_pnl_node.find('p','num ').get_text()))
#                profitPer1w_string = re.findall(r'\d.\d\d',(total_value_node.find('p','m-tips').get_text().split(' '))[1])
#                names['fund%d'%(i+1)].profitPer1w(float(profitPer1w_string[0]))
#                try:
#                    names['fund%d'%(i+1)].maturityDate(total_value_node.find('p','m-tips').get_text().split(' ')[2])
#                except:
#                    pass
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
                
        print('\nwrap up 之后的基金包括：')
        for i in self.organised_fund_list:
            print('This is fund %d'%(self.organised_fund_list.index(i)+1))
            i.displayKeyDetails()
    
    def getSubTotalPnL(self): #算出昨日总的固定收益和浮动收益
        self.fix_income_yes_pnl = 0
        self.float_income_yes_pnl = 0
        for i in self.organised_fund_list:
            if isinstance(i, Fund_new.SecureFund):
                self.fix_income_yes_pnl += i.yesterdayPnL()
            if isinstance(i, Fund_new.StableFund):
                self.fix_income_yes_pnl += i.yest_profit_loss
            if isinstance(i, Fund_new.ETFFund):
                self.float_income_yes_pnl += i.yest_profit_loss
    
    def identifyNewFund(self):
        execute_bool = False
        root = tkinter.Tk()
        root.withdraw()
        execute_bool = tkinter.messagebox.askyesno('Money!Money!', 'Anything new?')
        if execute_bool == True:
            new_fund_No_str = input("新买入基金编号为(请填从1开始的数字): ") # input为类似 1,4,5
        else:
            new_fund_No_str = '0'
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
            writer = pd.ExcelWriter(Config.tencent_doc_path,engine='openpyxl',mode='a') 
        except:
            writer = pd.ExcelWriter(Config.tencent_doc_path)
            
        for i in range(0,len(self.new_fund_list)):
            fund_table = self.new_fund_list[i].createTable(self.date)
            fund_table.to_excel(writer,'%s'%self.new_fund_list[i].name)
        #----------------创建 asset table------------------#
        if self.date == Config.tencent_start_date: # 数据起始日
            asset_table = self.createAssetTable()
            asset_table.to_excel(writer,'总资产')
        writer.save()
            
    def updateTable(self):
        existing_workbook = openpyxl.load_workbook(Config.tencent_doc_path)
        updated_table_list = []
        sheet_name_list = []
        #----------------更新asset table------------------#
        if self.date != Config.tencent_start_date: # 数据起始日
            asset_table_new = self.createAssetTable()
            sheet_name = '总资产'
            current_worksheet = existing_workbook[sheet_name]
            asset_table_old = pd.read_excel(Config.tencent_doc_path, sheet_name=sheet_name, index_col=0)
            existing_workbook.remove(current_worksheet)
            asset_table = pd.concat([asset_table_old,asset_table_new], sort=True)
            updated_table_list.append(asset_table)
            sheet_name_list.append(sheet_name)
        #----------------更新fund table------------------#
        for i in range(0, len(self.existing_fund_list)):
            sheet_name = '%s'%self.existing_fund_list[i].name
            current_worksheet = existing_workbook[sheet_name]
            fund_table_old = pd.read_excel(Config.tencent_doc_path, sheet_name=sheet_name, index_col=0)
            existing_workbook.remove(current_worksheet)
            fund_table_new = self.existing_fund_list[i].createTable(self.date)
            fund_table = pd.concat([fund_table_old,fund_table_new], sort=True)
            updated_table_list.append(fund_table)
            sheet_name_list.append(sheet_name)
        try:
            existing_workbook.save(Config.tencent_doc_path)
            writer = pd.ExcelWriter(Config.tencent_doc_path,engine='openpyxl',mode='a') 
        except:
            os.remove(Config.tencent_doc_path)
            writer = pd.ExcelWriter(Config.tencent_doc_path)
        for i in range(0,len(updated_table_list)):
            updated_table_list[i].to_excel(writer, sheet_name_list[i])
        writer.save()
        
        
    
if __name__ == '__main__':
    '''
    start_date = '2018-12-07'
    doc_path = '/Users/YoYo/Desktop/智能记账/Tencent.xlsx'
    while start_date <= time.strftime('%Y-%m-%d',time.localtime(time.time())):
        try:
            TencentGetData(start_date)
        except:
            pass
        start_date = (pd.to_datetime(start_date)+timedelta(1)).strftime('%Y-%m-%d')
    '''
    TencentGetData()

