from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from market.models import Market
from django.shortcuts import reverse


# from utils.main import disable_for_loaddata

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, null=True)
    alter_name = models.CharField(max_length=100, null=True)
    dsc = models.CharField(max_length=1000, null=True, blank=True, default=None)
    image = models.ImageField(upload_to='category/')

    def __str__(self):
        return self.alter_name


class SubCategory(models.Model):
    name = models.CharField(max_length=200, null=True)
    alter_name = models.CharField(max_length=200, null=True)
    id_category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.alter_name


class Product(models.Model):
    name = models.CharField(max_length=500, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True)
    article = models.CharField(max_length=20, null=True)
    cost = models.CharField(max_length=100)
    price = models.FloatField(default=0.0)
    count = models.CharField(max_length=100)
    dsc = models.TextField(null=True)
    is_new = models.BooleanField(default=False)
    is_hit = models.BooleanField(default=False)
    is_sovet = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'category': self.category.name, "index": self.id})

    def get_url(self):
        url = ''
        url += self.category.name
        url += '/' + str(self.id)
        return url

    def __str__(self):
        return "Товар %s" % self.name

    class Meta:
        ordering = ['count']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class ProductImage(models.Model):
    path = models.FilePathField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.path)


class Likes(models.Model):
    id_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)


class Status(models.Model):
    name = models.CharField(max_length=24, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Статус заказа'
        verbose_name_plural = 'Статусы заказа'


class Order(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, default=None, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      default=0)  # total price for all products in order
    customer_name = models.CharField(max_length=64, blank=True, null=True, default=None)
    customer_email = models.EmailField(blank=True, null=True, default=None)
    customer_phone = models.CharField(max_length=48, blank=True, null=True, default=None)
    customer_address = models.CharField(max_length=128, blank=True, null=True, default=None)
    delivery = models.CharField(max_length=50, blank=True, null=True, default=None)
    payment = models.CharField(max_length=50, blank=True, null=True, default=None)
    comments = models.TextField(blank=True, null=True, default=None)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "Заказ %s %s" % (self.id, self.status.name)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)


class ProductInOrder(models.Model):
    order = models.ForeignKey(Order, blank=True, null=True, default=None, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    nmb = models.IntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # price*nmb
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.product.name

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def save(self, *args, **kwargs):
        price_per_item = self.product.price
        self.price_per_item = price_per_item
        self.total_price = int(self.nmb) * price_per_item
        super(ProductInOrder, self).save(*args, **kwargs)


# @disable_for_loaddata
def product_in_order_post_save(sender, instance, created, **kwargs):
    order = instance.order
    all_products_in_order = ProductInOrder.objects.filter(order=order, is_active=True)

    order_total_price = 0
    for item in all_products_in_order:
        order_total_price += item.total_price

    instance.order.total_price = order_total_price
    instance.order.save(force_update=True)


post_save.connect(product_in_order_post_save, sender=ProductInOrder)


class ProductInBasket(models.Model):
    session_key = models.CharField(max_length=128, blank=True, null=True, default=None)
    order = models.ForeignKey(Order, blank=True, null=True, default=None, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    nmb = models.IntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # price*nmb
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.product.name

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'

    def save(self, *args, **kwargs):
        price_per_item = self.product.price
        self.price_per_item = price_per_item
        self.total_price = int(self.nmb) * price_per_item
        super(ProductInBasket, self).save(*args, **kwargs)


class ProductInMarket(models.Model):
    product = models.ForeignKey(Product, blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    market = models.ForeignKey(Market, blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    count = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.product.name

    class Meta:
        verbose_name = 'Товар в магазине'
        verbose_name_plural = 'Товары в магазине'
