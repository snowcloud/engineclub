
function validate_location(location_name){

    $.ajax({
        data: {location: location_name, max: 1},
        dataType: 'jsonp',
        url: 'http://aliss.org/api/resources/search/',
        success: function(response){

            if(!response.errors.length && response.data.length > 0){
                $('.error.location').hide();
                $('#livingwellform').attr('v', true);
                $('#livingwellform').submit();
                return;
            } else {
                $('#livingwellform').attr('v', '');
            }

            $('.error.location').show();

        }
    });

}

function aliss_query(defaults, handler){
    $.ajax({
        data: defaults,
        dataType: 'jsonp',
        url: 'http://aliss.org/api/resources/search/',
        success: handler
    });
}

function add_pagination_buttons(div_id, defaults, count, events){

    if (defaults.start > 0){
        $(div_id).append(' <a href="#" class="pagination previous">&lt;- Previous</a>');
        if (events){
            $(div_id + " a.previous").click(function(){
                var previous_params = jQuery.extend({}, defaults);
                previous_params.start -= previous_params.max;
                if (previous_params.start < 0){
                    previous_params.start = 0;
                }
                aliss_search(previous_params, div_id, true);
            });
        }
    }

    if (count >= defaults.max){
        $(div_id).append(' <a href="#" class="pagination next">Next -&gt;</a>');
        if (events){
            $(div_id + " a.next").click(function(){
                var next_params = jQuery.extend({}, defaults);
                next_params.start += next_params.max;
                aliss_search(next_params, div_id, true);
            });
        }
    }

}

function aliss_search(data, div_id, paginate){

    $(div_id).html("<h3>Loading...</h3>");

    $('#map_canvas').css({height: '20em'});

    var google_map = new google.maps.Map(document.getElementById("map_canvas"), {
      zoom: 8,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      center: new google.maps.LatLng(55.83333, -3.43333)
    });


    var defaults = {
        'max':4,
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

            } else {



                if (response.data[0].location[0]){
                    var latlng = response.data[0].location[0].split(', ');
                    google_map.setCenter(new google.maps.LatLng(latlng[0], latlng[1]));
                }

                var items = [];
                var markers = [];

                $.each(response.data[0].results, function(index, value){
                    items.push('<li><a href="' + value.uri + '">' + value.title + '</a><p>' + value.description + '</p></li>');
                    if (value.locations[0]){
                        var latlng = value.locations[0].split(', ');
                        var glatlng = new google.maps.LatLng(latlng[0], latlng[1]);
                        markers.push(new google.maps.Marker({
                            map:google_map,
                            draggable:true,
                            animation: google.maps.Animation.DROP,
                            position: glatlng
                        }));
                    }
                });

                $(div_id).html("");

                // Add pagination buttons to the top and bottom
                if (paginate){
                    add_pagination_buttons(div_id, defaults, count);
                }

                $(div_id).append('\n<ul></ul>');

                $(div_id + ' ul').append(items.join(''));

            }

            if (paginate){
                add_pagination_buttons(div_id, defaults, count, true);
            }

        }

    });

}