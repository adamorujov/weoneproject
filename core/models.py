from django.db import models
from django.contrib.auth.models import AbstractUser
from tinymce.models import HTMLField

class CustomUser(AbstractUser):
    PAYMENT_STATUS = (
        ("S", "Satış qiyməti"),
        ("E", "Endirimli qiymət"),
    )
    address = models.TextField("Ünvan", blank=True, null=True)
    phone_number = models.CharField("Telefon nömrəsi", max_length=20, blank=True, null=True)
    status = models.CharField("Ödəniş statusu", max_length=2, choices=PAYMENT_STATUS, blank=True, null=True)
    website = models.CharField("Vebsayt", max_length=256, blank=True, null=True)
    is_supplier = models.BooleanField("Tədarükçü statusu", default=False)

class SiteSettings(models.Model):
    logo = models.ImageField("Loqo", upload_to="site_imgs/", blank=True, null=True)
    favicon = models.ImageField("Favikon", upload_to="site_imgs/", blank=True, null=True)

    about_title = models.TextField("Haqqımızda başlıq", blank=True, null=True)
    about_content = models.TextField("Haqqımızda kontent", blank=True, null=True)
    about_image = models.ImageField("Haqqımızda şəkil", upload_to="site_imgs/", blank=True, null=True)

    address = models.TextField("Ünvan", blank=True, null=True)
    contact_number = models.CharField("Əlaqə nömrəsi", max_length=20, blank=True, null=True)

    about_services = models.TextField("Xidmətlərimiz", blank=True, null=True)

    contact_title = models.TextField("Əlaqə başlıq", blank=True, null=True)
    contact_content = models.TextField("Əlaqə kontent", blank=True, null=True)
    contact_image = models.ImageField("Əlaqə şəkil", upload_to="site_imgs/", blank=True, null=True)

    class Meta:
        verbose_name = "parametr"
        verbose_name_plural = "Parametrlər"

    def __str__(self):
        return "Parametrlər"

class Banner(models.Model):
    title = models.CharField("Başlıq", max_length=150)
    content = models.TextField("Kontent")
    image = models.ImageField("Şəkil", upload_to="banner_imgs/")

    class Meta:
        verbose_name = "banner"
        verbose_name_plural = "Bannerlər"
        ordering = ("-id",)

    def __str__(self):
        return self.title
    
class ProductCategory(models.Model):
    name = models.CharField("Ad", max_length=100)
    image = models.ImageField("Şəkil", upload_to="category_imgs/")

    class Meta:
        verbose_name = "məhsul kateqoriyası"
        verbose_name_plural = "Məhsul kateqoriyaları"
        ordering = ("-id",)

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name = models.CharField("Ad", max_length=100)
    
    class Meta:
        verbose_name = "marka"
        verbose_name_plural = "Markalar"
        ordering = ("-id",)

    def __str__(self):
        return self.name
    
class Store(models.Model):
    name = models.CharField("Ad", max_length=100)
    
    class Meta:
        verbose_name = "brend"
        verbose_name_plural = "Brendlər"
        ordering = ("-id",)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    CURRENCIES = (
        ('M', 'Manat'),
        ('D', 'Dollar'),
        ('R', 'Rubl')
    )
    name = models.CharField("Ad", max_length=256, unique=True)
    about = HTMLField("Haqqında", blank=True, null=True)
    image = models.ImageField("Şəkil", upload_to="product_imgs/", blank=True, null=True)
    cost_price = models.FloatField("Maya dəyəri", default=0)
    purchase_price = models.FloatField("Alış qiyməti", default=0)
    currency = models.CharField("Valyuta", max_length=1, default='M')
    price = models.FloatField("Satış qiyməti", default=0)
    discount_price = models.FloatField("Endirimli qiyməti", blank=True, null=True)
    category = models.ForeignKey(ProductCategory, verbose_name="Kateqoriya", on_delete=models.SET_NULL, related_name="category_products", blank=True, null=True)
    brand = models.ForeignKey(Brand, verbose_name="Marka", on_delete=models.SET_NULL, related_name="brand_products", blank=True, null=True)
    store = models.ForeignKey(Store, verbose_name="Brend", on_delete=models.SET_NULL, related_name="store_products", blank=True, null=True)
    amount = models.IntegerField("Miqdar", default=0)
    date = models.DateField("Gəliş tarixi")

    class Meta:
        verbose_name = "məhsul"
        verbose_name_plural = "Məhsullar"
        ordering = ("-id",)

    def __str__(self):
        return self.name
    
