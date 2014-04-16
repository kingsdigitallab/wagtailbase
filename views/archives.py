from datetime import datetime, timedelta
from django.shortcuts import render

from wagtailbase import models

def serve(request, path):
    # two_days_ago = datetime.utcnow() - timedelta(days=2)
    # recent_posts = models.BlogPost.objects.filter(date__gt=two_days_ago).all()
    # return render(recent_posts)

    if not request.site:
        raise Http404

    path_components = [component for component in path.split('/') if component]

    archives_divider = path_components.index('archives')

    if archives_divider == -1:
        raise Http404

    path_to_index = path_components[0:archives_divider]
    index = request.site.root_page.specific.route(request, path_to_index)

    archives_filter = path_components[archives_divider+1:]

    filter_type, filter_args = archives_filter[0], archives_filter[1:]

    if filter_type == 'author':
        return index.serve_by_author(request, *filter_args)