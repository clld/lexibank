<%inherit file="../home_comp.mako"/>

<%def name="sidebar()">
##    <div class="well">
 ##       <h3>Sidebar</h3>
##        <p>
##            Content
##        </p>
##    </div>
</%def>

<h2>Welcome to lexibank</h2>

<p class="lead">
    The lexicon of the world's languages.
</p>
    <table class="table table-nonfluid">
        <tbody>
            <tr><th>Wordlists</th><td class="right">${stats['contribution']}</td></tr>
            <tr><th>Languages</th><td class="right">${stats['language']}</td></tr>
            <tr><th>Families</th><td class="right">${stats['family']}</td></tr>
            <tr><th>Lexical items</th><td class="right">${stats['value']}</td></tr>
            <tr><th>Concepts</th><td class="right">${stats['parameter']}</td></tr>
        </tbody>
    </table>
