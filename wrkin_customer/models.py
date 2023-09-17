from django.db import models

# Create your models here.

class CompanyProfile(models.Model):
    name = models.TextField(blank=True, null=True)
    logo = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    no_of_emp = models.IntegerField(blank=True, null=True)
    type_of_org = models.TextField(blank=True, null=True)
    reg_id = models.TextField(blank=True, null=True)
    country_code = models.IntegerField(blank=True, null=True)
    phone_no = models.BigIntegerField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_enabled = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'company_profile'

class Designations(models.Model):
    company_profile = models.ForeignKey('CompanyProfile', models.DO_NOTHING, db_column='company_profile', blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_enabled = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'designations'

class CustomerUser(models.Model):
    name = models.TextField(blank=True, null=True)
    country_code = models.IntegerField(blank=True, null=True)
    phone_no = models.BigIntegerField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)  # This field type is a guess.
    designations = models.ForeignKey('Designations', models.DO_NOTHING, db_column='designations', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    company_profile = models.ForeignKey('CompanyProfile', models.DO_NOTHING, db_column='company_profile', blank=True, null=True)
    secure_token = models.TextField(blank=True, null=True)
    created_at = models.DateField(blank=True, null=True)
    updated_at = models.DateField(blank=True, null=True)
    last_login_at = models.DateField(blank=True, null=True)
    is_enabled = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer_user'

class OtpVerify(models.Model):
    country_code = models.IntegerField(blank=True, null=True)
    phone_no = models.BigIntegerField(blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
    try_count = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'otp_verify'


