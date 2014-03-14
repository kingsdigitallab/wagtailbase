from base import AbstractRelatedLink, BaseIndexPage, BaseRichTextPage

from datetime import date

from django.db import models
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from taggit.models import TaggedItemBase

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.models import Orderable


class IndexPage(BaseIndexPage):
    search_name = 'Index Page'


class IndexPageRelatedLink(Orderable, AbstractRelatedLink):
    page = ParentalKey(
        'wagtailbase.IndexPage', related_name='related_links')

IndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('introduction', classname='full'),
    InlinePanel(IndexPage, 'related_links', label='Related links')
]


class RichTextPage(BaseRichTextPage):
    search_name = 'Rich Text Page'


class RichTextPageRelatedLink(Orderable, AbstractRelatedLink):
    page = ParentalKey(
        'wagtailbase.RichTextPage', related_name='related_links')

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
        """Returns a list of the blog pages that are children of this page."""
        posts = self.children.order_by('-date')

        return posts

    def serve(self, request):
        """Renders the blog posts."""
        posts = self.posts

        # Filters by tag
        tag = request.GET.get('tag')
        if tag:
            posts = posts.filter(tags__name=tag)

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(posts, settings.BLOG_POSTS_PER_PAGE)

        try:
            posts = paginator.page(page)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            posts = paginator.page(1)

        return render(request, self.template, {'self': self, 'posts': posts})


class BlogIndexPageRelatedLink(Orderable, AbstractRelatedLink):
    page = ParentalKey(
        'wagtailbase.BlogIndexPage', related_name='related_links')

BlogIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('introduction', classname='full'),
    InlinePanel(BlogIndexPage, 'related_links', label='Related links')
]


class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey(
        'wagtailbase.BlogPost', related_name='tagged_items')


class BlogPost(BaseRichTextPage):
    date = models.DateField('Post Date', default=date.today)
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)

    search_name = 'Blog post'


class BlogPostRelatedLink(Orderable, AbstractRelatedLink):
    page = ParentalKey(
        'wagtailbase.BlogPost', related_name='related_links')

BlogPost.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('date'),
    FieldPanel('content', classname='full'),
    InlinePanel(BlogPost, 'related_links', label='Related links')
]
