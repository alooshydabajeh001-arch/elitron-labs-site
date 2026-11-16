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
    ['t01-paris','Limestone & olive'],['t02-hill-country','Cedar beam hearth'],
    ['t03-venice','Canal loggia'],['t04-santa-barbara','Plaster & bougainvillea'],
    ['t05-charleston','Brick vault gallery'],['t06-vienna','Coffered garden pavilion'],
    ['t07-steel-glass','Steel, glass & fire'],['t11-orangery','Iron orangery'],
    ['t09-tuscan','Vineyard hearth'],['t10-michigan-lake','Great Lakes porch']];
  var g=document.getElementById('set');
  rooms.forEach(function(x,i){
    var d=document.createElement('div'); d.className='room';
    var n=String(i+1).padStart(2,'0');
    d.innerHTML='<img loading="lazy" src="assets/studio/'+x[0]+'.jpg" alt="'+x[1]+' (AI concept render)">'+
      '<span class="m">'+n+'</span><span class="n">'+x[1].toUpperCase()+'</span>';
    g.appendChild(d);
  });
})();
