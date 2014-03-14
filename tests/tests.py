from django.test import TestCase
from wagtailbase.models import (
    IndexPage,
    RichTextPage,
    IndexPageRelatedLink)

from wagtail.wagtailcore.models import Page


class TestRelatedLink(TestCase):
    fixtures = ['wagtailbase.json', 'wagtailcore.json']

    def setUp(self):
        self.link = IndexPageRelatedLink.objects.get(id=1)

    def test_link(self):
        self.assertEqual('http://www.duckduckgo.com/', self.link.link)


class TestIndexPage(TestCase):
    fixtures = ['wagtailbase.json', 'wagtailcore.json']

    def setUp(self):
        self.index_page = IndexPage.objects.filter(slug='standard-index').first()
        self.child_page = RichTextPage.objects.filter(slug="first-page-index").first()

    def test_children(self):
        #self.assertEqual(1, len(self.index_page.children))

        self.assertEqual(self.child_page, self.index_page.get_children().first().specific)
        self.assertEqual(self.child_page, self.index_page.children.first())

        #self.assertIsNone(self.child_page.children)
