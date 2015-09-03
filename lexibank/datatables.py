from clld.db.util import get_distinct_values, icontains
from clld.db.models.common import Value
from clld.web.util.helpers import map_marker_img, external_link
from clld.web.util.htmllib import HTML

from clld.web.datatables.base import Col, IdCol, LinkCol, DetailsRowLinkCol, LinkToMapCol
from clld.web.datatables.language import Languages
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values, RefsCol

from clld_glottologfamily_plugin.datatables import MacroareaCol, FamilyLinkCol
from clld_glottologfamily_plugin.models import Family

from models import LexibankLanguage, Counterpart, Concept, Cognateset, Wordlist


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
        if self.contribution:
            return [
                LinkCol(self, 'form', model_col=Counterpart.name),
                LinkCol(
                    self,
                    'concept',
                    model_col=Concept.name,
                    get_object=lambda i: i.valueset.parameter),
                Col(self, 'annotation', model_col=Value.description),
                MaybeLinkCol(
                    self,
                    'cognate_set',
                    model_col=Cognateset.name,
                    get_object=lambda i: i.cognateset),
                Col(self, 'loan', model_col=Counterpart.loan),
                RefsCol(self, 'source'),
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
                    'wordlist',
                    model_col=Wordlist.name,
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
    def base_query(self, query):
        return query.outerjoin(Family)

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
            ConcepticonLink(self, 'Concepticon'),
        ]


def includeme(config):
    config.register_datatable('languages', LexibankLanguages)
    config.register_datatable('parameters', Concepts)
    config.register_datatable('values', Counterparts)
