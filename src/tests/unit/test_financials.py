from decimal import Decimal, InvalidOperation

import pytest

from app.utils import financials
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
        result = financials.apply_vat_rate(net, vat)
        assert result == expected

    def test_apply_vat_rate_no_quantize_returns_precise_decimal(self):
        """If quantize_to is None, exact Decimal arithmetic should be returned."""
        res = financials.apply_vat_rate(1, Decimal('0.3333'), quantize_to=None)
        assert res == Decimal('1.3333')

    def test_apply_vat_rate_rounding_half_up(self):
        """
        Ensure rounding is ROUND_HALF_UP by default. 2.005 -> 2.01 when quantized to 2 decimals.
        """
        result = financials.apply_vat_rate(Decimal('2.005'), Decimal('0'), quantize_to=Decimal('0.01'))
        assert result == Decimal('2.01')

    def test_apply_vat_rate_negative_vat_behaves_as_discount(self):
        """Negative VAT acts like a discount (net reduced)."""
        result = financials.apply_vat_rate(Decimal('100'), Decimal('-0.10'))
        assert result == Decimal('90.00')

    def test_apply_vat_rate_invalid_input_raises(self):
        """Non-numeric inputs should raise Decimal.InvalidOperation (propagated)."""
        with pytest.raises(InvalidOperation):
            financials.apply_vat_rate('not-a-number', '0.23')


class TestDecimalToInt(TestBaseUnit):
    @pytest.mark.parametrize(
        'amount, expected',
        [
            (Decimal('10.00'), 1_000),
            (Decimal('19.99'), 1_999),
            (Decimal('0.01'), 1),
            (100, 10_000),
            ('5.25', 525),
            (19.999, 2_000),  # rounding test
            (Decimal('19.994'), 1_999),  # rounding down
        ],
    )
    def test_decimal_to_int_standard(self, amount, expected):
        assert financials.decimal_to_int(amount) == expected

    def test_decimal_to_int_rounding_behavior(self):
        """Ensure ROUND_HALF_UP behavior is respected."""
        val = Decimal('1.234')
        result = financials.decimal_to_int(val)
        # 1.234 * 100 = 123.4 -> rounds to 123
        assert result == 123

        val2 = Decimal('1.235')
        result2 = financials.decimal_to_int(val2)
        # 1.235 * 100 = 123.5 -> rounds to 124 (half up)
        assert result2 == 124

    def test_decimal_to_int_with_quantization(self):
        """Custom quantization should work correctly."""
        result = financials.decimal_to_int(Decimal('1.2399'), quantize_to=Decimal('0.001'))
        # quantize to 0.001 -> 1.240 * 100 = 124
        assert result == 124


class TestCalculateVatAmount(TestBaseUnit):
    def test_basic_vat(self):
        assert financials.calculate_vat_amount(100, 0.23, round_to=Decimal('0.01')) == Decimal('23.00')

    def test_float_input(self):
        assert financials.calculate_vat_amount(99.99, 0.20, round_to=Decimal('0.01')) == Decimal('20.00')

    def test_string_input(self):
        assert financials.calculate_vat_amount('150.50', '0.10', round_to=Decimal('0.01')) == Decimal('15.05')

    def test_no_rounding(self):
        # NOTE: Exact decimal without rounding
        assert financials.calculate_vat_amount(100, 0.3333, round_to=None) == Decimal('33.33')

    def test_zero_vat(self):
        assert financials.calculate_vat_amount(100, 0, round_to=Decimal('0.01')) == Decimal('0.00')

    def test_zero_amount(self):
        assert financials.calculate_vat_amount(0, 0.23, round_to=Decimal('0.01')) == Decimal('0.00')
