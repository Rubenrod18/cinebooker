import os

from app.models import AuthUser, Customer
from tests.acceptance.routers.customer._base_customers_test import _TestBaseCustomerEndpoints


# pylint: disable=attribute-defined-outside-init
class TestCreateCustomerEndpoint(_TestBaseCustomerEndpoints):
    def test_create_customer(self):
        payload = {
            'first_name': self.faker.first_name(),
            'last_name': self.faker.last_name(),
            'email': self.faker.email(),
            'password': os.getenv('TEST_USER_PASSWORD'),
            'birth_date': self.faker.date(),
        }

        response = self.client.post(url=self.base_path, json=payload)
        json_response = response.json()

        assert json_response
        assert json_response['first_name'] == payload['first_name']
        assert json_response['last_name'] == payload['last_name']
        assert json_response['email'] == payload['email']
        assert json_response['birth_date'] == str(payload['birth_date'])

        with self.app.container.session() as session:
            auth_user = session.query(AuthUser).first()
            assert auth_user.email == payload['email']
            assert auth_user.inactive_at is None
            assert auth_user.password != payload['password']

            customer = session.query(Customer).first()
            assert customer.auth_user_id == auth_user.id
