# -*- coding:utf-8 -*-

import datetime

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

'''
auctionSystem 总model文件
'''
    
PEEL_LEVEL = (
    ("1", "1"),
    ("2", "2"),
    ("3", "3")
)
ACCOUNT_TYPE = (
    ("CUS",   u"客户账户"),
    ("COM",   u"公司账户"),
    ("AUT",   u"拍卖会账户"),
    ("OTHER", u"其他账户"),
)
AUCTION_ACCOUNT_TYPE = (
    ("AMERICAN", u"美元账户"),
    ("LOCAL", u"本地账户")
)
SEX_TYPE = (
    ('f', "female"),
    ('m', "male"),
)

class LotSize(models.Model):
    '''
    LOT的大小配置表
    '''
    size = models.CharField(max_length=30)

    def __unicode__(self):
        return self.size

class LotLevel(models.Model):
    '''
    LOT的等级配置表
    '''
    level = models.CharField(max_length=30)

    def __unicode__(self):
        return self.level

class LotColor(models.Model):
    '''
    LOT的颜色配置表
    '''
    color = models.CharField(max_length=30)

    def __unicode__(self):
        return self.color

class LotClear(models.Model):
    '''
    LOT的清晰度
    '''
    definition = models.CharField(max_length=30)
    def __unicode__(self):
        return self.definition
    
class Commission(models.Model):
    '''佣金计算配置表
    '''
    formular = models.CharField(max_length=500)
    a_scale = models.IntegerField()
    b_scale = models.IntegerField()
    c_scale = models.IntegerField()
    d_scale = models.IntegerField()

class Account(models.Model):
    '''
    账户表
    '''
    name = models.CharField(max_length=30, unique=True)
    balance = models.IntegerField(default=0)
    style = models.CharField(choices=ACCOUNT_TYPE, max_length=10, default="OTHER")
    def __unicode__(self):
        return self.name

class AuctionField(models.Model):
    """
    拍卖场
    """
    # 拍卖场名字
    name = models.CharField(max_length=50, unique=True)
    # 货币种类
    currency = models.CharField(max_length=50)
    is_dollar = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(AuctionField, self).save(*args, **kwargs)
        try:
            account_obj_a = AuctionAccount(name=self.name, auction=self, style="AMERICAN")
            account_obj_l = AuctionAccount(name=self.name, auction=self, style="LOCAL")
        except Exception, e:
            print str(e)
        else:
            account_obj_a.save()
            account_obj_l.save()

    def __unicode__(self):
        return self.name

class AuctionEvent(models.Model):
    '''
    拍卖场场次
    '''
    auction = models.ForeignKey(AuctionField)
    event = models.CharField(max_length=20)

    def __unicode__(self):
        return self.auction.name

    def get_year(self):
        return self.event.split("-")[0]

class AuctionFormula(models.Model):
    '''
    拍卖场发票的计算公司配置表
    '''
    auction = models.ForeignKey(AuctionField)
    #美金总额计算公式(初始发票, sex male)
    pre_invoice_dollar_male = models.TextField(max_length=500)
    #美金总额计算公式(初始发票, sex female)
    pre_invoice_dollar_female = models.TextField(max_length=500)
    #生皮总额计算公式(初始发票, sex male)
    pre_invoice_cost_male = models.TextField(max_length=500)
    #生皮总额计算公式(初始发票, sex female)
    pre_invoice_cost_female = models.TextField(max_length=500)
    #美金总额计算公式(最终发票, sex male)
    final_invoice_dollar_male = models.TextField(max_length=500)
    #美金总额计算公式(最终发票, sex female)
    final_invoice_dollar_female = models.TextField(max_length=500)
    #生皮总额计算公式(最终发票, sex male)
    final_invoice_cost_male = models.TextField(max_length=500)
    #生皮总额计算公式(最终发票, sex female)
    final_invoice_cost_female = models.TextField(max_length=500)

    def __unicode__(self):
        return self.auction.name

class TransferRecord(models.Model):
    """
        转账记录
    """
    # 转账方
    fro = models.ForeignKey(Account)
    # 接收方
    to = models.ForeignKey(Account, related_name="trans_to")
    # 转账金额
    money = models.IntegerField()
    # 转账日期
    date = models.DateTimeField()
    def toDICT(self):
        record = []
        fields = [f.name for f in self._meta.fields]
        for field in fields:
            if field == "date":
                try:
                    record.append((field, getattr(self, field).strftime("%Y-%m-%d %H:%m")))
                except AttributeError:
                    record.append((field, ''))
            elif field in ["fro", "to"]:
                try:
                    record.append((field, getattr(getattr(self, field), "name")))
                except AttributeError:
                    record.append((field, ''))
            else:
                record.append((field, getattr(self, field)))
        return dict(record)
        

