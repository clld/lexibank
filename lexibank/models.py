from uuid import uuid1

from zope.interface import implementer
from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    String,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import Language, Parameter, Contribution, Value

from clld_glottologfamily_plugin.models import HasFamilyMixin

from lexibank.interfaces import ICognateset


def uuid():
    return uuid1().urn.split(':')[2]


@implementer(interfaces.IContribution)
class Wordlist(CustomModelMixin, Contribution):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship(Language, backref='wordlists')


@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    representation = Column(Integer)
    concepticon_url = Column(Unicode)


@implementer(interfaces.ILanguage)
class LexibankLanguage(CustomModelMixin, Language, HasFamilyMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)


@implementer(ICognateset)
class Cognateset(Base):
    id = Column(String, default=uuid, unique=True)
    name = Column(Unicode, unique=True)
    # FIXME: are cognate sets concept-specific? If so, they should be related to the
    # corresponding Concept.


@implementer(interfaces.IValue)
class Counterpart(CustomModelMixin, Value):
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)
    cognateset_pk = Column(Integer, ForeignKey('cognateset.pk'))
    cognateset = relationship(Cognateset, backref='counterparts')
    loan = Column(Boolean, default=False)
