from __future__ import unicode_literals

from nameparser import HumanName
import transaction

from clldutils.misc import slug
from clld.db.meta import DBSession
from clld.db.models.common import ValueSet, Language
from clld.scripts.util import Data
from pycldf.dataset import Dataset
from pycldf.util import MD_SUFFIX

from lexibank.models import LexibankLanguage, Concept, Counterpart, Provider


def import_dataset(ds, contrib, languoids, conceptsets):
    #bibpath = os.path.join(dirpath, basename + '.bib')
    #if os.path.exists(bibpath):
    #    for rec in Database.from_file(bibpath):
    #        if rec['key'] not in data['Source']:
    #            data.add(Source, rec['key'], _obj=bibtex2source(rec))

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
        vid = row['ID']

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

        #for key, src in data['Source'].items():
        #    if key in vs.source:
        #        ValueSetReference(valueset=vs, source=src, key=key)


def import_cldf(srcdir, md, languoids, conceptsets):
    with transaction.manager:
        contrib = Provider(
            id=srcdir.name,
            name=md['dcterms:title'],
            description=md.get('dcterms:bibliographicCitation'))
        DBSession.add(contrib)
        cldfdir = srcdir.joinpath('cldf')
        for fname in cldfdir.glob('*' + MD_SUFFIX):
            ds = Dataset.from_file(cldfdir.joinpath(fname.name[:-len(MD_SUFFIX)]))
            import_dataset(ds, contrib, languoids, conceptsets)
