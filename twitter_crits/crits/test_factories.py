from datetime import datetime
import pyfactory

class TrackableFactory(pyfactory.FactoryObject):
    class Meta:
        klass = 'crits.models.Trackable'
        name  = 'trackable'
    class Elements:
        name = pyfactory.Generator(lambda i: "Test Movie %d" % i)
        type = "movie"
        score = 10
        last_id = 1
        created_at = datetime.now()

class UserFactory(pyfactory.FactoryObject):
    class Meta:
        klass = 'crits.models.User'
        name  = 'user'
    class Elements:
        name    = pyfactory.Generator(lambda i: "user%d" % i)
        url     = 'http://twitter.com/user1'
        network = 'twitter'

class ReviewFactory(pyfactory.FactoryObject):
    class Meta:
        klass = 'crits.models.Review'
        name  = 'review'
    class Elements:
        score      = 10
        created_at = datetime.now()
        user       = pyfactory.Foreign('user')
        trackable  = pyfactory.Foreign('trackable')
