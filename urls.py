from django.conf.urls import patterns, include, url

from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailsearch.urls import frontend as wagtailsearch_frontend_urls

# Signal handlers
from wagtail.wagtailsearch.signal_handlers import register_signal_handlers as \
    wagtailsearch_register_signal_handlers
wagtailsearch_register_signal_handlers()

urlpatterns = patterns('',
                       url(r'^wagtail/', include(wagtailadmin_urls)),
                       url(r'^search/', include(wagtailsearch_frontend_urls)),
                       url(r'^documents/', include(wagtaildocs_urls)),
                       url(r'', include(wagtail_urls)),
                       )
