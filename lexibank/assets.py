from clld.web.assets import environment
from path import path

import lexibank


environment.append_path(
    path(lexibank.__file__).dirname().joinpath('static'), url='/lexibank:static/')
environment.load_path = list(reversed(environment.load_path))
