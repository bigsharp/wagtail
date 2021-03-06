from django.test import TestCase, RequestFactory

from wagtail.wagtailcore.models import Page, Site
from wagtail.tests.models import RoutablePageTest, routable_page_external_view
from wagtail.contrib.wagtailroutablepage.templatetags.wagtailroutablepage_tags import routablepageurl


class TestRoutablePage(TestCase):
    def setUp(self):
        self.home_page = Page.objects.get(id=2)
        self.routable_page = self.home_page.add_child(instance=RoutablePageTest(
            title="Routable Page",
            slug='routable-page',
            live=True,
        ))

    def test_resolve_main_view(self):
        view, args, kwargs = self.routable_page.resolve_subpage('/')

        self.assertEqual(view, self.routable_page.main)
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {})

    def test_resolve_archive_by_year_view(self):
        view, args, kwargs = self.routable_page.resolve_subpage('/archive/year/2014/')

        self.assertEqual(view, self.routable_page.archive_by_year)
        self.assertEqual(args, ('2014', ))
        self.assertEqual(kwargs, {})

    def test_resolve_archive_by_author_view(self):
        view, args, kwargs = self.routable_page.resolve_subpage('/archive/author/joe-bloggs/')

        self.assertEqual(view, self.routable_page.archive_by_author)
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {'author_slug': 'joe-bloggs'})

    def test_resolve_external_view(self):
        view, args, kwargs = self.routable_page.resolve_subpage('/external/joe-bloggs/')

        self.assertEqual(view, routable_page_external_view)
        self.assertEqual(args, ('joe-bloggs', ))
        self.assertEqual(kwargs, {})

    def test_reverse_main_view(self):
        url = self.routable_page.reverse_subpage('main')

        self.assertEqual(url, '')

    def test_reverse_archive_by_year_view(self):
        url = self.routable_page.reverse_subpage('archive_by_year', args=('2014', ))

        self.assertEqual(url, 'archive/year/2014/')

    def test_reverse_archive_by_author_view(self):
        url = self.routable_page.reverse_subpage('archive_by_author', kwargs={'author_slug': 'joe-bloggs'})

        self.assertEqual(url, 'archive/author/joe-bloggs/')

    def test_reverse_external_view(self):
        url = self.routable_page.reverse_subpage('external_view', args=('joe-bloggs', ))

        self.assertEqual(url, 'external/joe-bloggs/')

    def test_get_main_view(self):
        response = self.client.get(self.routable_page.url)

        self.assertContains(response, "MAIN VIEW")

    def test_get_archive_by_year_view(self):
        response = self.client.get(self.routable_page.url + 'archive/year/2014/')

        self.assertContains(response, "ARCHIVE BY YEAR: 2014")

    def test_get_archive_by_author_view(self):
        response = self.client.get(self.routable_page.url + 'archive/author/joe-bloggs/')

        self.assertContains(response, "ARCHIVE BY AUTHOR: joe-bloggs")

    def test_get_external_view(self):
        response = self.client.get(self.routable_page.url + 'external/joe-bloggs/')

        self.assertContains(response, "EXTERNAL VIEW: joe-bloggs")


class TestRoutablePageTemplateTag(TestRoutablePage):
    def setUp(self):
        super(TestRoutablePageTemplateTag, self).setUp()
        self.rf = RequestFactory()
        self.request = self.rf.get(self.routable_page.url)
        self.request.site = Site.find_for_request(self.request)
        self.context = {'request': self.request}

    def test_templatetag_reverse_main_view(self):
        url = routablepageurl(self.context, self.routable_page,
                              'main')
        self.assertEqual(url, self.routable_page.url)

    def test_templatetag_reverse_archive_by_year_view(self):
        url = routablepageurl(self.context, self.routable_page,
                              'archive_by_year', '2014')

        self.assertEqual(url, self.routable_page.url + 'archive/year/2014/')

    def test_templatetag_reverse_archive_by_author_view(self):
        url = routablepageurl(self.context, self.routable_page,
                              'archive_by_author', author_slug='joe-bloggs')

        self.assertEqual(url, self.routable_page.url + 'archive/author/joe-bloggs/')

    def test_templatetag_reverse_external_view(self):
        url = routablepageurl(self.context, self.routable_page,
                              'external_view', 'joe-bloggs')

        self.assertEqual(url, self.routable_page.url + 'external/joe-bloggs/')
