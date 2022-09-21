
var mymap = L.map('mapid').fitWorld().zoomIn();

mymap.on('resize', function(e) {
  mymap.fitWorld({reset: true}).zoomIn();
});

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
	maxZoom: 15,
	id: 'mapbox/dark-v10',
	accessToken: 'pk.eyJ1Ijoic3BlcmFsYSIsImEiOiJjbDJwdGhybmIyb3E2M2tzYnBnNXIxaXEyIn0.aDT5UfoeU7kuP-5Xae-viQ'
}).addTo(mymap);



var source = new EventSource('/topic/twitter_sentiment_stream');
source.onmessage = function(event) {
  obj = String(event.data);
  var strnew = obj.replace(/[{()}]/g, '').replace(/[\[\]']+/g,'');
  var elems = strnew.split(',');
  var lat = elems[0];
  var long = elems[1];
  var pol = elems[2];
  var sent = elems[3].trim();
  console.log(lat + ' ' + long + ' ' + pol+ ' ' + sent);
  if (sent.valueOf() == "very positive") {
    var circle = L.circle([lat, long], {
      color: '#50cc1b',
      fillColor: '#8bde68',
      fillOpacity: 0.5,
      radius: 200,
      title: "very positive"
    }).addTo(mymap);
    circle.bindPopup("Very Postive, " + pol);
  } else if (sent.valueOf() == "positive") {
    var circle = L.circle([lat, long], {
      color: '#68dea3',
      fillColor: '#c7fce2',
      fillOpacity: 0.5,
      radius: 200,
      title: "positive"
    }).addTo(mymap);
    circle.bindPopup("Postive, " + pol);
  } else if (sent.valueOf() == "neutral") {
    var circle = L.circle([lat, long], {
      color: '#ede742',
      fillColor: '#fcfab3',
      fillOpacity: 0.5,
      radius: 200,
      title: "neutral"
    }).addTo(mymap);
    circle.bindPopup("Neutral, " + pol);
  } else if (sent.valueOf() == "negative") {
    var circle = L.circle([lat, long], {
      color: '#3810eb',
      fillColor: '#8b73f5',
      fillOpacity: 0.5,
      radius: 200,
      title: "negative"
    }).addTo(mymap);
    circle.bindPopup("Negative, " + pol);
  } else if (sent.valueOf() == "very negative") {
    var circle = L.circle([lat, long], {
      color: '#f01111',
      fillColor: '#f54040',
      fillOpacity: 0.5,
      radius: 200,
      title: "very negative"
    }).addTo(mymap);
    circle.bindPopup("Very Negative, " + pol);
  } else {
    console.log('Not Plotted')
  }

};

