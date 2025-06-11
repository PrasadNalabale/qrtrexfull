from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def get_category_labels(menu_items):
    return [
        ('veg', 'Vegetarian'),
        ('non-veg', 'Non-Vegetarian')
    ]

@register.filter
def star_rating(value):
    try:
        value = int(value)
    except:
        value = 0
    return "★" * value + "☆" * (5 - value)