import os
import pathlib
import itertools
import collections
import urllib.parse

import transaction
from pycldf import Database, Dataset
from csvw.dsv import reader
from clld.cliutil import Data, bibtex2source
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.bibtex import EntryType
from clld_glottologfamily_plugin.util import load_families
from clldutils.jsonlib import load
from pyclts import CLTS
from pyclts.models import Sound
from nameparser import HumanName
from clld_ipachart_plugin.util import load_inventories

import lexibank
from lexibank.models import LexibankLanguage, Concept, LexibankDataset, Form


def iter_rows(db, table, query, params=None):
    with db.connection() as conn:
        cu = conn.cursor()
        cu.execute(f'select * from  {table} limit 1')
        cols = [r[0] for r in cu.description]

    for row in db.query(query, params or ()):
        yield dict(zip(cols, row))


def main(args):
    assert args.glottolog
    project_dir = args.cldf.directory / '..' / '..'

    bipa = CLTS(project_dir / 'clts-data').bipa
    clics4 = Dataset.from_metadata(project_dir / 'clics4' / 'cldf' / 'Wordlist-metadata.json')
    cluster = collections.defaultdict(list)
    for c in clics4.iter_rows('ParameterTable'):
        if c['CentralConcept']:
            cluster[c['CentralConcept']].append(c['Concepticon_ID'])
    rcluster = {}
    for cc, cids in cluster.items():
        if len(cids) > 1:
            for cid in cids:
                rcluster[cid] = cc
    cluster = rcluster

    cldf = args.cldf
    db = Database(cldf, fname=cldf.directory / '..' / 'lexibank.sqlite')
    c2con = {}

    with transaction.manager:
        data = Data()
        dataset = common.Dataset(
            id=lexibank.__name__,
            name="lexibank",
            publisher_name="Max Planck Institute for Evolutionary Anthropology",
            publisher_place="Leipzig",
            publisher_url="https://www.eva.mpg.de",
            license="http://creativecommons.org/licenses/by/4.0/",
            domain='lexibank.clld.org',
            contact='lexibank@eva.mpg.de',
            jsondata={
                'license_icon': 'cc-by.png',
                'license_name': 'Creative Commons Attribution 4.0 International License'})
        DBSession.add(dataset)

        zenodo = load(cldf.directory / '..' / '.zenodo.json')
        for i, name in enumerate((c['name'] for c in zenodo['creators']), start=1):
            n = HumanName(name)
            c = data.add(common.Contributor, n.last, id=n.last, name=name)
            DBSession.add(common.Editor(contributor=c, dataset=dataset, ord=i))


        contribs = {
            #ID,Name,Description,Contributor,Citation,Collection_IDs,Glottocodes,Doculects,Concepts,Senses,Forms,Source
            row['ID']: row for row in reader(cldf.directory / 'contributions.csv', dicts=True)
        }
        assert 'barlowkilliantomoip' in contribs
        for cid, c in contribs.items():
            src = cldf.sources[cid]
            c['dataset_source'] = src
            assert src['doi'] and src['github']
            assert 'zenodo' in src['doi'], src['doi']

            comps = urllib.parse.urlparse(src['github']).path.split('/')
            assert comps[-2] == 'tree'
            dl_dir = project_dir / 'lexibank-analysed' / 'raw' / cid
            if not dl_dir.exists():
                os.system(f'gh release download {comps[-1]} -A zip -R {comps[1]}/{comps[2]} -D {dl_dir}')
                os.system(f'unzip {dl_dir}/*.zip -d {dl_dir}')
                os.system(f'rm {dl_dir}/*.zip')

        profiles = collections.defaultdict(dict)
        for row in db.query("select distinct sourcetable_id from formtable_sourcetable"):
            contrib = contribs[row[0].lower()]
            d = cldf.directory / '..' / 'raw' / contrib['ID']
            assert d.exists(), d
            subdirs = [dd for dd in d.iterdir() if dd.is_dir()]
            assert len(subdirs) == 1
            d = subdirs[0]

            for p in d.joinpath('etc').glob('orthography'):
                if p.is_dir():
                    for pp in p.glob('*.tsv'):
                        profiles[row[0]][pp.stem] = f'{p.name}/{pp.name}'
            global_profile = d / 'etc' / 'orthography.tsv'
            if global_profile.exists():
                profiles[row[0]][None] = global_profile.name

            src = cldf.sources[row[0]]
            try:
                src.genre = EntryType.get(src.genre)
            except ValueError:
                src.genre = EntryType.misc
            source = data.add(common.Source, row[0], _obj=bibtex2source(src))
            md = load(d / 'metadata.json')
            conceptlist = md.get('conceptlist', [])
            url, _, version = src['github'].partition('/tree/')
            data.add(
                LexibankDataset, row[0],
                id=contrib['ID'],
                name=contrib['Name'],
                url=url,
                version=version,
                doi=src.get('doi'),
                source=source,
                jsondata=dict(conceptlists=[conceptlist] if isinstance(conceptlist, str) else conceptlist),
            )

        l2ds = {
            row[0]: row[1] for row in db.query(
                "select distinct f.cldf_languagereference, s.sourcetable_id from formtable as f, formtable_sourcetable as s where s.formtable_cldf_id = f.cldf_id;")
        }

        for row in iter_rows(
                db,
                'languagetable',
                "select l.* from languagetable as l where l.cldf_id in (select cldf_languagereference from formtable)",
        ):
            data.add(
                LexibankLanguage, row['cldf_id'],
                id=row['cldf_id'],
                name=row['cldf_name'],
                contribution=data['LexibankDataset'][l2ds[row['cldf_id']]],
                latitude=row['cldf_latitude'],
                longitude=row['cldf_longitude'],
                glottocode=row['cldf_glottocode'])

        for row in cldf.iter_rows('ParameterTable'):
            c2con[row['ID']] = row['Concepticon_ID']
            cc = cluster.get(row['Concepticon_ID'])
            data.add(
                Concept, row['ID'],
                id=row['Concepticon_ID'],
                name=row['Name'],
                cluster_id=cc,
                central_concept=cc,
            )

        DBSession.flush()
        for key in data:
            data[key] = {k: v.pk for k, v in data[key].items()}

    sounds = {}
    concepts = collections.defaultdict(lambda: dict(nwords=0, datasets=set(), languages=set()))
    for src in data['Source']:
        with transaction.manager:
            vss = Data()
            print(f'{src} ...')
            dscids, dsnwords = set(), 0
            for nlangs, (lid, rows) in enumerate(itertools.groupby(
                iter_rows(
                    db,
                    'formtable',
                    "select f.* from formtable as f, formtable_sourcetable as s "
                    "where s.formtable_cldf_id = f.cldf_id and s.sourcetable_id = ? order by f.cldf_languageReference",
                    (src,)),
                lambda r: r['cldf_languageReference']
            ), start=1):
                cids = set()
                for nwords, row in enumerate(rows, start=1):
                    cid = row['cldf_parameterReference']
                    concepts[cid]['nwords'] += 1
                    concepts[cid]['datasets'].add(src)
                    concepts[cid]['languages'].add(lid)
                    cids.add(cid)
                    vsid = (src, lid, cid)
                    vs = vss['ValueSet'].get(vsid)
                    if not vs:
                        vs = vss.add(
                            common.ValueSet,
                            vsid,
                            id='{}-{}-{}'.format(*vsid),
                            language_pk=data['LexibankLanguage'][lid],
                            parameter_pk=data['Concept'][cid],
                            contribution_pk=data['LexibankDataset'][src],
                        )

                    profile = None
                    if lid.split('-')[1] in profiles[src]:
                        profile = profiles[src][lid.split('-')[1]]
                    elif None in profiles[src]:
                        profile = profiles[src][None]

                    for s in row['cldf_segments'].split():
                        sound = bipa[s]
                        if isinstance(sound, Sound):
                            sounds[s] = sound.name
                    DBSession.add(Form(
                        id=row['cldf_id'],
                        name=row['cldf_form'],
                        segments=row['cldf_segments'],
                        profile=profile,
                        CV_Template=row['CV_Template'],
                        Prosodic_String=row['Prosodic_String'],
                        Dolgo_Sound_Classes=row['Dolgo_Sound_Classes'],
                        SCA_Sound_Classes=row['SCA_Sound_Classes'],
                        valueset=vs))
                lang = LexibankLanguage.get(lid)
                lang.nwords = nwords
                lang.nconcepts = len(cids)
                dscids |= cids
                dsnwords += nwords
            ds = LexibankDataset.get(data['LexibankDataset'][src])
            ds.nwords = dsnwords
            ds.nlangs = nlangs
            ds.nconcepts = len(dscids)

    with transaction.manager:
        for cid, data in concepts.items():
            c = Concept.get(c2con[cid])
            c.nwords = data['nwords']
            c.ndatasets = len(data['datasets'])
            c.nlangs = len(data['languages'])

        load_families(
            Data(),
            [(l.glottocode, l) for l in DBSession.query(LexibankLanguage)],
            glottolog_repos=args.glottolog,
            strict=False,
            isolates_icon='tcccccc')
        DBSession.add(common.Config(key='bipa_mapping', jsondata=sounds))
        load_inventories(db, CLTS(project_dir / 'clts-data'), {l.id: l for l in DBSession.query(LexibankLanguage)})


def prime_cache(args):
    pass

