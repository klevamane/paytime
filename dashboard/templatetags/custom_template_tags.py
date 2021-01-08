from __future__ import absolute_import

from django import template

register = template.Library()


@register.filter(name="humanize_number", is_safe=False)
def humanize_number(value, precision=2):
    try:
        int_val = int(value)
    except ValueError:
        raise template.TemplateSyntaxError(
            f"Value must be an integer. {value} is not an integer"
        )
    if int_val < 1000:
        return str(int_val)
    elif int_val < 1_000_000:
        return f"{ int_val/1000.0:.{precision}f}".rstrip("0").rstrip(".") + "K"
    else:
        return f"{int_val/1_000_000.0:.{precision}f}".rstrip("0").rstrip(".") + "M"
