#coding:utf-8


from django import forms


from auctionweb.models import Commodity




class CommodityForm(forms.ModelForm):
    
    class Meta:
        model = Commodity
        exclude = (
            "peel_field", "auction", "is_invoice", 
            "peel_inform", "invoice", "peel_time",
            "out_peel_time", "delivery_time", "peel_level",
            "peel_time_flag", "peel_mo_num", "peel_mo_time", "peel_comment"
        )
