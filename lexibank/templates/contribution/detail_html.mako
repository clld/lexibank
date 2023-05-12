<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<%def name="sidebar()">
<div class="well">
    <h3>CLDF Dataset</h3>
    ${u.dataset_provenance(req, ctx, with_conceptlists=True)|n}
</div>
</%def>

<h2>Dataset ${ctx.id}</h2>

<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#languages" data-toggle="tab">Varieties</a></li>
        <li><a href="#words" data-toggle="tab">Words</a></li>
    </ul>
    <div class="tab-content" style="overflow: visible;">
        <div id="languages" class="tab-pane active">
            ${map.render()}

            ${request.get_datatable('languages', h.models.Language, contribution=ctx).render()}
        </div>
        <div id="words" class="tab-pane">
            ${request.get_datatable('values', h.models.Value, contribution=ctx).render()}
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
