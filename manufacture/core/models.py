from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db import connection

class UserActivity(models.Model):
    user = models.IntegerField()
    username = models.CharField(max_length=150)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"User: {self.username} (ID: {self.user}) - {self.path} - {self.timestamp}"

    @classmethod
    def switch_table(cls):
        # Tentukan batas jumlah rows
        row_limit = 30  # Ubah dengan limit yang diinginkan

        # Cek jumlah row di tabel saat ini
        current_table = cls._meta.db_table  # Nama tabel saat ini

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {current_table}")
            row_count = cursor.fetchone()[0]

        # Jika jumlah row lebih dari limit, buat tabel baru
        if row_count >= row_limit:
            table_suffix = now().strftime('%Y%m%d%H%M%S')  # Gunakan timestamp untuk nama tabel baru
            new_table_name = f"{current_table}_{table_suffix}"

            # Buat tabel baru dengan nama yang berbeda pada database yang benar
            cls.create_new_table(new_table_name, 'dump')

            # Berpindah ke tabel baru
            cls._meta.db_table = new_table_name

    @classmethod
    def create_new_table(cls, new_table_name, db_alias):
        # Pastikan kamu membuat tabel dengan skema yang benar pada database yang dituju
        with connection.schema_editor(using=db_alias) as schema_editor:
            schema_editor.create_model(cls)
        
        # Menambahkan nama tabel baru yang diinginkan pada model, jika perlu
        # untuk menyesuaikan nama tabel saat migrasi (jika diperlukan)
        with connection.cursor() as cursor:
            cursor.execute(f"""
                CREATE TABLE {new_table_name} (
                    id SERIAL PRIMARY KEY,
                    user INTEGER NOT NULL,
                    username VARCHAR(150) NOT NULL,
                    path VARCHAR(255) NOT NULL,
                    method VARCHAR(10) NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    ip_address INET NOT NULL
                );
            """)
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'dump'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'dump'
        super().delete(*args, **kwargs)

class Deleted(models.Model) :
    user_activity = models.ForeignKey(UserActivity, on_delete=models.CASCADE)
    deleted_as = models.TextField()
    value = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'core'
        db_table = 'deleted_value'
        managed = True
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'dump'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'dump'
        super().delete(*args, **kwargs)