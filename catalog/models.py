from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import m2m_changed
from django.dispatch import receiver


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ['email']
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('owner', 'Владелец магазина'),
        ('admin', 'Администратор'),
    ]

    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)

    def is_owner(self):
        return self.role == 'owner'

    def is_admin(self):
        return self.role == 'admin'


class AddressBase(models.Model):
    city = models.CharField(max_length=100, default="Курчатов")
    street = models.CharField(max_length=150)

    class Meta:
        unique_together = ('city', 'street')

    def __str__(self):
        return f"{self.city}, {self.street}"


class Store(models.Model):
    name = models.CharField(max_length=255)
    owners = models.ManyToManyField('User', related_name='stores', blank=True)

    address_base = models.ForeignKey(
        AddressBase, on_delete=models.SET_NULL, null=True, blank=True)
    house_number = models.CharField(max_length=20, blank=True)

    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    def full_address(self):
        if self.address_base:
            return f"{self.address_base}, {self.house_number}"
        return self.house_number


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


def product_image_path(instance, filename):
    return f'products/{instance.id}/{filename}'


class Product(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Кг'),
        ('pcs', 'Шт.'),
        ('ml', 'Мл.'),
    ]

    image = models.ImageField(
        upload_to=product_image_path,
        blank=True,
        null=True,
        default='no-photo.png'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.SET_NULL, null=True, blank=True)
    quantity_value = models.FloatField(max_length=10)
    quantity_unit = models.CharField(
        max_length=10, choices=UNIT_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.quantity_value} {self.get_quantity_unit_display()})"


class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    price = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'store'], name='unique_product_per_store')
        ]


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('review', 'В рассмотрении'),
        ('resolved', 'Решена')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    description = models.TextField()
    image = models.ImageField(upload_to='complaints/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='new')
    response = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(m2m_changed, sender=Store.owners.through)
def manage_user_owner_role(sender, instance, action, pk_set, **kwargs):
    from .models import User

    if action == 'post_add':
        users = User.objects.filter(pk__in=pk_set)
        for user in users:
            if user.role != 'admin':
                user.role = 'owner'
                user.save()

    elif action == 'post_remove':
        for user_id in pk_set:
            user = User.objects.get(pk=user_id)
            if user.role == 'owner':
                if not user.owned_stores.exists():
                    user.role = 'user'
                    user.save()
