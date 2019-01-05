#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  8 18:34:43 2018

@author: YoYo
"""
import pandas as pd
import time
from datetime import datetime,timedelta

class Fund():
    
    def __init__(self, name, fund_id):
        self.name = name
        self.fund_id = fund_id
    
    def fundCalculateDay(self, calculate_day): # 365 or 252
        self.calculate_day = calculate_day
    
    def currentTotalValue(self, total_value): # 目前用的是这个函数，yesterdayValue函数没有用到
        self.total_value = total_value
    
    def yesterdayValue(self, yesterdayValue):
        self.yesterday_value = yesterdayValue
    
    def yesterdayPnL(self, yest_profit_loss):
        self.yest_profit_loss = yest_profit_loss
    
    def cumPnL(self, cum_profit_loss):
        self.cum_profit_loss = cum_profit_loss
        
    def realTimeROA(self): #年化收益率
        if self.total_value == 0:
            return 0
        
        roa = (1 + self.yest_profit_loss/self.total_value)**self.calculate_day - 1     
        
        return round(roa*100, 2)
    
    def displayKeyDetails(self):
        print('产品名称: ', self.name)
        print('产品编号: ', self.fund_id)
        print('资产市值: ', self.total_value)
        print('昨日浮动盈亏: ', self.yest_profit_loss)
        try: 
            print('累计盈亏: ', self.cum_profit_loss)
        except:
            pass
        print('实时年化收益%: ', self.realTimeROA())
        



class StableFund(Fund):
    
    def __init__(self, name, fund_id):
        super().__init__(name, fund_id)
        
    def currentPeriodPnL(self, current_period_pnl):
        self.current_period_pnl = current_period_pnl
    
    def maturityDate(self, maturity_date):
        self.maturity_date = maturity_date
        #today_date = pd.to_datetime(time.strftime('%Y-%m-%d',time.localtime(time.time())))
        #self.day_to_maturity = (pd.to_datetime(self.maturity_date) - today_date).days
    
    def profitPer1w(self, profit_per_1w):
        self.profit_per_1w = profit_per_1w
    
    def yesterdayPnL(self):
        yest_profit_loss = self.profit_per_1w * self.total_value/10000
        return yest_profit_loss
    
    def realTimeROA(self):
        roa = (1 + self.profit_per_1w/10000)**self.calculate_day - 1
        return round(roa*100, 2)
    
    def displayKeyDetails(self):
        print('产品名称: ', self.name)
        print('产品编号: ', self.fund_id)
        print('到期时间： ', self.maturity_date)
        print('资产市值: ', self.total_value)
        print('昨日浮动盈亏: ', round(self.yesterdayPnL(),3))
        print('当期累计盈亏: ', self.current_period_pnl)
        print('实时年化收益: ', self.realTimeROA())
    
    def createTable(self, date): # date格式为'2018-12-12'
        table_index = ['资产市值', '昨日浮动盈亏', '当期累计盈亏', '实时年化收益%']#, '到期时间', '本期剩余天数']
        table = pd.DataFrame(index=table_index)
        table[date] = [self.total_value, self.yesterdayPnL(), self.current_period_pnl, self.realTimeROA()]#, 
                #self.maturity_date, self.day_to_maturity]
        
        return table.T
    
        
class ETFFund(Fund):

    def __init__(self, name, fund_id):
        super().__init__(name, fund_id) 
        
    def buyDate(self, purchase_date): # buy_date is string like '2018-02-14'
        self.purchase_date = purchase_date
    
    '''
    def cumROA(self):
        today_date = pd.to_datetime(time.strftime('%Y-%m-%d',time.localtime(time.time())))
        holding_period = (today_date - pd.to_datetime(self.purchase_date)).days
        to_date_roa = (self.cum_profit_loss/(self.total_value - self.cum_profit_loss))/holding_period*self.calculate_day
        
        return to_date_roa
     '''   
     
    def createTable(self, date): # date是pandas的时间格式
        table_index = ['资产市值', '昨日浮动盈亏', '累计盈亏', '实时年化收益%']
        table = pd.DataFrame(index=table_index)
        table[date] = [self.total_value, self.yest_profit_loss, self.cum_profit_loss, self.realTimeROA()]
        
        return table.T
             

class SecureFund(Fund):
    
    def __init__(self, name, fund_id):
        super().__init__(name, fund_id)
        
        
    def createTable(self, date): # date是pandas的时间格式
        table_index = ['资产市值', '昨日浮动盈亏', '累计盈亏', '实时年化收益%']
        table = pd.DataFrame(index=table_index)
        table[date] = [self.total_value, self.yest_profit_loss, self.cum_profit_loss, self.realTimeROA()]
        
        return table.T
    
        
        
        
        
        
        
        
        
        
        
        
        
        