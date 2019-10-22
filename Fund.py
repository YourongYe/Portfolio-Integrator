#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 13:19:15 2019

@author: YoYo
"""

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
        


#----------保险理财产品----------#
class SecureFund(Fund):
    
    def __init__(self, name, fund_id):
        super().__init__(name, fund_id)
        
    def currentPeriodPnL(self, current_period_pnl): #当期累计收益
        self.current_period_pnl = current_period_pnl
    
    def maturityDate(self, maturity_date): #到期时间
        self.maturity_date = maturity_date
    
    def day2maturity(self, day_to_maturity): #离本期结束时间
        self.day_to_maturity = day_to_maturity
    
    def duration(self, duration): #产品持有周期
        self.duration = duration
    
    def yesterdayPnL(self): #昨日收益(平均估计值)
        try:
            yest_profit_loss = self.current_period_pnl / (self.duration - self.day_to_maturity)
        except:
            yest_profit_loss = 0
        return round(yest_profit_loss, 3)
    
    def realTimeROA(self):
        try:
            roa = (1 + self.yest_profit_loss/self.total_value) ** self.calculate_day - 1
        except AttributeError:
            try:
                roa = (1 + self.yesterdayPnL()/self.total_value) ** self.calculate_day - 1
            except ZeroDivisionError:
                roa = 0
#        try:
#            daily_return = (self.current_period_pnl / (self.duration - self.day_to_maturity)) / self.total_value
#            roa = (1 + daily_return)**self.calculate_day - 1
#        except:
#            roa = 0
        return round(roa*100, 2)
    
    def displayKeyDetails(self):
        print('产品名称: ', self.name)
        print('产品编号: ', self.fund_id)
        print('到期时间： ', self.maturity_date)
        print('资产市值: ', self.total_value)
        try:
            print('昨日浮动盈亏: ', self.yest_profit_loss)
        except:
            print('昨日浮动盈亏: ', self.yesterdayPnL())
        print('当期累计盈亏: ', self.current_period_pnl)
        print('实时年化收益: ', self.realTimeROA())
    
    def createTable(self, date): # date格式为'2018-12-12'
        table_index = ['资产市值', '昨日浮动盈亏', '当期累计盈亏', '实时年化收益%']#, '到期时间', '本期剩余天数']
        table = pd.DataFrame(index=table_index)
        table[date] = [self.total_value, self.yesterdayPnL(), self.current_period_pnl, self.realTimeROA()]#, 
                #self.maturity_date, self.day_to_maturity]
        
        return table.T
    
#----------指数基金----------#
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


#----------货币基金理财产品----------#
class StableFund(Fund): 
    
    def __init__(self, name, fund_id):
        super().__init__(name, fund_id)
        
        
    def createTable(self, date): # date是pandas的时间格式
        table_index = ['资产市值', '昨日浮动盈亏', '累计盈亏', '实时年化收益%']
        table = pd.DataFrame(index=table_index)
        table[date] = [self.total_value, self.yest_profit_loss, self.cum_profit_loss, self.realTimeROA()]
        
        return table.T
    
        
        
        
        
        
        
        
        
        
        
        
        
        