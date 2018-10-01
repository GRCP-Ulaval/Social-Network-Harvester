from django.db import models

from SocialNetworkHarvester.loggers.viewsLogger import log, pretty
from .FBPage import FBPage
from .FBUser import FBUser
from .FBVideo import FBVideo


class FBGroup(models.Model):
    _ident = models.CharField(max_length=255, unique=True)


class FBEvent(models.Model):
    _ident = models.CharField(max_length=255, unique=True)


class FBApplication(models.Model):
    _ident = models.CharField(max_length=255, unique=True)


class FBPhoto(models.Model):
    _ident = models.CharField(max_length=255, unique=True)


class FBProfile(models.Model):
    '''
    A Facebook "Profile" object can be any one of the following:
    <FBUser>, <FBPage>, <FBGroup>, <FBEvent>, <FBApplication>.
    FBProfile is used here to simplify the database structure.
    '''
    _ident = models.CharField(max_length=225, unique=True)
    type = models.CharField(max_length=1)  # U/P/G/E/A/V/H
    deleted_at = models.DateTimeField(null=True)

    ### A single one of the following fields is non-null ###
    fbUser = models.OneToOneField(FBUser, null=True, related_name='fbProfile', on_delete=models.CASCADE)
    fbPage = models.OneToOneField(FBPage, null=True, related_name='fbProfile', on_delete=models.CASCADE)
    fbGroup = models.OneToOneField(FBGroup, null=True, related_name='fbProfile', on_delete=models.CASCADE)
    fbEvent = models.OneToOneField(FBEvent, null=True, related_name='fbProfile', on_delete=models.CASCADE)
    fbApplication = models.OneToOneField(FBApplication, null=True, related_name='fbProfile', on_delete=models.CASCADE)
    fbVideo = models.OneToOneField(FBVideo, null=True, related_name='fbProfile', on_delete=models.CASCADE)
    fbPhoto = models.OneToOneField(FBPhoto, null=True, related_name='fbProfile', on_delete=models.CASCADE)

    def __str__(self):
        if self.type:
            return str(self.getInstance())
        else:
            return "Profil non-identifié"

    def getStr(self):
        return str(self)

    def migrateId(self, newId):
        newProfile = FBProfile.objects.filter(_ident=newId).first()
        currentInstance = self.getInstance()
        if newProfile:
            newInstance = newProfile.getInstance()
            if newInstance:
                log('migrating fbProfile:')
                log('   current: %s' % currentInstance)
                log('   to:      %s' % newInstance)
                if currentInstance:
                    if hasattr(currentInstance, "fowardConnections"):
                        currentInstance.fowardConnections(newInstance)
                    currentInstance.delete()
                self.findAndSetInstance()
        elif currentInstance:
            currentInstance._ident = newId
            currentInstance.save()
        self._ident = newId
        self.save()

    def getInstance(self):
        d = {
            "U": self.fbUser,
            "P": self.fbPage,
            "G": self.fbGroup,
            "E": self.fbEvent,
            "A": self.fbApplication,
            "V": self.fbVideo,
            "H": self.fbPhoto,
        }
        return d[self.type] if self.type in d else None

    def update(self, jObject):
        try:
            self.createAndSetInstance(jObject['metadata']['type'])
            self.save()
        except:
            pretty(jObject)
            raise

    def findAndSetInstance(self):
        attrs = {"fbUser": FBUser, "fbPage": FBPage, "fbGroup": FBGroup, "fbEvent": FBEvent,
                 "fbApplication": FBApplication, "fbVideo": FBVideo, "fbPhoto": FBPhoto}
        for attr, model in attrs.items():
            instance = model.objects.filter(_ident=self._ident).first()
            if instance:
                setattr(self, attr, instance)
                self.save()
                return True
        return False

    def createAndSetInstance(self, strType):
        if self.getInstance(): return  # Object instance already set
        d = {
            "user": ("fbUser", "U", FBUser),
            "page": ("fbPage", "P", FBPage),
            "group": ("fbGroup", "G", FBGroup),
            "event": ("fbEvent", "E", FBEvent),
            "application": ("fbApplication", "A", FBApplication),
            "video": ("fbVideo", "V", FBVideo),
            "photo": ("fbPhoto", "H", FBPhoto),
        }
        if strType not in d.keys():
            log('profile type "%s" is not recognised' % strType)
            return
        attr, type, model = d[strType]
        setattr(self, attr, model.objects.create(_ident=self._ident))
        self.type = type

    def getLink(self):
        d = {
            "U": 'user',
            "P": 'page',
            "G": 'group',
            "E": 'event',
            "A": 'application',
        }
        if self.type in ['V', 'H']: return "#"  # photos and videos objects have no url
        if not self.type in d or not self.getInstance(): return None
        return "/facebook/%s/%s" % (d[self.type], self.getInstance().pk)
