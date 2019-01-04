#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 20:19:05 2018

@author: YoYo
"""
import pandas as pd
import time
import re
import BankProducts
import openpyxl
import os
import Config
from datetime import timedelta
from bs4 import BeautifulSoup

class BankGetData():
    
    def __init__(self, specify_date=None, card='main'):
        if specify_date == None:
            date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        else:
            date = specify_date
        
        if card == 'main':
            self.soup = BeautifulSoup(open(Config.bank_main_soup_path + '/%s.html'%date),'lxml')
            try:
                self.fund_soup = BeautifulSoup(open(Config.bank_main_soup_path + '/fund/%s.html'%date),'lxml')
            except:
                pass
        else:
            self.soup = BeautifulSoup(open(Config.bank_small_soup_path + '/%s.html'%date),'lxml')
            try:
                self.fund_soup = BeautifulSoup(open(Config.bank_small_soup_path + '/fund/%s.html'%date),'lxml')
            except:
                pass
            
        self.date = date
        if card == 'main':
            self.doc_path = Config.bank_main_doc_path
            self.start_date = Config.bank_main_start_date
        else:
            self.doc_path = Config.bank_small_doc_path
            self.start_date = Config.bank_small_start_date
            
        self.getAllFundsIDList()
        self.getEachFundDetails()
        self.identifyNewFund()
        if self.new_fund_list:
            self.createTable()
        if self.existing_fund_list:
            self.updateFundTable()
        self.updateProductTable()
    
    def getAssetDetails(self):
        self.total_asset = float(self.soup.find('div','asset').find('span').get_text().replace(',', ''))
    
    def createAssetTable(self):
        self.getAssetDetails()
        asset_table = pd.DataFrame(index=['总资产'])
        asset_table[self.date] = [self.total_asset]
        
        return asset_table.T
    
    def getAllFundsIDList(self):
        self.fund_name_list = []
        self.fund_id_list = []
        fund_name_nodes = self.soup.select('td[style="text-align:left"]')
        for i in fund_name_nodes:
            self.fund_name_list.append(i.get_text().split(' (')[0])
            self.fund_id_list.append(i.get_text().split(' (')[1])
    
    def getEachFundDetails(self):
        self.fund_list = []
        self.fixed_products_list = []
        for i in range(0,len(self.fund_name_list)):
            current_node = self.soup.find(text=self.fund_name_list[i])    
            names = locals()
            #---------------将 在途 资金项去掉---------------#
            if re.findall(r'在途', self.fund_name_list[i]):
                continue
                
            if current_node.find_parent(id="wealthDetail1_divWealthContent"):
                #---------------代码开头为11的是结构性产品---------------#
                if re.findall(r'代码：11',self.fund_id_list[i]):
                    names['fund%d'%(i+1)] = BankProducts.StructuredProducts(self.fund_name_list[i])
                    self.fixed_products_list.append(names['fund%d'%(i+1)])
                #---------------将 朝招金 单独列出来---------------#
                elif re.findall(r'朝招金',self.fund_name_list[i]):
                    names['fund%d'%(i+1)] = BankProducts.dailyProducts(self.fund_name_list[i])
                    self.fund_list.append(names['fund%d'%(i+1)])
                else:
                    names['fund%d'%(i+1)] = BankProducts.StableProducts(self.fund_name_list[i])
                    self.fixed_products_list.append(names['fund%d'%(i+1)])
         
                total_value = float(current_node.find_next('td').find_next('td').find_next('td').find_next('td').get_text().replace(',', ''))
                start_date = current_node.find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').get_text()
                maturity_date = current_node.find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').get_text()
                names['fund%d'%(i+1)].totalValue(total_value)
                names['fund%d'%(i+1)].startDate(start_date)
                names['fund%d'%(i+1)].maturityDate(maturity_date)
            
            if current_node.find_parent(id="wealthDetail2_divWealthContent"):
                names['fund%d'%(i+1)] = BankProducts.Fund(self.fund_name_list[i])
                total_value = float(current_node.find_next('td').find_next('td').find_next('td').get_text().replace(',', ''))
                cum_profit_loss = float(current_node.find_next('td').find_next('td').find_next('td').find_next('td').get_text().replace(',', ''))
                names['fund%d'%(i+1)].totalValue(total_value)
                names['fund%d'%(i+1)].cumPnL(cum_profit_loss)
                try:
                    current_fund_node = self.fund_soup.find(text=' %s '%self.fund_name_list[i])
                    hist_total_value = float(current_fund_node.find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').get_text())
                    dividend = float(current_fund_node.find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').get_text())
                    names['fund%d'%(i+1)].histTotalValue(hist_total_value)
                    names['fund%d'%(i+1)].fundDividend(dividend)
                except:
                    pass
                self.fund_list.append(names['fund%d'%(i+1)])
        
        print('银行理财产品包括以下：')
        for i in self.fixed_products_list:
            print('This is product %d'%(self.fixed_products_list.index(i)+1))
            i.displayKeyDetails()
        print('银行基金产品包括以下：')
        for i in self.fund_list:
            print('This is fund %d'%(self.fund_list.index(i)+1))
            i.displayKeyDetails()    
    
    def identifyNewFund(self):
        new_product_No_str = input("新买入理财产品编号为(请填从1开始的数字): ")
        if new_product_No_str == '0': # 如果当天没有新的基金的话就填0
            self.new_product_list = None
            self.existing_product_list = self.fixed_products_list      
        else:
            self.new_product_list = []
            self.existing_product_list = []
            
            try:
                new_product_No = [int(x) for x in new_product_No_str.split(',')]  # type = str
            except:
                new_product_No = [int(new_product_No_str)] 
            
            for i in new_product_No:   
                new_product = self.fixed_products_list[i - 1]
                self.new_product_list.append(new_product)
            
            all_product_No = list(range(1, len(self.fixed_products_list)+1))
            existing_product_No = list(set(all_product_No).difference(set(new_product_No)))
            
            for i in existing_product_No:   
                existing_product = self.fixed_products_list[i - 1]
                self.existing_product_list.append(existing_product)
                
        new_fund_No_str = input("新买入基金编号为(请填从1开始的数字): ") # input为类似 1,4,5
        if new_fund_No_str == '0': # 如果当天没有新的基金的话就填0
            self.new_fund_list = None
            self.existing_fund_list = self.fund_list      
        else:
            self.new_fund_list = []
            self.existing_fund_list = []
            
            try:
                new_fund_No = [int(x) for x in new_fund_No_str.split(',')]  # type = str
            except:
                new_fund_No = [int(new_fund_No_str)] 
            
            for i in new_fund_No:   
                new_fund = self.fund_list[i - 1]
                self.new_fund_list.append(new_fund)
            
            all_fund_No = list(range(1, len(self.fund_list)+1))
            existing_fund_No = list(set(all_fund_No).difference(set(new_fund_No)))
            
            for i in existing_fund_No:   
                existing_fund = self.fund_list[i - 1]
                self.existing_fund_list.append(existing_fund)
            
    def createTable(self):
        try:
            writer = pd.ExcelWriter(self.doc_path,engine='openpyxl',mode='a') 
        except:
            writer = pd.ExcelWriter(self.doc_path)
        
        #----------------创建 asset table------------------#
        if self.date == self.start_date: # 数据起始日
            asset_table = self.createAssetTable()
            asset_table.to_excel(writer,'总资产')
        #----------------创建 bank product table------------------#
        if self.date == self.start_date: # 数据起始日
            fixed_products_table = pd.DataFrame()
            for i in range(0,len(self.new_product_list)):
                temp_table = self.new_product_list[i].createTable()
                if i == 0:
                    fixed_products_table = temp_table
                else:
                    fixed_products_table = pd.concat([fixed_products_table, temp_table])
            fixed_products_table.to_excel(writer,'理财产品')
                
        for i in range(0,len(self.new_fund_list)):
            fund_table = self.new_fund_list[i].createTable(self.date)
            fund_table.to_excel(writer,'%s'%self.new_fund_list[i].name)
        
        writer.save()
        
    def updateFundTable(self):
        existing_workbook = openpyxl.load_workbook(self.doc_path)
        updated_table_list = []
        sheet_name_list = []
        #----------------更新 asset table------------------#
        if self.date != self.start_date: # 数据起始日
            asset_table_new = self.createAssetTable()
            sheet_name = '总资产'
            current_worksheet = existing_workbook[sheet_name]
            asset_table_old = pd.read_excel(self.doc_path, sheet_name=sheet_name, index_col=0)
            existing_workbook.remove(current_worksheet)
            asset_table = pd.concat([asset_table_old,asset_table_new])
            updated_table_list.append(asset_table)
            sheet_name_list.append(sheet_name)
        #----------------更新 fund table------------------#
        for i in range(0, len(self.existing_fund_list)):
            sheet_name = '%s'%self.existing_fund_list[i].name
            current_worksheet = existing_workbook[sheet_name]
            fund_table_old = pd.read_excel(self.doc_path, sheet_name=sheet_name, index_col=0)
            existing_workbook.remove(current_worksheet)
            fund_table_new = self.existing_fund_list[i].createTable(self.date)
            fund_table = pd.concat([fund_table_old,fund_table_new])
            updated_table_list.append(fund_table)
            sheet_name_list.append(sheet_name)
        try:
            existing_workbook.save(self.doc_path)
            writer = pd.ExcelWriter(self.doc_path,engine='openpyxl',mode='a') 
        except:
            os.remove(self.doc_path)
            writer = pd.ExcelWriter(self.doc_path)
        for i in range(0,len(updated_table_list)):
            updated_table_list[i].to_excel(writer, sheet_name_list[i])
        writer.save()
    
    def updateProductTable(self):
        #----------------更新 bank product table------------------#
        if self.date != self.start_date: # 数据起始日
            if self.new_product_list:
                existing_workbook = openpyxl.load_workbook(self.doc_path)
                product_table_new = pd.DataFrame()
                for i in range(len(self.new_product_list)):
                    temp_product_table = self.new_product_list[i].createTable()
                    if i == 0:
                        product_table_new = temp_product_table
                    else:
                        product_table_new = pd.concat([product_table_new, temp_product_table])
                sheet_name = '理财产品'
                current_worksheet = existing_workbook[sheet_name]
                product_table_old = pd.read_excel(self.doc_path, sheet_name=sheet_name, index_col=0)
                existing_workbook.remove(current_worksheet)
                product_table = pd.concat([product_table_old, product_table_new])
                #----------------存储表格------------------#
                existing_workbook.save(self.doc_path)
                writer = pd.ExcelWriter(self.doc_path,engine='openpyxl',mode='a') 
                product_table.to_excel(writer, sheet_name)
                writer.save()

if __name__ == '__main__':
    '''
    start_date = '2018-12-12'
    while start_date <= time.strftime('%Y-%m-%d',time.localtime(time.time())):
        try:
            BankGetData(start_date)
        except:
            pass
        start_date = (pd.to_datetime(start_date)+timedelta(1)).strftime('%Y-%m-%d')

    '''
    start_date = '2018-12-13'
    while start_date <= time.strftime('%Y-%m-%d',time.localtime(time.time())):
        try:
            BankGetData(start_date, card='small')
        except:
            pass
        start_date = (pd.to_datetime(start_date)+timedelta(1)).strftime('%Y-%m-%d')





















     
