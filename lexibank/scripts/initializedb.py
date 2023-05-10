import pathlib
import itertools
from collections import defaultdict

import transaction
from pycldf.db import Database
from csvw.dsv import reader
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from clld.cliutil import Data, bibtex2source
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.bibtex import EntryType
from clld_glottologfamily_plugin.util import load_families
from clldutils.path import Path
from clldutils.jsonlib import load
from pyglottolog.api import Glottolog
from pyconcepticon.api import Concepticon

import lexibank
#from lexibank.scripts.util import import_cldf
from lexibank.models import LexibankLanguage, Concept, Provider, Form

CLICS_LIST = pathlib.Path('/home/robert/projects/concepticon/concepticon-cldf/raw/'
                          'concepticon-data/concepticondata/conceptlists/Rzymski-2020-1624.tsv')


def main(args):
    cldf = args.cldf
    db = Database(cldf, fname=cldf.directory / '..' / 'lexibank.sqlite')
    clusters = {row['CONCEPTICON_ID']: row for row in reader(CLICS_LIST, delimiter='\t', dicts=True)}

    with transaction.manager:
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

        #
        # ID>-----Organization>---Dataset>Source>-Zenodo>-Todo>---ClicsCore>------LexiCore>-------CogCore>ProtoCore>------Version
        contribs = {
            row['Source']: row for row in reader(
                cldf.directory / '..' / 'etc' / 'lexibank-bliss.tsv', delimiter='\t', dicts=True)
        }
        data = Data()

        for row in db.query("select distinct sourcetable_id from formtable_sourcetable"):
            contrib = contribs[row[0]]
            src = cldf.sources[row[0]]
            try:
                src.genre = EntryType.get(src.genre)
            except ValueError:
                src.genre = EntryType.misc
            p = data.add(Provider, row[0], id=row[0], name='{}. {}. {}'.format(src.get('author') or src.get('editor'), src['year'], src['title']))
            data.add(common.Source, row[0], _obj=bibtex2source(src))
        for row in cldf.iter_rows('LanguageTable'):
            data.add(LexibankLanguage, row['ID'], id=row['ID'], name=row['Name'])

        for row in cldf.iter_rows('ParameterTable'):
            cluster = clusters.get(row['Concepticon_ID'])
            data.add(
                Concept, row['ID'],
                id=row['Concepticon_ID'],
                name=row['Name'],
                cluster_id=cluster['COMMUNITY'] if cluster else None,
                central_concept=cluster['CENTRAL_CONCEPT'] if cluster else None)

        DBSession.flush()
        for key in data:
            data[key] = {k: v.pk for k, v in data[key].items()}

    with db.connection() as conn:
        cu = conn.cursor()
        cu.execute('select f.* from formtable as f')
        formcols = [r[0] for r in cu.description]

    for src in data['Source']:
        with transaction.manager:
            vss = Data()
            print('{} ...'.format(src))
            for row in db.query(
                "select f.* from formtable as f, formtable_sourcetable as s "
                "where s.formtable_cldf_id = f.cldf_id and s.sourcetable_id = ?",
                (src,)
            ):
                row = dict(zip(formcols, row))
                vsid = (src, row['cldf_languageReference'], row['cldf_parameterReference'])
                vs = vss['ValueSet'].get(vsid)
                if not vs:
                    vs = vss.add(
                        common.ValueSet,
                        vsid,
                        id='{}-{}-{}'.format(*vsid),
                        language_pk=data['LexibankLanguage'][row['cldf_languageReference']],
                        parameter_pk=data['Concept'][row['cldf_parameterReference']],
                        contribution_pk=data['Provider'][src],
                    )
                DBSession.add(Form(
                    id=row['cldf_id'],
                    name=row['cldf_form'],
                    segments=row['cldf_segments'],
                    CV_Template=row['CV_Template'],
                    Prosodic_String=row['Prosodic_String'],
                    Dolgo_Sound_Classes=row['Dolgo_Sound_Classes'],
                    SCA_Sound_Classes=row['SCA_Sound_Classes'],
                    valueset=vs))
    return

    glottolog_repos = Path(
        lexibank.__file__).parent.parent.parent.parent.joinpath('glottolog3', 'glottolog')
    languoids = {l.id: l for l in Glottolog(glottolog_repos).languoids()}
    concepticon = Concepticon(
        Path(lexibank.__file__).parent.parent.parent.parent.joinpath('concepticon', 'concepticon-data'))
    conceptsets = {c.id: c for c in concepticon.conceptsets.values()}

    skip = True
    for dname in sorted(repos.joinpath('datasets').iterdir(), key=lambda p: p.name):
        #if dname.name == 'benuecongo':
        #    skip = False
        #if skip:
        #    continue
        if dname.is_dir() and dname.name != '_template':
            mdpath = dname.joinpath('cldf', 'metadata.json')
            if mdpath.exists():
                print(dname.name)
                import_cldf(dname, load(mdpath), languoids, conceptsets)

    with transaction.manager:
        load_families(
            Data(),
            DBSession.query(LexibankLanguage),
            glottolog_repos=glottolog_repos,
            isolates_icon='tcccccc')


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
    for concept in DBSession.query(Concept):
        concept.representation = DBSession.query(common.Language)\
            .join(common.ValueSet)\
            .filter(common.ValueSet.parameter_pk == concept.pk)\
            .distinct()\
            .count()

    for prov in DBSession.query(Provider):
        q = DBSession.query(common.ValueSet.language_pk)\
            .filter(common.ValueSet.contribution_pk == prov.pk)\
            .distinct()
        prov.language_count = q.count()
        prov.update_jsondata(language_pks=[r[0] for r in q])

        prov.parameter_count = DBSession.query(common.ValueSet.parameter_pk) \
            .filter(common.ValueSet.contribution_pk == prov.pk) \
            .distinct() \
            .count()
        prov.lexeme_count = DBSession.query(common.Value.pk)\
            .join(common.ValueSet)\
            .filter(common.ValueSet.contribution_pk == prov.pk)\
            .count()
