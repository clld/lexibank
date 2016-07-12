<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Parameter')} ${ctx.name}</%block>

<h2>${_('Parameter')} ${ctx.name} ${u.concepticon_link(request, ctx)}</h2>
<div>
    ${h.alt_representations(req, ctx, doc_position='right', exclude=['snippet.html'])|n}
    % if ctx.description:
        <div class="alert alert-info">${ctx.description}</div>
    % endif
</div>

% if map_ or request.map:
${(map_ or request.map).render()}
% endif

${request.get_datatable('values', h.models.Value, parameter=ctx).render()}