# -*- coding:utf-8 -*-
from django.db import models

'''
auctionSystem 总model文件
'''

class Customer(models.Model):
    """客户类"""
    name = models.CharField(max_length=50) # 客户姓名
    identifier = models.CharField(max_length=20) # 客户编号
    phone = models.CharField(max_length=20) # 客户电话
    address = models.TextField() # 客户地址
    def __str__(self):
        return self.name

class PeelField(models.Model):
    """削皮场"""
    name = models.CharField(max_length=100) # 名称
    address = models.CharField(max_length=150) # 地点
    zip_code =  models.CharField(max_length=10) # 邮编
    call_person = models.CharField(max_length=10) # 收件人
    call_phone = models.CharField(max_length=15) # 联系人电话
    def __str__(self):
        return self.name

class Commodity(models.Model):
    """商品"""
    lot = models.CharField(max_length=20, primary_key=True) # 商品lot号
    types = models.CharField(max_length=50) # 品种
    sex = models.CharField(max_length=50) # 性别
    customer_id = models.CharField(max_length=20) # 客户编号
    size = models.CharField(max_length=20) # 尺码
    level = models.CharField(max_length=20) # 等级
    color = models.CharField(max_length=20) # 颜色
    definition = models.CharField(max_length=20) # 清晰度
    number = models.IntegerField() # 数量
    final_price = models.IntegerField() # 敲槌价
    evaluation =  models.CharField(max_length=100) # 评价
    remarks = models.CharField(max_length=100) # 备注
    is_invoice = models.IntegerField() # 发票生成标志
    peel_field = models.ForeignKey(PeelField) # 削皮场
    peel_inform = models.CharField(max_length=100) # 削皮指示
    def __str__(self):
        return self.lot

class Invoice(models.Model):
    """发票"""
    commodity = models.ForeignKey(Commodity)
    invoice_nu = models.CharField(max_length=20) # 发票号
    customer_id = models.CharField(max_length=20) # 客户号
    goods_type = models.CharField(max_length=50) # 品种
    goods_nu = models.IntegerField() # 数量
    dollar_sum = models.IntegerField() # 美金总额
    cost_sum = models.IntegerField() # 生皮总金额
    auction_invoice = models.CharField(max_length=50) # 拍卖会发票
    final_exchange_rate = models.FloatField() # 最终汇率
    begin_exchange_rate = models.FloatField() # 初始汇率
    modify_times = models.IntegerField() # 修改次数
    modify_date = models.DateField() # 修改时间
    def __str__(self):
        return self.invoice_nu
