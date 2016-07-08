from sqlalchemy.orm import aliased, joinedload

from clld.db.meta import DBSession
from clld.db.util import get_distinct_values, icontains
from clld.db.models.common import Value, Contribution, ValueSet
from clld.web.util.helpers import map_marker_img, external_link
from clld.web.util.htmllib import HTML

from clld.web.datatables.base import Col, IdCol, LinkCol, DetailsRowLinkCol, LinkToMapCol
from clld.web.datatables.language import Languages
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values, RefsCol
from clld.web.datatables.contribution import Contributions

from clld_glottologfamily_plugin.datatables import MacroareaCol, FamilyLinkCol
from clld_glottologfamily_plugin.models import Family

from models import LexibankLanguage, Counterpart, Concept, Cognateset, Provider


class MaybeLinkCol(LinkCol):
    def format(self, item):
        obj = self.get_obj(item)
        if obj:
            return LinkCol.format(self, item)
        return ''


class Counterparts(Values):
    def base_query(self, query):
        query = Values.base_query(self, query)
        if self.parameter:
            query = query\
                .outerjoin(Counterpart.cognateset)\
                .outerjoin(LexibankLanguage.family)
        if self.language:
            query = query.join(ValueSet.contribution)\
                .options(joinedload(Value.valueset, ValueSet.contribution))
        return query

    def col_defs(self):
        if self.parameter:
            return [
                LinkCol(self, 'form', model_col=Counterpart.name),
                LinkCol(
                    self,
                    'language',
                    model_col=LexibankLanguage.name,
                    get_object=lambda i: i.valueset.language),
                MaybeLinkCol(
                    self,
                    'family',
                    model_col=Family.name,
                    get_object=lambda i: i.valueset.language.family),
                MaybeLinkCol(
                    self,
                    'cognate_set',
                    model_col=Cognateset.name,
                    get_object=lambda i: i.cognateset),
                Col(self, 'loan', model_col=Counterpart.loan),
            ]
        if self.language:
            return [
                LinkCol(self, 'form', model_col=Counterpart.name),
                LinkCol(
                    self,
                    'concept',
                    model_col=Concept.name,
                    get_object=lambda i: i.valueset.parameter),
                LinkCol(
                    self,
                    'provider',
                    model_col=Contribution.name,
                    get_object=lambda i: i.valueset.contribution),
            ]
        return Values.col_defs(self)


#class FeatureIdCol(IdCol):
#    def search(self, qs):
#        if self.model_col:
#            return self.model_col.contains(qs)

#    def order(self):
#        return Feature.sortkey_str, Feature.sortkey_int


class LanguageIdCol(LinkCol):
    def get_attrs(self, item):
        return dict(label=item.id)


class LexibankLanguages(Languages):
    __constraints__ = [Contribution]

    def base_query(self, query):
        if self.contribution:
            sq = DBSession.query(ValueSet.language_pk)\
                .filter(ValueSet.contribution_pk == self.contribution.pk)\
                .distinct()\
                .subquery()
            query = query.filter(LexibankLanguage.pk.in_(sq))
        return query.outerjoin(Family).options(joinedload(LexibankLanguage.family))

    def col_defs(self):
        return [
            LanguageIdCol(self, 'id'),
            LinkCol(self, 'name'),
            LinkToMapCol(self, 'm'),
            Col(self,
                'latitude',
                sDescription='<small>The geographic latitude</small>'),
            Col(self,
                'longitude',
                sDescription='<small>The geographic longitude</small>'),
            MacroareaCol(self, 'macroarea', LexibankLanguage),
            FamilyLinkCol(self, 'family', LexibankLanguage),
        ]


class ConcepticonLink(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        return external_link(item.concepticon_url)


class Concepts(Parameters):
    def col_defs(self):
        return [
            IdCol(self, 'id'),
            LinkCol(self, 'Concept'),
            Col(self, 'Languages', model_col=Concept.representation),
            Col(self, 'semantic_field', model_col=Concept.semanticfield, choices=get_distinct_values(Concept.semanticfield)),
            ConcepticonLink(self, 'Concepticon'),
        ]


class Providers(Contributions):
    def col_defs(self):
        return [
            IdCol(self, 'id'),
            LinkCol(self, 'name'),
            Col(self, 'cite', model_col=Contribution.description),
            Col(self, 'language_count', sTitle='# languages', model_col=Provider.language_count),
            Col(self, 'parameter_count', sTitle='# concepts', model_col=Provider.parameter_count),
            Col(self, 'lexeme_count', sTitle='# lexemes', model_col=Provider.lexeme_count),
        ]


def includeme(config):
    config.register_datatable('languages', LexibankLanguages)
    config.register_datatable('contributions', Providers)
    config.register_datatable('parameters', Concepts)
    config.register_datatable('values', Counterparts)
