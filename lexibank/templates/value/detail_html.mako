<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>
<%block name="title">${_('Value')} ${ctx.name}</%block>

<%def name="sidebar()">
    <div class="well">
       <h3>Dataset</h3>
        <p>${h.link(request, ctx.valueset.contribution)}</p>
        <small>cite as</small>
        <blockquote>
            ${ctx.valueset.contribution.description}
       </blockquote>
    </div>
</%def>

<h2>${_('Value')} ${ctx.name}</h2>

% if ctx.external_url:
    <p>${h.external_link(ctx.external_url)}</p>
% endif

<table class="table table-nonfluid">
    <tr>
        <th>Language:</th>
        <td>${h.link(request, ctx.valueset.language)} [${ctx.variety_name}]</td>
    </tr>
    <tr>
        <th>Parameter:</th>
        <td>${h.link(request, ctx.valueset.parameter)}</td>
    </tr>
    % if ctx.references:
        <tr>
            <th>Source:</th>
            <td>${h.linked_references(request, ctx)}</td>
        </tr>
    % endif
    % if ctx.context:
        <tr>
            <th>Context:</th>
            <td>${ctx.context}</td>
        </tr>
    % endif
    % if ctx.description:
        <tr>
            <th>Comment:</th>
            <td>${ctx.description}</td>
        </tr>
    % endif
</table>

% if synonyms:
    <h3>Synonyms</h3>
    <dl>
        % for prov, counterparts in synonyms:
            <dt>${h.link(request, prov)}</dt>
            <dd>
                <ul>
                    % for cp in counterparts:
                        <li>
                            ${h.link(request, cp)}
                            [${cp.variety_name}]
                        </li>
                    % endfor
                </ul>
            </dd>
        % endfor
    </dl>
% endif
