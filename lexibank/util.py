# coding: utf8
from __future__ import unicode_literals

from sqlalchemy import func, desc, text
from clld_glottologfamily_plugin.models import Family
from clld import RESOURCES
from clld.db.meta import DBSession

from lexibank.models import LexibankLanguage


def dataset_detail_html(context=None, request=None, **kw):
    families = DBSession.query(Family.name, func.count(LexibankLanguage.id).label('c'))\
        .join(LexibankLanguage)\
        .group_by(Family.name)\
        .order_by(desc(text('c')))

    return dict(
        families=families,
        stats=context.get_stats(
            [rsc for rsc in RESOURCES
             if rsc.name in ['language', 'family', 'contribution', 'value', 'parameter']]))
