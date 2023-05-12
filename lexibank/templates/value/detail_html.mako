<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "values" %>
<%block name="title">${_('Value')} ${ctx.name}</%block>

<%def name="sidebar()">
    <div class="well">
       <h3>Dataset</h3>
        <dl>
            <dt>CLDF dataset:</dt>
            <dd>Zenodo: <a href="https://doi.org/${ctx.valueset.contribution.doi}">${ctx.valueset.contribution.doi}</a></dd>
            <dd>GitHub:
                <a href="https://doi.org/${ctx.valueset.contribution.url}">${'/'.join(ctx.valueset.contribution.url.split('/')[-2:])}</a>
                [${ctx.valueset.contribution.version}]
            </dd>
            <dt>Source:</dt>
            <dd>${h.link(request, ctx.valueset.contribution.source)}</dd>
        </dl>
    </div>
</%def>

<h2>Form ${ctx.name}</h2>


<dl>
        <dt>Language:</dt>
        <dd>${h.link(request, ctx.valueset.language)} [${ctx.valueset.language.name}]</dd>
    % if ctx.valueset.language.glottocode:
        <dd>Glottolog: ${u.glottolog.link(req, id=ctx.valueset.language.glottocode, label=ctx.valueset.language.glottocode)}</dd>
    % endif
        <dt>Concept:</dt>
        <dd>${h.link(request, ctx.valueset.parameter)}</dd>
        <dd>Concepticon conceptset: ${u.concepticon.link(request, ctx.valueset.parameter.id, label=ctx.valueset.parameter.name)}</dd>
    % if ctx.valueset.parameter.clics_url:
        <dd>CLICS cluster: <a href="${ctx.valueset.parameter.clics_url}">${ctx.valueset.parameter.central_concept}</a></dd>
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
