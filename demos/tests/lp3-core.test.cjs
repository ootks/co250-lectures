const assert=require('node:assert/strict');
const lp=require(require('node:path').join(__dirname,'../lib/lp3-core.js'));
let seed=48317;const rand=n=>{seed=(Math.imul(seed,1664525)+1013904223)|0;return (seed>>>0)%n;};
function check(p){
 const d=lp.dual(p),r=lp.solve(p),s=lp.solve(d);
 assert.deepEqual(lp.dual(d),p);
 if(r.status==='optimal')assert(lp.feasible(p,r.x));
 if(s.status==='optimal')assert(lp.feasible(d,s.x));
 if(r.status==='optimal'||s.status==='optimal'){
  assert.equal(r.status,'optimal',JSON.stringify(p));assert.equal(s.status,'optimal',JSON.stringify(p));
  assert(Math.abs(r.value-s.value)<1e-5*Math.max(1,Math.abs(r.value),Math.abs(s.value)),JSON.stringify({p,r,s}));
 }
 if(r.status==='unbounded')assert.equal(s.status,'infeasible');
 if(s.status==='unbounded')assert.equal(r.status,'infeasible');
 if(r.status==='infeasible')assert(['infeasible','unbounded'].includes(s.status));
 if(s.status==='infeasible')assert(['infeasible','unbounded'].includes(r.status));
 assert.notEqual(r.status,'numerical');assert.notEqual(s.status,'numerical');
 // Every displayed polygon vertex must satisfy the actual constraints.
 const faces=lp.mesh(p,8);
 if(r.status==='infeasible')assert.equal(faces.length,0);
 for(const face of faces)for(const v of face.points)assert(lp.feasible(p,v,1e-6),JSON.stringify({p,v}));
 return {p,r,s};
}
for(let k=0;k<2000;k++){
 check({sense:rand(2)?'max':'min',A:Array.from({length:3},()=>Array.from({length:3},()=>rand(7)-3)),b:Array.from({length:3},()=>rand(11)-5),c:Array.from({length:3},()=>rand(7)-3),rel:Array.from({length:3},()=>['<=','=','>='][rand(3)]),signs:Array.from({length:3},()=>['nonnegative','free','nonpositive'][rand(3)])});
}
// Independent vertex enumeration for bounded nonnegative problems.
function intersection(rows,b){
 const D=rows.map((r,i)=>[...r,b[i]]);
 for(let j=0;j<3;j++){let k=j;while(k<3&&Math.abs(D[k][j])<1e-8)k++;if(k===3)return null;[D[j],D[k]]=[D[k],D[j]];let a=D[j][j];D[j]=D[j].map(v=>v/a);for(let i=0;i<3;i++)if(i!==j){a=D[i][j];D[i]=D[i].map((v,k)=>v-a*D[j][k]);}}
 return D.map(r=>r[3]);
}
for(let k=0;k<300;k++){
 const p={sense:rand(2)?'min':'max',A:Array.from({length:3},()=>Array.from({length:3},()=>1+rand(5))),b:Array.from({length:3},()=>1+rand(20)),c:Array.from({length:3},()=>rand(11)-5),rel:['<=','<=','<='],signs:['nonnegative','nonnegative','nonnegative']};
 const rows=lp.inequalities(p),values=[];
 for(let i=0;i<rows.length;i++)for(let j=i+1;j<rows.length;j++)for(let k=j+1;k<rows.length;k++){
  const x=intersection([rows[i].a,rows[j].a,rows[k].a],[rows[i].b,rows[j].b,rows[k].b]);if(x&&lp.feasible(p,x))values.push(lp.dot(p.c,x));
 }
 const expected=(p.sense==='max'?Math.max:Math.min)(...values),r=lp.solve(p);
 assert.equal(r.status,'optimal');assert(Math.abs(r.value-expected)<1e-7);
}
// Lower-dimensional line and point, negative variable and no-vertex affine set.
for(const b of [[0,0,0],[1,2,3]]){
 const p={sense:'min',A:[[1,0,0],[0,1,0],[0,0,1]],b,c:[2,-1,3],rel:['=','=','='],signs:['free','free','free']};check(p);
}
console.log('Passed: 2,000 mixed random pairs, dual-of-dual, feasible meshes, 300 independent vertex optima, and equality/point cases.');

// Highlight only constraints tight at an actual optimum, including sign bounds.
{
 const p={sense:'max',A:[[1,1,1],[2,1,0],[0,1,2]],b:[6,8,6],c:[3,2,4],rel:['<=','<=','<='],signs:['nonnegative','nonnegative','nonnegative']};
 for(const model of [p,lp.dual(p)])assert.deepEqual(lp.tightConstraints(model,lp.solve(model)),{rows:[true,false,true],signs:[false,true,false]});
 assert.deepEqual(lp.tightConstraints(p,{status:'infeasible'}),{rows:[false,false,false],signs:[false,false,false]});
}
