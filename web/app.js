const formatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0
})

function collapseSection(element) {
  // get the height of the element's inner content, regardless of its actual size
  var sectionHeight = element.scrollHeight;
  
  // temporarily disable all css transitions
  var elementTransition = element.style.transition;
  element.style.transition = '';
  
  // on the next frame (as soon as the previous style change has taken effect),
  // explicitly set the element's height to its current pixel height, so we 
  // aren't transitioning out of 'auto'
  requestAnimationFrame(function() {
    element.style.height = sectionHeight + 'px';
    element.style.transition = elementTransition;
    
    // on the next frame (as soon as the previous style change has taken effect),
    // have the element transition to height: 0
    requestAnimationFrame(function() {
      element.style.height = 0 + 'px';
    });
  });
  
  // mark the section as "currently collapsed"
  element.setAttribute('data-collapsed', 'true');
}

function expandSection(element) {
  // get the height of the element's inner content, regardless of its actual size
  var sectionHeight = element.scrollHeight;
  
  // have the element transition to the height of its inner content
  element.style.height = sectionHeight + 'px';

  // when the next css transition finishes (which should be the one we just triggered)
  element.addEventListener('transitionend', function(e) {
    // remove this event listener so it only gets triggered once
    element.removeEventListener('transitionend', arguments.callee);
    
    // remove "height" from the element's inline styles, so it can return to its initial value
    element.style.height = null;
  });
  
  // mark the section as "currently not collapsed"
  element.setAttribute('data-collapsed', 'false');
}

function setMap(lat, long) {
   var map = L.map('map').setView([lat, long], 13);
   L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }).addTo(map);
   var marker = L.marker([lat, long]).addTo(map);
}

function postPredict() {
  fm = document.getElementById('entry');
  collapseSection(fm);
}

const userAction = async() => {
    const response = await fetch('http://137.184.141.234:8181/predict', {
        method: 'POST',
        body: JSON.stringify({
            'zipcode': document.getElementById('zipcode').value,
            'beds': document.getElementById('beds').value,
            'baths': document.getElementById('baths').value,
            'sqft': document.getElementById('sqft').value,
            'lsize': document.getElementById('lotsize').value,
            'ybuilt': document.getElementById('ybuilt').value
        }), // string or object
        headers: {
            'Content-Type': 'application/json'
        }
    });
    jQuery('#map').animate({height: '350px'}, 500);
    await new Promise(resolve => setTimeout(resolve, 300));
    const myJson = await response.json(); //extract JSON from the http response
    setMap(myJson.lat, myJson.long);
    chartJSON = myJson.charts[0]
    chartJSON2 = myJson.charts[1]
    var data = JSON.parse(chartJSON);
    var data2 = JSON.parse(chartJSON2);
    var ctx = document.getElementById('myChart').getContext('2d');
    var ctx2 = document.getElementById('myChart2').getContext('2d');
    document.getElementById('charts').style.visibility = 'visible';
    document.getElementById('charts').style.height = 'auto';
    var myChart = new Chart(ctx, data);
    var myChart2 = new Chart(ctx2, data2);
    postPredict();
    document.getElementById('yourprop').style.visibility = 'visible';
    document.getElementById('yourprop').style.height = 'auto';
    document.getElementById('mapheader').style.visibility = 'visible';
    document.getElementById('mapheader').style.height = 'auto';
    document.getElementById('againbtn').style.visibility = 'visible';
    document.getElementById('againbtn').style.height = 'auto';
    document.getElementById('pred').innerHTML = formatter.format(Math.round(myJson.price));
    document.getElementById('predh').style.visibility = 'visible';
    document.getElementById('predh').style.height = 'auto';

    // do something with myJson
}