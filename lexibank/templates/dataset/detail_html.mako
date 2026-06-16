<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<%def name="sidebar()">
    <img src="${request.static_url('lexibank:static/glottobank_all.jpg')}"/>
    <div class="well well-small">
        <h3>Statistics</h3>
        <table class="table table-condensed">
            <tbody>
            <tr>
                <th><a href="${req.route_url('languages')}">Languages</a></th>
                <td class="right">${'{:,}'.format(stats['language'])}</td>
            </tr>
            <tr>
                <th><a href="${req.route_url('parameters')}">Concepts</a></th>
                <td class="right">${'{:,}'.format(stats['parameter'])}</td>
            </tr>
            <tr>
                <th><a href="${req.route_url('values')}">Words</a></th>
                <td class="right">${'{:,}'.format(stats['value'])}</td>
            </tr>
            </tbody>
        </table>
    </div>
</%def>

<h2>Welcome to Lexibank</h2>

<p>
    Lexibank is different things:
</p>
<ul>
    <li>A framework to curate lexical data. (See ${h.external_link('https://github.com/lexibank/')}.)</li>
    <li>A <a href="https://zenodo.org/communities/lexibank">Zenodo community</a>, collecting released Lexibank datasets.</li>
    <li>This clld web application, serving an annotated aggregation of selected data from
        <a href="${req.route_url('contributions')}">${stats['contribution']} <em>Lexibank datasets</em></a>.</li>
</ul>

<h3>How to cite Lexibank 2</h3>
<p>Please cite the Lexibank paper</p>
<blockquote>
    List, JM., Forkel, R., Greenhill, S.J. et al. Lexibank, a public repository of standardized wordlists with computed phonological and lexical features. Sci Data 9, 316 (2022). <a href="https://doi.org/10.1038/s41597-022-01432-0">DOI: 10.1038/s41597-022-01432-0</a>
</blockquote>
<p>as well as the underlying dataset for version 2</p>
<blockquote>
    Frederic Blum, Carlos Barrientos, Johannes Englisch, Robert Forkel, Simon J. Greenhill, Christoph Rzymski, & Johann-Mattis List. (2026). Lexibank 2: pre-computed features for large-scale lexical data (v2.2) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.20712996
</blockquote>
<p>and its description</p>
<blockquote>
    Blum, Frederic, Carlos Barrientos, Johannes Englisch, Robert Forkel, Simon J. Greenhill, Christoph Rzymski & Johann-Mattis List. 2025a. Lexibank 2: pre-computed features for large-scale lexical data. Open Research Europe 5(126). 1–27.
    <a href="https://doi.org/10.12688/openreseurope.20216.2">https://doi.org/10.12688/openreseurope.20216.2</a>.
</blockquote>
