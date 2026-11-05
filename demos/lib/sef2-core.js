/* SEF primal/dual core for LPs with 2 equality constraints and 3 variables.
   Primal: max c.x  s.t. Ax = b, x >= 0       (A is 2x3)
   Dual:   min b.y  s.t. A^T y >= c, y free   (y in R^2)
   Reuses the general solver in lp3-core.js. */
(function(root){
'use strict';
const LP3=typeof module!=='undefined'&&module.exports?require('./lp3-core.js'):root.LP3;
const dot=LP3.dot;
const primalLP=p=>({sense:'max',A:p.A,b:p.b,c:p.c,rel:['=','='],signs:['nonnegative','nonnegative','nonnegative']});
const column=(p,j)=>[p.A[0][j],p.A[1][j]];
const dualLP=p=>({sense:'min',A:[0,1,2].map(j=>column(p,j)),b:p.c.slice(),c:p.b.slice(),rel:['>=','>=','>='],signs:['free','free']});
function solvePrimal(p){return LP3.solve(primalLP(p));}
function solveDual(p){
 // Embed the 2-variable dual in the 3-variable solver with the extra equation y3 = 0.
 const d=dualLP(p);
 const r=LP3.solve({sense:'min',A:[...d.A.map(row=>[row[0],row[1],0]),[0,0,1]],b:[...d.b,0],c:[...d.c,0],rel:['>=','>=','>=','='],signs:['free','free','free']});
 if(!r.x)return r;
 const out={status:r.status,x:r.x.slice(0,2),value:r.value};
 if(r.ray)out.ray=r.ray.slice(0,2);
 return out;
}
// Dual slack s_j = a_j . y - c_j (>= 0 when y is dual feasible).
const dualSlacks=(p,y)=>[0,1,2].map(j=>dot(column(p,j),y)-p.c[j]);
const api={primalLP,dualLP,solvePrimal,solveDual,dualSlacks,column};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.SEF2=api;
})(typeof globalThis!=='undefined'?globalThis:this);
