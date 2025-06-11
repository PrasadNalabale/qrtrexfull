from django.db import models
# from django.contrib.auth.models import User
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
import random
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import os
from django.utils.dateparse import parse_datetime
from datetime import datetime




class Restaurant(models.Model):

    CATEGORY_CHOICES = [
        ("veg","Vegetarian"),
        ("non-veg","Non-Vegetarian"),
        ("veg-nonveg","Both"),
        ]

    TYPE_CHOICES = [
        ("restaurant","Restaurant"),
        ("restaurant_and_bar","Restaurant And Bar"),
        ("dhaba","Dhaba"),
        ("dhaba_with_liquor","Dhaba With Liquor"),
        ("cafe","Cafe")
    ]
    

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurant')
    restaurant_id = models.IntegerField(unique=True,blank=False,null=False, editable=False)
    restaurant_name = models.CharField(max_length=250,null=False,blank=False)
    address = models.TextField()
    description = models.TextField()
    restaurant_type = models.CharField(max_length=50,choices=TYPE_CHOICES)
    mobile = models.CharField(max_length=12,null=False,blank=False)
    wifi = models.CharField(max_length=100,default="No Wifi")
    email = models.EmailField()
    logo = models.ImageField(upload_to="restaurant_logos/",blank=True, null=True)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add = True)
    fassai = models.IntegerField()
     


    def save(self,*args,**kwargs):
        if self.restaurant_id is None:
            self.restaurant_id = self.generate_id()
        
        
        super().save(*args,**kwargs)


    def generate_id(self):
        attempts=0
        max_attempts = 100
        while attempts < max_attempts :
            restaurant_id = random.randint(100000,999999)
            if not Restaurant.objects.filter(restaurant_id=restaurant_id).exists():
                return restaurant_id
            attempts+=1
        raise Exception("There is a problem in generating new Id, please contact support. Call : 9623920576 or Mail : support@qrtrex.com")

    def __str__(self):
        return f"{self.restaurant_id},{self.restaurant_name}"


class UserMembership(models.Model):
    MEMBERSHIP = [
        ('monthly', 'Monthly'),
        ('semi annual', 'Semi Annual'),
        ('annual', 'Annual')
    ]

    restaurant = models.ForeignKey('Restaurant', related_name='membership', on_delete=models.CASCADE)
    membership_type = models.CharField(max_length=15, choices=MEMBERSHIP)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)  # optional if calculated from membership_type

    def clean(self):
        if self.duration is not None and self.duration <= 0:
            raise ValidationError('Duration must be a positive integer.')

    def is_active(self):
        return self.end_date >= timezone.now().date() if self.end_date else False

    def days_to_expire(self):
        return (self.end_date - timezone.now().date()).days if self.end_date else None

    def save(self, *args, **kwargs):
        # Set start_date to today if not provided
        if not self.start_date:
            self.start_date = timezone.now().date()

        # Set duration based on membership_type
        membership_durations = {
            'monthly': 1,
            'semi annual': 6,
            'annual': 12
        }

        if self.membership_type in membership_durations:
            self.duration = membership_durations[self.membership_type]

        # Calculate end_date based on duration
        if self.start_date and self.duration:
            self.end_date = self.start_date + relativedelta(months=self.duration)

        self.clean()
        super().save(*args, **kwargs)

    def renew(self):
        """
        Renews the membership by extending from the current end_date.
        """
        if not self.end_date:
            raise ValueError("Cannot renew membership without an end_date.")

        self.start_date = self.end_date  # New cycle starts when the previous ends

        # Ensure duration is set (fallback to membership_type if needed)
        if not self.duration:
            membership_durations = {
                'monthly': 1,
                'semi annual': 6,
                'annual': 12
            }
            self.duration = membership_durations.get(self.membership_type)

        self.end_date = self.start_date + relativedelta(months=self.duration)
        self.save()

    def __str__(self):
        return f"Membership for {self.restaurant.restaurant_name} - {self.membership_type} ({self.start_date} to {self.end_date})"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    signature = models.TextField(blank=True, null=True)
    amount = models.IntegerField()  # in paisa
    status = models.CharField(max_length=20, default='created')
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} - ₹{self.amount / 100}"

