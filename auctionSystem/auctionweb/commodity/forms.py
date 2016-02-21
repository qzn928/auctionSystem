#coding:utf-8


from django import forms


from auctionweb.models import Commodity, AuctionField




class CommodityForm(forms.ModelForm):
    
    class Meta:
        model = Commodity
        exclude = (
            "peel_field", "is_invoice", 
            "peel_inform", "invoice", "peel_time", "auction_time",
            "out_peel_time", "delivery_time", "peel_level",
            "peel_time_flag", "peel_mo_num", "peel_mo_time", "peel_comment"
        )

    def clean(self):
        self.cleaned_data = super(CommodityForm, self).clean()
        lot = self.cleaned_data["lot"]
        auction = self.cleaned_data["auction"]
        auction_event = self.cleaned_data["auction_event"]#拍卖场次
        try:
            auction_obj = AuctionField.objects.get(id=auction.id)
        except AuctionField.DoesNotExist:
            raise forms.ValidationError("auction does not exist")
        filter_com = Commodity.objects.filter(
            auction_event=auction_event, auction=auction_obj).values_list("lot", flat=True)
        if lot in filter_com:
            msg = u"lot has existed in this auction"
            self.add_error("lot", msg)
