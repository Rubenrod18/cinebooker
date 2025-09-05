import pytest


# pylint: disable=attribute-defined-outside-init, unused-argument
class TestBaseIntegration:
    @pytest.fixture(autouse=True)
    def integration_setup(self, app, faker):
        self.app = app
        self.faker = faker


class TestCliBaseIntegration(TestBaseIntegration):
    @pytest.fixture(autouse=True)
    def cli_integration_setup(self, runner):
        self.runner = runner
