from django import template

register = template.Library()

@register.filter
def sum_values(queryset, attribute):
    total = 0
    for item in queryset:
        value = getattr(item, attribute, 0)
        try:
            total += float(value)
        except (ValueError, TypeError):
            pass
    return total