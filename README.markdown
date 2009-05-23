# twit-miner

twit-miner is an attempt to build a movie recommendation application. 
Moreover it has a global list of total score for each movie, which is 
incremented by 1 if a user likes the given movie and decremented if he hates 
the movie.

## How does this work?

It works by searching in twitter for a list of recent movies. Tweets with 
movie-titles are classified as like/hate using simple word matching (no 
magic is going on here). When a matching tweet is found, all other tweets of 
the user are searched for other movie titles to create a like/hate profile of 
the user for the list of movies.

If a user has only mentioned a single movie in his twitter-history, the user 
isn't imported since it he doesn't help us to give recommendations. The 
total global "score" of the movie is updated, though.

The actual classification is done by a math magic trick: [Latend Semantic Indexing](http://en.wikipedia.org/wiki/Latent_semantic_indexing).

The SVD matrix creation and the twitter-import is handled by the *launch.py* 
script in the project-root directory. You must set the DJANGO_SETTINGS_MODULE 
environment variable to "settings" to launch the script.
The script tries to prune "unnecessary" user data in order to keep the SVD 
matrix small. If all data would have been stored the computation may result 
in a MemoryError on smaller VPS.

## How can I run the tests?

The tests can be run with [modipyd](http://www.metareal.org/p/modipyd/).

## What are the dependencies?

There are a lot of dependencies for running twit-miner:
* [Django 1.0](http://djangoproject.com)
* [Python >= 2.5](http://python.org)
* [PyFactory](http://github.com/mop/PyFactory/tree/master)
* [NumPy](http://numpy.scipy.org/)
* [PorterStemmer](http://bitbucket.org/methane/porterstemmer/)
* [modipyd](http://www.metareal.org/p/modipyd/)
* [simplejson](http://pypi.python.org/pypi/simplejson/)
* [multiprocessing](http://code.google.com/p/python-multiprocessing/) Only needed if you are running on Python 2.5, since 2.6 has it already included.
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)
* [feedparser](http://www.feedparser.org/)
