from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, \
    PageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField


from model_utils.managers import InheritanceManager


class AbstractLinkField(models.Model):

    """Abstract class for link fields."""
    link_document = models.ForeignKey('wagtaildocs.Document', blank=True,
                                      null=True, related_name='+')
    link_external = models.URLField('External link', blank=True, null=True)
    link_page = models.ForeignKey('wagtailcore.Page', blank=True,
                                  null=True, related_name='+')

    panels = [
        DocumentChooserPanel('link_document'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page')
    ]

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    class Meta:
        abstract = True


class AbstractRelatedLink(AbstractLinkField):

    """Abstract class for related links."""
    title = models.CharField(max_length=256, help_text='Link title')

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(AbstractLinkField.panels, 'Link')
    ]

    class Meta:
        abstract = True


class BasePage(Page):

    """
    Abstract class Page which uses InheritanceManager. This class
    is not abstract to Django because it needs access to the
    manager. It will not appear in the Wagtail admin, however.
    """

    objects = InheritanceManager()
    is_abstract = True


class BaseIndexPage(BasePage):

    """Abstract class for index pages. Index pages are pages that will have
    children pages."""
    introduction = RichTextField(blank=True)

    indexed_fields = ('introduction', )
    is_abstract = True

    @property
    def children(self):
        """Returns a list of the pages that are children of this page."""
        children = BasePage.objects.filter(
            live=True,
            path__startswith=self.path).exclude(id=self.id).select_subclasses()

        return children



class BaseRichTextPage(BasePage):

    """Abstract class for rich text pages."""
    content = RichTextField()

    indexed_fields = ('content', )
    is_abstract = True

    @property
    def index_page(self):
        """Finds and returns the index page from the page ancestors."""
        for ancestor in reversed(self.get_ancestors()):
            if isinstance(ancestor.specific, BaseIndexPage):
                return ancestor

        # No ancestors are index pages, returns the first page
        return Page.objects.first()

