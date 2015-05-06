# -*- coding:utf-8 -*-
from django.db import models

# Create your models here.

# 客户类
class Customer(models.Model):
    # 客户姓名
    name = models.CharField(max_length=50)
    # 客户编号
    identifier = models.CharField(max_length=20)
    # 客户电话
    phone = models.CharField(max_length=20)
    # 客户地址
    address = models.TextField()

# 削皮场
class PeelField(models.Model):
    # 名称
    name = models.CharField(max_length=100)
    # 地点
    address = models.CharField(max_length=150)
    # 邮编
    zip_code =  models.CharField(max_length=10)
    # 收件人
    call_person = models.CharField(max_length=10)
    # 联系人电话
    call_phone = models.CharField(max_length=15)

# 商品
class Commodity(models.Model):
    # 商品lot号
    lot = models.CharField(max_length=20, primary_key=True)
    # 品种
    types = models.CharField(max_length=50)
    # 性别
    sex = models.CharField(max_length=50)
    # 客户编号 
    customer_id = models.CharField(max_length=20)
    # 尺码
    size = models.CharField(max_length=20)
    # 等级
    level = models.CharField(max_length=20)
    # 颜色
    color = models.CharField(max_length=20)
    # 清晰度
    definition = models.CharField(max_length=20)
    # 数量
    number = models.IntegerField()
    # 敲槌价
    final_price = models.IntegerField()
    # 评价
    evaluation =  models.CharField(max_length=100)
    # 备注
    remarks = models.CharField(max_length=100)
    # 发票生成标志
    is_invoice = models.IntegerField()
    # 削皮场
    peel_field = models.CharField(max_length=100)
    # 削皮指示
    peel_inform = models.CharField(max_length=100)

# 发票
class Invoice(models.Model):
    # 发票号
    invoice_nu = models.CharField(max_length=20)
    # 客户号
    customer_id = models.CharField(max_length=20)
    # 品种
    goods_type = models.CharField(max_length=50)
    # 数量
    goods_nu = models.IntegerField()
    # 美金总额
    dollar_sum = models.IntegerField()
    # 生皮总金额
    cost_sum = models.IntegerField()
    # 拍卖会发票
    auction_invoice = models.CharField(max_length=50)
    # 最终汇率
    final_exchange_rate = models.FloatField(max_digits=10, decimal_places=2)
    # 初始汇率
    begin_exchange_rate = models.FloatField(max_digits=10, decimal_places=2)
    # 修改次数
    modify_times = models.IntegerField()
    # 修改时间
    modify_date = models.DateField()

