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

<table class="table table-nonfluid">
    <tr>
        <td>Concepts</td>
        <td class="right">${ctx.parameter_count}</td>
    </tr>
    <tr>
        <td>Lexemes</td>
        <td class="right">${'{0:,}'.format(ctx.lexeme_count)}</td>
    </tr>
    <tr>
        <td>Synonymy index</td>
        <td class="right">${'{0:.2f}'.format(ctx.synonym_index)}</td>
    </tr>
</table>

<h3>Languages</h3>

${map.render()}

${request.get_datatable('languages', h.models.Language, contribution=ctx) .render()}
