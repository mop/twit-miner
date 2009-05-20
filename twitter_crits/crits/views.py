import models
from django.shortcuts import render_to_response

# Create your views here.
def movies_index(request):
    objects = models.Trackable.ranking_by_type('movie')
    return render_to_response('movies/index.html', {
        'movies_top': objects[0:5],
        'movies_normal': objects[5:20]
    })
    
