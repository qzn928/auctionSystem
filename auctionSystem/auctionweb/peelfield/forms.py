#coding:utf-8


from django import forms


from auctionweb.models import PeelField


class PeelFieldForm(forms.ModelForm):
    class Meta:
        model = PeelField
