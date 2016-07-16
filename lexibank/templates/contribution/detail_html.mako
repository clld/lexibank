<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<h2>${_('Contribution')} ${ctx.name}</h2>

<small>cite as</small>
<blockquote>
    ${ctx.description}
</blockquote>
% if ctx.url:
    <p>Available online at ${h.external_link(ctx.url)}</p>
% endif

<h3>Languages</h3>

${map.render()}

${request.get_datatable('languages', h.models.Language, contribution=ctx) .render()}
