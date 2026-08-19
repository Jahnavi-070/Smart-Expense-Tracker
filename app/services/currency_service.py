"""
Currency Service: Handles exchange rates, amount conversion, and live currency calculator.
"""

class CurrencyService:
    # Baseline Exchange Rates (USD Base)
    EXCHANGE_RATES_TO_USD = {
        'USD': 1.0,
        'EUR': 0.92,
        'GBP': 0.79,
        'INR': 83.50,
        'CAD': 1.36,
        'AUD': 1.52,
        'JPY': 155.00,
        'AED': 3.67,
        'SGD': 1.35,
        'CHF': 0.91,
        'CNY': 7.24,
        'BRL': 5.15,
        'KRW': 1370.00,
        'MXN': 17.00
    }

    @classmethod
    def get_conversion_rate(cls, from_currency: str, to_currency: str) -> float:
        """Calculates exchange rate between any two supported currencies."""
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:
            return 1.0

        rate_from = cls.EXCHANGE_RATES_TO_USD.get(from_currency, 1.0)
        rate_to = cls.EXCHANGE_RATES_TO_USD.get(to_currency, 1.0)

        # Convert: (amount / rate_from) * rate_to
        return rate_to / rate_from

    @classmethod
    def convert_amount(cls, amount: float, from_currency: str, to_currency: str) -> float:
        """Converts an amount from one currency to another."""
        rate = cls.get_conversion_rate(from_currency, to_currency)
        return round(amount * rate, 2)

    @classmethod
    def convert_user_data(cls, user, new_currency: str):
        """
        Converts all existing transaction amounts and budget limits
        for a user from user.currency to new_currency using exchange rates.
        """
        old_currency = user.currency
        if old_currency == new_currency:
            return 0, 0, 1.0

        rate = cls.get_conversion_rate(old_currency, new_currency)

        # Convert transactions
        transactions = user.transactions.all()
        for t in transactions:
            t.amount = round(t.amount * rate, 2)

        # Convert budgets
        budgets = user.budgets.all()
        for b in budgets:
            b.amount = round(b.amount * rate, 2)

        user.currency = new_currency
        return len(transactions), len(budgets), rate
