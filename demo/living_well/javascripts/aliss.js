
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

function add_pagination_buttons(div_id, defaults, count, events, google_map, markers){

    var remove_markers = function(){
        if (markers) {
            $.each(markers, function(index, marker){
                marker.setMap(null);
            });
            markers.length = 0;
        }
    };

    if (defaults.start > 0){
        $(div_id).append(' <a href="#" class="pagination previous">&lt;- Previous</a>');
        if (events){
            $(div_id + " a.previous").click(function(){
                remove_markers();
                var previous_params = jQuery.extend({}, defaults);
                previous_params.start -= previous_params.max;
                if (previous_params.start < 0){
                    previous_params.start = 0;
                }
                aliss_search(previous_params, div_id, true, google_map);
            });
        }
    }

    if (count >= defaults.max){
        $(div_id).append(' <a href="#" class="pagination next">Next -&gt;</a>');
        if (events){
            $(div_id + " a.next").click(function(){
                remove_markers();
                var next_params = jQuery.extend({}, defaults);
                next_params.start += next_params.max;
                aliss_search(next_params, div_id, true, google_map);
            });
        }
    }

}



function aliss_search(data, div_id, paginate, google_map){

    var markers = [];

    $(div_id).html("<h3>Loading...</h3>");

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

                $(div_id).html("<h3>oops, we didn't find anything</h3>");

            } else {


                if (google_map){
                    var latlngbounds = new google.maps.LatLngBounds();
                    $.each(response.data[0].results, function(index, value){
                        if (value.locations[0]){
                            var ll = value.locations[0].split(', ');
                            var gll = new google.maps.LatLng(ll[0], ll[1]);
                            latlngbounds.extend(gll);
                        }
                    });

                    google_map.fitBounds(latlngbounds);

                }

                var items = [];

                $.each(response.data[0].results, function(index, value){

                    var url = value.uri;
                    if (!url){
                        url = 'http://aliss.org';
                    }
                    items.push('<li><a href="' + value.uri + '">' + value.title + '</a><p>' + value.description + '</p></li>');
                    if (value.locations[0]){
                        var latlng = value.locations[0].split(', ');
                        var glatlng = new google.maps.LatLng(latlng[0], latlng[1]);

                        if (google_map){
                            var marker = new google.maps.Marker({
                                map:google_map,
                                draggable:true,
                                animation: google.maps.Animation.DROP,
                                position: glatlng
                            });
                            markers.push(marker);
                            var infowindow = new google.maps.InfoWindow({
                                content: "<p>" + value.title + "</p>"
                            });
                            google.maps.event.addListener(marker, 'click', function() {
                              infowindow.open(google_map,marker);
                            });
                        }
                    }
                });

                $(div_id).html("");

                // Add pagination buttons to the top and bottom
                if (paginate){
                    add_pagination_buttons(div_id, defaults, count, false, google_map, markers);
                }

                $(div_id).append('\n<ul></ul>');

                $(div_id + ' ul').append(items.join(''));

            }

            if (paginate){
                add_pagination_buttons(div_id, defaults, count, true, google_map, markers);
            }

        }

    });

}