class AuctionAccount(models.Model):
    '''
    拍卖会账户
    '''
    name = models.CharField(max_length=30)
    balance = models.IntegerField(default=0)
    style = models.CharField(choices=AUCTION_ACCOUNT_TYPE, max_length=10, default="AMERICAN")
    auction = models.ForeignKey(AuctionField)
    def __unicode__(self):
        return self.name

class Variety(models.Model):
    """
    货物品种
    """
    # 品种名称
    name = models.CharField(max_length=50, unique=True)
    auction = models.ManyToManyField(AuctionField)   
    def __unicode__(self):
        return self.name

class Customer(models.Model):
    """客户类"""
    # 客户名称
    name = models.CharField(max_length=50, unique=True) 
    # 客户编号
    identifier = models.CharField(max_length=20) 
    # 客户电话
    phone = models.CharField(max_length=20) 
    # 客户地址
    address = models.TextField() 
    # 客户账户
    account = models.OneToOneField(Account, null=True)

    def save(self, *args, **kwargs):
        try:
            account_obj = Account(name=self.name, style="CUS")
            account_obj.save()
            self.account = account_obj
        except:
            pass
        super(Customer, self).save(*args, **kwargs)

    def __unicode__(self):
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
    def __unicode__(self):
        return self.name

class PeelInform(models.Model):
    '''削皮指示'''
    # 名称
    name = models.CharField(max_length=100) 
    # 削皮场
    peel_field = models.ManyToManyField(PeelField)
    # 品种
    variety = models.ManyToManyField(Variety, null=True)
    # 尺码
    size = models.ManyToManyField(LotSize, null=True)
    # 性别
    sex = models.CharField(choices=SEX_TYPE, max_length=2, null=True, blank=True)
    # 价格
    peel_price = models.FloatField()
    def __unicode__(self):
        return self.name

class Clearance(models.Model):
    '''清关公司'''
    # 清关公司名字
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name
    
