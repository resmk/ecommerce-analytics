
# Register your models here.
from django.contrib import admin
from .models import DimCustomer, DimProduct, DimTime, FactOrder

admin.site.register(DimCustomer)
admin.site.register(DimProduct)
admin.site.register(DimTime)
admin.site.register(FactOrder)
