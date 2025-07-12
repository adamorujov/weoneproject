from django.db import models
from core.models import Product, CustomUser

class Purchase(models.Model):
    STATUS = (
        ('G', 'Gözləyir'),
        ('A', 'Anbarda')
    )
    supplier = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="supplier_purchases")
    product = models.ForeignKey(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="purchases")
    amount = models.IntegerField("Miqdar", default=0)
    date = models.DateField("Alış tarixi")
    status = models.CharField("Status", choices=STATUS, max_length=1, default='G')

    class Meta:
        ordering = ("-id",)
        verbose_name = "Məhsul alışı"
        verbose_name_plural = "Məhsul alışı"

    def __str__(self):
        return self.product.name
    
class Stock(models.Model):
    product = models.OneToOneField(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="stock")
    amount = models.IntegerField(default=0)

    class Meta:
        ordering = ("-id",)
        verbose_name = "Stok"
        verbose_name_plural = "Anbar"

    def __str__(self):
        return self.product.name

class Sale(models.Model):
    STATUS = (
        ('G', 'Gözləyir'),
        ('S', 'Satılıb')
    )
    seller = models.ForeignKey(CustomUser, verbose_name="Satıcı", on_delete=models.CASCADE, related_name="seller_sales")
    customer = models.ForeignKey(CustomUser, verbose_name="Müştəri", on_delete=models.CASCADE, related_name="customer_sales")
    product = models.ForeignKey(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="product_sales")
    amount = models.IntegerField("Miqdar", default=0)
    datetime = models.DateTimeField("Tarix və vaxt")
    price = models.FloatField("Satış qiyməti")
    status = models.CharField("Status", choices=STATUS, max_length=1, default='G')

    class Meta:
        ordering = ("-id",)
        verbose_name = "Məhsul satışı"
        verbose_name_plural = "Məhsul satışı"

    def __str__(self):
        return self.product.name + " | " + self.customer.username
    
class Payment(models.Model):
    customer = models.ForeignKey(CustomUser, verbose_name="Müştəri", on_delete=models.CASCADE, related_name="payments")
    datetime = models.DateTimeField("Tarix və vaxt")
    amount = models.FloatField("Ödənilən məbləğ", default=0)

    class Meta:
        ordering = ("-id",)
        verbose_name = "Ödəniş"
        verbose_name_plural = "Ödənişlər"

    def __str__(self):
        return self.customer.username
    
class ProductAction(models.Model):
    product = models.ForeignKey(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="product_actions")
    customer = models.ForeignKey(CustomUser, verbose_name="Müştəri", on_delete=models.CASCADE, related_name="customer_product_actions", blank=True, null=True)
    date = models.DateField("Tarix")
    incoming_product_number = models.IntegerField("Gələn məhsul sayı", blank=True, null=True)
    sold_product_number = models.IntegerField("Satılan məhsul sayı", blank=True, null=True)
    remaining_product_number = models.IntegerField("Qalan məhsul sayı", blank=True, null=True)
    return_product_number = models.IntegerField("Qaytarılan məhsul sayı", blank=True, null=True)

    class Meta:
        ordering = ("-id",)
        verbose_name = "Məhsul hərəkəti"
        verbose_name_plural = "Məhsul hərəkəti"

    def __str__(self):
        return self.product.name
    
class CustomerAction(models.Model):
    customer = models.ForeignKey(CustomUser, verbose_name="Müştəri", on_delete=models.CASCADE, related_name="customer_actions")
    product = models.ForeignKey(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="product_customer_actions", blank=True, null=True)
    date = models.DateField("Tarix")
    product_price = models.FloatField("Məhsul qiyməti", blank=True, null=True)
    payment_amount = models.FloatField("Ödənilən məbləğ", blank=True, null=True)
    total_amount = models.FloatField("Ümumi gəlir", blank=True, null=True)
    remaining_amount = models.FloatField("Qalan məbləğ", blank=True, null=True)
    return_amount = models.FloatField("Qaytarılan məbləğ", blank=True, null=True)

    class Meta:
        ordering = ("-id",)
        verbose_name = "Müştəri hərəkəti"
        verbose_name_plural = "Müştəri hərəkəti"

    def __str__(self):
        return self.customer.username
    
class ReturnBack(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="returnbacks")
    date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    amount = models.IntegerField()

    class Meta:
        verbose_name = "Geri qaytarma"
        verbose_name_plural = "Geri qaytarılan məhsullar"

    def __str__(self):
        return self.sale.product.name
    
class Expense(models.Model):
    name = models.CharField(max_length=200)
    amount = models.FloatField()
    date = models.DateField()

    class Meta:
        verbose_name = "Xərc"
        verbose_name_plural = "Xərclər"

    def __str__(self):
        return self.name
    




"""
Product --- Purchase
CustomUser - one --- Sale - many
Product - one --- Sale - many

"""

