#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mock import patch, Mock, MagicMock
from collections import namedtuple
from django.urls import reverse
from django.test import TestCase, Client
from django.test import Client
from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from urllib.parse import parse_qs
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from common.djangoapps.student.tests.factories import UserFactory
import re
import json
import uuid
import base64
import urllib.parse

from .views import create_auto_login, EolAutoLoginView
from .models import EolAutoLogin

class TestAutoLogin(ModuleStoreTestCase):
    def setUp(self):
        super(TestAutoLogin, self).setUp()
        self.client = Client()
        with patch('common.djangoapps.student.models.cc.User.save'):
            self.user = UserFactory(
                username='testuser1',
                password='12345',
                email='test555@test.test')
            self.user2 = UserFactory(
                username='testuser2',
                password='12345',
                email='test222@test.test')
        self.auto_login = EolAutoLogin.objects.create(user=self.user, uuid=str(uuid.uuid4()))

    def test_login(self):
        """
            Test normal process
        """
        token = base64.b64encode('{}/{}/{}'.format(self.auto_login.user.id, self.auto_login.user.username, self.auto_login.uuid).encode("utf-8")).decode("utf-8")
        response = self.client.get("{}?token={}".format(reverse('eol_auto_login:login'), token))
        self.assertEqual(response.status_code, 302)
        # Check that session and CSRF are set in the response
        for cookie in ['csrftoken', 'sessionid']:
            self.assertIn(cookie, response.cookies)
            self.assertTrue(response.cookies[cookie].value)

    def test_login_no_token(self):
        """
            Test without token
        """
        token = ""
        response = self.client.get("{}?token={}".format(reverse('eol_auto_login:login'), token))
        self.assertEqual(response.status_code, 404)
    
    def test_login_wrong_token(self):
        """
            Test wrong token
        """
        token = "asdhjaskdhsajkdsajkdsaj"
        result = self.client.get("{}?token={}".format(reverse('eol_auto_login:login'), token))
        self.assertEqual(result.status_code, 404)

    def test_login_wrong_payload(self):
        """
            Test wrong payload
        """
        # wrong username
        token = base64.b64encode('{}/{}/{}'.format(self.auto_login.user.id, "asdasdasd", self.auto_login.uuid).encode("utf-8")).decode("utf-8")
        result = self.client.get("{}?token={}".format(reverse('eol_auto_login:login'), token))
        self.assertEqual(result.status_code, 404)
        token = base64.b64encode('{}/{}/{}'.format(self.auto_login.user.id, self.user2.username, self.auto_login.uuid).encode("utf-8")).decode("utf-8")
        result = self.client.get("{}?token={}".format(reverse('eol_auto_login:login'), token))
        self.assertEqual(result.status_code, 404)
        #wrong id
        token = base64.b64encode('{}/{}/{}'.format("123456", self.auto_login.user.username, self.auto_login.uuid).encode("utf-8")).decode("utf-8")
        result = self.client.get("{}?token={}".format(reverse('eol_auto_login:login'), token))
        self.assertEqual(result.status_code, 404)
        #wrong uuid
        token = base64.b64encode('{}/{}/{}'.format(self.auto_login.user.id, self.auto_login.user.username, "aadas45d4a5ds45asd64f56sad").encode("utf-8")).decode("utf-8")
        result = self.client.get("{}?token={}".format(reverse('eol_auto_login:login'), token))
        self.assertEqual(result.status_code, 404)
    
    def test_create_auto_login(self):
        """
            Test normal process
        """
        link = create_auto_login(self.user2.username)
        self.assertTrue(EolAutoLogin.objects.filter(user=self.user2).exists())
        LMS_BASE = settings.LMS_BASE
        auto_login2 = EolAutoLogin.objects.get(user=self.user2)
        token = base64.b64encode('{}/{}/{}'.format(self.user2.id, self.user2.username, auto_login2.uuid).encode("utf-8")).decode("utf-8")
        self.assertEqual('{}{}?token={}'.format(LMS_BASE, reverse('eol_auto_login:login'), token), link)

    def test_create_auto_login_exists_user(self):
        """
            Test normal process when user exists
        """
        aux = self.auto_login.uuid
        link = create_auto_login(self.user.username)
        LMS_BASE = settings.LMS_BASE
        auto_login2 = EolAutoLogin.objects.get(user=self.user)
        token = base64.b64encode('{}/{}/{}'.format(self.user.id, self.user.username, auto_login2.uuid).encode("utf-8")).decode("utf-8")
        self.assertEqual('{}{}?token={}'.format(LMS_BASE, reverse('eol_auto_login:login'), token), link)
        self.assertNotEqual(aux, auto_login2.uuid)
    
    def test_create_auto_login_wrong_username(self):
        """
            Test normal process when username is wrong
        """
        link = create_auto_login('dasdasdasd')
        self.assertEqual(link, None)