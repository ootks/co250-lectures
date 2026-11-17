const assert=require('node:assert/strict');
const path=require('node:path');
const lp=require(path.join(__dirname,'../lib/lp3-core.js'));
const sef=require(path.join(__dirname,'../lib/sef2-core.js'));
let seed=9127;const rand=n=>{seed=(Math.imul(seed,1664525)+1013904223)|0;return (seed>>>0)%n;};
const rnd=(lo,hi)=>lo+rand(hi-lo+1);
const tally={};
// Independent check: for SEF the optimum (if any) is at a basic feasible solution.
function bfsValues(p){
 const out=[];
 for(let i=0;i<3;i++)for(let j=i+1;j<3;j++){
  const [a,b]=[sef.column(p,i),sef.column(p,j)],det=a[0]*b[1]-a[1]*b[0];
  if(Math.abs(det)<1e-9)continue;
  const xi=(p.b[0]*b[1]-p.b[1]*b[0])/det,xj=(a[0]*p.b[1]-a[1]*p.b[0])/det;
  if(xi<-1e-9||xj<-1e-9)continue;
  const x=[0,0,0];x[i]=xi;x[j]=xj;out.push(lp.dot(p.c,x));
 }
 // single-column bases for rank-deficient A (including the zero point when b = 0)
 for(let i=0;i<3;i++){
  const a=sef.column(p,i);
  for(const k of [0,1]){if(Math.abs(a[k])>1e-9){const t=p.b[k]/a[k];if(t>=-1e-9&&Math.abs(a[1-k]*t-p.b[1-k])<1e-9){const x=[0,0,0];x[i]=t;out.push(lp.dot(p.c,x));}}}
 }
 if(p.b.every(v=>v===0))out.push(0);
 return out;
}
for(let k=0;k<4000;k++){
 const p={A:[0,1].map(()=>[0,1,2].map(()=>rnd(-3,3))),b:[rnd(-5,5),rnd(-5,5)],c:[0,1,2].map(()=>rnd(-4,4))};
 const r=sef.solvePrimal(p),s=sef.solveDual(p),key=r.status+'/'+s.status;tally[key]=(tally[key]||0)+1;
 assert.notEqual(r.status,'numerical',JSON.stringify(p));assert.notEqual(s.status,'numerical',JSON.stringify(p));
 // dual of the dual is the primal data (transpose structure)
 const d=sef.dualLP(p);assert.deepEqual(d.b,p.c);assert.deepEqual(d.c,p.b);
 if(r.status==='optimal'){
  assert(r.x.every(v=>v>=-1e-7),'primal x>=0');
  [0,1].forEach(i=>assert(Math.abs(lp.dot(p.A[i],r.x)-p.b[i])<1e-6));
  const vals=bfsValues(p);assert(vals.length>0,JSON.stringify(p));
  assert(Math.abs(Math.max(...vals)-r.value)<1e-6,JSON.stringify({p,r,vals}));
 }
 if(s.status==='optimal')sef.dualSlacks(p,s.x).forEach(v=>assert(v>=-1e-6,'dual feasible'));
 if(r.status==='optimal'||s.status==='optimal'){
  assert.equal(r.status,'optimal',JSON.stringify(p));assert.equal(s.status,'optimal',JSON.stringify(p));
  assert(Math.abs(r.value-s.value)<1e-6*Math.max(1,Math.abs(r.value)),'strong duality '+JSON.stringify({p,r,s}));
  // complementary slackness x_j * s_j = 0
  const sl=sef.dualSlacks(p,s.x);sl.forEach((v,j)=>assert(Math.abs(v*r.x[j])<1e-5,'CS '+JSON.stringify({p,r,s})));
 }
 if(r.status==='unbounded')assert.equal(s.status,'infeasible',JSON.stringify(p));
 if(s.status==='unbounded')assert.equal(r.status,'infeasible',JSON.stringify(p));
 if(r.status==='infeasible')assert(['infeasible','unbounded'].includes(s.status));
 if(s.status==='infeasible')assert(['infeasible','unbounded'].includes(r.status));
}
console.log('sef2-core tests passed',tally);
