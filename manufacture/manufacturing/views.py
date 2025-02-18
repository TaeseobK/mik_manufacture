import json
import os
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from inventory.models import *
from django.core.files.storage import default_storage
from master.models import *
from .models import *
from user_profile.models import *
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.models import User, Group

def staff_required(user) :
    return user.is_staff

def group_required(group_name) :
    def in_group(user) :
        return (user.is_authenticated and user.groups.filter(name=group_name).exists()) or user.is_superuser
    return user_passes_test(in_group)

@login_required
@user_passes_test(staff_required, login_url='/login/')
def home(request) :
    user = request.user
    profiles = Profile.objects.using('profile').get(user=int(user.pk))
    user_group = user.groups.all()

    groups = []

    for data in user_group :
        groups.append({
            'name' : data.name
        })

    return render(request, 'pages_manufacture/home.html', {
        'title' : 'manufacturing',
        'title_1' : 'Home',
        'feature' : 'Cant Add',
        'profile' : profiles,
        'user' : user,
        'groups' : groups
    })

@login_required
@group_required('Manufacture')
@user_passes_test(staff_required, login_url='login/')
def manufacturing_orders(request) :
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
        return render(request, 'pages_manufacture/manufacturing_orders.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_manufacture/manufacturing_orders.html', {
        'title_1' : 'Manufacture',
        'title_2' : 'Manufacturing Orders',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Manufacture')
@user_passes_test(staff_required, login_url='login/')
def unbuild_orders(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    return render(request, 'pages_manufacture/unbuild_orders.html', {
        'title_1' : 'Manufacture',
        'title_2' : 'Unbuild Orders',
        'profile' : profile
    })

@login_required
@group_required('Manufacture')
@user_passes_test(staff_required, login_url='login/')
def scrap_orders(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    return render(request, 'pages_manufacture/scrap_orders.html', {
        'title_1' : 'Manufacture',
        'title_2' : 'Scrap Orders',
        'profile' : profile
    })

@login_required
@group_required('Manufacture')
@user_passes_test(staff_required, login_url='login/')
def new_mo(request):
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    products = Product.objects.using('inventory').all()
    boms = BillofMaterials.objects.using('manufacturing').filter(bom_type="Manufacture This Product")
    companies = Entity.objects.using('master').all()
    warehouses = Warehouse.objects.using('inventory').all()
    respons = User.objects.using('default').filter(is_superuser=False, groups__name='Manufacture')

    bom_product_name = []

    for bom in boms :
        bom=bom
        product_id = Product.objects.using('inventory').get(id=int(bom.product_id))
        bom_product_name.append({
            'bom' : bom,
            'product_id' : product_id
        })

    if request.method == 'POST' :

        #for Manufacturing Orders
        product_id_post = request.POST['products']
        scheduled_date = request.POST['scheduled-date']
        quantity_bom = request.POST['quantity-bom']
        res_id = request.POST['responsible']
        bom_number = request.POST['bom']

        responsible = User.objects.using('default').get(id=int(res_id))

        #for StockMove
        operation_type = "Manufacture"
        source_warehouse = request.POST['component-location']
        destination_warehouse = request.POST['finish-product']
        document = request.FILES['source-document']
        company = request.POST['company']
        internal_notes = request.POST['notes']

        destination_wr = Warehouse.objects.using('inventory').get(id=int(destination_warehouse))
        source_wr = Warehouse.objects.using('inventory').get(id=int(source_warehouse))

        file_name = default_storage.save(document.name, document)
        file = default_storage.open(file_name)
        file_url = default_storage.url(file_name)

        warehouse = Warehouse.objects.using('inventory').get(id=int(source_warehouse))
        year_now = datetime.now().strftime('%Y')
        month_now = datetime.now().strftime('%m')
        last_mo = ManufacturingOrders.objects.using('manufacturing').filter(
            warehouse=source_warehouse
        ).count()

        mo_code = f"MO/{year_now}/{month_now}/{warehouse.code}/{last_mo:03d}"
        while ManufacturingOrders.objects.using('manufacturing').filter(mo_number=mo_code).exists() :
            last_mo += 1
            mo_code = f"MO/{year_now}/{month_now}/{warehouse.code}/{last_mo:03d}"
        

        bom = BillofMaterials.objects.using('manufacturing').get(id=int(bom_number))

        component_list = []
        product_ids = []
        product_quantities = []

        for product_id, quantity, warehouse_id in zip(bom.component, bom.quantity, bom.warehouse) :
            product = Product.objects.using('inventory').get(id=int(product_id))
            warehouse = Warehouse.objects.using('inventory').get(id=int(warehouse_id))
            component_data = {
                'product_id' : product.pk,
                'product_name' : product.name,
                'warehouse_id' : warehouse.pk,
                'product_cost' : float(product.cost) * float(quantity_bom),
                'product_price' : float(product.salesprice) * float(quantity_bom),
                'product_quantity' : float(quantity) * float(quantity_bom),
                'status' : "draft"
            }
            component_list.append(component_data)
            product_ids.append(str(product.pk))
            product_quantities.append(str(float(quantity) * float(quantity_bom)))

        wr = Warehouse.objects.using('inventory').get(id=int(destination_warehouse))
        last_manufacture = StockMove.objects.using('inventory').filter(
            operation_type=operation_type,
            source=source_warehouse,
            destination=destination_warehouse
        ).count()
        
        move_code = mo_code

        new_mo = ManufacturingOrders.objects.using('manufacturing').create(
            mo_number=mo_code,
            product=product_id_post,
            bom_number=bom_number,
            quantity=quantity_bom,
            status="draft",
            responsible=responsible.pk,
            product_component=component_list,
            start_date=scheduled_date,
            warehouse=str(source_warehouse),
            approved_by=0,
            stock_move_id=0
        )
        new_mo.save()

        new_stockmove = StockMove.objects.using('inventory').create(
            code=move_code,
            operation_type=operation_type,
            source=str(source_wr.pk),
            destination=destination_wr.pk,
            scheduled_date=scheduled_date,
            files=file_name if file_name else 'Doesnt Exists',
            responsible=responsible.pk,
            company=company,
            notes=internal_notes,
            products=json.dumps(product_ids),
            product_quantities=json.dumps(product_quantities)
        )
        new_stockmove.save()
        
        stock_move_pk = StockMove.objects.using('inventory').get(code=move_code).pk
        new_mo.stock_move_id = stock_move_pk
        new_mo.save()

        return redirect('manufacture:manufacturing_orders')

    return render(request, 'manufacture_new/new_mo.html', {
        'title_1': 'manufacturing',
        'title_2': 'New Manufacturing Orders',
        'feature': 'Cant Add',
        'products': products,
        'boms': bom_product_name,
        'companies' : companies,
        'warehouses' : warehouses,
        'profile' : profile,
        'respons' : respons
    })

@login_required
@group_required('Manufacture')
@user_passes_test(staff_required, login_url='login/')
def product_list(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    search_query = request.GET.get('search', '')

    products = Product.objects.using('inventory').all()

    product_data = []

    for product in products :
        stock_total = StockTotal.objects.using('inventory').filter(product=product)
        on_hand = stock_total.first().stock if stock_total.exists() else 0

        product_data.append({
            'product' : product,
            'stock' : int(on_hand)
        })
    
    if search_query :
        product_data = [
            data for data in product_data
            if (
                search_query.lower() in str(data['product'].name).lower() or
                search_query.lower() in str(data['product'].sku).lower() or
                search_query.lower() in str(data['product'].product_type).lower()
            )
        ]

    paginator = Paginator(product_data, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_manufacture/product_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_manufacture/product_list.html', {
        'title_1' : 'Manufacture',
        'title_2' : 'Product List',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Manufacture')
@user_passes_test(staff_required, login_url='/login/')
def list_bom(request):
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    search_query = request.GET.get('search', '')

    boms = BillofMaterials.objects.using('manufacturing').all()

    bom_data = []

    for bom in boms:
        try:
            product = Product.objects.using('inventory').get(id=bom.product_id)
        except Product.DoesNotExist:
            product = None

        # Append bom and product data for each iteration
        bom_data.append({
            'bom': bom,
            'product': product
        })

    if search_query :
        bom_data = [
            data for data in bom_data
            if (
                search_query.lower() in str(data['product'].name).lower() or
                search_query.lower() in str(data['bom'].bom).lower() or
                search_query.lower() in str(data['bom'].bom_type).lower() or
                search_query.lower() in str(data['product'].company_id).lower()
            )
        ]

    paginator = Paginator(bom_data, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_manufacture/bom_list.html', {
            'page_obj' : page_obj
        })
    
    return render(request, 'pages_manufacture/bom_list.html', {
        'title_1': 'Manufacturing',
        'title_2': 'Bill of Materials',
        'page_obj': page_obj,
        'profile' : profile
    })

@login_required
@group_required('Manufacture')
@user_passes_test(staff_required, login_url='/login/')
def new_bom(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    products = Product.objects.using('inventory').all()
    warehoses = Warehouse.objects.using('inventory').all()

    if request.method == 'POST' :
        id_product = request.POST['products']
        bom_type = request.POST['bom_type']
        components = request.POST.getlist('components[]')
        quantities = request.POST.getlist('components_quantity[]')
        warehouses = request.POST.getlist('components_warehouse[]')

        last_bom = BillofMaterials.objects.using('manufacturing').order_by('id').last()
        if last_bom :
            last_bom_id = last_bom.id
        else :
            last_bom_id = 0

        current_year = datetime.now().strftime('%Y')
        current_month = datetime.now().strftime('%m')

        bom_number = f"BOM/{current_year}/{current_month}/{id_product}/{last_bom_id + 1:02d}"

        new_bom = BillofMaterials.objects.using('manufacturing').create(
            bom = bom_number,
            product_id = id_product,
            component = components,
            quantity = quantities,
            bom_type = bom_type,
            warehouse = warehouses
        )

        new_bom.save()

        return redirect('manufacture:bom_list')

    return render(request, 'manufacture_new/new_bom.html', {
        'title_1' : 'Manufacture',
        'feature' : 'Cant Add',
        'title_2' : 'New BOM',
        'products' : products,
        'warehouses' : warehoses,
        'profile' : profile
    })

@login_required
@group_required('Manufacture')
@user_passes_test(staff_required, login_url='/login/')
def detail_bom(request, bom_id):
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    # Mengambil BOM dari database 'manufacturing' berdasarkan ID
    bom = BillofMaterials.objects.using('manufacturing').get(id=bom_id)
    
    # Mengambil product dari database 'inventory' yang terkait dengan BOM
    products = Product.objects.using('inventory').all()

    warehouses = Warehouse.objects.using('inventory').all()

    bom_components = []

    for component_id, quantity, warehouse_id in zip(bom.component, bom.quantity, bom.warehouse):
        try:
            product = Product.objects.using('inventory').get(pk=int(component_id))
            warehouse = Warehouse.objects.using('inventory').get(pk=int(warehouse_id))
            bom_components.append({
                'product': {
                    'pk': product.pk,
                    'name': product.name,
                    'price' : int(product.salesprice),
                    'cost' : int(product.cost),
                    'warehouses' : warehouse.pk
                },
                'quantity': int(quantity),
                'warehouses' : warehouse.code
            })
        except Product.DoesNotExist:
            pass
    
    # Jika request adalah POST (pengguna mengirim form)
    if request.method == 'POST':
        metode = request.POST.get('metode')

        if metode == 'delete' :

            bom.delete()
            return redirect('manufacture:bom_list')
        
        elif metode == 'post' :

            # Update BOM fields berdasarkan data dari form
            bom.product_id = request.POST.get('products', bom.product_id)
            bom.bom_type = request.POST.get('bom_type', bom.bom_type)
            bom.component = request.POST.getlist('components[]')
            bom.quantity = request.POST.getlist('components_quantity[]')
            
            bom.save()  # Simpan perubahan ke database 'manufacturing'
            return redirect('manufacture:bom_list')  # Redirect ke daftar BOM

    # Jika request adalah GET, kembalikan data sebagai JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # JSON response untuk API
        product_data = products.values('pk', 'name', 'salesprice', 'cost')
        warehouse_data = warehouses.values('pk', 'warehouse', 'code')

        product_list = [
            {
                'pk' : p['pk'],
                'name' : p['name'],
                'salesprice' : int(p['salesprice']),
                'cost' : int(p['cost'])
            }
            for p in product_data
        ]

        return JsonResponse({
            'bom_components': bom_components,
            'products': product_list
        }, safe=False)

    # Render template jika tidak melalui API
    return render(request, 'detail_manufacture/detail_bom.html', {
        'bom': bom,
        'feature' : 'Cant Add',
        'bom_components': bom_components,
        'products': products,
        'title_1': 'manufacturing',
        'warehouses' : warehouses,
        'profile' : profile
    })

@login_required
@group_required('Manufacture')
@user_passes_test(staff_required, login_url='/login/')
def detail_mo(request, mo_id) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    mos = ManufacturingOrders.objects.using('manufacturing').get(id=int(mo_id))
    mos.warehouse = int(mos.warehouse)
    mos.responsible = User.objects.using('default').get(id=int(mos.responsible))
    companies = Entity.objects.using('master').all()
    product_all = Product.objects.using('inventory').all()
    boms = BillofMaterials.objects.using('manufacturing').all()
    whs = Warehouse.objects.using('inventory').all()

    mos.start_date = datetime.strftime(mos.start_date, "%Y-%m-%d")

    bom_product_name = []
    for bom in boms :
        product_data = Product.objects.using('inventory').get(id=int(bom.product_id))
        bom_product_name.append({
            'bom' : bom,
            'product' : product_data
        })

    mo_stock_move = {
        'stock_move' : StockMove.objects.using('inventory').get(id=mos.stock_move_id),
        'mo' : mos
    }

    file_type = None
    if mo_stock_move['stock_move'].files:
        ext = os.path.splitext(mo_stock_move['stock_move'].files.name)[1].lower()
        if ext in ['.jpg', '.png', '.jpeg', '.webp', '.svg', '.gif', '.bmp', '.tiff', '.heif', '.heic', '.ico'] :
            file_type = 'image'
        elif ext == '.pdf' :
            file_type = 'pdf'
    
    component_data = []
    for component in mos.product_component :
        products = Product.objects.using('inventory').get(id=int(component['product_id']))
        warehouse = Warehouse.objects.using('inventory').get(id=int(component['warehouse_id']))

        if StockTotal.objects.using('inventory').filter(product_id=int(component['product_id']), warehouse_id=int(component['warehouse_id'])).exists() :
            stock_k = StockTotal.objects.using('inventory').get(product_id=int(component['product_id']), warehouse_id=int(component['warehouse_id']))
            
            if int(component['product_quantity']) >= int(stock_k.stock) :
                status_f = "Not Ready"
            elif int(component['product_quantity']) <= int(stock_k.stock) :
                status_f = "Ready"
        
        else :
            status_f = "Not Ready"

        component_data.append({
            'product_id' : products.pk,
            'product_name' : products.name,
            'cost' : int(component['product_cost']),
            'price' : int(component['product_price']),
            'quantity' : int(component['product_quantity']),
            'warehouse' : warehouse,
            'status' : status_f,
            'status_f' : component['status']
        })

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == "update" :
            mo_id = request.POST['mo_id']
            component_id = request.POST['component_id']
            component_cost = request.POST['component_cost']
            component_price = request.POST['component_price']
            component_quantity = request.POST['component_quantity']
            warehouse_id = request.POST['warehouse_id']
            status = request.POST['status']

            manufacture_component = ManufacturingOrders.objects.using('manufacturing').get(id=int(mo_id))

            updated = False
            for component in manufacture_component.product_component :
                if (
                    int(component['product_id']) == int(component_id) and 
                    int(component['warehouse_id']) == int(warehouse_id) and 
                    int(component['product_cost']) == int(component_cost) and
                    int(component['product_price']) == int(component_price) and
                    int(component['product_quantity']) == int(component_quantity)
                    ) :
                    component['status'] = status
                    updated = True
            
            if updated :
                manufacture_component.save(using='manufacturing')
            
            stock_now = StockTotal.objects.using('inventory').get(product_id=int(component_id), warehouse_id=int(warehouse_id))
            stock_total = stock_now.stock
            stock_cal = int(component_quantity)

            if stock_total >= stock_cal :
                stock_now.stock = stock_total - stock_cal
                stock_now.save()
            else : 
                return redirect('manufacture:detail_mo', mo_id=mo_id)
            
            if all(item['status'] == "done" for item in manufacture_component.product_component) :
                manufacture_component.status = "done"
                manufacture_component.save()
            elif any(item['status'] == "done" for item in manufacture_component.product_component) and any(item['status'] == "draft" for item in manufacture_component.product_component) :
                manufacture_component.status = "in progress"
                manufacture_component.save()
            elif all(item['status'] == "draft" for item in manufacture_component.product_component) :
                manufacture_component.status = "draft"
                manufacture_component.save()
            elif manufacture_component.approved_by != 0 and manufacture_component.status == "draft" :
                manufacture_component.status = "confirmed"
                manufacture_component.save()

            if manufacture_component.status == "done" :
                stock_n, created = StockTotal.objects.using('inventory').get_or_create(
                    product_id=manufacture_component.product,
                    warehouse_id=int(mo_stock_move['stock_move'].destination),
                    stock=int(manufacture_component.quantity)
                )

                if not created :
                    stock_n.stock = stock_n.stock + int(manufacture_component.quantity)
                
                stock_n.save()
                
            return redirect('manufacture:detail_mo', mo_id=mo_id)
                
    return render(request, 'detail_manufacture/detail_mo.html', {
        'title_1' : 'Manufacture',
        'title_2' : 'Manufacturing Orders',
        'feature' : 'Cant Add',
        'boms' : bom_product_name,
        'mo' : mo_stock_move,
        'products' : product_all,
        'components_data' : component_data,
        'warehouses' : whs,
        'companies' : companies,
        'file_type' : file_type,
        'profile' : profile
    })