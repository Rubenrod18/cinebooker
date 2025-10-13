from decimal import Decimal, InvalidOperation

import pytest

from app.utils.financials import apply_vat_rate
from tests.common.base_tests.test_base_unit import TestBaseUnit


class TestApplyVatRate(TestBaseUnit):
    @pytest.mark.parametrize(
        'net, vat, expected',
        [
            (Decimal('13.37'), Decimal('0.23'), Decimal('16.45')),
            (100, '0.10', Decimal('110.00')),
            ('13.37', 0.23, Decimal('16.45')),
            (0, 0.23, Decimal('0.00')),
            (Decimal('100.00'), Decimal('0'), Decimal('100.00')),
        ],
    )
    def test_apply_vat_rate_basic(self, net, vat, expected):
        """Basic conversions with default quantization to 2 decimals."""
        result = apply_vat_rate(net, vat)
        assert result == expected

    def test_apply_vat_rate_no_quantize_returns_precise_decimal(self):
        """If quantize_to is None, exact Decimal arithmetic should be returned."""
        res = apply_vat_rate(1, Decimal('0.3333'), quantize_to=None)
        assert res == Decimal('1.3333')

    def test_apply_vat_rate_rounding_half_up(self):
        """
        Ensure rounding is ROUND_HALF_UP by default. 2.005 -> 2.01 when quantized to 2 decimals.
        """
        result = apply_vat_rate(Decimal('2.005'), Decimal('0'), quantize_to=Decimal('0.01'))
        assert result == Decimal('2.01')

    def test_apply_vat_rate_negative_vat_behaves_as_discount(self):
        """Negative VAT acts like a discount (net reduced)."""
        result = apply_vat_rate(Decimal('100'), Decimal('-0.10'))
        assert result == Decimal('90.00')

    def test_apply_vat_rate_invalid_input_raises(self):
        """Non-numeric inputs should raise Decimal.InvalidOperation (propagated)."""
        with pytest.raises(InvalidOperation):
            apply_vat_rate('not-a-number', '0.23')
