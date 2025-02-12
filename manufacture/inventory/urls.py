from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'inventory'

urlpatterns = [

    #Pages untuk list
    path('manufacture/inventory/', views.overview, name='overview'),
    path('manufacture/inventory/receipts/', views.receipt_list, name='receipts_list'),
    path('manufacture/inventory/list-product/', views.product_list, name='product_list'),
    path('manufacture/inventory/list-delivery/', views.delivery_list, name='delivery_list'),
    path('manufacture/inventory/internal-transfers/', views.internal_transfers, name='internal_transfers'),
    path('manufacture/inventory/manufacturings/', views.manufacturings, name='manufacturings'),
    path('manufacture/inventory/inventory-adjustment/', views.inventory_adjusment, name='inventory_adjustment'),
    path('manufacture/inventory/category-list/', views.category_list, name='category_list'),
    path('manufacture/inventory/scrap/', views.scrap, name='scrap'),
    path('manufacture/inventory/warehouse/', views.warehouse_list, name='warehouse_list'),
    path('manufacture/inventory/location/', views.location_list, name='location_list'),
    path('manufacture/inventory/storage-categories/', views.storage_category_list, name='storage_category_list'),
    path('manufacture/inventory/shipping-list/', views.shipping_list, name='shipping_list'),

    #Pages untuk penambahan Data
    path('manufacture/inventory/new-product/', views.new_product, name='new_product'),
    path('manufacture/inventory/new-category/', views.new_category, name='new_categories'),
    path('manufacture/inventory/new-warehouse/', views.new_warehouse, name='new_warehouse'),
    path('manufacture/inventory/new-receipt/', views.new_receipt, name='new_receipt'),
    path('manufacture/inventory/new-location/', views.new_location, name='new_location'),
    path('manufacture/inventory/new-storage-category/', views.new_storage_category, name='new_storage_category'),
    path('manufacture/inventory/new-internal-transfer/', views.new_internal_transfer, name='new_internal_transfer'),
    path('manufacture/inventory/new-shippping/', views.new_shipping, name='new_shipping'),
    path('manufacture/inventory/new-delivery/', views.new_delivery, name='new_delivery'),

    #Pages untuk Edit
    path('manufacture/inventory/detail-product/<int:product_id>/', views.detail_product, name='detail_product'),
    path('manufacture/inventory/detail-category/<int:category_id>/', views.detail_category, name='detail_category'),
    path('manufacture/inventory/detail-warehouse/<int:warehouse_id>/', views.detail_warehouse, name='detail_warehouse'),
    path('manufacture/inventory/detail-storage-category/<int:storage_category_id>/', views.detail_storage_category, name='detail_storage_category'),
    path('manufacture/inventory/detail-internal-transfer/<int:st_id>/', views.detail_internal_transfer, name='detail_internal_transfer'),
    path('manufacture/inventory/detail-receipt/<int:receipt_id>/', views.detail_receipt, name='detail_receipt'),
    
]

if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)