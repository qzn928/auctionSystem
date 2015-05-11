#from django.contrib import xadmin

# Register your models here.
#from django.contrib import xadmin

import xadmin
from auctionweb.models import *


class CustomerAdmin(object):
    pass

xadmin.site.register(Customer, CustomerAdmin)


class PeelFieldAdmin(object):
    pass


xadmin.site.register(PeelField, PeelFieldAdmin)

class CommodityAdmin(object):
    pass

xadmin.site.register(Commodity, CommodityAdmin)
 
class InvoiceAdmin(object):
    pass
xadmin.site.register(Invoice, InvoiceAdmin)


