from __future__ import unicode_literals
import sys
import os
import transaction

from clld.scripts.util import initializedb, Data
from clld.db.meta import DBSession
from clld.db.models import common
from clld_glottologfamily_plugin.util import load_families

import lexibank
from lexibank.scripts.util import import_cldf
from lexibank.models import LexibankLanguage, Concept


def main(args):
    datadir = '/home/robert/venvs/glottobank/lexibank'

    with transaction.manager:
        dataset = common.Dataset(
            id=lexibank.__name__,
            name="LexiBank",
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

    for provider in [
        'transnewguinea',
        'abvd',
        'ids',
    ]:
        import_cldf(os.path.join(datadir, provider, 'cldf'), provider)

    with transaction.manager:
        load_families(Data(), DBSession.query(LexibankLanguage), isolates_icon='tcccccc')


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
    for concept in DBSession.query(Concept):
        concept.representation = DBSession.query(common.ValueSet)\
            .filter(common.ValueSet.parameter_pk == concept.pk)\
            .count()


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
