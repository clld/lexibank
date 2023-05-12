<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>
<%block name="title">${_('Contributions')}</%block>

<h2>${_('Contributions')}</h2>
<p>
    Note that the dataset served here only aggregates a selection of the data from its constituent
    datasets. Only varieties with at least 100 segmented words for at least 100 different concepts
    are taken into account. In addition, only one variety per Glottocode - the one with the biggest
    number of words - from all datasets was included.
</p>
<div>
    ${ctx.render()}
</div>
