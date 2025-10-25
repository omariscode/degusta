from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import product_model, user_model


class CheckoutTests(APITestCase):
	def setUp(self):
		self.user = user_model.User.objects.create(email='t@t.com', name='T', phone='923000001')
		self.user.set_password('pass')
		self.user.is_active = True
		self.user.save()

		self.product = product_model.Product.objects.create(name='P', price=10.0, stock=10)

	def test_checkout_and_my_orders(self):
		# obtain token
		resp = self.client.post(reverse('token_obtain_pair'), {'phone': self.user.phone, 'password': 'pass'}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		token = resp.data['access']

		# checkout
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
		checkout_payload = {'delivery_address': 'Rua X', 'items': [{'product': self.product.id, 'qty': 2}]}
		resp = self.client.post(reverse('checkout'), checkout_payload, format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

		# my orders
		resp = self.client.get(reverse('my-orders'))
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertTrue(len(resp.data) >= 1)
from django.test import TestCase

# Create your tests here.
