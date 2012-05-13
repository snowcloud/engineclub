
function validate_location(location_name){

    $.ajax({
        data: {location: location_name, max: 1},
        dataType: 'jsonp',
        url: 'http://www.aliss.org/api/resources/search/',
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
        url: 'http://www.aliss.org/api/resources/search/',
        success: handler
    });
}


function aliss_search(div_id, google_map){

    var markers = [];

    $(div_id).html("<h3>Loading...</h3>");

    var defaults = {
        'start':0,
        'accounts': '4ece5493baa2b1744d000006'
    };

    if (!defaults.location || defaults.location === true){
        delete defaults.location;
    }

    $.ajax({

        data: defaults,
        dataType: 'jsonp',
        url: 'http://www.aliss.org/api/resources/search/',
        success: function(response){

            var count = response.data[0].results.length;

            if (count < 1){

                $(div_id).html("<h3>oops, we didn't find anything</h3>");

            } else {


                var latlngbounds = new google.maps.LatLngBounds();
                $.each(response.data[0].results, function(index, value){
                    if (value.locations[0]){
                        var ll = value.locations[0].split(', ');
                        var gll = new google.maps.LatLng(ll[0], ll[1]);
                        latlngbounds.extend(gll);
                    }
                });

                google_map.fitBounds(latlngbounds);


                var html = "";

                $.each(response.data[0].results, function(index, value){

                    var url = value.uri;
                    if (!url){
                        url = 'http://www.aliss.org';
                    }
                    html += '<li><a href="' + value.uri + '">' + value.title + '</a> - ' + value.locationnames[0];
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

                $(div_id).html("<ul>" + html + '</ul>');

            }

        }

    });

}
