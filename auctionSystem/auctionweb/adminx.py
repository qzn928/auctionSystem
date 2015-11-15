#from django.contrib import xadmin

# Register your models here.
#from django.contrib import xadmin

import xadmin
from auctionweb.models import *


class CustomerAdmin(object):
    exclude = ('account',)
xadmin.site.register(Customer, CustomerAdmin)


class PeelFieldAdmin(object):
    pass


xadmin.site.register(PeelField, PeelFieldAdmin)

class AuctionFieldAdmin(object):
    pass

xadmin.site.register(AuctionField, AuctionFieldAdmin)

class VarietyAdmin(object):
    pass
    
xadmin.site.register(Variety, VarietyAdmin)

class PeelInformAdmin(object):
    pass
    
xadmin.site.register(PeelInform, PeelInformAdmin)

class ClearanceAdmin(object):
    pass
    
xadmin.site.register(Clearance, ClearanceAdmin)

class DeliveryAdmin(object):
    pass
    
xadmin.site.register(Delivery, DeliveryAdmin)

class HarbourAdmin(object):
    pass
    
xadmin.site.register(Harbour, HarbourAdmin)

class ForeignShipAdmin(object):
    pass
    
xadmin.site.register(ForeignShip, ForeignShipAdmin)

class AccountAdmin(object):
    pass

xadmin.site.register(Account, AccountAdmin)

class AuctionAccountAdmin(object):
    fields = ("name", "style", "balance")

xadmin.site.register(AuctionAccount, AuctionAccountAdmin)
