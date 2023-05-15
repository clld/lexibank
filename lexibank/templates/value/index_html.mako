<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>Words</h2>
<div class="alert alert-info">
    <button type="button" class="close" data-dismiss="alert">&times;</button>
    <p>Lexibank allows searching for words along several axes. You can filter words</p>
    <ul>
        <li>based on the form as it appears in the source datasets</li>
        <li>by variety or language family</li>
        <li>
            by meaning - or similar meaning where <em>similarity</em> is defined as "meanings appearing
            in the same colexification cluster in <a href="https://clics.clld.org/">CLICS</a>"
        </li>
        <li>
            by characteristics of individual segments, specified as <a href="https://clts.clld.org/contributions/bipa">BIPA sounds</a>
            or as sound classes (such as Dolgopolsky and SCA sound classes or CV templates).
        </li>
    </ul>
    <p>
        The search inputs below the column headers in the search table allow a limited set of "regular expression"
        functionality for more precise search queries:
    </p>
    <ul>
        <li><strong>^</strong> can be used to specify that a query must match at the start of the searched string.</li>
        <li><strong>$</strong> can be used to specify that a query must match at the start of the searched string.</li>
        <li><strong>_</strong> can be used to specify a one-character wildcard in the middle of a search query.</li>
    </ul>
</div>

<div>
    ${ctx.render()}
</div>
