from datetime import datetime

from django.db import models
from django.utils.timezone import utc

from .FBLocation import FBLocation
from .FBVideo import FBVideo
from SocialNetworkHarvester.loggers.viewsLogger import log
from SocialNetworkHarvester.models import replaceEmojisFromFields, today


class FBPage(models.Model):
    _ident = models.CharField(max_length=225, unique=True)
    category = models.CharField(max_length=128)

    ### Core fields ###
    name = models.CharField(max_length=128, null=True)
    username = models.CharField(max_length=64, null=True)
    about = models.TextField(null=True)
    cover = models.CharField(max_length=512, null=True)
    current_location = models.CharField(max_length=512, null=True)
    description_html = models.TextField(null=True)
    # display_subtext = models.CharField(max_length=1024, null=True) useless, redundant information
    # displayed_message_response_time = models.CharField(max_length=128, null=True) useless
    emails = models.CharField(max_length=2048, null=True)
    featured_video = models.ForeignKey(FBVideo, null=True, related_name='featured_on_pages', on_delete=models.PROTECT)
    general_info = models.TextField(null=True)
    # impressum = models.CharField(max_length=128, null=True)
    link = models.CharField(max_length=4096, null=True)
    members = models.TextField(null=True)
    is_community_page = models.BooleanField(default=False)
    is_unclaimed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    location = models.ForeignKey(FBLocation, null=True, on_delete=models.PROTECT)
    parent_page = models.ForeignKey('self', null=True, on_delete=models.PROTECT)
    phone = models.CharField(max_length=256, null=True)
    verification_status = models.CharField(max_length=64, null=True)
    website = models.CharField(max_length=512, null=True)

    ### Statistics fields ###
    checkins = models.IntegerField(null=True)
    fan_count = models.IntegerField(null=True)
    overall_star_rating = models.FloatField(null=True)
    rating_count = models.IntegerField(null=True)
    talking_about_count = models.IntegerField(null=True)
    were_here_count = models.IntegerField(null=True)

    ### People ###
    birthday = models.CharField(max_length=128, null=True)
    affiliation = models.CharField(max_length=225, null=True)
    personal_info = models.TextField(null=True)
    personal_interests = models.TextField(null=True)

    ### Vehicules ###
    built = models.CharField(max_length=64, null=True)
    features = models.TextField(null=True)
    mpg = models.CharField(max_length=256, null=True)  # mpg = miles per gallons... yep.

    ### Compagnies, restaurants, nightlife ###
    company_overview = models.TextField(null=True)
    mission = models.TextField(null=True)
    products = models.TextField(null=True)
    founded = models.TextField(null=True)
    general_manager = models.CharField(max_length=256, null=True)
    price_range = models.CharField(max_length=16, null=True)  # can be $, $$, $$$, $$$$ or Unspecified
    hours = models.TextField(null=True)
    pharma_safety_info = models.TextField(null=True)
    is_permanently_closed = models.BooleanField(default=False)
    is_always_open = models.BooleanField(default=False)

    ### TV Shows and films ###
    network = models.CharField(max_length=512, null=True)
    schedule = models.TextField(null=True)
    season = models.CharField(max_length=64, null=True)
    written_by = models.CharField(max_length=512, null=True)
    awards = models.TextField(null=True)
    directed_by = models.TextField(null=True)
    genre = models.TextField(null=True)
    plot_outline = models.TextField(null=True)
    produced_by = models.TextField(null=True)
    release_date = models.CharField(max_length=64, null=True)
    screenplay_by = models.TextField(null=True)
    starring = models.TextField(null=True)
    studio = models.TextField(null=True)

    ### Musicians and bands ###
    artists_we_like = models.TextField(null=True)
    band_interests = models.TextField(null=True)
    band_members = models.CharField(max_length=4096, null=True)
    bio = models.TextField(null=True)
    booking_agent = models.TextField(null=True)
    hometown = models.TextField(null=True)
    influences = models.TextField(null=True)
    press_contact = models.TextField(null=True)
    record_label = models.TextField(null=True)

    ### Functionnal private fields ###
    last_updated = models.DateTimeField(null=True)
    error_on_update = models.BooleanField(default=False)
    error_on_harvest = models.BooleanField(default=False)
    last_feed_harvested = models.DateTimeField(null=True)

    def __str__(self):
        if self.name:
            return "Page Facebook de %s" % self.name
        else:
            return "Page Facebook non identifiée"

    def get_fields_description(self):
        return {
            "_ident": {
                "name": "Identifiant",
                "description": "String unique identifiant la page.",
                "type": "integer",
                "options": {}
            },
            "category": {
                "name": "Catégorie",
                "description": "Catégorie dans laquelle se retrouve la page.",
                "type": "short_string",
            },
            "name": {
                "name": "Nom",
                "description": "Nom ou titre donné à la page.",
                "type": "short_string",
                "searchable": True,
            },
            "username": {
                "name": "Nom d'utilisateur",
                "description": "Nom d'authentification de la page",
                "type": "long_string",
                "searchable": True,
            },
            "about": {
                "name": "À propos",
                "description": "Description de la page",
                "type": "long_string",
            },
            "cover": {
                "name": "Couverture",
                "description": "Url de l'image de couverture de la page",
                "type": "image_url",
                "options": {"displayable": False, 'downloadable': True},
            },
            "current_location": {
                "name": "Position actuelle",
                "description": "Position actuelle, si la page divulgue sa position en temps réel.",
                "type": "short_string"

            },
            "description_html": {
                "name": "Description (html)",
                "description": "Description de la page, incluant les tags html",
                "type": "long_string",
            },
            "emails": {
                "name": "Courriels",
                "description": "Adresses courrielles associées à la page",
                "type": "long_string",
            },
            "featured_video": {
                "name": "Vidéo en vedette",
                "description": "Vidéo présentement mise en vedette par la page",
                "type": "object",
            },
            "general_info": {
                "name": "Informations générales",
                "description": "Informations générales de la page.",
                "type": "long_string",
            },
            "link": {
                "name": "Lien permanent",
                "description": "Lien permanent vers la Page sur Facebook.",
                "type": "link_url",
                "options": {
                    "displayable": False,
                }
            },
            "members": {
                "name": "Membres",
                "description": "Personnes (profils Facebook) associés à la page, s'il s'agit d'un regroupement.",
                "type": "long_string",
            },
            "is_community_page": {
                "name": "Est une communauté",
                "description": "(booléen) Indique s'il s'agit d'une page représentant une communauté.",
                "type": "boolean",
            },
            "is_unclaimed": {
                "name": "N'est pas réclamée",
                "description": "(Booléen) Indique si la page n'est pas réclamée par l'organisation qu'elle prétend "
                               "représenter.",
                "type": "boolean",
            },
            "is_verified": {
                "name": "Vérifié",
                "description": "(Booléen) Détermine si l'identité de la page est vérifiée par la communauté Facebook",
                "type": "boolean",
            },
            "location": {
                "name": "Location",
                "description": "Position enregistrée de la page, s'il s'agit d'un commerce, etc.",
                "type": "short_string",
            },
            "parent_page": {
                "name": "Page parente",
                "description": "Page à laquelle la page est affiliée (Page de produit affiliée à une page de "
                               "compagnie, par exemple).",
                "type": "link_url",
            },
            "phone": {
                "name": "Téléphone",
                "description": "Numéro de téléphone.",
                "type": "short_string",
            },
            "verification_status": {
                "name": "Status de vérification",
                "description": "État de la procédure de vérification de la page.",
                "type": "short_string",
            },
            "website": {
                "name": "Site web",
                "description": "Lien vers le site-web du propriétaire de la page.",
                "type": "link_url",
            },
            "checkins": {
                "name": "Entrées",
                "description": "Nombre de personnes ayant précisé qu'il étaient présent à la location de la page. ("
                               "Pertinent s'il s'agit d'un pub/bar/restaurant/etc.)",
                "type": "integer",
            },
            "fan_count": {
                "name": "Fans",
                "description": "Nombre de personnes ayant aimé la page.",
                "type": "integer",
            },
            "overall_star_rating": {
                "name": "Classement",
                "description": "Classement (1 à 5 étoiles) de l'établissement.",
                "type": "integer"
            },
            "rating_count": {
                "name": "Nombre Classements",
                "description": "Nombre de notes ayant contribués au classement.",
                "type": "integer"
            },
            "talking_about_count": {
                "name": "Nombre de mentions",
                "description": "Nombre de status/commentaires mentionnant la page.",
                "type": "integer"
            },
            "were_here_count": {
                "name": "Personnes présentes",
                "description": "Nombre de personnes ayant mentionné avoir visité la location de la page",
                "type": "integer"
            },
            "birthday": {
                "name": "Anniversaire",
                "description": "Date d'aniversaire de la page, s'il s'agit d'une personne.",
                "type": "date",
            },
            "affiliation": {
                "name": "Affiliation",
                "description": "Affiliation de la page, s'il s'agit d'une personalité politique",
                "type": "short_string",
            },
            "personal_info": {
                "name": "Infos personnelles",
                "description": "Informations personnelles de la personne, si la page représente une personne.",
                "type": "long_string",
            },
            "personal_interests": {
                "name": "Intérêts personnels",
                "description": "Sujets d'intérêts de la pesonne.",
                "type": "long_string",
            },
            "built": {
                "name": "Construction",
                "description": "Date de mise en ligne de la page",
                "type": "date",
            },
            "features": {
                "name": "En vedette",
                "description": "Pages mises en vedette par la page",
                "type": "link_url",
            },
            "mpg": {
                "name": "Miles par gallons",
                "description": "Nombre de miles pouvant être parcouru avec un gallon d'essence, si la page représente"
                               " une voiture.",
                "type": "integer",
            },
            "company_overview": {
                "name": "Apperçu de compagnie",
                "description": "Apperçu général de la compagnie, si la page représente une compagnie",
                "type": "long_string",
            },
            "mission": {
                "name": "Mission",
                "description": "Mission ou engagement social de la compagnie.",
                "type": "long_string",
            },
            "products": {
                "name": "Produits",
                "description": "Produits offerts par la compagnie",
                "type": "long_string",
            },
            "founded": {
                "name": "Fondé en",
                "description": "Date de fondation de la compagnie.",
                "type": "date",
            },
            "general_manager": {
                "name": "Gérant général",
                "description": "Nom de la personne gérant la compagnie visée.",
                "type": "short_string",
            },
            "price_range": {
                "name": "Gamme de prix",
                "description": "Gamme de prix dans laquelle l'établissement (ou le produit) se situe. Peut être $, "
                               "$$, $$$ ou $$$$",
                "type": "short_string",
            },
            "hours": {
                "name": "Heures",
                "description": "Heures d'ouverture ou de service de l'établissement.",
                "type": "long_string",
            },
            "pharma_safety_info": {
                "name": "Sécurité pharmaceutique",
                "description": "Informations de sécurité quand au produit, s'il s'agit d'un produit pharmaceutique.",
                "type": "long_string",
            },
            "is_permanently_closed": {
                "name": "Permanement fermé",
                "description": "(Booléen) Indique si l'établissement est fermé de façon permanente.",
                "type": "boolean",
            },
            "is_always_open": {
                "name": "Toujours ouvert",
                "description": "(Booléen) Indique si l'établissement est ouvert à tout moment.",
                "type": "boolean",
            },
            "network": {
                "name": "Réseau",
                "description": "Réseau de diffusion ou compagnie de distribution, s'il s'agit d'un artiste ou d'un "
                               "programme télévisé.",
                "type": "short_string",
            },
            "schedule": {
                "name": "Horaire",
                "description": "Heures de diffusion de la série télévisée, si applicable.",
                "type": "long_string",
            },
            "season": {
                "name": "Saison",
                "description": "Numéro de la saison de la série télévisé, si applicable.",
                "type": "short_string",
            },
            "written_by": {
                "name": "Écrit par",
                "description": "Auteur de la série télévisée, si applicable.",
                "type": "short_string",
            },
            "awards": {
                "name": "Prix gagnés",
                "description": "Prix gagnés par le film, si applicable.",
                "type": "long_string",
            },
            "directed_by": {
                "name": "Directeur",
                "description": "Directeur ou directeurs du film, si applicable.",
                "type": "short_string",
            },
            "genre": {
                "name": "Genre",
                "description": "Genre applicable au film, si applicable.",
                "type": "short_string",
            },
            "plot_outline": {
                "name": "Synopsis",
                "description": "Synopsis du film, si applicable.",
                "type": "long_string",
            },
            "produced_by": {
                "name": "Producteurs",
                "description": "Producteurs du film, si applicable.",
                "type": "long_string",
            },
            "release_date": {
                "name": "Date de sortie",
                "description": "Date de sortie du film, si applicable.",
                "type": "date",
            },
            "screenplay_by": {
                "name": "Scénarisé par",
                "description": "Scénarisateur du film, si applicable.",
                "type": "long_string",
            },
            "starring": {
                "name": "En vedette",
                "description": "Acteurs mis en vedette dans le film, si applicable.",
                "type": "long_string",
            },
            "studio": {
                "name": "Studio",
                "description": "Studio du film, si applicable.",
                "type": "short_string",
            },
            "artists_we_like": {
                "name": "Artistes aimés",
                "description": "Artistes aimés par le groupe de musique, si applicable",
                "type": "long_string",
            },
            "band_interests": {
                "name": "Intérêts du groupe",
                "description": "Intérêts du groupe de musique, si applicable.",
                "type": "long_string",
            },
            "band_members": {
                "name": "Membre du groupe",
                "description": "Membres du groupe de musique, si applicable.",
                "type": "long_string",
            },
            "bio": {
                "name": "Biographie",
                "description": "Biographie de la personne ou du groupe de musique, si applicable.",
                "type": "long_string",
            },
            "booking_agent": {
                "name": "Agent de réservation",
                "description": "Agent du groupe, si applicable.",
                "type": "short_string",
            },
            "hometown": {
                "name": "Ville d'origine",
                "description": "Ville d'origine du groupe de musique, si applicable.",
                "type": "short_string",
            },
            "influences": {
                "name": "Influences",
                "description": "Influences musicales du groupe de musique, si applicable.",
                "type": "long_string",
            },
            "press_contact": {
                "name": "Contact de presse",
                "description": "Agent de presse du groupe de musique, si applicable.",
                "type": "short_string",
            },
            "record_label": {
                "name": "Maison de disque",
                "description": "Maison de disque du groupe de musique, si applicable.",
                "type": "short_string",
            },
            "last_updated": {
                "name": "Last updated",
                "type": "date",
                "options": {
                    'admin_only': True,
                    "downloadable": False,
                },
            },
            "error_on_update": {
                "name": "Error on update",
                "type": "boolean",
                "options": {
                    'admin_only': True,
                    "downloadable": False,
                },
            },
            "error_on_harvest": {
                "name": "Error on harvest",
                "type": "boolean",
                "options": {
                    'admin_only': True,
                    "downloadable": False,
                },
            },
            "last_feed_harvested": {
                "name": "Last feed-harvested",
                "type": "date",
                "options": {
                    'admin_only': True,
                    "downloadable": False,
                },
            },
        }

    def get_obj_ident(self):
        return "FBPage__%s" % self.pk

    def fowardConnections(self, instance):
        # TODO: transfer all connections to the new instance
        pass

    ### UPDATE ROUTINE METHODS ###
    basicFields = {
        '_ident': ['id'],
        'category': ['category'],
        'checkins': ['checkins'],
        'fan_count': ['fan_count'],
        'overall_star_rating': ['overall_star_rating'],
        'rating_count': ['rating_count'],
        'talking_about_count': ['talking_about_count'],
        'were_here_count': ['were_here_count'],
        'name': ['name'],
        'username': ['username'],
        'about': ['about'],
        'cover': ['cover', 'source'],
        'current_location': ['current_location'],
        'description_html': ['description_html'],
        'emails': ['emails'],
        'general_info': ['general_info'],
        'link': ['link'],
        'members': ['members'],
        'is_community_page': ['is_community_page'],
        'is_unclaimed': ['is_unclaimed'],
        'is_verified': ['is_verified'],
        'phone': ['phone'],
        'verification_status': ['verification_status'],
        'website': ['website'],
        'birthday': ['birthday'],
        'affiliation': ['affiliation'],
        'personal_info': ['personal_info'],
        'personal_interests': ['personal_interests'],
        'built': ['built'],
        'features': ['features'],
        'mpg': ['mpg'],
        'company_overview': ['company_overview'],
        'mission': ['mission'],
        'products': ['products'],
        'founded': ['founded'],
        'general_manager': ['general_manager'],
        'price_range': ['price_range'],
        'hours': ['hours'],
        'pharma_safety_info': ['pharma_safety_info'],
        'is_permanently_closed': ['is_permanently_closed'],
        'is_always_open': ['is_always_open'],
        'network': ['network'],
        'schedule': ['schedule'],
        'season': ['season'],
        'written_by': ['written_by'],
        'awards': ['awards'],
        'directed_by': ['directed_by'],
        'genre': ['genre'],
        'plot_outline': ['plot_outline'],
        'produced_by': ['produced_by'],
        'screenplay_by': ['screenplay_by'],
        'starring': ['starring'],
        'studio': ['studio'],
        'artists_we_like': ['artists_we_like'],
        'band_interests': ['band_interests'],
        'band_members': ['band_members'],
        'bio': ['bio'],
        'booking_agent': ['booking_agent'],
        'hometown': ['hometown'],
        'influences': ['influences'],
        'press_contact': ['press_contact'],
        'record_label': ['record_label'],
    }
    statistics = {
        'checkins_counts': ['checkins'],
        'fan_counts': ['fan_count'],
        'overall_star_rating_counts': ['overall_star_rating'],
        'rating_counts': ['rating_count'],
        'talking_about_counts': ['talking_about_count'],
        'were_here_counts': ['were_here_count'],
    }

    # @facebookLogger.debug(showClass=True)
    def update(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object from Youtube must be passed as argument.')
        self.copyBasicFields(jObject)
        self.updateStatistics(jObject)
        self.updateFeaturedVideo(jObject)
        self.setParentPage(jObject)
        self.setLocation(jObject)
        self.setReleaseDate(jObject)
        replaceEmojisFromFields(self, [])
        self.last_updated = today()
        self.save()

    def copyBasicFields(self, jObject):
        for attr in self.basicFields:
            if self.basicFields[attr][0] in jObject:
                val = jObject[self.basicFields[attr][0]]
                for key in self.basicFields[attr][1:]:
                    if key in val:
                        val = val[key]
                    else:
                        val = None
                if val:
                    field = self._meta.get_field(attr)
                    if field.max_length and field.max_length < len(val) and field.max_length >= 30:
                        log("DATA TOO LONG TO FIT <%s> FIELD \"%s\" (value: %s)" % (self, attr, val))
                        val = "DATA TOO LONG. CONTENT SKIPPED"
                    setattr(self, attr, val)

    # @youtubeLogger.debug()
    def updateStatistics(self, jObject):
        for attrName in self.statistics:
            countObjs = getattr(self, attrName).order_by('-recorded_time')
            objType = countObjs.model
            val = jObject
            for key in self.statistics[attrName]:
                if key in val:
                    val = val[key]
                else:
                    val = None
                    break
            if val:
                if not countObjs.exists():
                    objType.objects.create(fbPage=self, value=val)
                else:
                    if countObjs[0].value != int(val) and countObjs[0].recorded_time != today():
                        objType.objects.create(fbPage=self, value=val)

    def updateFeaturedVideo(self, jObject):
        if "featured_video" in jObject:
            video, new = FBVideo.objects.get_or_create(_ident=jObject['featured_video']['id'])
            video.update(jObject['featured_video'])
            self.featured_video = video

    def setParentPage(self, jObject):
        if 'parent_page' in jObject:
            log('PARENT PAGE: %s' % jObject['parent_page'])
            # page, new = FBPage.objects.get_or_create(_ident=jObject['parent_page']['id'])
            # page.update()

    def setLocation(self, jObject):
        if 'location' in jObject:
            location = self.location
            if not location:
                location = FBLocation.objects.create()
                self.location = location
            location.update(jObject['location'])

    def setReleaseDate(self, jObject):
        if 'release_date' in jObject:
            try:
                release_date = datetime.strptime(jObject['release_date'], '%Y%m%d')
                self.release_date = release_date.replace(tzinfo=utc)
            except ValueError as e:
                pass  # release date is in a weird format (00-indexed days of month?) TODO: filter bad dates