class Article(models.Model):
    name = models.CharField("Artikl", max_length=50, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="articles")

    class Meta:
        verbose_name = "artikl"
        verbose_name_plural = "Artikllar"
        ordering = ("-id",)

    def __str__(self):
        return self.name

class Application(models.Model):
    name = models.CharField("Ad", max_length=50)
    surname = models.CharField("Soyad", max_length=50)
    email = models.EmailField("Email", max_length=256)
    phone_number = models.CharField("Telefon nömrəsi", max_length=20)
    note = models.TextField("Qeyd")
    created_at = models.DateTimeField("Göndərildi", auto_now_add=True)

    class Meta:
        verbose_name = "müraciət"
        verbose_name_plural = "Müraciətlər"
        ordering = ("-id",)

    def __str__(self):
        return self.name + " " + self.surname
    
class SocialMedia(models.Model):
    icon = models.TextField("İkon")
    link = models.URLField("Link", max_length=256)

    class Meta:
        verbose_name = "sosial media"
        verbose_name_plural = "Sosial Media Hesabları"
        ordering = ("-id",)

    def __str__(self):
        return self.link
    
class Advantage(models.Model):
    icon = models.TextField("İkon")
    title = models.CharField("Başlıq", max_length=150)
    content = models.TextField("Kontent")

    class Meta:
        verbose_name = "üstünlük"
        verbose_name_plural = "Üstünlüklər"
        ordering = ("-id",)

    def __str__(self):
        return self.title
    
class Activity(models.Model):
    name = models.CharField("Ad", max_length=150)
    value = models.CharField("Qiymət", max_length=150)

    class Meta:
        verbose_name = "fəaliyyət"
        verbose_name_plural = "Fəaliyyətlər"
        ordering = ("-id",)

    def __str__(self):
        return self.name
    
class Service(models.Model):
    title = models.CharField("Başlıq", max_length=256)
    image = models.ImageField("Şəkil", upload_to="service_imgs/")

    class Meta:
        verbose_name = "xidmət"
        verbose_name_plural = "xidmətlər"
        ordering = ("-id",)

    def __str__(self):
        return self.title
    
class Mission(models.Model):
    title = models.CharField("Başlıq", max_length=256)
    content = models.TextField("Kontent")
    image = models.ImageField("Şəkil", upload_to="service_imgs/")

    class Meta:
        ordering = ("-id",)
        verbose_name = "missiya və baxış"
        verbose_name_plural = "Missiyalar və Baxışlar"

    def __str__(self):
        return self.title


class BasketItem(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name="İstifadəçi", on_delete=models.CASCADE, related_name="user_basketitems")
    product = models.ForeignKey(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="product_basketitems")
    quantity = models.IntegerField("Miqdar", default=1)

    class Meta:
        verbose_name = "səbət elementi"
        verbose_name_plural = "Səbət elementləri"
        ordering = ("-id",)

    def __str__(self):
        return self.user.username + " | " + self.product.name

class Order(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name="İstifadəçi", on_delete=models.CASCADE, related_name="orders")
    amount = models.FloatField("Ümumi məbləğ")
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "sifariş"
        verbose_name_plural = "Sifarişlər"
        ordering = ("-id",)

    def __str__(self):
        return self.user.username
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_orderitems")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_orderitems")
    quantity = models.IntegerField(default=1)

    class Meta:
        verbose_name = "sifariş elementi"
        verbose_name_plural = "Sifariş elementləri"
        ordering = ("-id",)

    def __str__(self):
        return self.product.name
    
