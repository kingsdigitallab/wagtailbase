from base import AbstractIndexPage, AbstractRelatedLink, AbstractRichTextPage

from datetime import date

from django.db import models
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from taggit.models import TaggedItemBase

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.models import Orderable, Page


class HomePage(Page, AbstractRichTextPage):
    search_name = 'Home Page'

    class Meta:
        verbose_name = 'Homepage'

HomePage.content_panels = AbstractRichTextPage.panels


class StandardIndexPageRelatedLink(Orderable, AbstractRelatedLink):
    page = ParentalKey('cms.StandardIndexPage', related_name='related_links')


class StandardIndexPage(Page, AbstractIndexPage):
    search_name = 'Standard Index Page'

StandardIndexPage.content_panels = AbstractIndexPage.panels + [
    InlinePanel(StandardIndexPage, 'related_links', label='Related links')
]


class StandardPageRelatedLink(Orderable, AbstractRelatedLink):
    page = ParentalKey('cms.StandardPage', related_name='related_links')


class StandardPage(Page, AbstractRichTextPage):
    search_name = 'Standard page'

StandardPage.content_panels = AbstractRichTextPage.panels + [
    InlinePanel(StandardPage, 'related_links', label='Related links')
]


class BlogIndexPageRelatedLink(Orderable, AbstractRelatedLink):
    page = ParentalKey('cms.BlogIndexPage', related_name='related_links')


class BlogIndexPage(Page, AbstractIndexPage):
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

BlogIndexPage.content_panels = AbstractIndexPage.panels + [
    InlinePanel(BlogIndexPage, 'related_links', label='Related links')
]


class BlogPostRelatedLink(Orderable, AbstractRelatedLink):
    page = ParentalKey('cms.BlogPost', related_name='related_links')


class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey('cms.BlogPost', related_name='tagged_items')


class BlogPost(Page, AbstractRichTextPage):
    date = models.DateField('Post Date', default=date.today)
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)

    search_name = 'Blog post'

BlogPost.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('date'),
    FieldPanel('content', classname='full'),
    InlinePanel(BlogPost, 'related_links', label='Related links')
]
