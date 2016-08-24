from uuid import uuid1

from zope.interface import implementer
from sqlalchemy import (
    Column,
    Integer,
    Float,
    Unicode,
    String,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from uritemplate import expand

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import (
    Language, Parameter, Contribution, Value, HasSourceMixin, Source,
)

from clld_glottologfamily_plugin.models import HasFamilyMixin

from lexibank.interfaces import ICognateset


def uuid():
    return uuid1().urn.split(':')[2]


@implementer(interfaces.IContribution)
class Provider(CustomModelMixin, Contribution):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    url = Column(Unicode)
    license = Column(Unicode)
    aboutUrl = Column(Unicode)
    language_count = Column(Integer)
    parameter_count = Column(Integer)
    lexeme_count = Column(Integer)
    synonym_index = Column(
        Float,
        default=0.0,
        doc="""A measure how often a dataset provides multiple synonyms for
a concept in a language. 1 means for each concept in each language at most one counterpart
is given.""")


@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    representation = Column(Integer)
    semanticfield = Column(Unicode)

    @property
    def concepticon_url(self):
        return 'http://concepticon.clld.org/parameters/{0}'.format(self.id)


@implementer(interfaces.ILanguage)
class LexibankLanguage(CustomModelMixin, Language, HasFamilyMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    level = Column(Unicode)


@implementer(interfaces.ISource)
class LexibankSource(CustomModelMixin, Source):
    pk = Column(Integer, ForeignKey('source.pk'), primary_key=True)
    provider_pk = Column(Integer, ForeignKey('provider.pk'))
    provider = relationship(Provider, backref='sources')


@implementer(ICognateset)
class Cognateset(Base):
    id = Column(String, default=uuid, unique=True)
    name = Column(Unicode)
    type = Column(Unicode)  # automatic, ...
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    contribution = relationship(Contribution, backref='cognatesets')
    representation = Column(Integer)


@implementer(interfaces.IValue)
class Counterpart(CustomModelMixin, Value):
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)
    loan = Column(Boolean, default=False)
    variety_name = Column(Unicode)
    context = Column(Unicode)

    @property
    def external_url(self):
        if self.valueset.contribution.aboutUrl:
            return expand(
                self.valueset.contribution.aboutUrl,
                dict(ID=self.id.split('-', 1)[1]))


class CognatesetCounterpart(Base):
    cognateset_pk = Column(Integer, ForeignKey('cognateset.pk'))
    cognateset = relationship(Cognateset, backref='counterparts')
    counterpart_pk = Column(Integer, ForeignKey('counterpart.pk'))
    counterpart = relationship(Counterpart, backref='cognatesets')
    doubt = Column(Boolean, default=False)
    cognate_detection_method = Column(Unicode)
    alignment = Column(Unicode)
    alignment_method = Column(Unicode)


class CounterpartReference(Base, HasSourceMixin):
    counterpart_pk = Column(Integer, ForeignKey('counterpart.pk'))
    counterpart = relationship(Counterpart, backref="references")
