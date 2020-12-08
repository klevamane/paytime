from __future__ import absolute_import

from django import template

register = template.Library()


@register.filter(name="addcss")
def addcss(field, css):
    if field and field != "":
        return field.as_widget(attrs={"class": css})


@register.filter(name="lookup")
def lookup(dictionary, key):
    """Get dictionary item via template"""
    return dictionary.get(key.name)
