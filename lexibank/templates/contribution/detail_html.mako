<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<%def name="sidebar()">
<div class="well">
<dl>
    <dt>CLDF dataset:</dt>
    <dd>${ctx.name}</dd>
    <dd>Zenodo: <a href="https://doi.org/${ctx.doi}">${ctx.doi}</a></dd>
    <dd>GitHub:
        <a href="https://doi.org/${ctx.url}">${'/'.join(ctx.url.split('/')[-2:])}</a>
        [${ctx.version}]
    </dd>
    <dt>Source:</dt>
    <dd>${ctx.source.bibtex().text()}</dd>
    % if ctx.jsondata['conceptlists']:
        <dt>Concept lists:</dt>
        % for cl in ctx.jsondata['conceptlists']:
            <dd>${u.concepticon.link(req, id=cl, obj_type='ConceptList', label=cl)}</dd>
        % endfor
    % endif
</dl>
</div>
</%def>


<h2>Dataset ${ctx.id}</h2>

${map.render()}

${request.get_datatable('languages', h.models.Language, contribution=ctx).render()}
