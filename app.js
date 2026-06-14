// mobile menu
function toggleMenu(){document.getElementById('mobileNav').classList.toggle('open');}
// scroll reveal
const io=new IntersectionObserver((e)=>{e.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});},{threshold:.12});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
