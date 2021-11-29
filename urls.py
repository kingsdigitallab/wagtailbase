from django.conf.urls import include, url

from wagtail.core import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from .views import search

urlpatterns = [
    url(r"^wagtail/", include(wagtailadmin_urls)),
    url(r"^search/", search, name='search'),
    url(r"^documents/", include(wagtaildocs_urls)),
    url(r"", include(wagtail_urls)),
]
