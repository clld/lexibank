import math

from sqlalchemy.orm import joinedload
from clld import RESOURCES
from clld.db.meta import DBSession
from clld.db.models.common import Language, Config
from clld.web.util.htmllib import HTML, literal
from clld.web.util import glottolog
from clld.web.util import concepticon
from clld.web.util.helpers import link

from lexibank.models import LexibankLanguage
from lexibank.maps import DatasetLanguagesMap


assert glottolog and concepticon
#
# FIXME:
#  CLICS-link
#


def concepticon_link(request, concept, label=None):
    return HTML.a(
        HTML.img(
            src=request.static_url('lexibank:static/concepticon_logo.png'),
            width=20),
        literal('&nbsp;' + label) if label else '',
        title='corresponding concept set at Concepticon',
        href=concept.concepticon_url)


def clics_link(request, concept, label=None):
    if concept.clics_url:
        return HTML.a(
            HTML.img(
                src=request.static_url('lexibank:static/clics.svg'),
                width=20),
            literal('&nbsp;' + label) if label else '',
            title='corresponding infomap cluster in CLICS3',
            href=concept.clics_url)


def dataset_provenance(req, contribution, with_conceptlists=False):
    dl = [
        HTML.dt('Zenodo:'),
        HTML.dd(HTML.a(contribution.doi, href="https://doi.org/{}".format(contribution.doi))),
        HTML.dt('GitHub:'),
        HTML.dd(HTML.a('/'.join(contribution.url.split('/')[-2:]),
                       href="{}/tree/{}".format(contribution.url, contribution.version)),
                literal('&nbsp;[' + contribution.version + ']')),
        HTML.dt('Source:'),
        HTML.dd(HTML.blockquote(contribution.source.bibtex().text()))
    ]
    if with_conceptlists:
        for i, cl in enumerate(contribution.jsondata['conceptlists']):
            if i == 0:
                dl.append(HTML.dt('Conceptlists:'))
            dl.append(HTML.dd(concepticon.link(req, id=cl, obj_type='ConceptList', label=cl)))
    return HTML.div(link(req, contribution, label=contribution.name), HTML.dl(*dl))


def value_detail_html(context=None, request=None, **kw):
    bipa = DBSession.query(Config).filter(Config.key=='bipa_mapping').one().jsondata
    return {'segments': [(s, bipa.get(s)) for s in context.segments.split()]}


def contribution_detail_html(context=None, request=None, **kw):
    langs = DBSession.query(Language)\
        .filter(LexibankLanguage.contribution==context)\
        .options(joinedload(LexibankLanguage.family))
    return {'map': DatasetLanguagesMap(context, request, list(langs))}


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
    return dict(
        stats=context.get_stats(
            [rsc for rsc in RESOURCES if rsc.name in ['language', 'parameter', 'value', 'contribution']]))
