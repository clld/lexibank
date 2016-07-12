<%inherit file="../home_comp.mako"/>

<%def name="sidebar()">
    <img src="${request.static_url('lexibank:static/glottobank_all.jpg')}"/>

    ##<div class="well">
    ##   <h3>Sidebar</h3>
    ##    <p>
    ##        Content
     ##   </p>
    ##</div>
</%def>

<h2>Welcome to lexibank</h2>

<p class="lead">
    The lexicon of the world's languages.
</p>
<p>
    lexibank aggregates data from many <a href="${request.route_url('contributions')}">providers</a>.
</p>
    <table class="table table-nonfluid">
        <tbody>
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
