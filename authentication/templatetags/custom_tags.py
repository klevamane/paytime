from __future__ import absolute_import

from django import template

register = template.Library()


@register.filter(name="addcss")
def addcss(field, css):
    try:
        if field and field != "":
            return field.as_widget(attrs={"class": css})
    except AttributeError:
        pass


@register.filter(name="lookup")
def lookup(dictionary, key):
    try:
        """Get dictionary item via template"""
        return dictionary.get(key.name)
    except AttributeError:
        pass
