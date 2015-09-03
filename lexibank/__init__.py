from pyramid.config import Configurator

from clld_glottologfamily_plugin.util import LanguageByFamilyMapMarker
from clld.interfaces import IValue, IValueSet, IMapMarker

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
    config.register_resource('cognateset', models.Cognateset, ICognateset)
    return config.make_wsgi_app()