class Menu(models.Model):

    restaurant = models.ForeignKey(Restaurant,related_name = 'menus', on_delete=models.CASCADE)
    menu_name = models.CharField(max_length=100)

    def __str__(self):
        return self.menu_name

class MenuItem(models.Model):

    CATEGORY = [
        ('veg','Vegetarian'),
        ('non-veg','Non-Vegetarian'),
        ]
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu,related_name='items', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places = 2, blank=False, null=False)
    category = models.CharField(max_length=15, choices=CATEGORY)
    is_available = models.BooleanField(default=True)

    def clean(self):
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")

    def __str__(self):
        return f"{self.name},{self.price}"

class LiquorTypes(models.Model):
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE,related_name='liquors')
    name = models.CharField(max_length=255,null=False,blank=False)

    def __str__(self):
        return self.name

class Liquor(models.Model):
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE)
    liquorTypes = models.ForeignKey(LiquorTypes,related_name='liquorItems',on_delete=models.CASCADE)
    name = models.CharField(max_length=255,blank=False,null=False)
    image = models.ImageField(upload_to='liquor_images/',blank=True,null=True)
    description = models.TextField(null=True,blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2 ,null=False,blank=False)
    is_available = models.BooleanField(default=True)

    def clean(self):
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")

    def __str__(self):
        return f"{self.restaurant},{self.name},{self.price},{self.liquorTypes}"


class Rating(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="ratings")
    name = models.CharField(max_length=255,blank=True,null=True)
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True, null=True)
    reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.stars}⭐ by {self.name or 'Anonymous'}"

class Offer(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=100)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.end_date:
            if isinstance(self.end_date, str):
                self.end_date = parse_datetime(self.end_date)

            if timezone.is_naive(self.end_date):
                self.end_date = timezone.make_aware(self.end_date)

            if self.end_date < timezone.now():
                self.is_active = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Enquiry(models.Model):

    STATUS_CHOICES = (
        ('unread','Unread'),
        ('read','Read'),
    )
    name = models.CharField(max_length=255,null=False,blank=False)
    email = models.EmailField(null=False,blank=False)
    number = models.CharField(max_length=12,null=False,blank=False)
    message = models.TextField()
    status = models.CharField(max_length=10,choices = STATUS_CHOICES,default='unread')
    created_at = models.DateTimeField(auto_now_add=True)

    def mars_as_read(self):
        self.status = 'read'
        self.save()

    def __str__(self):
        return f"self.name,self.email,self.number,self.message"

@receiver(pre_save, sender=Restaurant)
def delete_old_logo_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_logo = Restaurant.objects.get(pk=instance.pk).logo
    except Restaurant.DoesNotExist:
        return

    new_logo = instance.logo
    if old_logo and old_logo != new_logo:
        if os.path.isfile(old_logo.path):
            os.remove(old_logo.path)

@receiver(post_delete, sender=Restaurant)
def delete_logo_on_delete(sender, instance, **kwargs):
    if instance.logo and os.path.isfile(instance.logo.path):
        os.remove(instance.logo.path)


@receiver(pre_save, sender=MenuItem)
def delete_old_menu_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # New object, skip

    try:
        old_image = MenuItem.objects.get(pk=instance.pk).image
    except MenuItem.DoesNotExist:
        return

    new_image = instance.image
    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)

@receiver(post_delete, sender=MenuItem)
def delete_menu_image_on_delete(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)


@receiver(pre_save, sender=Liquor)
def delete_old_menu_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # New object, skip

    try:
        old_image = Liquor.objects.get(pk=instance.pk).image
    except Liquor.DoesNotExist:
        return

    new_image = instance.image
    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)

@receiver(post_delete, sender=Liquor)
def delete_menu_image_on_delete(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)