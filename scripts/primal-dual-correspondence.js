/* Position the correspondence arrows against the actual MathJax color groups. */
(() => {
  const host=document.getElementById('primal-dual-correspondence');
  if(!host)return;
  const svg=host.querySelector('svg');
  const links=[
    ['#1f6fd6','rgb(31, 111, 214)'],
    ['#cb4b16','rgb(203, 75, 22)'],
    ['#708400','rgb(112, 132, 0)'],
    ['#8b4bad','rgb(139, 75, 173)']
  ];
  let pending=false;
  function colorGroup(column,color){
    return [...column.querySelectorAll('.MathJax [style]')]
      .filter(el=>el.style.color&&getComputedStyle(el).color===color)
      .map(el=>el.getBoundingClientRect())
      .filter(r=>r.width>0&&r.height>0)
      .sort((a,b)=>b.width*b.height-a.width*a.height)[0];
  }
  function draw(){
    pending=false;
    const rect=host.getBoundingClientRect(),width=host.clientWidth,height=host.clientHeight;
    if(!width||!height||!rect.width||!rect.height)return;
    svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
    const sx=width/rect.width,sy=height/rect.height;
    links.forEach(([,color],i)=>{
      const left=colorGroup(host.querySelector('.correspondence-primal'),color);
      const right=colorGroup(host.querySelector('.correspondence-dual'),color);
      const path=host.querySelector(`[data-correspondence="${i}"]`);
      if(!left||!right){path.setAttribute('d','');return;}
      const x1=(left.right-rect.left)*sx+9,y1=(left.top+left.height/2-rect.top)*sy;
      const x2=(right.left-rect.left)*sx-9,y2=(right.top+right.height/2-rect.top)*sy;
      const reach=Math.max(24,(x2-x1)*.42);
      // Keep the green connector below the dual's s.t. label until it
      // approaches the colored constraint on the right.
      const control1=i===2?x2-25:x1+reach,control2=i===2?x2-25:x2-reach;
      path.setAttribute('d',`M ${x1} ${y1} C ${control1} ${y1}, ${control2} ${y2}, ${x2} ${y2}`);
    });
  }
  function schedule(){if(!pending){pending=true;requestAnimationFrame(draw);}}
  new ResizeObserver(schedule).observe(host);
  // Observe newly typeset MathJax, but not the SVG attribute updates themselves.
  new MutationObserver(schedule).observe(host,{subtree:true,childList:true,characterData:true});
  window.addEventListener('resize',schedule);
  window.addEventListener('load',schedule);
  if(document.fonts)document.fonts.ready.then(schedule);
  if(window.Reveal){Reveal.on('ready',schedule);Reveal.on('slidechanged',schedule);Reveal.on('resize',schedule);Reveal.on('pdf-ready',schedule);}
  schedule();
})();
