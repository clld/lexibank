# coding: utf8
from __future__ import unicode_literals

from sqlalchemy import func, desc, text
from clld_glottologfamily_plugin.models import Family
from clld import RESOURCES
from clld.db.meta import DBSession
from clld.db.models.common import Language, ValueSet
from clld.web.util.htmllib import HTML
from clld.web.maps import SelectedLanguagesMap

from lexibank.models import LexibankLanguage


def concepticon_link(request, concept):
    return HTML.a(
        HTML.img(
            src=request.static_url('lexibank:static/concepticon_logo.png'),
            height=20,
            width=30),
        title='corresponding concept set at Concepticon',
        href=concept.concepticon_url)


def contribution_detail_html(context=None, request=None, **kw):
    langs = DBSession.query(Language).join(Language.valuesets)\
        .filter(ValueSet.contribution == context).distinct()
    map_ = SelectedLanguagesMap(context, request, list(langs))
    return {'map': map_}


def dataset_detail_html(context=None, request=None, **kw):
    families = DBSession.query(Family.id, Family.name, func.count(LexibankLanguage.id).label('c'))\
        .join(LexibankLanguage)\
        .group_by(Family.id, Family.name)\
        .order_by(desc(text('c')))

    return dict(
        families=families,
        stats=context.get_stats(
            [rsc for rsc in RESOURCES
             if rsc.name in ['language', 'family', 'contribution', 'value', 'parameter']]))
