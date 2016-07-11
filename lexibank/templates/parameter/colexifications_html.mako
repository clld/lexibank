<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>

<h2>Colexifications for concept ${ctx.name}</h2>

<blockquote>
    ${ctx.description}
</blockquote>

<table class="table">
<thead></thead>
    <tbody>
    % for v1, v2 in pairs:
    <tr>
        <td>${h.link(request, values[v1])}</td>
        <td>${h.link(request, values[v1].valueset.parameter)}</td>
        <td>${h.link(request, values[v2])}</td>
        <td style="background-color: ${'coral' if len(families[values[v2].valueset.parameter_pk]) > 1 else '#eee'}">
            ${h.link(request, values[v2].valueset.parameter)}
        </td>
        <td>${h.link(request, values[v2].valueset.language)}</td>
        <td>${values[v2].valueset.language.family or 'isolate'}</td>
        <td>${h.link(request, values[v2].valueset.contribution)}</td>
    </tr>
    % endfor
    </tbody>
</table>