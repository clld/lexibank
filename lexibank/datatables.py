from sqlalchemy.orm import joinedload

from clld.db.meta import DBSession
from clld.db.util import get_distinct_values
from clld.db.models.common import Value, Contribution, ValueSet, Parameter, Language
from clld.web.util.helpers import external_link, linked_references

from clld.web.datatables.base import Col, IdCol, LinkCol, LinkToMapCol, DataTable
from clld.web.datatables.language import Languages
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values
from clld.web.datatables.contribution import Contributions
from clld.web.datatables.source import Sources

from clld_glottologfamily_plugin.datatables import MacroareaCol, FamilyLinkCol
from clld_glottologfamily_plugin.models import Family

from lexibank.models import LexibankLanguage, Form, Concept, LexibankDataset


class MaybeLinkCol(LinkCol):
    def format(self, item):
        obj = self.get_obj(item)
        if obj:
            return LinkCol.format(self, item)
        return ''


class RefsCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        return linked_references(self.dt.req, item)


class Counterparts(Values):
    def base_query(self, query):
        query = query.join(ValueSet).options(
            joinedload(Value.valueset).joinedload(ValueSet.contribution),
        )

        if self.language:
            query = query \
                .join(ValueSet.parameter) \
                .join(ValueSet.contribution) \
                .options(
                    joinedload(Value.valueset, ValueSet.contribution),
                    joinedload(Value.valueset, ValueSet.parameter))
            return query.filter(ValueSet.language_pk == self.language.pk)

        if self.parameter:
            query = query \
                .join(ValueSet.language) \
                .outerjoin(LexibankLanguage.family) \
                .options(joinedload(Value.valueset).joinedload(ValueSet.language).joinedload(LexibankLanguage.family))
            return query.filter(ValueSet.parameter_pk == self.parameter.pk)

        if self.contribution:
            query = query.join(ValueSet.parameter)
            return query.filter(ValueSet.contribution_pk == self.contribution.pk)

        return query \
            .join(ValueSet.parameter)\
            .join(ValueSet.language).outerjoin(LexibankLanguage.family)\
            .options(
                joinedload(Value.valueset).joinedload(ValueSet.parameter),
                joinedload(Value.valueset).joinedload(ValueSet.language).joinedload(LexibankLanguage.family),
            )

    def col_defs(self):
        if self.parameter:
            return [
                LinkCol(self, 'form', model_col=Form.name),
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
            ]
        if self.language:
            return [
                LinkCol(self, 'form', model_col=Form.name),
                LinkCol(
                    self,
                    'concept',
                    model_col=Concept.name,
                    get_object=lambda i: i.valueset.parameter),
                Col(self, 'Segments', model_col=Form.segments),
            ]
        return [
            LinkCol(self, 'form', model_col=Value.name),
            LinkCol(
                self,
                'language',
                model_col=Language.name,
                get_object=lambda i: i.valueset.language),
            MaybeLinkCol(
                self,
                'family',
                model_col=Family.name,
                get_object=lambda i: i.valueset.language.family),
            LinkCol(
                self,
                'concept',
                model_col=Parameter.name,
                get_object=lambda i: i.valueset.parameter),
            Col(self, 'Central_concept', model_col=Concept.central_concept, get_object=lambda i: i.valueset.parameter),
            Col(self, 'Segments', model_col=Form.segments),
            Col(self, 'CV_Template', model_col=Form.CV_Template),
            Col(self, 'Dolgopolsky', model_col=Form.Dolgo_Sound_Classes),
            Col(self, 'SCA', model_col=Form.SCA_Sound_Classes),
        ]


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
            LinkCol(self, 'name', sTitle='Concept'),
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
            Col(self, 'language_count', sTitle='# languages', model_col=LexibankDataset.language_count),
            Col(self, 'parameter_count', sTitle='# concepts', model_col=LexibankDataset.parameter_count),
            Col(self,
                'lexeme_count',
                sTitle='# lexemes',
                model_col=LexibankDataset.lexeme_count,
                format=lambda i: '{:,}'.format(i.lexeme_count)),
            Col(self,
                'synonymy',
                sDescription=LexibankDataset.synonym_index.doc,
                model_col=LexibankDataset.synonym_index,
                format=lambda i: '{:.3f}'.format(i.synonym_index))
        ]


class ProviderCol(LinkCol):
    def __init__(self, dt, name, **kw):
        kw['model_col'] = Contribution.name
        kw['choices'] = [(p.id, p.name) for p in DBSession.query(LexibankDataset)]
        LinkCol.__init__(self, dt, name, **kw)

    def search(self, qs):
        return Contribution.id == qs


def includeme(config):
    config.register_datatable('languages', LexibankLanguages)
    config.register_datatable('contributions', Providers)
    config.register_datatable('parameters', Concepts)
    config.register_datatable('values', Counterparts)
