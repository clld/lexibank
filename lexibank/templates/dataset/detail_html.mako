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

<h3>How to cite Lexibank</h3>
<p>Please cite the Lexibank paper</p>
<blockquote>
    List, JM., Forkel, R., Greenhill, S.J. et al. Lexibank, a public repository of standardized wordlists with computed phonological and lexical features. Sci Data 9, 316 (2022). <a href="https://doi.org/10.1038/s41597-022-01432-0">DOI: 10.1038/s41597-022-01432-0</a>
</blockquote>
<p>as well as the underlying dataset</p>
<blockquote>
    Johann-Mattis List, Robert Forkel, Simon J. Greenhill, Christoph Rzymski, Johannes Englisch, & Russell D. Gray. (2023). Lexibank Analysed [Data set]. In Scientific Data (v1.0, Vol. 9, Number 316, pp. 1–31). Zenodo. <a href="https://doi.org/10.5281/zenodo.7836668">DOI: 10.5281/zenodo.7836668</a>
</blockquote>


