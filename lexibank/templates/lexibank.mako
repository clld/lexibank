<%inherit file="app.mako"/>

##
## define app-level blocks:
## #263681
<%block name="brand">
    <a class="brand" href="${request.route_url('dataset')}"
       style="padding-top: 7px; padding-bottom: 2px;">
        <img width="34" src="${request.static_url('lexibank:static/logo.png')}"/>
        <span style="color: #f05622; font-weight: bold">lexibank</span>
    </a>
</%block>

${next.body()}
