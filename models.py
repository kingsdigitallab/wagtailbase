from base import AbstractRelatedLink, BaseIndexPage, BaseRichTextPage

from datetime import date

from django.db import models
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.conf.urls import url
import calendar

from django.http import Http404

from taggit.models import TaggedItemBase

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.models import Orderable, Page


import logging
logger = logging.getLogger(__name__)


class IndexPage(BaseIndexPage):
    search_name = 'Index Page'

    def serve(self, request):
        """Renders the children pages."""
        pages = self.children

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(pages, settings.ITEMS_PER_PAGE)

        try:
            pages = paginator.page(page)
        except EmptyPage:
            pages = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            pages = paginator.page(1)

        return render(request, self.template, {'self': self, 'pages': pages})


class IndexPageRelatedLink(Orderable, AbstractRelatedLink):
    page = ParentalKey('wagtailbase.IndexPage',
                       related_name='related_links')

IndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('introduction', classname='full'),
    InlinePanel(IndexPage, 'related_links', label='Related links')
]


class RichTextPage(BaseRichTextPage):
    search_name = 'Rich Text Page'


class RichTextPageRelatedLink(Orderable, AbstractRelatedLink):
    page = ParentalKey('wagtailbase.RichTextPage',
                       related_name='related_links')

RichTextPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('content', classname='full'),
    InlinePanel(RichTextPage, 'related_links', label='Related links')
]


class HomePage(BaseRichTextPage):
    search_name = 'Home Page'

    class Meta:
        verbose_name = 'Homepage'

HomePage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('content', classname='full')
]


class BlogIndexPage(BaseIndexPage):
    search_name = 'Blog'

    @property
    def posts(self):
        """Returns a list of the blog posts that are children of this page."""
        return BlogPost.objects.filter(
            live=True, path__startswith=self.path).order_by('-date')

    @property
    def active_months(self):
        dates = self.posts.values('date').distinct()
        new_dates = set([date(d['date'].year, d['date'].month, 1)
                        for d in dates])

        return sorted(new_dates, reverse=True)

    def get_subpage_urls(self):
        return [
            url(r'^$', self.serve, name='main'),
            url(r'^author/(?P<author>\w+)/$',
                self.archive, name='archive_author'),
            url(r'^tag/(?P<tag>\w+)/$', self.archive, name='archive_tag'),
            url((r'^date'
                 r'/(?P<year>\d{4})'
                 r'/$'),
                self.archive, name='archive_date'),
            url((r'^date'
                 r'/(?P<year>\d{4})'
                 r'/(?P<month>(?:\w+|\d{1,2}))'
                 r'/$'),
                self.archive, name='archive_date'),
            url((r'^date'
                 r'/(?P<year>\d{4})'
                 r'/(?P<month>(?:\w+|\d{1,2}))'
                 r'/(?P<day>\d{1,2})'
                 r'/$'),
                self.archive, name='archive_date'),
        ]

    def serve(self, request):
        """Renders the blog posts."""
        posts = self.posts

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(posts, settings.ITEMS_PER_PAGE)

        try:
            posts = paginator.page(page)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            posts = paginator.page(1)

        return render(request, self.template, {'self': self, 'posts': posts})

    def archive(self, request,
                author=None,
                tag=None,
                year=None,
                month=None,
                day=None):
        """Renders filtered blog posts."""

        ft = None
        filter_type = None
        filter_format = None

        if author:
            posts = self.posts.filter(owner__username=author)
            ft = ('author', author)

        elif tag:
            posts = self.posts.filter(tags__name=tag)
            ft = ('tag', tag)

        elif year:
            date_filter = {'date__year': int(year)}
            date_factory = [int(year)]
            date_format = ['Y']

            if month:
                m = self.get_month_number(month.title())

                if m:
                    date_filter['date__month'] = m
                    date_factory.append(int(m))
                else:
                    date_filter['date__month'] = month
                    date_factory.append(int(month))

                date_format.append('N')
            else:
                date_factory.append(1)

            if day:
                date_filter['date__day'] = int(day)
                date_factory.append(int(day))
                date_format.append('d')
            else:
                date_factory.append(1)

            ft = ('date', date(*date_factory))
            filter_format = ' '.join(reversed(date_format))

            try:
                posts = self.posts.filter(**date_filter)
            except ValueError:
                # Invalid date filter
                raise Http404
        else:
            raise Http404

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(posts, settings.ITEMS_PER_PAGE)

        try:
            posts = paginator.page(page)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            posts = paginator.page(1)

        return render(request,
                      self.template,
                      {'self': self,
                       'posts': posts,
                       'filter': ft[1],
                       'filter_type': ft[0],
                       'filter_format': filter_format
                       })

    def get_month_number(self, month):
        names = dict((v, k) for k, v in enumerate(calendar.month_name))
        abbrs = dict((v, k) for k, v in enumerate(calendar.month_abbr))

        month_str = month.title()

        try:
            return names[month_str]
        except KeyError:
            try:
                return abbrs[month_str]
            except KeyError:
                return 0


class BlogIndexPageRelatedLink(Orderable, AbstractRelatedLink):
    page = ParentalKey('wagtailbase.BlogIndexPage',
                       related_name='related_links')

BlogIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('introduction', classname='full'),
    InlinePanel(BlogIndexPage, 'related_links', label='Related links')
]


class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey('wagtailbase.BlogPost',
                                 related_name='tagged_items')


class BlogPost(BaseRichTextPage):
    date = models.DateField('Post Date', default=date.today)
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)

    search_name = 'Blog post'

    @property
    def blog_index(self):
        # Find blog index in ancestors
        for ancestor in reversed(self.get_ancestors()):
            if isinstance(ancestor.specific, BlogIndexPage):
                return ancestor

        # No ancestors are blog indexes,
        # just return first blog index in database
        return BlogIndexPage.objects.first()


class BlogPostRelatedLink(Orderable, AbstractRelatedLink):
    page = ParentalKey('wagtailbase.BlogPost', related_name='related_links')

BlogPost.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('date'),
    FieldPanel('content', classname='full'),
    InlinePanel(BlogPost, 'related_links', label='Related links')
]

BlogPost.promote_panels = Page.promote_panels[:]
BlogPost.promote_panels.insert(0, FieldPanel('tags'))
