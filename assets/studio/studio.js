// Elitron Studio page: before/after slider and style-set grid. No inline JS (site CSP is script-src self).
// before/after slider
(function(){
  var ba=document.getElementById('ba'); if(!ba) return; var r=ba.querySelector('input');
  function set(v){ba.style.setProperty('--pos',v+'%')}
  set(r.value); r.addEventListener('input',function(){set(r.value)});
})();
// style set grid
(function(){
  var rooms=[
    ['t01-paris','Paris garden terrace',1],['t02-hill-country','Texas Hill Country room',1],
    ['t03-venice','Venetian loggia',1],['t04-santa-barbara','Santa Barbara terrace',1],
    ['t05-charleston','Charleston brick loggia',1],['t06-vienna','Viennese pavilion',1],
    ['t07-steel-glass','Steel & glass pavilion',1],['t08-plain-modern','Plain modern patio',0],
    ['t09-tuscan','Tuscan portico',1],['t10-michigan-lake','Michigan lake porch',1]];
  var g=document.getElementById('set');
  rooms.forEach(function(x,i){
    var d=document.createElement('div'); d.className='room'+(x[2]?'':' no');
    var n=String(i+1).padStart(2,'0');
    d.innerHTML='<img loading="lazy" src="assets/studio/'+x[0]+'.jpg" alt="'+x[1]+' (AI concept render)">'+
      '<span class="n">'+n+'/10<br>'+x[1].toUpperCase()+'</span><span class="m">'+(x[2]?'&#10003;':'&#10005;')+'</span>';
    g.appendChild(d);
  });
})();
