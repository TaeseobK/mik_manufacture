from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'manufacture'

urlpatterns = [
    #Pages Manufacture
    path('manufacture/', views.home, name='home'),
    path('manufacture/manufacturing-orders/', views.manufacturing_orders, name='manufacturing_orders'),
    path('manufacture/unbuild-orders/', views.unbuild_orders, name='unbuild_orders'),
    path('manufacture/scrap-orders/', views.scrap_orders, name='scrap_orders'),
    path('manufacture/product/', views.product_list, name='product_list'),
    path('manufacture/bom-list/', views.list_bom, name='bom_list'),

    #New Pages
    path('manufacture/new-mo/', views.new_mo, name='new_manufacturing_orders'),
    path('manufacture/new-bom/', views.new_bom, name='new_bom'),

    #Pages Detail
    path('manufacture/manufacture/bom/<int:bom_id>/', views.detail_bom, name='detail_bom'),
    path('manufacture/manufacture/mo/<int:mo_id>/', views.detail_mo, name='detail_mo'),
]

if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)