class Delivery(models.Model):
    '''地接公司'''
    # 名称
    name = models.CharField(max_length=50, unique=True)
    account = models.OneToOneField(Account)
    
    def save(self, *args, **kwargs):
        try:
            account_obj = Account(name=self.name, style="OTHER")
            account_obj.save()
            self.account = account_obj
        except:
            pass
        super(Delivery, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name
    
class Harbour(models.Model):
    '''港口'''
    # 港口名字
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name

class ForeignShip(models.Model):
    '''国外货运'''
    # 公司名称
    name = models.CharField(max_length=50, unique=True)
    # 货币种类
    currency = models.CharField(max_length=50)
    account = models.OneToOneField(Account, null=True)

    def save(self, *args, **kwargs):
        try:
            account_obj = Account(name=self.name, style="OTHER")
            account_obj.save()
            self.account = account_obj
        except:
            pass
        super(ForeignShip, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

class PaymentOrder(models.Model):
    '''账户还款记录'''
    # 账户
    account = models.ForeignKey(Account)
    # 抵账
    credit_note = models.IntegerField(null=True)
    # 还款
    payment = models.IntegerField()
    def __unicode__(self):
        return self.account.name

class Shiping(models.Model):
    '''货运表'''
    # 货运号
    shiping_nu = models.CharField(max_length=20) 
    # 货物数量
    com_num = models.IntegerField()
    #货运单发票号
    invoice_nu = models.CharField(max_length=50, null=True)
    # 国外货运公司
    foreign_ship = models.ForeignKey(ForeignShip, null=True)
    # 发票总额
    invoice_count = models.FloatField()
    # 地接费用
    delivery_fee = models.FloatField(null=True)
    # 代理费用
    proxy_fee = models.FloatField(null=True)
    # 总费用
    total_fee = models.FloatField(null=True)
    # 主单号
    master_nu = models.CharField(max_length=50, null=True)
    # 分单号
    branch_nu = models.CharField(max_length=50, null=True)
    # 计件数量
    ship_num = models.IntegerField(null=True)
    #计费重量
    charge_weight = models.IntegerField(null=True)
    # 起飞日期
    takeoff_time = models.DateField(null=True)
    #落地日期
    arrive_time = models.DateField(null=True)
    #清关日期
    clear_time = models.DateField(null=True)


    def __unicode__(self):
        return self.shiping_nu

    @classmethod
    def get_last_nu(cls):
        flag_str = "#00"
        o_count = cls.objects.all().count()
        return flag_str + str(o_count+1)

    @property
    def get_clear_status(self):
        if not self.clear_time:
            return "清关未完成"
        now = datetime.datetime.now()
        date = datetime.date(now.year, now.month, now.day)
        if date <= self.clear_time:
            status = "清关未完成"
        else:
            status = "清关已完成"
        return status

    @property
    def get_ship_status(self):
        now = datetime.datetime.now()
        date = datetime.date(now.year, now.month, now.day)
        if not self.takeoff_time or date<self.takeoff_time:
            status = "货未发"
        elif not self.arrive_time or self.takeoff_time<=date<self.arrive_time:
            status = "运输途中"
        else:
            status = "已到港"
        return status
        
    def toDICT(self):
        ship_list = []
        fields = [f.name for f in self._meta.fields]
        invoice_list = self.invoice_set.all()
        if invoice_list:
            auction_name = invoice_list[0].get_commodity()\
                .auction.name
            ship_list.extend([
                ("clearance_company", invoice_list[0].clearance_company.name),
                ("delivery_company", invoice_list[0].delivery_company.name),
                ("harbour", invoice_list[0].harbour.name),
                ("auction_name", auction_name),
            ])
        if self.total_fee:
            ship_list.extend([
                ("avg_num", "%.2f"%(self.total_fee/len(invoice_list))),
                ("avg_weight", "%.2f"%(self.total_fee/self.charge_weight))
            ])
        else:
            ship_list.extend([("avg_weight", ''), ("avg_num", '')])
        for field in fields:
            if field in ["foreign_ship"]:
                try:
                    ship_list.append((field, getattr(getattr(self, field), "name")))
                except AttributeError:
                    ship_list.append((field, ''))
            elif field in ["auction_date", "takeoff_time", "arrive_time", "clear_time"]:
                try:
                    ship_list.append((field, getattr(self, field).strftime("%Y-%m-%d")))
                except AttributeError:
                    ship_list.append((field, ''))
            else:
                ship_list.append((field, getattr(self, field)))
        return dict(ship_list)

class Invoice(models.Model):
    """发票"""
    # 发票号
    invoice_nu = models.CharField(max_length=20) 
    # 客户号
    customer_id = models.CharField(max_length=20) 
    # 数量
    goods_nu = models.IntegerField() 
    # 美金总额
    dollar_sum = models.IntegerField() 
    # 生皮总金额
    cost_sum = models.IntegerField() 
    # 拍卖会发票
    auction_invoice = models.CharField(max_length=50, null=True) 
    # 最终汇率
    final_exchange_rate = models.FloatField(null=True, blank=True) 
    # 初始汇率
    begin_exchange_rate = models.FloatField(null=True, blank=True) 
    # 佣金比例
    commission_rate = models.FloatField(null=True) 
    # 修改次数
    modify_times = models.IntegerField(null=True) 
    # 修改时间
    modify_date = models.DateTimeField(null=True) 
    # 是否是preinvoice
    is_pre = models.IntegerField(default=1) 
    # 是否货运
    is_ship = models.IntegerField(default=0) 
    #货运
    ship = models.ForeignKey(Shiping, null=True)
    # 清关公司
    clearance_company = models.ForeignKey(Clearance, null=True) 
    # 地接公司
    delivery_company = models.ForeignKey(Delivery, null=True)
    # 港口
    harbour = models.ForeignKey(Harbour, null=True)
    # 毛重
    not_net_weight = models.IntegerField(null=True) 
    # 美金对人民币汇率
    an_rmb_rate = models.FloatField(null=True)
    # 拍卖场次
    auction_event = models.ForeignKey(AuctionEvent, null=True)


    def __unicode__(self):
        return self.invoice_nu

    @classmethod
    def get_last_nu(cls):
        flag_str = "#00"
        o_count = cls.objects.all().count()
        return flag_str + str(o_count+1)
    
    @property
    def get_peeltime_status(self):
        now = datetime.datetime.now()
        date = datetime.date(now.year, now.month, now.day)
        try:
            if not self.peel_time or date<self.peel_time:
                status = "未下缸"
            elif not self.out_peel_time or self.peel_time<=date<self.out_peel_time:
                status = "已下缸未完成"
            elif not self.delivery_time or self.out_peel_time<=date<self.delivery_time:
                status = "已完成未发货"
            else:
                status = "已发货"
        except:
            return ""
        return status

    def commission_fee(self, commis_obj):
        coms = self.commodity_set.all()
        com_price = 0
        args = self.toDICT()
        if not args.get("final_exchange_rate"):
            args["final_exchange_rate"] = 1
        try:
            for c in coms:
                args["final_price"] = c.final_price
                args["number"] = c.number
                com_price += eval(commis_obj.formular.format(**args))
        except Exception, e:
            print str(e)
            return False, 0, {}
        com_price = round(com_price, 2)
        args["commission"] = com_price 
        args["a_scale"], args["b_scale"], args["c_scale"], args["d_scale"] = \
            com_price*commis_obj.a_scale/100, com_price*commis_obj.b_scale/100, \
            com_price*commis_obj.c_scale/100, com_price*commis_obj.d_scale/100
        return True, args 

    def toDICT(self):
        invoice_data = []
        fields = [f.name for f in self._meta.fields]
        commoditys = self.commodity_set.all()
        extra_info = [
            ("goods_type", ','.join(set([com.types for com in commoditys]))),
            ("auction_event", commoditys[0].auction_event if commoditys else ''),
            ("auction", commoditys[0].auction.name if commoditys else '')
        ]
        invoice_data.extend(extra_info)
        for field in fields:
            field_val = getattr(self, field)
            if field == "modify_date" and field_val:
                invoice_data.append((field, field_val.strftime("%Y-%m-%d %H:%M")))
            elif field in ["clearance_company", "delivery_company", "harbour"]:
                try:
                    invoice_data.append((field, getattr(getattr(self, field), "name")))
                except AttributeError:
                    invoice_data.append((field, ''))
            elif field == "ship":
                try:
                    invoice_data.append((field, getattr(getattr(self, field), "ship_nu")))
                except AttributeError:
                    invoice_data.append((field, ''))
            elif field in ["peel_time", "out_peel_time", "delivery_time"] and field_val:
                invoice_data.append((field, field_val.strftime("%Y-%m-%d")))
            elif field == "auction_event":pass
            else:
                invoice_data.append((field, field_val))
            invoice_data.append(("status", self.get_peel_status))
        return dict(invoice_data)

    def get_commodity(self):
        com_obj = self.commodity_set.all()
        return com_obj[0] if com_obj else '' 

    @property
    def get_peel_status(self):
        commodity_list = self.commodity_set.all()
        num = 0
        for com in commodity_list:
            peel_field = com.peel_field
            peel_inform = com.peel_inform
            if peel_field and peel_inform:
                num += 1
        if num == 0:
            status = "未添加削皮指示" 
        elif num < len(commodity_list):
            status = "部分已添加削皮指示" 
        else:    
            status = "已添加削皮指示"
        return status

class Commodity(models.Model):
    """商品"""
    # 商品lot号
    lot = models.CharField(max_length=20) 
    # 拍卖日期
    auction_time = models.DateField(auto_now_add=True)
    # 拍卖场次
    auction_event = models.CharField(max_length=30)
    # 品种
    types = models.CharField(max_length=50) 
    # 性别
    sex = models.CharField(max_length=50, null=True, blank=True) 
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
    remarks = models.CharField(max_length=100, null=True, blank=True) 
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
    # 下缸时间(货物到削皮场加工)
    peel_time = models.DateField(null=True) 
    # 出缸时间(货物到削皮场加工完成)
    out_peel_time = models.DateField(null=True) 
    # 发货时间
    delivery_time = models.DateField(null=True)
    # 削皮优先级
    peel_level = models.CharField(choices=PEEL_LEVEL, max_length=2, default="1")
    # 标记是否可以添加削皮时间
    peel_time_flag = models.IntegerField(default=0)
    # 削皮修改次数 
    peel_mo_num = models.IntegerField(default=0)
    # 削皮修改时间
    peel_mo_time = models.DateTimeField(null=True)
    #削皮备注
    peel_comment = models.CharField(max_length=100, null=True)

    def __unicode__(self):
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
                    commodity.append((field, getattr(getattr(self, field), "auction_invoice")))
                except AttributeError:
                    commodity.append((field, ''))
            elif field in ["auction_time", "peel_time", "out_peel_time", "delivery_time", "peel_mo_time"]:
                try:
                    commodity.append((field, getattr(self, field).strftime("%Y-%m-%d")))
                except AttributeError:
                    commodity.append((field, ''))
            else:
                commodity.append((field, getattr(self, field)))
        commodity.append(("peel_price", self.peel_inform.peel_price if self.peel_inform else ''))
        commodity.append(("peel_status", self.get_peeltime_status))
        return dict(commodity)
    @property
    def get_peeltime_status(self):
        now = datetime.datetime.now()
        date = datetime.date(now.year, now.month, now.day)
        try:
            if not self.peel_time or date<self.peel_time:
                status = "未下缸"
            elif not self.out_peel_time or self.peel_time<=date<self.out_peel_time:
                status = "已下缸未完成"
            elif not self.delivery_time or self.out_peel_time<=date<self.delivery_time:
                status = "已完成未发货"
            else:
                status = "已发货"
        except:
            return ""
        return status



