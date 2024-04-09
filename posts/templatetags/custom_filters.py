from django import template
from django.utils.timesince import timesince as django_timesince
from datetime import datetime

register = template.Library()

@register.filter
def custom_timesince(value, now=None):
    if not now:
        now = datetime.now()
    difference = now - value
    days = difference.days
    return '%d day%s' % (days, 's' if days != 1 else '')
