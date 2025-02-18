import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib.auth.models import User, Group
from datetime import datetime
from .models import *
from master.models import *
from manufacturing.models import *
from django.core.paginator import Paginator
from user_profile.models import Profile

def staff_required(user) :
    return user.is_staff

def group_required(group_name) :
    def in_group(user) :
        return (user.is_authenticated and user.groups.filter(name=group_name).exists()) or user.is_superuser
    return user_passes_test(in_group)

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def overview(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    search_query = request.GET.get('search', '')

    stock = StockTotal.objects.using('inventory').all()

    if search_query :
        stock = [
            data for data in stock
            if (
                search_query.lower() in str(data.product.name).lower() or
                search_query.lower() in str(data.product.salesprice).lower() or
                search_query.lower() in str(data.stock).lower()
            )
        ]

    paginator = Paginator(stock, 20)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_inventory/overview.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_inventory/overview.html', {
        'feature' : 'Cant Add',
        'title_1' : 'Inventory',
        'title_2' : 'Inventory Overview',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(user_passes_test, login_url='/login/')
def receipt_list(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    search_query = request.GET.get('search', '')

    receipts = Receipt.objects.using('inventory').all()

    receipts_data = []

    for data in receipts :
        stock_move = StockMove.objects.using('inventory').get(id=int(data.stock_move.pk))
        warehouse = Warehouse.objects.using('inventory').get(id=int(stock_move.destination))
        company = Entity.objects.using('master').get(id=int(stock_move.company))
        stock_move.responsible = User.objects.using('default').get(id=int(stock_move.responsible)).username
        
        words = company.entity.split()

        if len(words) == 1 :
            company.entity = company.entity
        
        else :
            company.entity = ''.join([word[0] for word in words[:3]])

        receipts_data.append({
            'receipt' : data,
            'stock_move' : stock_move,
            'warehouse' : warehouse,
            'company' : company
        })

    if search_query :
        receipts_data = [
            data for data in receipts_data
            if (
                search_query.lower() in str(data['stock_move'].code).lower() or
                search_query.lower() in str(data['receipt'].status).lower() or
                search_query.lower() in str(data['company'].entity).lower() or
                search_query.lower() in str(data['stock_move'].destination.code).lower() or
                search_query.lower() in str(data['stock_move'].source).lower() or
                search_query.lower() in str(data['stock_move'].responsible).lower() or
                search_query.lower() in str(data['stock_move'].scheduled_date).lower() or
                search_query.lower() in str(data['stock_move'].files).lower()
            )
        ]
    
    paginator = Paginator(receipts_data, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_inventory/receipts.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_inventory/receipts.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Receipts',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def location_list(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    return render(request, 'pages_inventory/locations_list.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Locations',
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def storage_category_list(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    search_query = request.GET.get('search', '')

    storage_categories = StorageCategories.objects.using('inventory').all()
    
    storage_data = []

    for storage_category in storage_categories :
        company = Entity.objects.using('master').get(id=storage_category.company_id)

        storage_data.append({
            'storage_category' : storage_category,
            'company' : company
        })
    
    if search_query :
        storage_data = [
            data for data in storage_data
            if (
                search_query.lower() in str(data['company'].entity).lower() or
                search_query.lower() in str(data['storage_category'].allow_new_product).lower() or
                search_query.lower() in str(data['storage_category'].max_weight).lower()
            )
        ]
    
    paginator = Paginator(storage_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_inventory/storage_category_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_inventory/storage_category_list.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Storage Categories',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def product_list(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    search_query = request.GET.get('search', '')

    data = []

    stock = StockTotal.objects.using('inventory').all()
    
    for d in stock :
        product = Product.objects.using('inventory').get(id=int(d.product.pk))
        warehouse = Warehouse.objects.using('inventory').get(id=int(d.warehouse.pk))

        data.append({
            'product' : product,
            'stock' : d,
            'warehouse' : warehouse
        })


    if search_query :
        data = [
            d for d in data
            if (
                search_query.lower() in str(d['product'].name) or
                search_query.lower() in str(d['product'].sku) or
                search_query.lower() in str(d['warehouse'].warehouse)
            )
        ]

    paginator = Paginator(data, 20)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_inventory/product_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_inventory/product_list.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Products',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(user_passes_test, login_url='/login/')
def delivery_list(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    return render(request, 'pages_inventory/deliveries.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Deliveries',
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(user_passes_test, login_url='/login/')
def internal_transfers(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    search_query = request.GET.get('search', '')

    internal_transfer = InternalTransfer.objects.using('inventory').all()

    internal_data = []

    for t in internal_transfer :
        stock_move = StockMove.objects.using('inventory').get(id=t.stock_move.pk)
        stock_move.source = Warehouse.objects.using('inventory').get(id=int(stock_move.source))
        stock_move.destination = Warehouse.objects.using('inventory').get(id=int(stock_move.destination))
        stock_move.responsible = User.objects.using('default').get(id=int(stock_move.responsible))
        stock_company = Entity.objects.using('master').get(id=int(stock_move.company))
        words = stock_company.entity.split()
        
        if len(words) == 1 :
            stock_company.entity = stock_company.entity
        
        else :
            stock_company.entity = ''.join([word[0].upper() for word in words[:3]])

        internal_data.append({
            'internal_transfer' : t,
            'stock_move' : stock_move,
            'company' : stock_company
        })
    
    if search_query :
        internal_data = [
            data for data in internal_data
            if (
                search_query.lower() in str(data['internal_transfer'].status).lower() or
                search_query.lower() in str(data['internal_transfer'].url_tracking).lower() or
                search_query.lower() in str(data['stock_move'].code).lower() or
                search_query.lower() in str(data['stock_move'].source.warehouse.warehouse).lower() or
                search_query.lower() in str(data['stock_move'].responsible).lower()
            )
        ]

    paginator = Paginator(internal_data, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_inventory/internal.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_inventory/internal.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Internal Transfers',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(user_passes_test, login_url='/login/')
def manufacturings(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    search_query = request.GET.get('search', '')

    sos = StockMove.objects.using('inventory').filter(operation_type="Manufacture").all()

    data = []

    for so in sos :
        mo = ManufacturingOrders.objects.using('manufacturing').get(stock_move_id=so.pk)
        mo.responsible = User.objects.using('default').get(id=int(mo.responsible))
        mo.product = Product.objects.using('inventory').get(id=int(mo.product))
        mo.warehouse = Warehouse.objects.using('inventory').get(id=int(mo.warehouse))
        company = Entity.objects.using('master').get(id=int(so.company))

        words = company.entity.split()

        if len(words) == 1 :
            word = words
        else :
            word = ''.join([w[0] for w in words[:3]])

        if not mo.approved_by == 0 :
            mo.approved_by = User.objects.using('default').get(id=int(mo.approved_by))
        else :
            mo.approved_by = mo.approved_by
        
        status_data = []
        
        for d in mo.product_component :

            if StockTotal.objects.using('inventory').filter(product_id=int(d['product_id']), warehouse_id=int(d['warehouse_id'])).exists() :
                stock_on_hand = StockTotal.objects.using('inventory').get(product_id=int(d['product_id']), warehouse_id=int(d['warehouse_id'])).stock

                if int(d['product_quantity']) >= int(stock_on_hand) :
                    status = "Not Ready"
                elif int(d['product_quantity']) <= int(stock_on_hand) :
                    status = "Ready"

            else :
                status = "Not Ready"
            
            status_data.append({
                'status' : status
            })

            if all(s['status'] == 'Ready' for s in status_data) :
                final_status = "All Components Ready"
            elif all(s['status'] == 'Not Ready' for s in status_data) :
                final_status = "All Components Not Ready"
            elif any(s['status'] == 'Ready' for s in status_data) :
                final_status = "One or More Components Not Ready"

        data.append({
            'mo' : mo,
            'status' : final_status,
            'word' : word
        })

    if search_query :
        data = [
            d for d in data
            if (
                search_query.lower() in str(d['mo'].mo_number).lower() or
                search_query.lower() in str(d['mo'].start_date).lower() or
                search_query.lower() in str(d['mo'].responsible).lower() or
                search_query.lower() in str(d['status']).lower() or
                search_query.lower() in str(d['mo'].product.name).lower() or
                search_query.lower() in str(d['mo'].warehouse.code).lower()
            )
        ]
    
    paginator = Paginator(data,12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_inventory/manufacturings.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_inventory/manufacturings.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Manufacturing Orders',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(user_passes_test, login_url='/login/')
def inventory_adjusment(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    return render(request, 'pages_inventory/inventory_adjustment.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Inventory Adjustment',
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(user_passes_test, login_url='/login/')
def scrap(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    return render(request, 'pages_inventory/scrap.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Scrap',
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(user_passes_test, login_url='/login/')
def new_product(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    if request.method == 'POST' :
        product_name = request.POST['product_name']
        category_id = request.POST['category']
        desc = request.POST['internalnotes']
        price = request.POST['price']
        cost = request.POST['cost']
        type = request.POST['producttype']
        company_id = request.POST['companyname']
        reference_id = request.POST.get('reference')

        category = TypeProduct.objects.using('inventory').get(id=category_id)
        companyname = Entity.objects.using('master').get(id=company_id)

        #Cek apakah product sudah ada pada database

        if Product.objects.using('inventory').filter(name=product_name).exists() :
            return redirect('inventory:new_product')
        
        else :
            reference = None
            if reference_id :
                reference = BillofMaterials.objects.using('manufacturing').get(id=reference_id)

            new_product = Product.objects.using('inventory').create(
                name = product_name,
                category_type = category,
                description = desc,
                product_type = type,
                company_id = companyname.pk,
                salesprice = price if price else None,
                cost = cost if cost else None,
                reference_id = reference.pk if reference else None
            )
            
            new_product.save()
            return redirect('inventory:product_list')
    
    categories = TypeProduct.objects.using('inventory').all()
    references = BillofMaterials.objects.using('manufacturing').all()
    entities = Entity.objects.using('master').all()

    return render(request, 'new_inventory/new_product.html', {
        'feature' : 'Cant Add',
        'title_1' : 'Inventory',
        'title_2' : 'New Product',
        'categories' : categories,
        'references' : references,
        'entities' : entities,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(user_passes_test, login_url='/login/')
def new_category(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    if request.method == 'POST' :
        type_product = request.POST['category_name']
        desc = request.POST['internalnotes']

        #Check apakah inputan sama dengan yang ada pada database
        
        if TypeProduct.objects.using('inventory').filter(product_type=type_product).exists() :
                return redirect('inventory:new_categories')
        
        else :
            new_categories = TypeProduct.objects.using('inventory').create(
                product_type=type_product,
                description=desc
            )
            new_categories.save()
            return redirect('inventory:category_list')

    return render(request, 'new_inventory/new_categories.html', {
        'feature' : 'Cant Add',
        'title_1' : 'Inventory',
        'title_2' : 'New Product Category',
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def category_list(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    search_query = request.GET.get('search', '')


    categories = TypeProduct.objects.using('inventory').all().order_by('id')

    if search_query :
        categories = [
            data for data in categories
            if (
                search_query.lower() in str(data.product_type).lower()
            )
        ]
    
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_inventory/product_category.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_inventory/product_category.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Product Categories',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def detail_product(request, product_id):
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    product = Product.objects.using('inventory').get(id=product_id)
    categories = TypeProduct.objects.using('inventory').all()
    references = BillofMaterials.objects.using('manufacturing').all()
    entities = Entity.objects.using('master').all()

    if request.method == 'POST':
        metode = request.POST['metode']

        if metode == 'post' :
            product.name = request.POST.get('product_name', product.name)
            product.description = request.POST.get('internalnotes', product.description)
            product.salesprice = request.POST.get('price', product.salesprice)
            product.cost = request.POST.get('cost', product.cost)
            company_id = request.POST.get('companyname')
            category_id = request.POST.get('category')

            if company_id :
                product.company = Entity.objects.using('master').get(id=company_id).pk

            # Update category jika category_id diisi
            if category_id:
                product.category_type = TypeProduct.objects.using('inventory').get(id=category_id)

            # Update reference hanya jika diisi (bukan kosong)
            reference_id = request.POST.get('reference', None)
            if reference_id:
                product.reference_id = reference_id
            elif reference_id == "":  # Jika form reference dikosongkan
                product.reference_id = 0  # Set ke None jika nullable

            product.save()

            return redirect('inventory:product_list')
        
        elif metode == 'delete' :
            product.delete()

            return redirect('inventory:product_list')

    return render(request, 'detail_inventory/detail_product.html', {
        'feature': 'Cant Add',
        'product': product,
        'categories': categories,
        'title_2': product.sku,
        'references': references,
        'title_1': 'Inventory',
        'entities' : entities,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def detail_category(request, category_id) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    category = TypeProduct.objects.using('inventory').get(id=category_id)

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            category.product_type = request.POST.get('category_name', category.product_type)
            category.description = request.POST.get('internalnotes', category.description)
            
            category.save()

            return redirect('inventory:category_list')
        
        elif metode == 'delete' :

            category.delete()

            return redirect('inventory:category_list')
    
    return render(request, 'detail_inventory/detail_categories.html', {
        'title_1' : 'inventory',
        'feature' : 'Cant Add',
        'title_2' : category.code,
        'category' : category,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def warehouse_list(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    search_query = request.GET.get('search', '')

    warehouses = Warehouse.objects.using('inventory').all()

    warehouse_data = []

    for warehouse in warehouses :

        try:
            company = Entity.objects.using('master').get(id=warehouse.company)

        except Entity.DoesNotExist:
            company = None

        warehouse_data.append({
            'code' : warehouse.code,
            'id' : warehouse.pk,
            'location' : warehouse.location,
            'warehouse' : warehouse,
            'company' : company
        })

    if search_query :
        warehouse_data = [
            data for data in warehouse_data
            if (
                search_query.lower() in str(data['warehouse'].warehouse or '').lower() or
                search_query.lower() in str(data['warehouse'].location or '').lower() or
                search_query.lower() in str(data['warehouse'].company or '').lower() or
                search_query.lower() in str(data['warehouse'].code or '').lower()
            )
        ]

    paginator = Paginator(warehouse_data, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_inventory/warehouse.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_inventory/warehouse.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Warehouses',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def new_warehouse(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    entities = Entity.objects.using('master').all()
    if request.method == 'POST' :
        warehouse_name = request.POST['warehouse-name']
        location = request.POST['address']
        company = request.POST['company']
        short_name = request.POST['short-name']
        desc = request.POST['description']

        if short_name == '' :
            words = warehouse_name.split()

            if len(words) == 1 :
                short_name = warehouse_name[:3].upper()
            else :
                short_name = ''.join([word[0].upper() for word in words[:3]])

        else :
            short_name = short_name.upper()

        code = f"{short_name}W/Stock"

        if Warehouse.objects.using('inventory').filter(warehouse=warehouse_name).exists() :
            return redirect('inventory:new_warehouse')
        
        else :
            new_warehouse = Warehouse.objects.using('inventory').create(
                warehouse = warehouse_name,
                code = code,
                location = location,
                company = company,
                desc = desc
            )

            new_warehouse.save()
            return redirect('inventory:warehouse_list')

    return render(request, 'new_inventory/new_warehouse.html', {
        'title_1' : 'Inventory',
        'title_2' : 'New Warehouse',
        'feature' : 'Cant Add',
        'entities' : entities,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def detail_warehouse(request, warehouse_id) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    warehouse = Warehouse.objects.using('inventory').get(id=warehouse_id)
    warehouse.code = warehouse.code.split('/')[0][0:3]
    entities = Entity.objects.using('master').all()

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            short_name = request.POST['short-name']

            if short_name == '' :
                words = warehouse.warehouse.split()

                if len(words) == 1 :
                    short_name = warehouse.warehouse[:3].upper()

                else :
                    short_name = ''.join([word[0].upper() for word in words[:3]])

            else :
                short_name = short_name.upper()
            
            code = f"{short_name}W/Stock"

            warehouse.warehouse = request.POST.get('warehouse-name', warehouse.warehouse)
            warehouse.location = request.POST.get('address', warehouse.location)
            warehouse.company = request.POST.get('company', warehouse.company)
            warehouse.desc = request.POST.get('description', warehouse.desc)
            warehouse.code = code

            return redirect('inventory:warehouse_list')
        
        elif metode == 'delete' :
            warehouse.delete()

            return redirect('inventory:warehouse_list')

    return render(request, 'detail_inventory/detail_warehouse.html', {
        'title_1' : 'Inventory',
        'title_2' : warehouse.warehouse,
        'feature' : 'Cant Add',
        'warehouse' : warehouse,
        'entities' : entities,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def new_receipt(request):
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    warehouses = Warehouse.objects.using('inventory').all()
    companies = Entity.objects.using('master').all()
    products = Product.objects.using('inventory').all()
    respons = User.objects.using('default').filter(is_superuser=False, groups__name='Inventory').all()

    if request.method == 'POST':
        operation_type = "Receipt"
        source = request.POST['source']
        destination = request.POST['destination-warehouse']
        scheduled_date = request.POST['scheduled-date']
        files = request.FILES['document']
        res_id = request.POST['responsible']
        company = request.POST['company']
        notes = request.POST['internalnotes']
        product = request.POST.getlist('products[]')
        product_quantity = request.POST.getlist('product-quantity[]')

        responsible = User.objects.using('default').get(id=int(res_id))

        file_name = None

        if files :
            file_name = default_storage.save(files.name, files)
            file_url = default_storage.url(file_name)

        warehouse = Warehouse.objects.using('inventory').get(id=int(destination))
        date = datetime.strptime(scheduled_date, '%d/%m/%Y')
        date_obj = date.strftime('%Y-%m-%d')

        wr_code = warehouse.code
        monthnow = datetime.now().strftime('%m')
        yearnow = datetime.now().strftime('%Y')
        last_receipt = StockMove.objects.using('inventory').filter(
            operation_type=operation_type, 
            source=source, 
            destination=destination
        ).count()

        # Buat kode baru dengan format yang sesuai
        new_code = f"{operation_type}/{wr_code}-{monthnow}-{yearnow}-{last_receipt:02d}"

        # Jika kode sudah ada, increment last_receipt
        while StockMove.objects.using('inventory').filter(code=new_code).exists():
            last_receipt += 1
            new_code = f"{operation_type}/{wr_code}-{monthnow}-{yearnow}-{last_receipt:02d}"

        product_json = json.dumps(product)
        product_quantity_json = json.dumps(product_quantity)

        # Simpan StockMove baru
        new_receipt = StockMove.objects.using('inventory').create(
            code=new_code,
            operation_type=operation_type,
            source=source,
            destination=str(warehouse.pk),
            scheduled_date=date_obj,
            files=file_name if file_name else 'Doesnt Exists',
            responsible=responsible.pk,
            company=company,
            notes=notes,
            products=product_json,
            product_quantities=product_quantity_json
        )

        product_data = []

        for prd, qty in zip(product, product_quantity) :
            product_id = Product.objects.using('inventory').get(id=int(prd))
            quantity = int(qty)
            product_data.append({
                'product' : product_id.pk,
                'quantity' : quantity,
                'warehouse' : warehouse.pk,
                'status' : 'draft'
            })

        print(product_data)

        new_data = Receipt.objects.using('inventory').create(
            product=product_data,
            status='draft',
            stock_move=new_receipt
        )

        return redirect('inventory:receipts_list')

    return render(request, 'new_inventory/new_receipt.html', {
        'title_1': 'Inventory',
        'title_2': 'New Receipt',
        'feature': 'Cant Add',
        'warehouses': warehouses,
        'companies': companies,
        'products': products,
        'profile' : profile,
        'respons' : respons
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def new_location(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    companies = Entity.objects.using('master').all()
    products = Product.objects.using('inventory').all()

    return render(request, 'new_inventory/new_location.html', {
        'title_1' : 'Inventory',
        'title_2' : 'New Location',
        'feature' : 'Cant Add',
        'products' : products,
        'companies' : companies,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def new_storage_category(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))
    products = Product.objects.using('inventory').all()
    companies = Entity.objects.using('master').all()

    if request.method == 'POST' :
        name = request.POST['source']
        allow_q = request.POST['allow-new-product']
        max_weight = request.POST['max-weight']
        company_id = request.POST['company']
        product_ids = request.POST.getlist('products[]')
        product_quantities = request.POST.getlist('product-quantities[]')

        json_product = json.dumps(product_ids)
        json_product_quantities = json.dumps(product_quantities)

        new_storage_category = StorageCategories.objects.using('inventory').create(
            name=name,
            allow_new_product=allow_q,
            max_weight=max_weight,
            company_id=company_id,
            products=json_product,
            quantity=json_product_quantities
        )
        new_storage_category.save()

        return redirect('inventory:storage_category_list')

    return render(request, 'new_inventory/new_storage_category.html', {
        'title_1' : 'Inventory',
        'title_2' : 'New Storage Category',
        'feature' : 'Cant Add',
        'products' : products,
        'companies' : companies,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def detail_storage_category(request, storage_category_id) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))
    sc = StorageCategories.objects.using('inventory').get(id=storage_category_id)
    company = Entity.objects.using('master').all()
    products = Product.objects.using('inventory').all()

    storage_data = []

    for product, quantity in zip(json.loads(sc.products), json.loads(sc.quantity)) :
        product = Product.objects.using('inventory').get(id=int(product))
        quantity = int(quantity)

        storage_data.append({
            'product' : product,
            'quantity' : quantity
        })

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            sc.name = request.POST.get('source', sc.name)
            sc.allow_new_product = request.POST.get('allow-new-product', sc.allow_new_product)
            sc.max_weight = request.POST.get('max-weight', sc.max_weight)
            company_id = request.POST.get('company', sc.company_id)
            product_data = request.POST.getlist('products[]')
            quantitities = request.POST.getlist('product-quantities[]')

            if company_id :
                sc.company_id = Entity.objects.using('master').get(id=company_id).pk

            json_products = json.dumps(product_data)
            json_quantities = json.dumps(quantitities)

            sc.products = json_products
            sc.quantity = json_quantities

            sc.save()
            return redirect('inventory:storage_category_list')
        
        elif metode == 'delete' :
            sc.delete()
            return redirect('inventory:storage_category_list')
        
    return render(request, 'detail_inventory/detail_storage_category.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Detail Storage Category',
        'feature' : 'Cant Add',
        'storage_data' : storage_data,
        'storage_category' : sc,
        'companies' : company,
        'products' : products,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def new_internal_transfer(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))
    warehouses = Warehouse.objects.using('inventory').all()
    products = Product.objects.using('inventory').all()
    companies = Entity.objects.using('master').all()
    transport = ShippingService.objects.using('master').all()
    respons = User.objects.using('default').filter(is_superuser=False, groups__name='Inventory').all()

    if request.method == 'POST' :
        operation_type = "Internal Transfer"
        source_wr = request.POST['source-warehouse']
        destination_wr = request.POST['destination-warehouse']
        scheduled_date = request.POST['scheduled-date']
        files = request.FILES['documents']
        product_ids = request.POST.getlist('products[]')
        components = request.POST.getlist('product-quantity[]')
        res_id = request.POST['responsible']
        company = request.POST['company']
        notes = request.POST['internalnotes']
        shipping_service = request.POST['shipping-service']
        url_tracking = request.POST['url-tracking']

        source_id = Warehouse.objects.using('inventory').get(id=int(source_wr))
        destination_id = Warehouse.objects.using('inventory').get(id=int(destination_wr))

        date_value = datetime.strptime(scheduled_date, '%d/%m/%Y')
        date_value_2 = date_value.strftime('%Y-%m-%d')

        responsible = User.objects.using('default').get(id=int(res_id))

        file_name = None

        if files :
            file_name = default_storage.save(files.name, files)
            file_url = default_storage.url(file_name)

        company_id = Entity.objects.using('master').get(id=int(company))

        def generate_code(source_id, operation_type) :
            wr_code = source_id.code
            month_now = datetime.now().strftime('%m')
            year_now = datetime.now().strftime('%Y')
            last_internal_transfer = StockMove.objects.using('inventory').filter(
                operation_type=operation_type,
                source=source_id,
                destination=destination_id
            ).count()

            operation_type_code = "Internal-Transfer"

            new_code = f"{operation_type_code}/{wr_code}-{month_now}-{year_now}-{last_internal_transfer:02d}"
        
            while StockMove.objects.using('inventory').filter(code=new_code).exists() :
                last_internal_transfer += 1
                new_code = f"{operation_type_code}/{wr_code}-{month_now}-{year_now}-{last_internal_transfer:02d}"

            return new_code

        new_code = generate_code(source_id, operation_type)

        product_json = json.dumps(product_ids)
        product_quantity_json = json.dumps(components)

        new_move = StockMove.objects.using('inventory').create(
            code=new_code,
            operation_type=operation_type,
            source=source_id.pk,
            destination=str(destination_id.pk),
            scheduled_date=date_value_2,
            files=file_name if file_name else 'Doesnt Exists',
            responsible=responsible.pk,
            company=company_id.pk,
            notes=notes,
            products=product_json,
            product_quantities=product_quantity_json
        )
        new_move.save()
        
        component_data = []
        for product, quantities in zip(json.loads(new_move.products), json.loads(new_move.product_quantities)) :
            product_id = Product.objects.using('inventory').get(id=int(product))
            qtys = int(quantities)

            component_data.append({
                'product' : int(product_id.pk),
                'quantity' : int(qtys),
                'status' : "waiting"
            })

        new_it = InternalTransfer.objects.using('inventory').create(
            stock_move=new_move,
            product=component_data,
            status="waiting",
            shipping_service=shipping_service,
            url_tracking=url_tracking
        )

        return redirect('inventory:internal_transfers')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        service_type = request.GET.get('service_type')
        services = ShippingService.objects.using('master').filter(service_type=service_type)

        service_list = list(services.values('id', 'name'))
        return JsonResponse({
            'services' : service_list
        })

    return render(request, 'new_inventory/new_internal_transfer.html', {
        'title_1' : "Inventory",
        'title_2' : "New Internal Transfer",
        'feature' : "Cant Add",
        'warehouses' : warehouses,
        'companies' : companies,
        'products' : products,
        'transport' : transport,
        'profile' : profile,
        'respons' : respons
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def detail_internal_transfer(request, st_id):
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))
    data = []
    stock_move = StockMove.objects.using('inventory').get(id=st_id)
    destination_w = Warehouse.objects.using('inventory').get(id=int(stock_move.destination))
    source_warehouse = Warehouse.objects.using('inventory').get(id=int(stock_move.source))
    company = Entity.objects.using('master').get(id=int(stock_move.company))
    internal_transfers = InternalTransfer.objects.using('inventory').get(stock_move_id=stock_move.pk)
    shipping_service = ShippingService.objects.using('master').get(id=internal_transfers.shipping_service)

    stock_move.scheduled_date = datetime.strftime(stock_move.scheduled_date, '%d/%m/%Y')
    stock_move.responsible = User.objects.using('default').get(id=int(stock_move.responsible))

    data_r = []

    for c in internal_transfers.product :
        stock = StockTotal.objects.using('inventory').get(product=int(c['product']), warehouse=int(stock_move.source))
        if int(c['quantity']) >= stock.stock :
            status_r = 'ready'
        else :
            status_r = 'not ready'
        
        data_r.append({
            'status' : status_r
        })

    if all(f['status'] == 'ready' for f in data_r) :
        internal_transfers.status = 'ready'
        internal_transfers.save()
    else :
        internal_transfers.status = 'waiting'
        internal_transfers.save()
    
    component_data = []
    for prd, qty in zip(json.loads(stock_move.products), json.loads(stock_move.product_quantities)) :
        product = Product.objects.using('inventory').get(id=int(prd))
        quantity = int(qty)
        component_data.append({
            'product' : product,
            'quantity' : quantity
        })
    
    transfer_component = []
    for d in internal_transfers.product :
        component = Product.objects.using('inventory').get(id=int(d['product']))
        component_quantity = int(d['quantity'])
        status = d['status']
        transfer_component.append({
            'product' : component,
            'quantity' : component_quantity,
            'status' : status
        })

    if stock_move.files :
        ext = os.path.splitext(stock_move.files.name)[1].lower()
        if ext in ['.jpg', '.png', '.jpeg', '.webp', '.svg', '.gif', '.bmp', '.tiff', '.heif', '.heic', '.ico'] :
            file_type = 'image'
        elif ext == '.pdf' :
            file_type = 'pdf'
        else :
            file_type = None
    
    data.append({
        'stock_move' : stock_move,
        'destination_w' : destination_w,
        'source' : source_warehouse,
        'company' : company,
        'transfer_component' : transfer_component,
        'components' : component_data,
        'shipping' : shipping_service,
        'internal_transfer' : internal_transfers,
        'file_type' : file_type
    })

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'update' :
            product_id = request.POST['product_id']
            product_quantity = request.POST['product_quantity']
            status = request.POST['status']
            source = request.POST.get('source_warehouse')
            destination = request.POST['destination_warehouse']

            # Cutting Source Stock
            cutt = StockTotal.objects.using('inventory').get(warehouse_id=int(source), product_id=int(product_id))
            stock_now = cutt.stock
            stock_update = stock_now - int(product_quantity)
            cutt.stock = stock_update
            cutt.save()

            #Append Destination Stock
            stock_u, created = StockTotal.objects.using('inventory').get_or_create(
                warehouse_id=destination,
                product_id=product_id,
                stock=int(product_quantity)
            )

            if not created :
                stock_u.stock = stock_u.stock + int(product_quantity)

                stock_u.save()

            #Update Internal Transfer
            for r in internal_transfers.product :
                if r['product'] == int(product_id) and r['quantity'] == int(product_quantity) :
                    r['status'] = status
                    internal_transfers.save()

            if all(p['status'] == 'done' for p in internal_transfers.product) :
                internal_transfers.status = 'done'
                internal_transfers.save()
            elif all(p['status'] == 'waiting' for p in internal_transfers.product) :
                internal_transfers.status = 'waiting'
                internal_transfers.save()
            elif all(p['product_quantity'] <= stock_now for p in internal_transfers.product) :
                internal_transfers.status = 'ready'
                internal_transfers.save()

    return render(request, 'detail_inventory/detail_internal_transfer.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Detail Internal Transfer',
        'feature' : 'Cant Add',
        'datas' : data,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def shipping_list(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))
    search_query = request.GET.get('search', '')

    shipping = ShippingService.objects.using('master').all()

    if search_query :
        shipping = [
            data for data in shipping
            if (
                search_query.lower() in str(data.name).lower() or
                search_query.lower() in str(data.contact_admin).lower() or
                search_query.lower() in str(data.website).lower() or 
                search_query.lower() in str(data.service_type).lower()
            )
        ]

    paginator = Paginator(shipping, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_inventory/shipping_list.html', {
            'page_obj' : page_obj
        })
    
    return render(request, 'pages_inventory/shipping_list.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Shipping List',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def new_shipping(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))
    if request.method == 'POST' :
        name = request.POST['service-name']
        category = request.POST['category']
        website = request.POST['website']
        contact = request.POST['contact-admin']
        desc = request.POST['desc']

        new_service = ShippingService.objects.using('master').create(
            name=name,
            service_type=category,
            website=website,
            contact_admin=contact,
            desc=desc
        )
        new_service.save()
        
        return redirect('inventory:shipping_list')
    
    return render(request, 'new_inventory/new_shipping.html', {
        'title_1' : 'Inventory',
        'title_2' : 'New Courier',
        'feature' : 'Cant Add',
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def new_delivery(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))
    data = []

    warehouse = Warehouse.objects.using('inventory').all()
    product = Product.objects.using('inventory').all()
    company = Entity.objects.using('master').all()

    data.append({
        'warehouse' : warehouse,
        'product' : product,
        'company' : company
    })

    if request.method == 'POST' :
        operation_type = 'Delivery Order'
        source = request.POST['source-warehouse']
        destination = request.POST['destination']
        scheduled_date = request.POST['scheduled-date']
        files = request.FILES['documents']
        responsible = request.POST['responsible']
        company_id = request.POST['company']
        notes = request.POST['internalnotes']
        product_list = request.POST.getlist('products[]')
        quantity_list = request.POST.getlist('product-quantity[]')
        shipping_service = request.POST['shipping-service']
        url_tracking = request.POST['url-tracking']

        source_warehouse = Warehouse.objects.using('inventory').get(id=int(source))
        company = Entity.objects.using('master').get(id=int(company_id))

        date_value = datetime.strptime(scheduled_date, '%d/%m/%Y')
        date_obj = date_value.strftime('%Y-%m-%d')

        file_name = None
        
        if files :
            file_name = default_storage.save(files.name, files)
            file_url = default_storage.url(file_name)

        def generate_code(source_id, operation_type) :
            wr_code = source_id.code
            month_now = datetime.now().strftime('%m')
            year_now = datetime.now().strftime('%Y')
            last_delivery = StockMove.objects.using('inventory').filter(
                operation_type=operation_type,
                source=source_id,
                destination=destination
            ).count()

            operation_type_code = "Delivery-Order"

            new_code = f"{operation_type_code}/{wr_code}-{month_now}-{year_now}-{last_delivery:02d}"

            while StockMove.objects.using('inventory').filter(code=new_code).exists() :
                last_delivery += 1
                new_code = f"{operation_type_code}/{wr_code}-{month_now}-{year_now}-{last_delivery:02d}"

            return new_code
        
        new_code = generate_code(source_warehouse, operation_type)

        product_json = json.dumps(product_list)
        quantity_json = json.dumps(quantity_list)

        new_move = StockMove.objects.using('inventory').create(
            code=new_code,
            operation_type=operation_type,
            source=source_warehouse.pk,
            destination=destination,
            scheduled_date=date_obj,
            files=file_name if file_name else 'Doesnt Exists',
            responsible=responsible,
            company=company.pk,
            notes=notes,
            products=product_json,
            product_quantities=quantity_json
        )
        new_move.save()

        component_data = []
        for product, quantities in zip(json.loads(new_move.products), json.loads(new_move.product_quantities)) :
            product_id = Product.objects.using('inventory').get(id=int(product))
            warehouse = Warehouse.objects.using('inventory').get(id=int(source))

            qtys = int(quantities)

            stock = StockTotal.objects.using('inventory').get(warehouse=warehouse.pk, product=product_id.pk)

            if qtys >= stock.stock :
                status = "waiting"
            elif qtys <= stock.stock :
                status = "ready"

            component_data.append({
                'product' : int(product_id.pk),
                'quantity' : int(qtys),
                'status' : status
            })

        if all(s['status'] == 'ready' for s in component_data) :
            status_2 = 'ready'
        elif all(s['status'] == 'waiting' for s in component_data) :
            status_2 = 'waiting'
        else :
            status_2 = 'waiting'

        new_do = DeliveryOrder.objects.using('inventory').create(
            stock_move=new_move,
            product=component_data,
            status=status_2,
            shipping_service=shipping_service,
            url_tracking=url_tracking
        )
        new_do.save()

        return redirect('inventory:delivery_list')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        service_type = request.GET.get('service_type')
        services = ShippingService.objects.using('master').filter(service_type=service_type)

        service_list = list(services.values('id', 'name'))
        return JsonResponse({
            'services' : service_list
        })

    return render(request, 'new_inventory/new_delivery.html', {
        'title_1' : 'Inventory',
        'title_2' : 'New Delivery',
        'feature' : 'Cant Add',
        'data' : data,
        'profile' : profile
    })

@login_required
@group_required('Inventory')
@user_passes_test(staff_required, login_url='/login/')
def detail_receipt(request, receipt_id) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    data = []

    stock_move = StockMove.objects.using('inventory').get(id=int(receipt_id))
    receipt = Receipt.objects.using('inventory').get(stock_move=int(stock_move.pk))
    company = Entity.objects.using('master').get(id=int(stock_move.company))
    warehouse = Warehouse.objects.using('inventory').get(id=int(stock_move.destination))

    stock_move.scheduled_date = stock_move.scheduled_date.strftime('%Y/%m/%d')
    stock_move.responsible = User.objects.using('default').get(id=int(stock_move.responsible))

    component = []

    for d in receipt.product :
        product = Product.objects.using('inventory').get(id=int(d['product']))
        warehouses = Warehouse.objects.using('inventory').get(id=int(d['warehouse']))
        status = d['status']
        component.append({
            'product' : product,
            'quantity' : int(d['quantity']),
            'warehouse' : warehouses,
            'status' : status
        })

    data.append({
        'stock_move' : stock_move,
        'receipt' : receipt,
        'company' : company,
        'warehouse' : warehouse,
        'component' : component
    })

    if all(s['status'] == 'done' for s in receipt.product) :
        receipt.status = 'done'
        receipt.save()
    elif all(s['status'] == 'draft' for s in receipt.product) :
        receipt.status = 'draft'
        receipt.save()
    else :
        receipt.status = 'ready'
        receipt.save()

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'update' :
            product_id = request.POST['product_id']
            product_quantity = request.POST['product_quantity']
            destination = request.POST['destination_warehouse']
            status = request.POST['status']
            
            product_d = Product.objects.using('inventory').get(id=int(product_id))
            warehouse_d = Warehouse.objects.using('inventory').get(id=int(destination))
            #Sum the Destination Stock
            up, created = StockTotal.objects.using('inventory').get_or_create(
                warehouse=warehouse_d, 
                product=product_d,
                defaults={'stock' : int(product_quantity)}
                )
            
            if not created :
                stock_now = up.stock
                stock_update = stock_now + int(product_quantity)
                up.stock = stock_update
                up.save()

            for r in receipt.product :
                if r['product'] == int(product_id) and r['quantity'] == int(product_quantity) :
                    r['status'] = status
                    receipt.save()

            if all(s['status'] == 'done' for s in receipt.product) :
                receipt.status = 'done'
                receipt.save()
            elif all(s['status'] == 'draft' for s in receipt.product) :
                receipt.status = 'draft'
                receipt.save()
            else :
                receipt.status = 'ready'
                receipt.save()

            print(receipt.product)
    
    return render(request, 'detail_inventory/detail_receipt.html', {
        'title_1' : 'Inventory',
        'title_2' : 'Detail Receipt',
        'feature' : 'Cant Add',
        'data' : data,
        'profile' : profile
    })