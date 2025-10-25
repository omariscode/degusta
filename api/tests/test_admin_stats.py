from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models.user_model import User
from ..models.order_model import Order
from django.utils import timezone
from datetime import timedelta
import json

class AdminStatsTests(TestCase):
    def setUp(self):
        # Create admin user
        self.admin = User.objects.create_superuser(
            'admin@test.com', 'testpass123')
        
        # Create normal user for orders
        self.user = User.objects.create_user(
            'user@test.com', 'testpass123')
        
        # Create API client
        self.client = APIClient()
        
        # Create test orders
        now = timezone.now()
        Order.objects.create(
            user=self.user,
            total=100.00,
            address='Test Address',
            items=[{'id': 1, 'quantity': 2}],
            status='delivered',
            created_at=now
        )
        Order.objects.create(
            user=self.user,
            total=200.00,
            address='Test Address 2',
            items=[{'id': 2, 'quantity': 1}],
            status='paid',
            created_at=now - timedelta(days=1)
        )

    def test_admin_stats_unauthorized(self):
        """Test that non-admin users cannot access stats"""
        url = reverse('admin-stats')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_stats_authorized(self):
        """Test that admin can get stats with correct format"""
        url = reverse('admin-stats')
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = json.loads(res.content)
        
        # Check response structure
        self.assertIn('cards', data)
        self.assertIn('daily_sales', data)
        
        # Check cards data
        cards = data['cards']
        self.assertIn('total_sales', cards)
        self.assertIn('customers', cards)
        self.assertIn('todays_orders', cards)
        self.assertIn('completion_rate', cards)
        
        # Check daily sales structure
        daily_sales = data['daily_sales']
        self.assertTrue(isinstance(daily_sales, list))
        if daily_sales:  # if there are sales in the test period
            sale = daily_sales[0]
            self.assertIn('day', sale)
            self.assertIn('total', sale)
            self.assertIn('count', sale)
            
        # Verify total sales matches test data
        total_sales = cards['total_sales']['value']
        self.assertEqual(float(total_sales), 300.00)  # Sum of test orders