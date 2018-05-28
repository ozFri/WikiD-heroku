//Toggle wonderbar visibility

require(['static/scripts/libs/Bacon'], function(Bacon) {

    var input = Bacon.fromEvent(document.getElementById("wonderbar-input"),'keyup').map(function(event) {return event.target.value}).toProperty("")
    var availabilityRequest = input.changes().map(function(input) { return { url: "/search/" + input }})
    

    //var availabilityRequest = input.changes().map(function(input) { 
        //var request = new XMLHttpRequest()
        //request.open('GET', "/search/" + input, true)
        //request.onload = function() {
          //if (this.status >= 200 && this.status < 400) {
            //// Success!
            //var resp = this.response
          //} else {
            //// We reached our target server, but it returned an error
          //}
        //}
        //request.onerror = function() {
          //// There was a connection error of some sort
        //}
        //return request
    //}).log()

    Bacon.EventStream.prototype.ajax = function() {
      return this["flatMapLatest"](function(params) { return Bacon.fromPromise($.ajax(params)) })
    }

    var availabilityResponse = availabilityRequest.ajax()
    console.log(availabilityResponse)
    var searchResults = availabilityResponse

    searchResults.onValue(function(val){document.getElementById("suggestions").innerHTML= val})
    




})

