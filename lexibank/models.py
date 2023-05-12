import urllib.parse

from zope.interface import implementer
from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import Language, Parameter, Contribution, Value, HasSourceMixin
from clld_glottologfamily_plugin.models import HasFamilyMixin


@implementer(interfaces.IContribution)
class LexibankDataset(CustomModelMixin, Contribution, HasSourceMixin):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    url = Column(Unicode)
    version = Column(Unicode)
    doi = Column(Unicode)

    nconcepts = Column(Integer)
    nlangs = Column(Integer)
    nwords = Column(Integer)

    def profile_url(self, name):
        return '{}/blob/{}/etc/{}'.format(self.url, self.version, name)


@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    cluster_id = Column(Unicode)
    central_concept = Column(Unicode)

    nwords = Column(Integer)
    nlangs = Column(Integer)
    ndatasets = Column(Integer)

    @property
    def concepticon_url(self):
        return 'https://concepticon.clld.org/parameters/{}'.format(self.id)

    @property
    def clics_url(self):
        if self.cluster_id:
            return 'https://clics.clld.org/graphs/infomap_{}_{}'.format(
                self.cluster_id, urllib.parse.quote(self.central_concept))


@implementer(interfaces.ILanguage)
class LexibankLanguage(CustomModelMixin, Language, HasFamilyMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    glottocode = Column(Unicode)
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    contribution = relationship(Contribution, backref='languages')

    nwords = Column(Integer)
    nconcepts = Column(Integer)


@implementer(interfaces.IValue)
class Form(CustomModelMixin, Value):
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)
    profile = Column(Unicode)
    segments = Column(Unicode)
    CV_Template = Column(Unicode)
    Prosodic_String = Column(Unicode)
    Dolgo_Sound_Classes = Column(Unicode)
    SCA_Sound_Classes = Column(Unicode)
