from __future__ import unicode_literals
import os

from nameparser import HumanName
import transaction

from clld.util import jsonload, slug
from clld.db.meta import DBSession
from clld.db.models.common import ValueSet, ContributionContributor, Contributor, Language
from clld.lib.dsv import reader
from clld.scripts.util import Data

from clldclient.glottolog import Glottolog

from lexibank.models import LexibankLanguage, Concept, Counterpart, Wordlist, Cognateset


def import_dataset(path, provider):
    # look for metadata
    # look for sources
    # then loop over values
    dirpath, fname = os.path.split(path)
    basename, ext = os.path.splitext(fname)
    glottolog = Glottolog()

    mdpath = path + '-metadata.json'
    assert os.path.exists(mdpath)
    md = jsonload(mdpath)
    md, parameters = md['properties'], md['parameters']

    cname = md['name']
    if 'id' in md:
        cname = '%s [%s]' % (cname, md['id'])
    contrib = Wordlist(id=basename, name=cname)
    contributors = md.get('typedby', md.get('contributors'))

    if contributors:
        contributor_name = HumanName(contributors)
        contributor_id = slug(contributor_name.last + contributor_name.first)
        contributor = Contributor.get(contributor_id, default=None)
        if not contributor:
            contributor = Contributor(id=contributor_id, name='%s' % contributor_name)

        DBSession.add(
            ContributionContributor(contribution=contrib, contributor=contributor))

    #bibpath = os.path.join(dirpath, basename + '.bib')
    #if os.path.exists(bibpath):
    #    for rec in Database.from_file(bibpath):
    #        if rec['key'] not in data['Source']:
    #            data.add(Source, rec['key'], _obj=bibtex2source(rec))

    data = Data()
    concepts = {p.id: p for p in DBSession.query(Concept)}
    language = None

    for i, row in enumerate(reader(path, dicts=True, delimiter=',')):
        if not row['Value'] or not row['Feature_ID']:
            continue

        fid = row['Feature_ID'].split('/')[-1]
        vsid = '%s-%s-%s' % (basename, row['Language_ID'], fid)
        vid = '%s-%s-%s' % (provider, basename, i + 1)

        if language:
            assert language.id == row['Language_ID']
        else:
            language = Language.get(row['Language_ID'], default=None)
            if language is None:
                # query glottolog!
                languoid = glottolog.languoid(row['Language_ID'])
                language = LexibankLanguage(
                    id=row['Language_ID'],
                    name=languoid.name,
                    latitude=languoid.latitude,
                    longitude=languoid.longitude)

        parameter = concepts.get(fid)
        if parameter is None:
            concepts[fid] = parameter = Concept(
                id=fid,
                name=parameters[row['Feature_ID']],
                concepticon_url=row['Feature_ID'])

        vs = data['ValueSet'].get(vsid)
        if vs is None:
            vs = data.add(
                ValueSet, vsid,
                id=vsid,
                parameter=parameter,
                language=language,
                contribution=contrib,
                source=row.get('Source'))

        counterpart = Counterpart(
            id=vid,
            valueset=vs,
            name=row['Value'],
            description=row.get('Comment'),
            loan=row.get('Loan') == 'yes')

        if row.get('Cognate_Set'):
            csid = row['Cognate_Set'].split(',')[0].strip()
            cs = Cognateset.get(csid, key='name', default=None)
            if cs is None:
                cs = Cognateset(name=csid)
            counterpart.cognateset = cs

        #for key, src in data['Source'].items():
        #    if key in vs.source:
        #        ValueSetReference(valueset=vs, source=src, key=key)

    contrib.language = language


def import_cldf(srcdir, provider):
    for dirpath, dnames, fnames in os.walk(srcdir):
        for fname in fnames:
            if os.path.splitext(fname)[1] in ['.tsv', '.csv']:
                try:
                    with transaction.manager:
                        import_dataset(os.path.join(dirpath, fname), provider)
                        print os.path.join(dirpath, fname)
                except:
                    print 'ERROR'
                    raise
                #break

    pass
