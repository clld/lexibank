from sqlalchemy.orm import joinedload

from clld.db.meta import DBSession
from clld.db.models.common import Value, Contribution, ValueSet, Parameter, Language
from clld.web.datatables.base import Col, IdCol, LinkCol, LinkToMapCol
from clld.web.datatables.language import Languages
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values
from clld.web.datatables.contribution import Contributions
from clld.web.util import concepticon
from clld_glottologfamily_plugin.datatables import MacroareaCol, FamilyCol
from clld_glottologfamily_plugin.models import Family

from lexibank.models import LexibankLanguage, Form, Concept, LexibankDataset


class Words(Values):
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
            query = query.join(ValueSet.parameter).join(ValueSet.language)\
                .options(
                    joinedload(Value.valueset).joinedload(ValueSet.language),
                    joinedload(Value.valueset).joinedload(ValueSet.parameter))
            return query.filter(ValueSet.contribution_pk == self.contribution.pk)

        return query \
            .join(ValueSet.parameter)\
            .join(ValueSet.language).outerjoin(LexibankLanguage.family)\
            .options(
                joinedload(Value.valueset).joinedload(ValueSet.parameter),
                joinedload(Value.valueset).joinedload(ValueSet.language).joinedload(LexibankLanguage.family),
            )

    def col_defs(self):
        famcol = FamilyCol(self, 'family', LexibankLanguage, get_object=lambda i: i.valueset.language)

        if self.parameter:
            famcol.choices = sorted(
                {
                    (vs.language.family.id, vs.language.family.name) for vs in
                    DBSession.query(ValueSet)
                    .join(ValueSet.language)
                    .join(LexibankLanguage.family)
                    .filter(ValueSet.parameter==self.parameter)
                    .options(joinedload(ValueSet.language).joinedload(LexibankLanguage.family))},
                key=lambda i: i[1])
            return [
                LinkCol(self, 'form', model_col=Form.name),
                LinkCol(
                    self,
                    'language',
                    model_col=LexibankLanguage.name,
                    get_object=lambda i: i.valueset.language),
                famcol,
            ]

        if self.contribution:
            famcol.choices = sorted(
                {
                    (vs.language.family.id, vs.language.family.name) for vs in
                    DBSession.query(ValueSet)
                    .join(ValueSet.language)
                    .join(LexibankLanguage.family)
                    .filter(ValueSet.contribution==self.contribution)
                    .options(joinedload(ValueSet.language).joinedload(LexibankLanguage.family))},
                key=lambda i: i[1])
            return [
                LinkCol(self, 'form', model_col=Form.name),
                LinkCol(
                    self,
                    'concept',
                    model_col=Concept.name,
                    get_object=lambda i: i.valueset.parameter),
                Col(self, 'Segments', model_col=Form.segments),
                LinkCol(
                    self,
                    'language',
                    model_col=LexibankLanguage.name,
                    get_object=lambda i: i.valueset.language),
                famcol,
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
            FamilyCol(
                self,
                'family', LexibankLanguage,
                get_object=lambda i: i.valueset.language),
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


class LanguageIdCol(LinkCol):
    def get_attrs(self, item):
        return dict(label=item.id)


class LexibankLanguages(Languages):
    __constraints__ = [Contribution]

    def base_query(self, query):
        if self.contribution:
            query = query.filter(LexibankLanguage.contribution==self.contribution)
        return query.outerjoin(Family).options(joinedload(LexibankLanguage.family))

    def col_defs(self):
        famcol = FamilyCol(self, 'family', LexibankLanguage)
        if self.contribution:
            famcol.choices = sorted(
                {
                    (l.family.id, l.family.name) for l in
                    DBSession.query(LexibankLanguage)
                    .join(LexibankLanguage.family)
                    .filter(LexibankLanguage.contribution==self.contribution)
                    .options(joinedload(LexibankLanguage.family))},
                key=lambda i: i[1])
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
            famcol,
            #
            # FIXME: list number of words!
            #
        ]


class ConcepticonLink(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        return concepticon.link(self.dt.req, item.id, label=item.name)


class Concepts(Parameters):
    def col_defs(self):
        return [
            IdCol(self, 'id'),
            LinkCol(self, 'name', sTitle='Concept'),
            Col(self, 'Datasets', sTitle='# datasets', model_col=Concept.ndatasets),
            Col(self, 'Languages', sTitle='# languages', model_col=Concept.nlangs),
            Col(self, 'Words', sTitle='# words', model_col=Concept.nwords),
            ConcepticonLink(self, 'Concepticon'),
        ]


class Datasets(Contributions):
    def col_defs(self):
        return [
            IdCol(self, 'id'),
            LinkCol(self, 'name'),
            Col(self, 'language count', sTitle='# languages', model_col=LexibankDataset.nlangs),
            Col(self, 'parameter_count', sTitle='# concepts', model_col=LexibankDataset.nconcepts),
            Col(self,
                'lexeme_count',
                sTitle='# words',
                model_col=LexibankDataset.nwords,
                format=lambda i: '{:,}'.format(i.nwords)),
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
    config.register_datatable('contributions', Datasets)
    config.register_datatable('parameters', Concepts)
    config.register_datatable('values', Words)
