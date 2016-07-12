# coding: utf-8
from __future__ import unicode_literals
from collections import defaultdict
from itertools import chain

from sqlalchemy.orm import joinedload, joinedload_all
from clld.db.meta import DBSession
from clld.db.models.common import Value, ValueSet
from clld.interfaces import IParameter
from clld.web.adapters.base import Representation

from lexibank.models import LexibankLanguage


SQL = """select s1.vpk, s2.vpk, s2.ppk, s2.fpk from
(
    select
        v1.name as form, v1.pk as vpk, vs1.parameter_pk as ppk, vs1.contribution_pk as cpk, vs1.language_pk as lpk
    from
        value as v1, valueset as vs1
    where
        v1.valueset_pk = vs1.pk
) as s1,
(
    select
        v2.name as form, v2.pk as vpk, vs2.parameter_pk as ppk, vs2.contribution_pk as cpk, vs2.language_pk as lpk, ll.family_pk as fpk
    from
        value as v2, valueset as vs2, language as l, lexibanklanguage as ll
    where
        v2.valueset_pk = vs2.pk and vs2.language_pk = l.pk and l.pk = ll.pk
) as s2
where
    -- same form, same language, same contribution, different concepts
    s1.form = s2.form and s1.lpk = s2.lpk and s1.cpk = s2.cpk and s1.ppk = {0} and s2.ppk != s1.ppk and s1.form != '**' and s1.form != '?'
order BY
    s2.ppk, s2.fpk
limit 100
"""


class Colexifications(Representation):
    """
    Colexifications are pairs of concepts, lexified with the same lexeme in the same
    language.
    """
    name = 'colexifications'
    template = 'parameter/colexifications_html.mako'
    mimetype = 'application/vnd.clld.colexifications+html'
    extension = 'colexifications.html'
    send_mimetype = 'text/html'
    rel = None

    def template_context(self, ctx, req):
        pairs = [(r[0], r[1]) for r in DBSession.execute(SQL.format(ctx.pk))]
        values = {
            v.pk: v for v in DBSession.query(Value)
            .filter(Value.pk.in_(list(chain(*pairs))))
            .options(
                joinedload_all(Value.valueset, ValueSet.language, LexibankLanguage.family),
                joinedload(Value.valueset, ValueSet.parameter),
                joinedload(Value.valueset, ValueSet.contribution))
            }
        distinct_families = defaultdict(set)
        for v1, v2 in pairs:
            distinct_families[values[v2].valueset.parameter_pk].add(
                values[v2].valueset.language.family_pk)
        return {'pairs': pairs, 'values': values, 'families': distinct_families}


def includeme(config):
    config.register_adapter(Colexifications, IParameter)
