from django import template

register = template.Library()

@register.filter
def sum_total_price(cart_items):
    """
    Custom filter to calculate the sum of total_price for items in the cart.
    """
    return sum(item['total_price'] for item in cart_items if 'total_price' in item)