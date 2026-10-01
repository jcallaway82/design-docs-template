// Deterministic helpers for the mockups (no real data — everything here is illustrative).
function rng(seed){let s=seed>>>0;return()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296}}
function gauss(r){return Math.sqrt(-2*Math.log(r()+1e-9))*Math.cos(2*Math.PI*r())}
function viridis(t){t=Math.max(0,Math.min(1,t));const st=[[68,1,84],[59,82,139],[33,145,140],[94,201,98],[253,231,37]];const x=t*4,i=Math.min(3,Math.floor(x)),f=x-i;return st[i].map((c,k)=>Math.round(c+(st[i+1][k]-c)*f))}
function rdi(cv,targets,opt={}){const w=cv.clientWidth,h=cv.clientHeight;cv.width=w;cv.height=h;const g=cv.getContext('2d'),r=rng(opt.seed||7);const nx=opt.nx||160,ny=opt.ny||100;const img=g.createImageData(nx,ny);
 for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){let v=0.18+0.05*gauss(r);for(const t of targets){const dx=(x-t.x*nx)/(t.s||2.2),dy=(y-t.y*ny)/(t.s||2.2);v+=t.a*Math.exp(-(dx*dx+dy*dy)/2)}
  if(Math.abs(y-ny/2)<2)v+=0.28*Math.exp(-Math.pow((x-nx*.05)/(nx*.35),2)); const c=viridis(v);const i=(y*nx+x)*4;img.data[i]=c[0];img.data[i+1]=c[1];img.data[i+2]=c[2];img.data[i+3]=255}
 const t=document.createElement('canvas');t.width=nx;t.height=ny;t.getContext('2d').putImageData(img,0,0);g.imageSmoothingEnabled=true;g.drawImage(t,0,0,w,h);
 g.strokeStyle='rgba(255,255,255,.12)';g.lineWidth=1;for(let i=1;i<8;i++){g.beginPath();g.moveTo(i*w/8,0);g.lineTo(i*w/8,h);g.stroke()}for(let i=1;i<6;i++){g.beginPath();g.moveTo(0,i*h/6);g.lineTo(w,i*h/6);g.stroke()}
 g.strokeStyle='#fff';g.lineWidth=1.5;for(const t of targets){if(!t.mark)continue;g.beginPath();g.arc(t.x*w,t.y*h,13,0,7);g.stroke();g.fillStyle='#fff';g.font='12px Segoe UI';g.fillText(t.mark,t.x*w+17,t.y*h-12)}}
function line(cv,pts,o={}){const w=cv.clientWidth,h=cv.clientHeight;cv.width=w;cv.height=h;const g=cv.getContext('2d');const m={l:46,r:14,t:12,b:30};const X=v=>m.l+(v-o.x0)/(o.x1-o.x0)*(w-m.l-m.r),Y=v=>h-m.b-(v-o.y0)/(o.y1-o.y0)*(h-m.t-m.b);
 g.strokeStyle='#3e3e42';g.fillStyle='#808080';g.font='11px Segoe UI';g.lineWidth=1;for(let i=0;i<=4;i++){const v=o.y0+(o.y1-o.y0)*i/4;g.beginPath();g.moveTo(m.l,Y(v));g.lineTo(w-m.r,Y(v));g.stroke();g.fillText(v.toFixed(o.yd??0),6,Y(v)+4)}
 for(let i=0;i<=5;i++){const v=o.x0+(o.x1-o.x0)*i/5;g.fillText(v.toFixed(o.xd??0),X(v)-8,h-10)}
 g.fillText(o.xl||'',w/2-30,h-0);g.strokeStyle=o.c||'#58a6ff';g.lineWidth=2;g.beginPath();pts.forEach((p,i)=>i?g.lineTo(X(p[0]),Y(p[1])):g.moveTo(X(p[0]),Y(p[1])));g.stroke();
 if(o.fill){g.lineTo(X(pts.at(-1)[0]),Y(o.y0));g.lineTo(X(pts[0][0]),Y(o.y0));g.fillStyle=o.fill;g.fill()}return{X,Y,g}}
