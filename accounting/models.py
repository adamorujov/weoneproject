from django.db import models
from core.models import Product

class Purchase(models.Model):
    STATUS = (
        ('G', 'Gözləyir'),
        ('A', 'Anbarda')
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="purchases")
    amount = models.IntegerField(default=0)
    date = models.DateField()
    status = models.CharField(choices=STATUS, max_length=1, default='G')
    in_stock = models.BooleanField(default=False)

    class Meta:
        ordering = ("-id",)
        verbose_name = "Məhsul alışı"
        verbose_name_plural = "Məhsul alışı"

    def __str__(self):
        return self.product.name
    



"""
Product --- Purchase




"""