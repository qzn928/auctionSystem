#coding:utf-8


from django import forms


from auctionweb.models import Invoice



class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            "commodity",
            "invoice_nu",
            "customer_id",
            "goods_type",
            "goods_nu",
            "dollar_sum",
            "cost_sum",
            "begin_exchange_rate"
        )

class FinalInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            "invoice_nu",
            "customer_id",
            "goods_type",
            "goods_nu",
            "dollar_sum",
            "cost_sum",
            "auction_invoice",
            "final_exchange_rate"
        )
