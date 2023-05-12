<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Parameter')} ${ctx.name}</%block>

<%def name="sidebar()">
<div class="well">
    <dl>
        <dt>Concepticon conceptset:</dt>
        <dd>${u.concepticon_link(req, ctx, label=ctx.name)}</dd>
        % if ctx.central_concept:
            <dt>CLICS cluster:</dt>
            <dd>${u.clics_link(req, ctx, label=ctx.central_concept)}</dd>
        % endif
        <dt>Representation:</dt>
        <dd>
            <table class="table-condensed table-nonfluid">
                <tbody>
                <tr><th style="text-align: left;">Datasets:</th><td style="text-align: right;">${ctx.ndatasets}</td></tr>
                <tr><th style="text-align: left;">Languages:</th><td style="text-align: right;">${ctx.nlangs}</td></tr>
                <tr><th style="text-align: left;">Words:</th><td style="text-align: right;">${ctx.nwords}</td></tr>
                </tbody>
            </table>
        </dd>
    </dl>
</div>
</%def>


<h2>${_('Parameter')} ${ctx.name}</h2>

% if map_ or request.map:
${(map_ or request.map).render()}
% endif

${request.get_datatable('values', h.models.Value, parameter=ctx).render()}