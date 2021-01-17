from __future__ import absolute_import

import json

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import (
    check_password,
    is_password_usable,
    make_password,
)
from django.test import TestCase
from django.urls import reverse

from dashboard.models import MessageCenter
from paytime import settings


class MessageCenterViewTest(TestCase):
    fixtures = ["users.json", "messages.json"]

    @classmethod
    def setUpTestData(cls):
        print(
            "setUpTestData: Run once to set up non-modified data for all class methods."
        )

    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")
        user = get_user_model().objects.create(email="fake@test.com", firstname="fake1")
        self.user_pwd = "fakePassword1@"
        user.set_password(self.user_pwd)
        user.save()
        self.user = user
        self.login_user()

    def create_user(self, password, email, **kwargs):
        user = get_user_model().objects.create(email=email)
        user.set_password(password)
        user.save()
        return user

    def test_user_send_message_pass(self):
        self.assertTrue(1)

    def login_user(self):
        self.client.login(email=self.user.email, password=self.user_pwd)

    def test_user_login(self):
        user = self.create_user(
            password="passwordTest1@", email="test@user.com", firstname="new_user"
        )
        # use password string because the current user password is hashed
        resp = self.client.post(
            reverse("account_login"),
            {"login": user.email, "password": "passwordTest1@"},
        )
        self.assertRedirects(
            resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False
        )

    def test_get_user_messages(self):
        response = self.client.get(reverse("message_inbox_view_url"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("inbox" in response.content.decode("utf-8"))

    def test_send_admin_msg(self):
        total_messages = MessageCenter.objects.all().count()
        response = self.client.post(
            reverse("message_new_view_url"),
            {"message": "This is a message to the admin", "subject": "Subject"},
        )
        self.assertEqual(MessageCenter.objects.all().count(), total_messages + 1)
        # assert that the message was sent by the logged in user
        last_msg = MessageCenter.objects.all().order_by("id").last()
        self.assertEqual(last_msg.sender, response.wsgi_request.user)
        self.assertEqual(last_msg.subject, "Subject")
