
function aliss_search(data, div_id, paginate){

    $(div_id).html("<h3>Loading...</h3>");

    var defaults = {
        'max':3,
        'start':0,
        'boostlocation': 10,
        'accounts': '4e1d7e9689cb164b5a000000'
    };

    $.extend(defaults, data);

    if (!defaults.location || defaults.location === true){
        delete defaults.location;
    }

    $.ajax({
        data: defaults,
        dataType: 'jsonp',
        url: 'http://aliss.org/api/resources/search/',
        success: function(response){

            var count = response.data[0].results.length;
            if (count < 1){

                $(div_id).html("<h3>No results found</h3>");
                return;
            }

            var items = [];

            $.each(response.data[0].results, function(index, value){
               items.push('<li><a href="' + value.uri + '">' + value.title + '</a><p>' + value.description + '</p></li>');
            });

            $(div_id).html("<h3>Support for " + response.data[0].query + " near to " +'' + "</h3>\n<ul></ul>");

            $(div_id + ' ul').append(items.join(''));

            if (paginate){

                if (defaults.start > 0){
                    $(div_id).append('<a hred="#" class="previous">Previous</a>');
                    $(div_id + " a.previous").click(function(){
                        var previous_params = jQuery.extend({}, defaults);
                        previous_params.start -= previous_params.max;
                        if (previous_params.start < 0){
                            previous_params.start = 0;
                        }
                        aliss_search(previous_params, div_id, paginate);
                    });
                }

                if (count >= defaults.max){
                    $(div_id).append('<a hred="#" class="next">Next</a>');
                    $(div_id + " a.next").click(function(){
                        var next_params = jQuery.extend({}, defaults);
                        next_params.start += next_params.max;
                        aliss_search(next_params, div_id, paginate);
                    });
                }


            }

        }

    });

}