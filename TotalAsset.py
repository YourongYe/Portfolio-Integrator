#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 12:57:30 2019

@author: YoYo
"""

#每天的总资产汇总，收益汇总，收益率
#每月的总资产汇总，收益汇总，收益率，以及各个产品的收益对比，分布

import pandas as pd
import Config
#import numpy as np
import OtherInvest


class TotalAsset():
    
    def __init__(self):
        self.readTotalAssetTable()
        self.otherTempInvestment()
        self.integrateTotalAsset()
        #self.toExcel()
        self.total_asset_table.to_excel(Config.total_asset_doc_path)
    

    def readTotalAssetTable(self):
        sheet_name = '总资产'
        self.table_name_list = ['tencent', 'bank_main', 'bank_small', 'xingye', 'other_invest']
        path_list = [Config.tencent_doc_path, Config.bank_main_doc_path, Config.bank_small_doc_path, 
                     Config.xingye_doc_path, Config.other_investment_doc_path]
        name = globals()
        for i in range(len(self.table_name_list)):
            name['%s_total_asset_table'%self.table_name_list[i]] = pd.read_excel(path_list[i], sheet_name=sheet_name, index_col=0)
    
    
    def otherTempInvestment(self):
        self.temp_invest_df = pd.read_excel(Config.temp_investment_doc_path, index_col=0).iloc[:,0]
        
    def integrateTotalAsset(self):
        total_asset_df = pd.concat([tencent_total_asset_table['总资产'], bank_main_total_asset_table, bank_small_total_asset_table,
                                    xingye_total_asset_table, other_invest_total_asset_table], axis=1, sort=True)
        total_asset_df.columns = self.table_name_list
        # -------------------------------将不会每天更新的数据填充------------------------------- #
        for i in ['xingye', 'other_invest']:
            total_asset_df.loc[:,i] = total_asset_df.loc[:,i].fillna(method='ffill',axis=0) 
        # -------------------------------将缺失数据行剔除，并将剩下完整数据加和------------------------------- #
        total_asset_df = total_asset_df.dropna()
        total_asset = total_asset_df.sum(1)
        # -------------------------------加上临时投资金额------------------------------- #
        for i in self.temp_invest_df.index:
            if i in total_asset.index:
                total_asset[i] += self.temp_invest_df[i]
        # -------------------------------根据每日总资产算参数------------------------------- #
        self.total_asset_table = total_asset.to_frame('总资产')
        self.total_asset_table['主要投资金额变动'] = total_asset.diff() - total_asset_df['other_invest'].diff() # 金额变动包括投资收益和转账
        self.total_asset_table['其他投资金额变动'] = total_asset_df['other_invest'].diff() # 金额变动包括投资收益和转账
#        self.total_asset_table['最新盈亏'] = total_asset.diff()  
        self.total_asset_table['datetime'] = pd.to_datetime(self.total_asset_table.index) # 把index转为日期格式
        # -------------------------------读取excel中的生活费cash flow，并做差得到真实P&L------------------------------- #
        cash_flow_df = pd.read_excel(Config.book_keeping_doc_path, sheet_name='生活费', index_col=0)
        current_start_point = pd.read_excel(Config.book_keeping_doc_path, sheet_name='本金', index_col=0).iloc[:1,:] # 默认第一行就是今年记账开始日期
        cash_flow_df = cash_flow_df.sort_index(ascending=False)
        cash_flow_df = cash_flow_df.cumsum(0)
        cash_flow_df = cash_flow_df.sort_index(ascending=True)
        adj_total_asset_df = pd.concat([cash_flow_df, self.total_asset_table['总资产']], axis=1, sort=True)
        adj_total_asset_df.loc[:,'金额'] = adj_total_asset_df.loc[:,'金额'].fillna(method='bfill',axis=0)
        adj_total_asset_df.loc[:,'金额'] = adj_total_asset_df.loc[:,'金额'].fillna(0)
        adj_total_asset_df = adj_total_asset_df.diff(axis=1)
        adj_total_asset_df = adj_total_asset_df.dropna(how='all')
        adj_total_asset_df = adj_total_asset_df.dropna(axis=1) # 得到最终前复权之后的总资产，相当于假设所有当年的CF都发生在年初
        self.total_asset_table['前复权总资产'] = adj_total_asset_df['总资产']
        self.total_asset_table['最新盈亏'] = adj_total_asset_df.diff()  
        for i in cash_flow_df.index:
            if i > current_start_point.index:
                current_start_point.iloc[0,0] -= cash_flow_df.loc[i,'金额'] # 记账开始日期也需要复权
        current_start_point.index = pd.to_datetime(current_start_point.index)
        # -------------------------------循环得到每日的盈亏和收益率------------------------------- #
        for i in range(0, len(self.total_asset_table.index)): 
            self.total_asset_table.loc[self.total_asset_table.index[i],'每日平均盈亏'] = (adj_total_asset_df['总资产'][i] - current_start_point.iloc[0,0]) / (self.total_asset_table['datetime'][i] - current_start_point.index).days
#            self.total_asset_table.loc[self.total_asset_table.index[i],'每日平均盈亏'] = (self.total_asset_table['总资产'][i] - self.total_asset_table['总资产'][0]) / (self.total_asset_table['datetime'][i] - self.total_asset_table['datetime'][0]).days
            self.total_asset_table.loc[self.total_asset_table.index[i],'实时年化收益%'] = (self.total_asset_table['最新盈亏'][i]/self.total_asset_table['总资产'][i-1])/(self.total_asset_table['datetime'][i] - self.total_asset_table['datetime'][i-1]).days*252*100
        self.total_asset_table['累计年化收益%'] = self.total_asset_table['每日平均盈亏']/self.total_asset_table['总资产']*252*100
        self.total_asset_table = self.total_asset_table.reindex(columns=['总资产', '前复权总资产', '每日平均盈亏', '累计年化收益%', '最新盈亏', '实时年化收益%', '主要投资金额变动', '其他投资金额变动'])
        
    def toExcel(self):
        try:
            existing_total_asset_table = pd.read_excel(Config.total_asset_doc_path)
        except:
            existing_total_asset_table = None
        
        if existing_total_asset_table == None:
            new_total_asset_table = self.total_asset_table
        else:  
            new_total_asset_table = pd.concat([self.total_asset_table, existing_total_asset_table], sort=True)
        
        new_total_asset_table.to_excel(Config.total_asset_doc_path)



if __name__ == '__main__':
    OtherInvest.OtherInvest()
    TotalAsset()
        







