#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 29 22:42:02 2018

@author: YoYo
"""
import pandas as pd
import numpy as np

class BankProducts():
    
    def __init__(self, name):
        self.name = name
    
    def fundCalculateDay(self, calculate_day): # 365 or 252
        self.calculate_day = calculate_day
    
    def totalValue(self, total_value):
        self.total_value = total_value
    
    def yesterdayPnL(self, yest_profit_loss):
        self.yest_profit_loss = yest_profit_loss
    
    def cumPnL(self, cum_profit_loss):
        self.cum_profit_loss = cum_profit_loss
    
    def realTimeROA(self): #年化收益率
        roa = (1 + self.yest_profit_loss/self.total_value)**self.calculate_day - 1     
        
        return round(roa*100, 2)
    
    def displayKeyDetails(self):
        print('产品名称: ', self.name)
        print('资产市值: ', self.total_value)
        print('昨日浮动盈亏: ', self.yest_profit_loss)
        try: 
            print('累计盈亏: ', self.cum_profit_loss)
        except:
            pass
        print('实时年化收益%: ', self.realTimeROA())
        

class StableProducts(BankProducts):
    
    def __init__(self, name):
        super().__init__(name)
        self.calculate_day = 360
    
    def maturityDate(self, maturity_date):
        self.maturity_date = maturity_date
    
    def startDate(self, start_date):
        self.start_date = start_date
    
    def expReturn(self, exp_return):
        self.exp_return = exp_return
        
    def displayKeyDetails(self):
        print('产品名称: ', self.name)
        print('资产市值: ', self.total_value)
        print('起始日: ', self.start_date)
        print('到期日: ', self.maturity_date)
    
    def createTable(self): # date是pandas的时间格式
        table_index = ['资产市值', '起始日', '到期日', '预期年化收益%', '实际年化收益%', '实际收益']
        table = pd.DataFrame(index=table_index)
        table[self.name] = [self.total_value, self.start_date, self.maturity_date, np.nan, np.nan, np.nan]
        
        return table.T

class StructuredProducts(BankProducts):
    
    def __init__(self, name):
        super().__init__(name)
        self.calculate_day = 360
    
    def maturityDate(self, maturity_date):
        self.maturity_date = maturity_date
    
    def startDate(self, start_date):
        self.start_date = start_date
    
    def expReturn(self, exp_return):
        self.exp_return = exp_return
    
    def displayKeyDetails(self):
        print('产品名称: ', self.name)
        print('资产市值: ', self.total_value)
        print('起始日: ', self.start_date)
        print('到期日: ', self.maturity_date)
    
    def createTable(self): # date是pandas的时间格式
        table_index = ['资产市值', '起始日', '到期日', '预期年化收益%', '实际年化收益%', '实际收益']
        table = pd.DataFrame(index=table_index)
        table[self.name] = [self.total_value, self.start_date, self.maturity_date, np.nan, np.nan, np.nan]
        
        return table.T

class dailyProducts(BankProducts): # 例如 朝招金，天天盈 等产品
    
    def __init__(self, name):
        super().__init__(name)
    
    def startDate(self, start_date):
        self.start_date = start_date
    
    def maturityDate(self, maturity_date):
        self.maturity_date = maturity_date
    
    def displayKeyDetails(self):
        print('产品名称: ', self.name)
        print('资产市值: ', self.total_value)
    
    def createTable(self, date):
        table_index = ['资产市值', '起始日']
        table = pd.DataFrame(index=table_index)
        table[date] = [self.total_value, self.start_date]
    
        return table.T

class Fund(BankProducts):
    
    def __init__(self, name):
        super().__init__(name)
        self.calculate_day = 252
    
    def histTotalValue(self, hist_total_value):
        self.hist_total_value = hist_total_value
    
    def costRate(self):
        if self.name in ['招商产业 C','招商安心收益']:
            cost_rate = 0
        else:
            cost_rate = 0.8
        
        return cost_rate
    
    def fundDividend(self, dividend):
        self.dividend = dividend
        
    def toDateROA(self): 
        roa = (self.dividend + self.total_value)/self.hist_total_value - 1  
        
        return round(roa*100, 2)
    
    def displayKeyDetails(self):
        print('产品名称: ', self.name)
        print('资产市值: ', self.total_value)
        print('累计盈亏: ', self.cum_profit_loss)
        try:
            print('目前净收益%: ', self.toDateROA())
            print('目前总收益%: ', round(self.toDateROA() + self.costRate(),2))
        except:
            pass
    
    def createTable(self, date): # date格式为'2018-12-12'
        table_index = ['资产成本', '资产市值', '累计盈亏', '分红', '目前净收益%', '目前总收益%']
        table = pd.DataFrame(index=table_index)
        try:
            table[date] = [self.hist_total_value, self.total_value, self.cum_profit_loss, self.dividend, self.toDateROA(), round(self.toDateROA() + self.costRate(),2)]
        except:
            table[date] = [np.nan, self.total_value, self.cum_profit_loss, 0, np.nan, np.nan]
        
        return table.T
    
    
    
    
    
    
    
    
    
    
    
    
    
    