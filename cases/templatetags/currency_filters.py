from django import template

register = template.Library()

CURRENCY_SYMBOLS = {
    # Fiat Currencies
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'AUD': 'A$',
    'CAD': 'C$',
    'ZAR': 'R',
    'CHF': 'CHF',
    'CNY': '¥',
    'INR': '₹',
    'SGD': 'S$',
    'NZD': 'NZ$',
    'HKD': 'HK$',
    'AED': 'د.إ',
    'BRL': 'R$',
    'MXN': 'Mex$',
    # Cryptocurrencies
    'BTC': '₿',
    'ETH': 'Ξ',
    'USDT': '₮',
    'LAC': 'L'
}

@register.filter
def currency_symbol(value, currency_code):
    """
    Template filter to format a value with its currency symbol.
    Usage: {{ value|currency_symbol:currency_code }}
    Example: {{ 42.50|currency_symbol:'USD' }} outputs: $42.50
    """
    symbol = CURRENCY_SYMBOLS.get(currency_code, '$')
    
    # Special formatting for cryptocurrencies
    if currency_code in ['BTC', 'ETH', 'USDT', 'LAC']:
        # Format with 8 decimal places for cryptocurrencies
        formatted_value = '{:.8f}'.format(float(value))
    else:
        # Format with 2 decimal places for fiat currencies
        formatted_value = '{:.2f}'.format(float(value))
    
    # Handle right-to-left currencies (like AED)
    if currency_code == 'AED':
        return f"{formatted_value} {symbol}"
    
    return f"{symbol}{formatted_value}"
