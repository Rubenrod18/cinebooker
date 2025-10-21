import pytest

from tests.common.base_tests.test_base_acceptance import TestBaseApi


# pylint: disable=attribute-defined-outside-init, unused-argument
class _TestBaseBookingEndpoints(TestBaseApi):
    @pytest.fixture(autouse=True)
    def base_setup(self, base_api_setup):
        self.base_path = f'{self.base_path}/bookings'
