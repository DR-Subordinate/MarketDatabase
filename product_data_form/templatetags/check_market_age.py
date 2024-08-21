import datetime
from django import template

register = template.Library()

@register.filter
def is_older_than_six_months(market_date):
    six_months_ago = datetime.date.today() - datetime.timedelta(days=6*30)
    return market_date < six_months_ago
