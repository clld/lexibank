<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>

<h2>Colexifications for concept ${h.link(request, ctx)}</h2>

<p>
    Concepts which are colexified with <em>${ctx.name}</em> in languages of more than one
    family are <span style="background-color: coral">highlighted</span>
</p>

<%util:table items="${pairs}" eid="colex" args="item" class_="table">\
    <%def name="head()">
        <th>lexeme</th>
        <th>concept</th>
        <th>lexeme</th>
        <th>concept</th>
        <th>language</th>
        <th>family</th>
        <th>dataset</th>
    </%def>
    <% v1, v2 = item %>
    <td>${h.link(request, values[v1])}</td>
    <td>${h.link(request, values[v1].valueset.parameter)}</td>
    <td>${h.link(request, values[v2])}</td>
    <td style="background-color: ${'coral' if len(families[values[v2].valueset.parameter_pk]) > 1 else '#eee'}">
        ${h.link(request, values[v2].valueset.parameter)}
    </td>
    <td>${h.link(request, values[v2].valueset.language)}</td>
    <td>${values[v2].valueset.language.family or 'isolate'}</td>
    <td>${h.link(request, values[v2].valueset.contribution)}</td>
</%util:table>

