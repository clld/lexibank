import math

from sqlalchemy.orm import joinedload
from matplotlib import colormaps, colors
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
        #HTML.dt('GitHub:'),
        #HTML.dd(HTML.a('/'.join(contribution.url.split('/')[-2:]),
        #               href="{}/tree/{}".format(contribution.url, contribution.version)),
        #        literal('&nbsp;[' + str(contribution.version) + ']')),
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
    def color(freq, maxfreq):
        hexnum = colors.to_hex(colormaps['viridis'](1 - (freq / float(2*maxfreq) + 0.5)))
        return 'c' + hexnum[1:], hexnum

    colorspec = {}
    css_class = {}
    maxfreq = max(context.jsondata['frequencies'].values())
    for c, freq in context.jsondata['frequencies'].items():
        cls, col = color(freq, maxfreq)
        colorspec[cls] = (col, None)
        css_class[c] = cls

    bipa = DBSession.query(Config).filter(Config.key=='bipa_mapping').one().jsondata

    def customize_segment(segment):
        if segment.sound_bipa in bipa:
            segment.sound_name = bipa[segment.sound_bipa]
            segment.css_class = css_class[segment.sound_bipa]
        return segment

    res = context.render_inventory(request=request, render_kw=dict(colorspec=colorspec), customize_segment=customize_segment)

    labels, colors_, lower = [], [], 0
    for i in range(1, 11):
        upper = math.ceil(i * 0.1 * maxfreq)
        labels.append(HTML.literal(f'{lower if lower == 0 else '&nbsp;&nbsp;'}-{upper}'))
        colors_.append(color(lower + (upper - lower) / 2.0, maxfreq)[1])
        lower = upper + 1

    res['frequency_legend'] = HTML.table(
        HTML.body(
            HTML.tr(*[HTML.td(label) for label in labels]),
            HTML.tr(*[HTML.td(HTML.literal('&nbsp;'), style=f'background-color: {c}') for c in colors_]),
        )
    )
    return res


def dataset_detail_html(context=None, request=None, **kw):
    return dict(
        stats=context.get_stats(
            [rsc for rsc in RESOURCES if rsc.name in ['language', 'parameter', 'value', 'contribution']]))
