from django.http import Http404
from datetime import datetime, timedelta
from django.shortcuts import render

from wagtailbase import models

def serve(request, index_path, archive_path):
    # two_days_ago = datetime.utcnow() - timedelta(days=2)
    # recent_posts = models.BlogPost.objects.filter(date__gt=two_days_ago).all()
    # return render(recent_posts)

    if not request.site:
        raise Http404

    path_to_index = [component for component in index_path.split('/') if component]


    index = request.site.root_page.specific.get_page_from_path(path_to_index)

    archives_filter = [component for component in archive_path.split('/') if component]

    if len(archives_filter):
        filter_type, filter_args = archives_filter[0], archives_filter[1:]
        return index.filter_serve(request, filter_type, *filter_args)

    else:
        raise Http404