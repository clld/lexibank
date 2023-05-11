import math
from itertools import groupby

from sqlalchemy import func, desc, text
from sqlalchemy.orm import joinedload
from clld_glottologfamily_plugin.models import Family
from clld import RESOURCES
from clld.db.meta import DBSession
from clld.db.models.common import Language, Value, ValueSet, Config
from clld.web.util.htmllib import HTML
from clld.web.maps import SelectedLanguagesMap
from clld.web.util import glottolog
from clld.web.util import concepticon

from lexibank.models import LexibankLanguage


#
# FIXME:
#  CLICS-link
#  CLTS-link
#


def concepticon_link(request, concept):
    return HTML.a(
        HTML.img(
            src=request.static_url('lexibank:static/concepticon_logo.png'),
            height=20,
            width=30),
        title='corresponding concept set at Concepticon',
        href=concept.concepticon_url)


def value_detail_html(context=None, request=None, **kw):
    bipa = DBSession.query(Config).filter(Config.key=='bipa_mapping').one().jsondata
    return {'segments': [(s, bipa.get(s)) for s in context.segments.split()]}


def contribution_detail_html(context=None, request=None, **kw):
    langs = DBSession.query(Language)\
        .filter(Language.pk.in_(context.jsondata['language_pks']))\
        .options(joinedload(LexibankLanguage.family))
    return {'map': SelectedLanguagesMap(context, request, list(langs))}


def language_detail_html(context=None, request=None, **kw):
    from pyclts.ipachart import VowelTrapezoid, PulmonicConsonants, Segment

    def color(freq, maxfreq):
        hexnum = hex(math.floor(128 - freq / maxfreq * 127)).upper().replace('0X', '')
        return 'c' + hexnum, '#{0}{0}{0}'.format(hexnum)

    colorspec = {}
    maxfreq = max(context.jsondata['inventory'].values())
    for freq in context.jsondata['inventory'].values():
        cls, col = color(freq, maxfreq)
        colorspec[cls] = (col, None)

    bipa = DBSession.query(Config).filter(Config.key=='bipa_mapping').one().jsondata
    inventory = [
        Segment(
            sound_bipa=v,
            sound_name=bipa[v],
            href='https://clts.clld.org/parameters/{}'.format(bipa[v].replace(' ', '_')),
            css_class=color(freq, maxfreq)[0],
        ) for v, freq in context.jsondata['inventory'].items()]

    res = {}
    d = VowelTrapezoid()
    covered = d.fill_slots(inventory)
    res['vowels_html'], res['vowels_css'] = d.render(colorspec=colorspec)
    d = PulmonicConsonants()
    covered = covered.union(d.fill_slots(inventory))
    res['consonants_html'], res['consonants_css'] = d.render(colorspec=colorspec)
    res['uncovered'] = [p for i, p in enumerate(inventory) if i not in covered]
    return res


def dataset_detail_html(context=None, request=None, **kw):
    families = DBSession.query(Family.id, Family.name, func.count(LexibankLanguage.id).label('c'))\
        .join(LexibankLanguage)\
        .group_by(Family.id, Family.name)\
        .order_by(desc(text('c')))

    return dict(
        families=families,
        stats=context.get_stats([rsc for rsc in RESOURCES if rsc.name in [
            'language', 'family', 'cognateset', 'contribution', 'value', 'parameter']]))
