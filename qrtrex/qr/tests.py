from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.files.base import ContentFile
from unittest.mock import patch
import base64
import json
import razorpay

class MembershipPaymentSuccessTest(TestCase):
    def setUp(self):
        MEMBERSHIP_PRICING = {
            'monthly': {'amount': 99900, 'duration': 1},        
            'semi annual': {'amount': 539400, 'duration': 6},   
            'annual': {'amount': 958800, 'duration': 12},       
        }
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.order_id = "order_test_id"
        self.payment_id = "pay_test_id"
        self.signature = "test_signature"

        session = self.client.session
        session['restaurant_form'] = {
            "restaurant_name": "Test Restaurant",
            "address": "123 Test Lane",
            "description": "A test place",
            "restaurant_type": "Cafe",
            "mobile": "1234567890",
            "wifi": True,
            "category": "Test Category",
            "fassai": "5871589123",
            "membership_type": "monthly"
        }
        session['has_logo'] = True
        session['restaurant_logo_name'] = 'logo.png'
        session['restaurant_logo_content'] = base64.b64encode(b'TestImageData').decode('utf-8')
        session.save()

        from qr.models import Payment  # Replace with your actual app name
        Payment.objects.create(
            user=self.user,
            order_id=self.order_id,
            amount="999",
            status="created"
        )

    @patch("razorpay.utility.verify_payment_signature", return_value=True)
    def test_membership_payment_success(self, mock_verify_signature):
        url = reverse('membership_payment_success')  # Adjust as needed
        data = {
            "razorpay_order_id": self.order_id,
            "razorpay_payment_id": self.payment_id,
            "razorpay_signature": self.signature
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

        print("Response JSON:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
