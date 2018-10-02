import sys
import json

from django.test import TestCase
from django.contrib.auth.models import User
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


class AdminBasicTest(TestCase):

    fixtures = ['users.json']

    def _login(self, username, password):
        try:
            user = User.objects.get(username=username)
            self.client.force_login(user)
        except AttributeError:  # in Django<1.9
            self.client.login(username=username, password=password)

    def test_admin_loads(self):
        for (username, password) in (('superuser', '123'), ('staff', '123')):
            self._login(username, password)
            response = self.client.get('/admin/')
            self.assertEqual(response.status_code, 200)
            self.client.logout()

    def test_custom_menu_media(self):
        self._login('superuser', '123')
        response = self.client.get('/admin/')
        self.assertContains(response, '<link rel="stylesheet" href="/static/test_app/menu.css" type="text/css" media="all"/>')
        self.assertContains(response, '/static/test_app/menu.js')
        self.client.logout()

    def test_custom_dashboard_media(self):
        self._login('superuser', '123')
        response = self.client.get('/admin/')
        self.assertContains(response, '<link rel="stylesheet" href="/static/test_app/dashboard.css" type="text/css" media="all"/>')
        self.assertContains(response, '/static/test_app/dashboard.js')
        self.client.logout()

    def test_permissions(self):
        self._login('staff', '123')
        index = self.client.get('/admin/')
        self.assertContains(index, 'Bars')
        self.assertNotContains(index, 'Foos')
        self.assertNotContains(index, 'Users')
        self.assertContains(index, 'Test app menu')
        self.client.logout()

        self._login('superuser', '123')
        super_index = self.client.get('/admin/')
        self.assertContains(super_index, 'Bars')
        self.assertContains(super_index, 'Foos')
        self.assertContains(super_index, 'Test app menu')
        self.assertContains(super_index, 'Users', 4) # menu and dashboard items
        self.client.logout()
        self.client.logout()

    def test_app_index(self):
        self._login('staff', '123')
        res = self.client.get('/admin/test_app/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Bars')
        self.assertNotContains(res, 'Foos')
        self.client.logout()

        self._login('superuser', '123')
        res = self.client.get('/admin/test_app/')
        self.assertContains(res, 'Foos')
        self.assertContains(res, 'Bars')
        self.assertContains(res, 'Users', 2) # only items from menu
