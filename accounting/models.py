from django.db import models
from core.models import Product, CustomUser

class Purchase(models.Model):
    STATUS = (
        ('G', 'Gözləyir'),
        ('A', 'Anbarda')
    )
    product = models.ForeignKey(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="purchases")
    amount = models.IntegerField("Miqdar", default=0)
    date = models.DateField("Alış tarixi")
    status = models.CharField("Status", choices=STATUS, max_length=1, default='G')
    in_stock = models.BooleanField("Anbarda", default=False)

    class Meta:
        ordering = ("-id",)
        verbose_name = "Məhsul alışı"
        verbose_name_plural = "Məhsul alışı"

    def __str__(self):
        return self.product.name
    
class Sale(models.Model):
    customer = models.ForeignKey(CustomUser, verbose_name="Müştəri", on_delete=models.CASCADE, related_name="customer_sales")
    product = models.ForeignKey(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="product_sales")
    amount = models.IntegerField("Miqdar", default=0)
    datetime = models.DateTimeField("Tarix və vaxt")
    price = models.FloatField("Satış qiyməti")

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

    class Meta:
        ordering = ("-id",)
        verbose_name = "Müştəri hərəkəti"
        verbose_name_plural = "Müştəri hərəkəti"

    def __str__(self):
        return self.customer.username



"""
Product --- Purchase
CustomUser - one --- Sale - many
Product - one --- Sale - many

"""

