

$(document).ready(function(){

    $('#lyric-input').submit(function(event){
        event.preventDefault();

        var lyrics = $('#lyrics-textarea').val();
        if (lyrics.length === 0) return;
        // EventSource makes a GET request, so we need to
        //  send the data through the url
        // So we need to limit length of url
        MAX_URL_LEN = 1900;
        if (lyrics.length > MAX_URL_LEN) {
            alert('The input is too long. Please use less input.');
            return;
        }
        var resultSource = new EventSource("/analyze/"+lyrics);
        resultSource.onmessage = function(e) {
            // TODO: call d3 visualization
            console.log(e);
            if (e.event === '__EOF__') {
                resultSource.close();
            }
            else {
                $('#graph').append($("p").html(e.data));
            }
        };
        resultSource.onerror = function(e) {
            $('#graph').append($("p").html("Data failed to finish loading"));
        };

    });

});



