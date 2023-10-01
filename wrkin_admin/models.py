from django.db import models

# Create your models here.

class AdminUser(models.Model):
    name = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    role = models.IntegerField(blank=True, null=True)
    country_code = models.IntegerField(blank=True, null=True)
    phone_no = models.BigIntegerField(blank=True, null=True)
    password = models.TextField(blank=True, null=True)
    token = models.TextField(blank=True, null=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    last_updated_at = models.DateTimeField(blank=True, null=True)
    is_enabled = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin_user'