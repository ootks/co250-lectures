/* Small LP/geometry core. No dependencies. Constraints are normalized to <=. */
(function(root){
'use strict';
const EPS=1e-9;
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const add=(a,b)=>a.map((v,i)=>v+b[i]);
const sub=(a,b)=>a.map((v,i)=>v-b[i]);
const mul=(a,k)=>a.map(v=>v*k);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const norm=a=>Math.hypot(...a);
function dual(p){
 const max=p.sense==='max';
 return {sense:max?'min':'max',A:p.A[0].map((_,j)=>p.A.map(row=>row[j])),b:p.c.slice(),c:p.b.slice(),
  rel:p.signs.map(s=>s==='free'?'=':s==='nonnegative'?(max?'>=':'<='):(max?'<=':'>=')),
  signs:p.rel.map(r=>r==='='?'free':r===(max?'<=':'>=')?'nonnegative':'nonpositive')};
}
function inequalities(p){
 const out=[];
 p.A.forEach((a,i)=>{
  if(p.rel[i]!=='>=')out.push({a:a.slice(),b:p.b[i],kind:'constraint'});
  if(p.rel[i]!=='<=')out.push({a:mul(a,-1),b:-p.b[i],kind:'constraint'});
 });
 p.signs.forEach((s,i)=>{if(s!=='free'){const a=[0,0,0];a[i]=s==='nonnegative'?-1:1;out.push({a,b:0,kind:'sign'});}});
 return out;
}
class Simplex{
 constructor(A,b,c){
  this.m=b.length;this.n=c.length;this.B=[];this.N=[];this.iter=0;
  const m=this.m,n=this.n;
  this.D=Array.from({length:m+2},()=>Array(n+2).fill(0));
  for(let i=0;i<m;i++){for(let j=0;j<n;j++)this.D[i][j]=A[i][j];this.B[i]=n+i;this.D[i][n]=-1;this.D[i][n+1]=b[i];}
  for(let j=0;j<n;j++){this.N[j]=j;this.D[m][j]=-c[j];}
  this.N[n]=-1;this.D[m+1][n]=1;
 }
 pivot(r,s){
  const {D,m,n}=this,inv=1/D[r][s];
  for(let i=0;i<m+2;i++)if(i!==r)for(let j=0;j<n+2;j++)if(j!==s)D[i][j]-=D[r][j]*D[i][s]*inv;
  for(let j=0;j<n+2;j++)if(j!==s)D[r][j]*=inv;
  for(let i=0;i<m+2;i++)if(i!==r)D[i][s]*=-inv;
  D[r][s]=inv;[this.B[r],this.N[s]]=[this.N[s],this.B[r]];
 }
 phase(which){
  const {D,m,n}=this,row=which===1?m+1:m;
  while(++this.iter<20000){
   // Bland's rule: smallest indexed improving nonbasic variable.
   let s=-1;
   for(let j=0;j<=n;j++)if(!(which===2&&this.N[j]===-1)&&D[row][j]<-EPS&&(s===-1||this.N[j]<this.N[s]))s=j;
   if(s===-1)return 'optimal';
   let r=-1;
   for(let i=0;i<m;i++)if(D[i][s]>EPS){
    const ratio=D[i][n+1]/D[i][s],old=r<0?Infinity:D[r][n+1]/D[r][s];
    if(r===-1||ratio<old-EPS||(Math.abs(ratio-old)<=EPS&&this.B[i]<this.B[r]))r=i;
   }
   if(r===-1){this.enter=s;return 'unbounded';}
   this.pivot(r,s);
  }
  return 'numerical';
 }
 solve(){
  const {D,m,n}=this;
  let r=-1;for(let i=0;i<m;i++)if(r<0||D[i][n+1]<D[r][n+1])r=i;
  if(r>=0&&D[r][n+1]<-EPS){
   this.pivot(r,n);const status=this.phase(1);
   if(status==='numerical')return {status};
   if(status!=='optimal'||D[m+1][n+1]<-EPS)return {status:'infeasible'};
   if(Math.abs(D[m+1][n+1])>1e-7)return {status:'numerical'};
   for(let i=0;i<m;i++)if(this.B[i]===-1){
    let s=-1;for(let j=0;j<=n;j++)if(this.N[j]!==-1&&Math.abs(D[i][j])>EPS&&(s<0||this.N[j]<this.N[s]))s=j;
    if(s>=0)this.pivot(i,s);
   }
  }
  const status=this.phase(2),x=Array(n).fill(0);
  for(let i=0;i<m;i++)if(this.B[i]>=0&&this.B[i]<n)x[this.B[i]]=D[i][n+1];
  const result={status,x};
  if(status==='unbounded'){
   const d=Array(n).fill(0),s=this.enter;if(this.N[s]>=0&&this.N[s]<n)d[this.N[s]]=1;
   for(let i=0;i<m;i++)if(this.B[i]>=0&&this.B[i]<n)d[this.B[i]]=-D[i][s];
   result.ray=d;
  }
  return result;
 }
}
function solve(p){
 const cols=[];
 p.signs.forEach((s,i)=>{cols.push({i,k:s==='nonpositive'?-1:1});if(s==='free')cols.push({i,k:-1});});
 const A=[],b=[];
 for(const row of inequalities({...p,signs:['free','free','free']})){
  const a=cols.map(({i,k})=>row.a[i]*k),scale=Math.max(...a.map(Math.abs));
  if(scale===0){if(row.b<0)return {status:'infeasible'};continue;}
  A.push(a.map(v=>v/scale));b.push(row.b/scale);
 }
 const objective=cols.map(({i,k})=>p.c[i]*k*(p.sense==='max'?1:-1));
 const os=Math.max(1,...objective.map(Math.abs));
 const raw=new Simplex(A,b,objective.map(v=>v/os)).solve();
 if(!raw.x)return raw;
 function map(values){const z=[0,0,0];cols.forEach(({i,k},j)=>z[i]+=k*values[j]);return z.map(v=>Math.abs(v)<1e-10?0:v);}
 const x=map(raw.x),result={status:raw.status,x,value:dot(p.c,x)};
 if(raw.ray)result.ray=map(raw.ray);
 // Never display a numerically inconsistent point as an optimum.
 if(!feasible(p,x,2e-6))return {status:'numerical'};
 if(result.ray){
  const d=result.ray;
  if(inequalities(p).some(r=>dot(r.a,d)>1e-6*Math.max(1,norm(r.a)*norm(d)))||dot(p.c,d)*(p.sense==='max'?1:-1)<=1e-8)return {status:'numerical'};
 }
 return result;
}
function feasible(p,x,tol=1e-7){return x.every(Number.isFinite)&&inequalities(p).every(r=>dot(r.a,x)<=r.b+tol*Math.max(1,Math.abs(r.b),norm(r.a)*norm(x)));}
function tightConstraints(p,result,tol=1e-7){
 const empty={rows:p.b.map(()=>false),signs:p.signs.map(()=>false)};
 if(!result||result.status!=='optimal'||!result.x)return empty;
 const x=result.x;
 return {
  rows:p.A.map((a,i)=>Math.abs(dot(a,x)-p.b[i])<=tol*Math.max(1,Math.abs(p.b[i]),norm(a)*norm(x))),
  signs:p.signs.map((sign,i)=>sign!=='free'&&Math.abs(x[i])<=tol)
 };
}
function unique(points,tol){const out=[];for(const p of points)if(!out.some(q=>norm(sub(p,q))<tol))out.push(p);return out;}
function order(points,n){
 if(points.length<3)return points;
 const center=mul(points.reduce(add,[0,0,0]),1/points.length),nn=mul(n,1/norm(n));
 const base=Math.abs(nn[0])<.8?[1,0,0]:[0,1,0],u=cross(nn,base),v=cross(nn,u);
 return points.slice().sort((a,b)=>Math.atan2(dot(sub(a,center),v),dot(sub(a,center),u))-Math.atan2(dot(sub(b,center),v),dot(sub(b,center),u)));
}
function mesh(p,R){
 let faces=[];
 for(let axis=0;axis<3;axis++)for(const side of [-1,1]){
  const other=[0,1,2].filter(i=>i!==axis),points=[];
  for(const [a,b] of [[-1,-1],[1,-1],[1,1],[-1,1]]){const q=[0,0,0];q[axis]=side*R;q[other[0]]=a*R;q[other[1]]=b*R;points.push(q);}
  faces.push({points,box:true});
 }
 const tol=1e-8*Math.max(1,R);
 for(const row of inequalities(p)){
  const length=norm(row.a);if(length===0){if(row.b<0)return [];continue;}
  const n=mul(row.a,1/length),rhs=row.b/length,cap=[],next=[];
  for(const face of faces){
   const points=face.points,clipped=[];
   for(let i=0;i<points.length;i++){
    const a=points[i],b=points[(i+1)%points.length],da=dot(n,a)-rhs,db=dot(n,b)-rhs;
    if(da<=tol)clipped.push(a);
    if((da>tol&&db<=tol)||(db>tol&&da<=tol)){
     const t=da/(da-db),q=add(a,mul(sub(b,a),t));clipped.push(q);cap.push(q);
    }
    if(Math.abs(da)<=tol)cap.push(a);
   }
   const clean=unique(clipped,tol);if(clean.length)next.push({points:clean,box:face.box});
  }
  const clean=unique(cap,tol);if(clean.length)next.push({points:order(clean,n),box:false});
  faces=next;if(!faces.length)break;
 }
 return faces;
}
function plane(c,value,R){
 if(norm(c)<1e-12)return [];
 const points=[],tol=1e-8*Math.max(1,R);
 for(let axis=0;axis<3;axis++)for(const a of [-R,R])for(const b of [-R,R]){
  const others=[0,1,2].filter(i=>i!==axis),q=[0,0,0];q[others[0]]=a;q[others[1]]=b;
  if(Math.abs(c[axis])<1e-12)continue;
  q[axis]=(value-dot(c,q))/c[axis];if(Math.abs(q[axis])<=R+tol)points.push(q);
 }
 return order(unique(points,tol),c);
}
const api={dual,inequalities,solve,feasible,tightConstraints,mesh,plane,dot,norm,add,sub,mul,cross};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.LP3=api;
})(typeof globalThis!=='undefined'?globalThis:this);
