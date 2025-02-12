from django.db import models
import json

"""
    Pemakaian database Inventory,

    flow :

    1. Input tipe product
        > Auto generate untuk code tipe product (Code Tipe, tidak perlu diisi, tidak akan ditampilkan pada view)
        > Deskripsi opsional untuk diisi

    2. Input Warehouse
        > Lokasi dapat diisi lengkap

    3. Input Product
        > Auto generate untuk SKU (didapat dari kode product dan nomor product)
        > Kategori produk diisi dengan mengikuti tipe produk
        > Deskripsi opsinal untuk diisi

    4. StockMove
        > Produk diisi dengan mengikuti table produk
        > Source warehouse diisi dengan mengikuti table warehouse (tempat keluarnya produk)
        > Destination warehouse diisi dengan mengikuti table warehouse (tempat masuknya barang)
        > Quantity diisi dengan kuantitas produk yang dikirim
        > Move type diisi dengan tipe bergeraknya produk (apakah produk masuk[pembelian], produk keluar[dipakai], dan transfer[warehouse to warehouse])

    5. StockTotal
        > Produk diisi dengan mengikuti produk dari table produk
        > Stock adalah pengurangan atau penambahan dari table Stock Move
        > Warehouse tidak wajib diisi karena hanya menampilkan product dari warehouse tersebut
"""

class Warehouse(models.Model) :
    warehouse = models.CharField(max_length=255)
    code = models.CharField(max_length=12, unique=True, editable=False)
    location = models.TextField(null=False, blank=False)
    company = models.IntegerField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'inventory'
        db_table = 'warehouse'
        managed = True

    def __str__(self):
        return self.warehouse
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().delete(*args, **kwargs)

class TypeProduct(models.Model) :
    product_type = models.CharField(max_length=255)
    code = models.CharField(max_length=12, editable=False, unique=True)
    description = models.TextField(blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'inventory'
        db_table = 'type_product'
        managed = True

    def __str__(self):
        return self.product_type
    
    def save(self, *args, **kwargs) :

        if not self.code :
            self.code = self.generate_code(self.product_type)

        kwargs['using'] = 'inventory'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().delete(*args, **kwargs)

    def generate_code(self, product_type) :
        words = product_type.split()

        if len(words) == 1 :

            code_name = self.product_type[:3].upper()
            total_code = TypeProduct.objects.using('inventory').filter(code=self.code).count() + 1
            code_number = f'{total_code:02d}'
            code = f'{code_name}-{code_number}'

        else :
            code_name = ''.join([word[0].upper() for word in words[:3]])
            total_code = TypeProduct.objects.using('inventory').filter(code=self.code).count() + 1
            code_number = f'{total_code:02d}'
            code = f'{code_name}-{code_number}'

        while TypeProduct.objects.using('inventory').filter(code=code).exists() :
            total_code += 1
            code_number = f'{total_code:02d}'
            code = f'{code_name}-{code_number}'

        return code

class Product(models.Model) :
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True)
    category_type = models.ForeignKey(TypeProduct, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=24)
    description = models.TextField(null=True, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)
    salesprice = models.DecimalField(decimal_places=2, blank=True, null=True, max_digits=11)
    cost = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=11)
    company_id = models.IntegerField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'inventory'
        db_table = 'product'
        managed = True

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs) :

        if not self.sku :
            self.sku = self.generate_sku()

        kwargs['using'] = 'inventory'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().delete(*args, **kwargs)

    def generate_sku(self) :
        category_type = self.category_type.code[:3].upper()
        total_products = Product.objects.using('inventory').filter(product_type = self.product_type).count() + 1
        product_number = f'{total_products:04d}'
        sku = f'{category_type}-{product_number}'

        while Product.objects.using('inventory').filter(sku=sku).exists() :
            total_products += 1
            product_number = f'{total_products:04d}'
            sku = f'{category_type}-{product_number}'

        return sku

class StockMove(models.Model) :
    code = models.TextField()
    operation_type = models.CharField(max_length=64)
    source = models.CharField(max_length=11)
    destination = models.CharField(max_length=11)
    scheduled_date = models.DateField(null=True, blank=True)
    files = models.FileField(upload_to="user_upload_file/")
    responsible = models.TextField()
    company = models.IntegerField()
    notes = models.TextField()
    products = models.TextField()
    product_quantities = models.TextField()

    class Meta :
        app_label = 'inventory'
        db_table = 'stock_move'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().delete(*args, **kwargs)

class StockTotal(models.Model) :
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock = models.DecimalField(max_digits=11, decimal_places=2)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    class Meta :
        app_label = 'inventory'
        db_table = 'stock_total'
        managed = True
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().delete(*args, **kwargs)

class StorageCategories(models.Model) :
    name = models.CharField(max_length=255)
    allow_new_product = models.TextField()
    max_weight = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
    company_id = models.IntegerField()
    products = models.TextField()
    quantity = models.TextField()

    class Meta :
        app_label = 'inventory'
        db_table = 'storage_categories'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().delete(*args, **kwargs)

class Receipt(models.Model) :
    stock_move = models.ForeignKey(StockMove, on_delete=models.CASCADE)
    product = models.JSONField()
    status = models.CharField(max_length=64)

    class Meta :
        app_label = 'inventory'
        db_table = 'receipt'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().delete(*args, **kwargs) 

class InternalTransfer(models.Model) :
    stock_move = models.ForeignKey(StockMove, on_delete=models.CASCADE)
    product = models.JSONField()
    status = models.CharField(max_length=64)
    shipping_service = models.IntegerField()
    url_tracking = models.URLField(blank=True, null=True)

    class Meta :
        app_label = 'inventory'
        db_table = 'internal_transfer'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().delete(*args, **kwargs)

class DeliveryOrder(models.Model) :
    stock_move = models.ForeignKey(StockMove, on_delete=models.CASCADE)
    product = models.JSONField()
    status = models.CharField(max_length=64)
    shipping_service = models.IntegerField()
    url_tracking = models.URLField(blank=True, null=True)

    class Meta :
        app_label = 'inventory'
        db_table = 'delivery_order'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'inventory'
        super().delete(*args, **kwargs)