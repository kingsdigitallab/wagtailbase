from django.shortcuts import render
from wagtail.core.models import Page
from wagtail.search.models import Query
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.conf import settings


def _paginate(request, items):
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(items, settings.ITEMS_PER_PAGE)

    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        page = paginator.page(1)

    return page


def search(request):
    # Search
    search_query = request.GET.get('q', None)

    if search_query:
        queryset = Page.objects.live().search(search_query)

        # logs the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        queryset = Page.objects.none()

    search_results = _paginate(request, queryset)

    # Render template
    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
    })