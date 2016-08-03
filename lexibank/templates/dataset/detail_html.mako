<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<%def name="sidebar()">
    <img src="${request.static_url('lexibank:static/glottobank_all.jpg')}"/>

    <%util:well title="lexibank data repository">
        <a href="${req.resource_url(req.dataset)}" style="font-family: monospace">lexibank.clld.org</a>
        serves the latest
        ${h.external_link('https://github.com/glottobank/lexibank-data/releases', label='released version')}
        of data curated at
        ${h.external_link('https://github.com/glottobank/lexibank-data', label='glottobank/lexibank-data')}.
    </%util:well>
</%def>

<h2>Welcome to lexibank</h2>

<p class="lead">
    The lexicon of the world's languages.
</p>
    <table class="table table-nonfluid">
        <tbody>
            <tr>
                <th><a href="${request.route_url('contributions')}">Datasets</a></th>
                <td class="right">${'{:,}'.format(stats['contribution'])}</td>
                <td></td>
            </tr>
            <tr>
                <th>Lexical items</th>
                <td class="right">${'{:,}'.format(stats['value'])}</td>
                <td></td>
            </tr>
            <tr>
                <th><a href="${request.route_url('parameters')}">Concepts</a></th>
                <td class="right">${'{:,}'.format(stats['parameter'])}</td>
                <td></td>
            </tr>
            <tr>
                <th><a href="${request.route_url('cognatesets')}">Cognate sets</a></th>
                <td class="right">${'{:,}'.format(stats['cognateset'])}</td>
                <td></td>
            </tr>
            <tr>
                <th><a href="${request.route_url('languages')}">Languages</a></th>
                <td class="right">${'{:,}'.format(stats['language'])}</td>
                <td>from ${stats['family']} families</td>
            </tr>
            % for fid, fname, count in families:
                <tr>
                    <td></td>
                    <td class="right">${count}</td>
                    <th><a href="${request.route_url('family', id=fid)}">${fname}</a></th>
                </tr>
            % endfor
        </tbody>
    </table>
