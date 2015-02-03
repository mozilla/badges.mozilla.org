import json
from nose.tools import eq_, ok_
from django.test import TestCase

class BadgesViewsTests(TestCase):

    def test_contribute_json(self):
        response = self.client.get('/contribute.json', follow=True)
        eq_(response.status_code, 200)
        # should be valid JSON
        ok_(json.loads(response.content))
        eq_(response['Content-Type'], 'application/json')
