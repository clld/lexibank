from sqlalchemy.orm import joinedload
from clld import interfaces
from clld.web.maps import ParameterMap, Map, SelectedLanguagesMap
from clld.web.adapters.geojson import GeoJsonParameter, GeoJson
from clld.db.models.common import ValueSet, Value
from clld.db.meta import DBSession

from lexibank.models import LexibankLanguage


class GeoJsonConcept(GeoJsonParameter):
    def get_query(self, ctx, req):
        return DBSession.query(ValueSet) \
            .filter(ValueSet.parameter == ctx) \
            .options(
                joinedload(ValueSet.values).joinedload(Value.valueset),
                joinedload(ValueSet.language).joinedload(LexibankLanguage.family))


class ConceptMap(ParameterMap):
    def get_options(self):
        return {'icon_size': 15}


class LanguagesMap(Map):
    def get_options(self):
        return {'icon_size': 15, 'max_zoom': 10}


class DatasetLanguagesMap(SelectedLanguagesMap):
    def get_options(self):
        res = SelectedLanguagesMap.get_options(self)
        res['max_zoom'] = 10
        return res


def includeme(config):
    config.register_map('parameter', ConceptMap)
    config.register_map('languages', LanguagesMap)
    config.register_adapter(
        GeoJsonConcept,
        interfaces.IParameter,
        name=GeoJson.mimetype)
