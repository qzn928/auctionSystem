# -*- coding:utf-8 -*-

import datetime

from django.db import models

'''
auctionSystem 总model文件
'''
    
class AuctionField(models.Model):
    """
    拍卖场
    """
    # 拍卖场名字
    name = models.CharField(max_length=50, unique=True)
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

class PeelInform(models.Model):
    '''削皮指示'''
    # 名称
    name = models.CharField(max_length=100) 
    # 削皮场
    peel_field = models.ManyToManyField(PeelField)
    # 价格
    peel_price = models.FloatField()
    def __str__(self):
        return self.name

class Clearance(models.Model):
    '''清关公司'''
    # 清关公司名字
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Delivery(models.Model):
    '''货运公司'''
    # 地接公司名字
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
class Harbour(models.Model):
    '''港口'''
    # 港口名字
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class ForeignShip(models.Model):
    '''国外货运'''
    # 公司名称
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Invoice(models.Model):
    """发票"""
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
    # 下缸时间(货物到削皮场加工)
    peel_time = models.DateField(null=True) 
    # 出缸时间(货物到削皮场加工完成)
    out_peel_time = models.DateField(null=True) 
    # 发货时间
    delivery_time = models.DateField(null=True)
    # 是否货运
    is_ship = models.IntegerField(default=0) 
    # 清关公司
    clearance_company = models.ForeignKey(Clearance, null=True) 
    # 地接公司
    delivery_company = models.ForeignKey(Delivery, null=True)
    # 港口
    harbour = models.ForeignKey(Harbour, null=True)

    def __str__(self):
        return self.invoice_nu

    @classmethod
    def get_last_nu(cls):
        flag_str = "#00"
        o_count = cls.objects.all().count()
        return flag_str + str(o_count+1)
    
    @property
    def get_peel_status(self):
        now = datetime.datetime.now()
        date = datetime.date(now.year, now.month, now.day)
        if date<self.peel_time:
            status = "为下缸"
        elif self.peel_time<date<self.out_peel_time:
            status = "已下缸未完成"
        elif self.out_peel_time<date<self.delivery_time:
            status = "已完成未发货"
        else:
            status = "已发货"
        return status

    def toDICT(self):
        invoice_data = []
        fields = [f.name for f in self._meta.fields]
        for field in fields:
            field_val = getattr(self, field)
            if field == "modify_date" and field_val:
                invoice_data.append((field, field_val.strftime("%Y-%m-%d %H:%M")))
            elif field in ["clearance_company", "delivery_company", "harbour"]:
                try:
                    invoice_data.append((field, getattr(getattr(self, field), "name")))
                except AttributeError:
                    invoice_data.append((field, ''))
            elif field in ["peel_time", "out_peel_time", "delivery_time"] and field_val:
                invoice_data.append((field, field_val.strftime("%Y-%m-%d")))
            else:
                invoice_data.append((field, field_val))
        return dict(invoice_data)
    
    def get_commodity_info(self):
        commodity_list = self.commodity_set.all()
        com_info_dict = {}
        if commodity_list:
            com_info_dict["commodity"] = commodity_list[0]
            peel_price = 0
            for com in commodity_list:
                peel_price += com.peel_inform.peel_price
            com_info_dict["peel_price"] = peel_price
        return com_info_dict

    
class Shiping(models.Model):
    '''货运表'''
    # 货运号
    shiping_nu = models.CharField(max_length=20) 
    # 拍卖日期
    auction_date = models.DateField()
    # 货物数量
    com_num = models.IntegerField()
    # 发票总额
    invoice_count = models.FloatField()
    # 国外货运公司
    foreign_ship =  models.ForeignKey(ForeignShip)
    # 地接公司
    delivery = models.ForeignKey(Delivery)
    # 货运单发票号
    invoice_nu = models.CharField(max_length=20)
    # 地接费用
    delivery_fee = models.FloatField()
    # 代理费用
    proxy_fee = models.FloatField()
    # 总费用
    total_fee = models.FloatField()
    # 清关公司
    clearance_company = models.ForeignKey(Clearance)
    # 主单号
    master_nu = models.CharField(max_length=50)
    # 分单号
    branch_nu = models.CharField(max_length=50)
    # 计件数量
    ship_num = models.IntegerField()
    #计费重量
    charge_weight = models.IntegerField()
    # 起飞日期
    takeoff_time = models.DateField()
    #落地日期
    arrive_time = models.DateField()

    def __str__(self):
        return self.shiping_nu

class Commodity(models.Model):
    """商品"""
    # 商品lot号
    lot = models.CharField(max_length=20, unique=True) 
    # 拍卖下来的日期
    auction_time = models.DateField()
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
    is_invoice = models.IntegerField(default=0) 
    # 削皮场
    peel_field = models.ForeignKey(PeelField, null=True) 
    # 发票
    invoice = models.ForeignKey(Invoice, null=True) 
    # 削皮指示
    peel_inform = models.ForeignKey(PeelInform, null=True) 
    # 拍卖场
    auction = models.ForeignKey(AuctionField)

    def __str__(self):
        return self.lot

    def toDICT(self):
        commodity = []
        fields = [f.name for f in self._meta.fields]
        for field in fields:
            if field in ["peel_field", "auction", "peel_inform"]:
                try:
                    commodity.append((field, getattr(getattr(self, field), "name")))
                except AttributeError:
                    commodity.append((field, ''))
            elif field == "invoice":
                try:
                    commodity.append((field, getattr(getattr(self, field), "invoice_nu")))
                except AttributeError:
                    commodity.append((field, ''))
            elif field == "auction_time":
                try:
                    commodity.append((field, getattr(self, field).strftime("%Y-%m-%d")))
                except AttributeError:
                    commodity.append((field, ''))
            else:
                commodity.append((field, getattr(self, field)))
        return dict(commodity)
