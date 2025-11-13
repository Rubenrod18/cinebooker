from decimal import Decimal, ROUND_HALF_UP

Money = Decimal | int | float | str


def _to_decimal(value: Money) -> Decimal:
    return Decimal(str(value))


def apply_vat_rate(
    net_amount: Money,
    vat_rate: Money,
    quantize_to: Decimal | None = Decimal('0.01'),
) -> Decimal:
    """Convert net amount to gross amount by applying a VAT rate.

    Args
    ----
        net_amount: net price (Decimal, int, float or numeric string).
        vat_rate: VAT rate as a fraction (e.g. 0.23 for 23%).
        quantize_to: Decimal quantization (e.g. Decimal('0.01') for cents).
                     Set to None to skip rounding.

    Returns
    -------
        Decimal: gross amount (net * (1 + vat_rate)), optionally rounded.
    """
    net = _to_decimal(net_amount)
    rate = _to_decimal(vat_rate)
    gross = net * (Decimal('1') + rate)
    if quantize_to is not None:
        return gross.quantize(quantize_to, rounding=ROUND_HALF_UP)
    return gross


def calculate_vat_amount(
    net_amount: Money,
    vat_rate: Money,
    round_to: Decimal | None = Decimal('0.01'),
) -> Decimal:
    """Calculate the VAT amount from a net amount.

    Args
    ----
        net_amount: The net price (int, float, str, or Decimal).
        vat_rate: VAT rate as a decimal fraction (e.g., 0.23 for 23% VAT).
        round_to: Optional Decimal for rounding the result.
                  Defaults to Decimal('0.01') for rounding to cents.
                  Set to None to skip rounding.

    Returns
    -------
        Decimal: VAT amount (net_amount * vat_rate), optionally rounded.
    """
    net = _to_decimal(net_amount)
    rate = _to_decimal(vat_rate)
    vat_amount = net * rate
    if round_to is not None:
        return vat_amount.quantize(round_to, rounding=ROUND_HALF_UP)
    return vat_amount


def decimal_to_int(amount: Money, quantize_to: Decimal | None = Decimal('0.01')) -> int:
    """Convert a decimal monetary value to an integer amount for Stripe.

    Args
    ----
        amount: The monetary value (Decimal, int, float, or str).
        quantize_to: Decimal quantization step before conversion.

    Returns
    -------
        int: Integer representation of the amount (e.g. cents).
    """
    dec = _to_decimal(amount)

    if quantize_to is not None:
        dec = dec.quantize(quantize_to, rounding=ROUND_HALF_UP)

    return int((dec * 100).to_integral_value(rounding=ROUND_HALF_UP))
