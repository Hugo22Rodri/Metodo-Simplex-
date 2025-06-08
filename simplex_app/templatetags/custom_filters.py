from django import template

register = template.Library()

@register.filter
def get_item(lst, index):
    return lst[index]

@register.filter
def make_range(number):
    return range(number)