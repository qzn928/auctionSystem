# -*- coding:utf-8 -*-
from django.db import models

'''
auctionSystem 总model文件
'''
    
class AuctionField(models.Model):
    """
    拍卖场
    """
    # 拍卖场名字
    name = models.CharField(max_length=50)
    # 货币种类
    currency = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Variety(models.Model):
    """
    货物品种
    """
    # 品种名称
    name = models.CharField(max_length=50)
    auction = models.ManyToManyField(AuctionField)   
    def __str__(self):
        return self.name

class Customer(models.Model):
    """客户类"""
    # 客户姓名
    name = models.CharField(max_length=50) 
    # 客户编号
    identifier = models.CharField(max_length=20) 
    # 客户电话
    phone = models.CharField(max_length=20) 
    # 客户地址
    address = models.TextField() 

    def __str__(self):
        return self.name

class PeelField(models.Model):
    """削皮场"""
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
    def __str__(self):
        return self.name

class Commodity(models.Model):
    """商品"""
    # 商品lot号
    lot = models.CharField(max_length=20, unique=True) 
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
    peel_field = models.ForeignKey(PeelField, null=True) 
    # 削皮指示
    peel_inform = models.CharField(max_length=100) 
    # 拍卖场
    auction = models.ForeignKey(AuctionField)
    def __str__(self):
        return self.lot

    def toDICT(self):
        commodity = []
        fields = [f.name for f in self._meta.fields]
        for field in fields:
            if field == "peel_field":
                try:
                    commodity.append(("peel_field", getattr(getattr(self, field), "name")))
                except AttributeError:
                    commodity.append(("peel_field", ''))
            else:
                commodity.append((field, getattr(self, field)))
        return dict(commodity)

class Invoice(models.Model):
    """发票"""
    # 商品lot号, 以逗号隔开(001,002...)
    commodity = models.CharField(max_length=100)
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
    auction_invoice = models.CharField(max_length=50, null=True) 
    # 最终汇率
    final_exchange_rate = models.FloatField(null=True) 
    # 初始汇率
    begin_exchange_rate = models.FloatField() 
    # 佣金比例
    commission_rate = models.FloatField(null=True) 
    # 修改次数
    modify_times = models.IntegerField(null=True) 
    # 修改时间
    modify_date = models.DateTimeField(null=True) 
    # 是否是preinvoice
    is_pre = models.IntegerField(default=1) 
    def __str__(self):
        return self.invoice_nu

    @classmethod
    def get_last_nu(cls):
        flag_str = "#00"
        o_count = cls.objects.all().count()
        return flag_str + str(o_count+1)

    def toDICT(self):
        invoice_data = []
        fields = [f.name for f in self._meta.fields]
        for field in fields:
            field_val = getattr(self, field)
            if field == "modify_date" and field_val:
                invoice_data.append((field, field_val.strftime("%Y-%m-%d %H:%M")))
            else:
                invoice_data.append((field, field_val))
        return dict(invoice_data)
