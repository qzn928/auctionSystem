#coding:utf-8


from django import forms


from auctionweb.models import Invoice



class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            "invoice_nu",
            "customer_id",
            "begin_exchange_rate",
            "an_rmb_rate",
            "commission_rate"
        )

class FinalInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            "invoice_nu",
            "customer_id",
            "auction_invoice",
            "final_exchange_rate"
        )
