from clld.web.assets import environment
from clldutils.path import Path

import lexibank


environment.append_path(
    Path(lexibank.__file__).parent.joinpath('static').as_posix(), url='/lexibank:static/')
environment.load_path = list(reversed(environment.load_path))
