LEXIBANK = {}
LEXIBANK.search_url = function (eid) {
    var iSortingCols = 0;
    var query = {};
    $('[id^="dt-filter-"]').each(function (index) {
        if ($(this).val()) {
            query['sSearch_' + index] = $(this).val();
        }
    })
    $('#' + eid).html('<a href="' + CLLD.url('/values', query) + '">' + CLLD.url('/values', query) + '</a>');
}
