from django.test import TestCase
from django.urls import reverse


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')        
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_404_custom(self):
        response = self.client.get('page_not_found')
        self.assertTemplateUsed(response, 'core/404.html')
