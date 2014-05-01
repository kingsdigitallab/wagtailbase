from base import AbstractRelatedLink, BaseIndexPage, BaseRichTextPage

from datetime import date

from django.db import models
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
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

    @property
    def active_months(self):
        return self.posts.values('date').distinct()

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

    def process_date_filter(self, date_params):
        date_filter = {}

        try:
            year = date_params.pop(0)

            date_filter['date__year'] = int(year)
        except IndexError:
            # no year specified in URL
            pass

        try:
            month = date_params.pop(0)

            m = self.get_month_number(month.title())

            if m:
                date_filter['date__month'] = m
            else:
                date_filter['date__month'] = month

        except IndexError:
            # No month specified in URL
            pass

        try:
            day = date_params.pop(0)
            date_filter['date__day'] = day
        except IndexError:
            pass

        return date_filter

    def filter_serve(self, request, filter_type, *args):
        """Renders the blog posts filtered by arguments."""

        ft = filter_type.lower()

        if ft == 'author':
            posts = self.posts.filter(owner__username=args[0])

        elif ft == 'tag':
            posts = self.posts.filter(tags__name=args[0])
        elif ft == 'date':
            date_filter = self.process_date_filter(list(args))

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
                       ('filter_' + filter_type): args,
                       'posts': posts})


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
