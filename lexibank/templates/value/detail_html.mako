<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "values" %>
<%block name="title">${_('Value')} ${ctx.name}</%block>

<%def name="sidebar()">
    <div class="well">
       <h3>Dataset</h3>
        ${u.dataset_provenance(req, ctx.valueset.contribution)|n}
    </div>
</%def>

<h2>Form ${ctx.name}</h2>


<dl>
        <dt>Variety:</dt>
        <dd>${h.link(request, ctx.valueset.language)} [${ctx.valueset.language.name}]</dd>
    % if ctx.valueset.language.glottocode:
        <dt>Glottolog:</dt>
        <dd>${u.glottolog.link(req, id=ctx.valueset.language.glottocode, label=ctx.valueset.language.glottocode)}</dd>
    % endif
        <dt>Concept:</dt>
        <dd>${h.link(request, ctx.valueset.parameter)}</dd>
        <dt>Concepticon conceptset:</dt>
        <dd>${u.concepticon_link(request, ctx.valueset.parameter, label=ctx.valueset.parameter.name)}</dd>
    % if ctx.valueset.parameter.clics_url:
        <dt>CLICS cluster:</dt>
        <dd>${u.clics_link(req, ctx.valueset.parameter, label=ctx.valueset.parameter.central_concept)}</dd>
    % endif
        <dt>Segments:</dt>
    % if ctx.profile:
    <dd>Orthography profile: <a href="${ctx.valueset.contribution.profile_url(ctx.profile)}">${ctx.profile}</a></dd>
    % endif
        <dd>
            <table class="table table-nonfluid table-condensed">
                <thead>
                    <tr>
                        <th> </th>
                        % for s, bipa in segments:
                            % if bipa:
                                <td>
                                    <a href="https://clts.clld.org/parameters/${bipa.replace(' ', '_')}" title="${bipa}">
                                        ${s}</a></td>
                            % else:
                                ${s}
                            % endif
                        % endfor
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th>CV</th>
                        % for s in ctx.CV_Template:
                        <td><a href="https://clts.clld.org/contributions/cv?sSearch_0=${s}">${s}</a></td>
                        % endfor
                    </tr>
                    <tr>
                        <th>Dolgopolsky</th>
                        % for s in ctx.Dolgo_Sound_Classes:
                        <td><a href="https://clts.clld.org/contributions/dolgo?sSearch_0=${s}">${s}</a></td>
                        % endfor
                    </tr>
                    <tr>
                        <th>SCA</th>
                        % for s in ctx.SCA_Sound_Classes:
                        <td><a href="https://clts.clld.org/contributions/sca?sSearch_0=${s}">${s}</a></td>
                        % endfor
                    </tr>
                </tbody>
            </table>
        </dd>

    % if ctx.valueset.references:
        <dt>Source:</dt>
        <dd>${h.linked_references(request, ctx.valueset)}</dd>
    % endif
    % if ctx.description:
        <dt>Comment:</dt>
        <dd>${ctx.description}</dd>
    % endif

</dl>
