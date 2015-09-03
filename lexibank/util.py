# coding: utf8
from __future__ import unicode_literals

from clld import RESOURCES


def dataset_detail_html(context=None, request=None, **kw):
    return dict(
        stats=context.get_stats(
            [rsc for rsc in RESOURCES
             if rsc.name in ['language', 'family', 'contribution', 'value', 'parameter']]))
