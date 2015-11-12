

$(document).ready(function(){
    // test if SSE available
    if(typeof(EventSource) === "undefined"){
        alert("Please use a different browser because this browser does not support SSE.")
    }
    // initialize resultSource via empty call to server
    var resultSource = new EventSource("/analyze");
    // initialize result data container
    var beaker = { words: [], rhymes: [], inlines: [] };

    $('#lyric-input').submit(function(event){
        event.preventDefault();
        // grab lyrics from input box
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

        // clear previous
        $('#graph').html("");
        resultSource.close();

        resultSource = new EventSource("/analyze?lyrics="+lyrics);
        // note resultSource.onmessage only fires for messages without event type
        resultSource.addEventListener('partial', function(e) {

            // TODO: load data into beaker
            beaker.words = [['rap', 'graph'], ['rap', 'graph']];
            beaker.rhymes = [[[0,0,2],[1,1,2]]];
            beaker.inlines = [[[0,1,2]],[[0,1,2]]];
            // call d3 visualizer; TODO: smarter update instead of redrawing everything
            runVisualization(beaker);
        });
        resultSource.addEventListener('__EOF__', function(e) {
            // finished receiving all data
            resultSource.close();
            $('#lyric-input-btn').removeClass('activespin');
        });
        resultSource.onerror = function(e) {
            $('#graph').append($("p").append("Data failed to finish loading"));
            $('#lyric-input-btn').removeClass('activespin');
        };
        resultSource.onopen = function(e) {
            $('#lyric-input-btn').addClass('activespin');
        };

    });

});



