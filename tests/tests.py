from django.test import TestCase
from wagtailbase.models import StandardIndexPage, StandardPage, StandardPageRelatedLink

class TestRelatedLink(TestCase):
    fixtures = ['wagtailbase.json']

    URL = 'http://www.duckduckgo.com/'

    def setUp(self):
        self.link = StandardPageRelatedLink.objects.get(id=1)


    def test_link(self):
        expected = self.URL
        self.assertEqual(expected, self.link.link)


class TestIndexPage(TestCase):
    fixtures = ['wagtailbase.json']

    # def setUp(self):
    #     self.index_page = StandardIndexPage()
    #     self.index_page.title = 'Standard Index Page'
    #     self.index_page.save()

    #     self.child_page = StandardPage()
    #     self.child_page.title = 'Standard Page'
    #     self.child_page.content = 'Standard page content'
    #     self.child_page.save()

    #     self.index_page.add_child(self.child_page)

    # def test_children(self):
    #     self.assertEqual(1, len(self.index_page.children))