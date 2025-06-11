import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import MenuItem,Restaurant

@receiver(post_delete, sender=MenuItem)
def delete_menu_item_image_on_delete(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

@receiver(pre_save, sender=MenuItem)
def delete_old_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # It's a new object, no old image
    try:
        old_item = MenuItem.objects.get(pk=instance.pk)
    except MenuItem.DoesNotExist:
        return
    if old_item.image and old_item.image != instance.image:
        if os.path.isfile(old_item.image.path):
            os.remove(old_item.image.path)

@receiver(post_delete, sender=Restaurant)
def delete_restaurant_images_on_delete(sender, instance, **kwargs):
    # If the restaurant has a logo, delete it
    if instance.logo and os.path.isfile(instance.logo.path):
        os.remove(instance.logo.path)

    # Now delete all images related to MenuItems for this restaurant
    menu_items = MenuItem.objects.filter(restaurant=instance)
    for item in menu_items:
        if item.image and os.path.isfile(item.image.path):
            os.remove(item.image.path)
