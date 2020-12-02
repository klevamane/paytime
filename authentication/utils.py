from __future__ import absolute_import

from django.utils.html import strip_tags


def clean_attr(attr):
    return strip_tags(attr.strip())
