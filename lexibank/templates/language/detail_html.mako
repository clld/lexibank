<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="head">
<style>
    table caption {
        text-align: left;
    }

    figure {
        display: table;
        margin-left: 0px;
    }

    figcaption {
        display: table-caption;
        caption-side: top;
        font-size: 120%;
    }

    ${vowels_css}
    ${consonants_css}
    ${consonants_css.replace('pulmonic-consonants', 'special-segments')}
    table caption {
        display: none !important;
    }

    figure figcaption {
        display: none !important;
    }
</style>
</%block>

<%block name="title">${_('Language')} ${ctx.name}</%block>


<%def name="sidebar()">
${util.codes()}
<div style="clear: both;" class="well">
    <h3>Dataset</h3>
    ${u.dataset_provenance(req, ctx.contribution)|n}
</div>
<div class="well">
    % if ctx.latitude is not None:
    ${request.map.render()}
    ${h.format_coordinates(ctx)}
    % endif
</div>
</%def>

<h2>Variety ${ctx.name} (${ctx.family.name if ctx.family else 'isolate'})</h2>


<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#words" data-toggle="tab">Words</a></li>
        <li><a href="#ipa" data-toggle="tab">IPA chart</a></li>
    </ul>
    <div class="tab-content" style="overflow: visible;">
        <div id="words" class="tab-pane active">
            ${request.get_datatable('values', h.models.Value, language=ctx).render()}
        </div>
        <div id="ipa" class="tab-pane">

            <h4>Consonants</h4>
            ${consonants_html.replace('&lt;sup&gt;', '<sup>').replace('&lt;/sup&gt;', '</sup>')|n}

            <h4 style="padding-top: 2em; clear: both;">Vowels</h4>
            ${vowels_html|n}

            <h4 style="padding-top: 2em;">Other segments</h4>
            <table class="table table-condensed table-nonfluid" id="special-segments">
                <caption>Other segments</caption>
                <tbody>
                % for segment in uncovered:
                <tr>
                    <td><a class="${segment.css_class}" href="${segment.href}">&nbsp;${segment.label|n}&nbsp;</a></td>￼
                    <td>${segment.title}</td>
                </tr>
                % endfor
                </tbody>
            </table>
        </div>
    </div>
    <script>
$(document).ready(function() {
    if (location.hash !== '') {
        $('a[href="#' + location.hash.substr(2) + '"]').tab('show');
    }
    return $('a[data-toggle="tab"]').on('shown', function(e) {
        return location.hash = 't' + $(e.target).attr('href').substr(1);
    });
});
    </script>
</div>
