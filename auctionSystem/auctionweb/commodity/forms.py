#coding:utf-8


from django import forms


from auctionweb.models import Commodity




class CommodityForm(forms.ModelForm):
    
    class Meta:
        model = Commodity
        exclude = ("peel_field", "auction")
