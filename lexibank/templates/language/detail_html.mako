<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${_('Language')} ${ctx.name}</%block>

<h2>${_('Language')} ${ctx.name}</h2>

${request.get_datatable('values', h.models.Value, language=ctx).render()}

<%def name="sidebar()">
    ${util.codes()}
    <div style="clear: right;"> </div>
    <div class="well">

        % if ctx.latitude is not None:
            ${request.map.render()}
            ${h.format_coordinates(ctx)}
        % endif
    </div>
</%def>
