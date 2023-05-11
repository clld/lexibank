from itertools import groupby

import transaction
from six import text_type
from clld.db.meta import DBSession
from clld.db.models.common import ValueSet
from clld.cliutil import Data
from clld.lib.bibtex import EntryType, FIELDS
from csvw.dsv import reader
from pycldf.dataset import Dataset
from tqdm import tqdm

from lexibank.models import (
    LexibankLanguage, Concept, Form, LexibankDataset,
    LexibankSource,
)


def unique_id(contrib, local_id):
    return '%s-%s' % (contrib.id, local_id)


def cldf2clld(source, contrib, id_):
    name = source.id
    if source.get('author'):
        name = source['author']
    if source.get('year'):
        name += ' %s' % source['year']
    description = source.get('title')
    return LexibankSource(
        id=unique_id(contrib, id_),
        provider=contrib,
        bibtex_type=getattr(EntryType, source.genre, EntryType.misc),
        name=name,
        description=description,
        **{k: v for k, v in source.items() if k in FIELDS and k not in ['institution']})


def import_dataset(ds, contrib, languoids, conceptsets, sources, values):
    data = Data()
    concepts = {p.id: p for p in DBSession.query(Concept)}
    langs = {l.id: l for l in DBSession.query(LexibankLanguage)}

    for i, row in enumerate(ds.rows):
        if not row['Value'] or not row['Parameter_ID'] or not row['Language_ID']:
            continue

        lid = row['Language_ID'].lower()
        if lid == 'none':
            continue

        if not row['Parameter_ID'].strip():
            continue

        language = langs.get(lid)
        if language is None:
            languoid = languoids.get(lid)
            if not languoid:
                continue
            langs[lid] = language = LexibankLanguage(
                id=lid,
                name=languoid.name,
                level=text_type(languoid.level.name),
                latitude=languoid.latitude if languoid.id != 'plau1238' else -10,
                longitude=languoid.longitude)

        concept = concepts.get(row['Parameter_ID'])
        if concept is None:
            cs = conceptsets[row['Parameter_ID']]
            concepts[row['Parameter_ID']] = concept = Concept(
                id=row['Parameter_ID'],
                name=cs.gloss,
                description=cs.definition,
                semanticfield=cs.semanticfield)

        vsid = unique_id(contrib, '%s-%s-%s' % (ds.name, language.id, concept.id))
        vid = unique_id(contrib, row['ID'])

        vs = data['ValueSet'].get(vsid)
        if vs is None:
            vs = data.add(
                ValueSet, vsid,
                id=vsid,
                parameter=concept,
                language=language,
                contribution=contrib,
                source=None)  # FIXME: add sources!

        counterpart = values.add(
            Form, row['ID'],
            id=vid,
            valueset=vs,
            name=row['Form'],
            description=row.get('Comment'),
            context=row['Value'],
            variety_name=row.get('Language_name'),
            loan=row.get('Loan', False),
        )

        for ref in row.refs:
            CounterpartReference(
                counterpart=counterpart,
                source=sources[ref.source.id],
                description=ref.description)


def import_cldf(srcdir, md, languoids, conceptsets):
    with transaction.manager:
        contrib = LexibankDataset(
            id=srcdir.name,
            name=md['dc:title'],
            description=md.get('dc:bibliographicCitation'),
            url=md.get('dc:identifier'),
            license=md.get('dc:license'),
            aboutUrl=md.get('aboutUrl'),
        )
        DBSession.add(contrib)
        sources = {}
        cldfdir = srcdir.joinpath('cldf')
        values = Data()
        for fname in tqdm(list(cldfdir.glob('*' + MD_SUFFIX)), leave=False):
            ds = Dataset.from_metadata(fname)
            for src in ds.sources.items():
                if src.id not in sources:
                    sources[src.id] = cldf2clld(src, contrib, len(sources) + 1)
            import_dataset(ds, contrib, languoids, conceptsets, sources, values)
            DBSession.flush()
