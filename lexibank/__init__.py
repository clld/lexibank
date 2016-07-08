from sqlalchemy.orm import joinedload
from pyramid.config import Configurator

from clld_glottologfamily_plugin.util import LanguageByFamilyMapMarker
from clld.interfaces import IValue, IValueSet, IMapMarker, ICtxFactoryQuery
from clld.web.app import CtxFactoryQuery
from clld.db.models.common import Contribution

# we must make sure custom models are known at database initialization!
from lexibank import models
from lexibank.interfaces import ICognateset


_ = lambda s: s
_('Parameter')
_('Parameters')
_('Contribution')
_('Contributions')
_('Value')
_('Values')
_('Valueset')
_('Valuesets')


class LexibankCtxFactoryQuery(CtxFactoryQuery):
    def refined_query(self, query, model, req):
        if model == Contribution:
            query = query.options(joinedload(Contribution.data))
        return query


class MyMapMarker(LanguageByFamilyMapMarker):
    def get_icon(self, ctx, req):
        if IValue.providedBy(ctx):
            ctx = ctx.valueset
        if IValueSet.providedBy(ctx):
            ctx = ctx.language
        return LanguageByFamilyMapMarker.get_icon(self, ctx, req)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clldmpg')
    config.include('clld_glottologfamily_plugin')
    config.registry.registerUtility(MyMapMarker(), IMapMarker)
    config.registry.registerUtility(LexibankCtxFactoryQuery(), ICtxFactoryQuery)
    config.register_resource('cognateset', models.Cognateset, ICognateset)
    return config.make_wsgi_app()
