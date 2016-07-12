from __future__ import unicode_literals

import transaction

from clld.db.meta import DBSession
from clld.db.models.common import ValueSet
from clld.scripts.util import Data
from clld.lib.bibtex import EntryType, FIELDS
from pycldf.dataset import Dataset
from pycldf.util import MD_SUFFIX

from lexibank.models import (
    LexibankLanguage, Concept, Counterpart, Provider, CounterpartReference,
    LexibankSource,
)


def cldf2clld(source, contrib, id_):
    name = source.id
    if source.get('author'):
        name = source['author']
    if source.get('year'):
        name += ' %s' % source['year']
    description = source.get('title')
    return LexibankSource(
        id='%s-%s' % (contrib.id, id_),
        provider=contrib,
        bibtex_type=getattr(EntryType, source.genre, EntryType.misc),
        name=name,
        description=description,
        **{k: v for k, v in source.items() if k in FIELDS})


def import_dataset(ds, contrib, languoids, conceptsets, sources):
    data = Data()
    concepts = {p.id: p for p in DBSession.query(Concept)}
    langs = {l.id: l for l in DBSession.query(LexibankLanguage)}

    for i, row in enumerate(ds.rows):
        if not row['Value'] or not row['Parameter_ID'] or not row['Language_ID']:
            continue

        lid = row['Language_ID'].lower()
        if lid == 'none':
            continue

        language = langs.get(lid)
        if language is None:
            languoid = languoids.get(lid)
            if not languoid:
                continue
            langs[lid] = language = LexibankLanguage(
                id=lid,
                name=languoid.name,
                latitude=languoid.latitude,
                longitude=languoid.longitude)

        concept = concepts.get(row['Parameter_ID'])
        if concept is None:
            cs = conceptsets[row['Parameter_ID']]
            concepts[row['Parameter_ID']] = concept = Concept(
                # FIXME: get gloss and description from concepticon!
                id=row['Parameter_ID'], name=cs['GLOSS'], description=cs['DEFINITION'], semanticfield=cs['SEMANTICFIELD'])

        vsid = '%s-%s-%s' % (ds.name, language.id, concept.id)
        vid = '%s-%s' % (contrib.id, row['ID'])

        vs = data['ValueSet'].get(vsid)
        if vs is None:
            vs = data.add(
                ValueSet, vsid,
                id=vsid,
                parameter=concept,
                language=language,
                contribution=contrib,
                source=None)  # FIXME: add sources!

        counterpart = Counterpart(
            id=vid,
            valueset=vs,
            name=row['Value'],
            description=row.get('Comment'),
            #loan=row.get('Loan') == 'yes'
        )

        #if row.get('Cognate_Set'):
        #    csid = row['Cognate_Set'].split(',')[0].strip()
        #    cs = Cognateset.get(csid, key='name', default=None)
        #    if cs is None:
        #        cs = Cognateset(name=csid)
        #    counterpart.cognateset = cs

        for ref in row.refs:
            CounterpartReference(
                counterpart=counterpart,
                source=sources[ref.source.id],
                description=ref.description)


def import_cldf(srcdir, md, languoids, conceptsets):
    with transaction.manager:
        contrib = Provider(
            id=srcdir.name,
            name=md['dcterms:title'],
            description=md.get('dcterms:bibliographicCitation'))
        DBSession.add(contrib)
        sources = {}
        cldfdir = srcdir.joinpath('cldf')
        for fname in cldfdir.glob('*' + MD_SUFFIX):
            ds = Dataset.from_file(cldfdir.joinpath(fname.name[:-len(MD_SUFFIX)]))
            for src in ds.sources.items():
                if src.id not in sources:
                    sources[src.id] = cldf2clld(src, contrib, len(sources) + 1)
            import_dataset(ds, contrib, languoids, conceptsets, sources)
