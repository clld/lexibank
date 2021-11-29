from pathlib import Path

from clld.web.assets import environment

import lexibank


environment.append_path(
    str(Path(lexibank.__file__).parent.joinpath('static')), url='/lexibank:static/')
environment.load_path = list(reversed(environment.load_path))
