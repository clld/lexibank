from __future__ import unicode_literals
import sys
import transaction
import os

from clld.scripts.util import initializedb, Data
from clld.db.meta import DBSession
from clld.db.models import common
from clld_glottologfamily_plugin.util import load_families
from clldutils.path import Path
from clldutils.jsonlib import load
from pyglottolog.api import Glottolog
from pyconcepticon.api import Concepticon

import lexibank
from lexibank.scripts.util import import_cldf
from lexibank.models import LexibankLanguage, Concept, Provider


def main(args):
    repos = Path(os.path.expanduser('~')).joinpath('venvs/lexibank/lexibank-data')

    with transaction.manager:
        dataset = common.Dataset(
            id=lexibank.__name__,
            name="lexibank",
            publisher_name="Max Planck Institute for the Science of Human History",
            publisher_place="Jena",
            publisher_url="http://shh.mpg.de",
            license="http://creativecommons.org/licenses/by/4.0/",
            domain='lexibank.clld.org',
            contact='forkel@shh.mpg.de',
            jsondata={
                'license_icon': 'cc-by.png',
                'license_name': 'Creative Commons Attribution 4.0 International License'})
        DBSession.add(dataset)

    glottolog = Glottolog(
        Path(lexibank.__file__).parent.parent.parent.parent.joinpath('glottolog3', 'glottolog'))
    languoids = {l.id: l for l in glottolog.languoids()}
    concepticon = Concepticon(
        Path(lexibank.__file__).parent.parent.parent.parent.joinpath('concepticon', 'concepticon-data'))
    conceptsets = {c['ID']: c for c in concepticon.conceptsets()}

    for dname in repos.joinpath('datasets').iterdir():
        if dname.is_dir() and dname.name != '_template':
            #if dname.name != 'zenodo34092':
            #    continue
            mdpath = dname.joinpath('metadata.json')
            if mdpath.exists():
                print(dname.name)
                import_cldf(dname, load(mdpath), languoids, conceptsets)

    with transaction.manager:
        load_families(
            Data(),
            DBSession.query(LexibankLanguage),
            glottolog=languoids,
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
        prov.language_count = DBSession.query(common.ValueSet.language_pk)\
            .filter(common.ValueSet.contribution_pk == prov.pk)\
            .distinct()\
            .count()
        prov.parameter_count = DBSession.query(common.ValueSet.parameter_pk) \
            .filter(common.ValueSet.contribution_pk == prov.pk) \
            .distinct() \
            .count()
        prov.lexeme_count = DBSession.query(common.Value.pk)\
            .join(common.ValueSet)\
            .filter(common.ValueSet.contribution_pk == prov.pk)\
            .count()


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
