from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, \
    PageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailcore.models import Page


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
