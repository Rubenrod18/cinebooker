import pytest


# pylint: disable=attribute-defined-outside-init, unused-argument
class TestBaseAcceptance:
    @pytest.fixture(autouse=True)
    def acceptance_setup(self, app, client, faker):
        self.app = app
        self.client = client
        self.faker = faker


class TestBaseApi(TestBaseAcceptance):
    @pytest.fixture(autouse=True)
    def base_api_setup(self):
        self.base_path = ''
