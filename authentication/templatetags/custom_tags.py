from __future__ import absolute_import

from django import template

register = template.Library()


@register.filter(name="addcss")
def addcss(field, css):
    return field.as_widget(attrs={"class": css})
