import * as THREE from '/skill/renderer/node_modules/three/build/three.module.js';

const p = await (await fetch('/project/project.json')).json();
const geo = await (await fetch('/project/geo.json')).json();
const $ = id => document.getElementById(id);
const base = p.aspect === '16:9' ? [1920,1080] : [1080,1920];
$('stage').style.width=base[0]+'px'; $('stage').style.height=base[1]+'px';
$('stage').style.transform='scale('+window.innerWidth/base[0]+')';
if(p.aspect==='16:9'){
  $('title').style.fontSize='62px';$('title').style.top='90px';
  $('subtitle').style.top='76%';$('credits').style.bottom='55px';
  $('diagram').style.cssText+=';left:560px;right:560px;top:24%;height:440px';
}
const canvas=$('map');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});
renderer.setSize(base[0],base[1],false);renderer.setPixelRatio(1);
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.setClearColor(p.colors.ocean);
const scene=new THREE.Scene();
scene.add(new THREE.HemisphereLight(0xddeeff,0x183044,2.0));
const sun=new THREE.DirectionalLight(0xffe3b9,2.1);sun.position.set(-300,300,500);scene.add(sun);
const camera=new THREE.OrthographicCamera(-1,1,1,-1,.01,30000);camera.up.set(0,1,0);
function merc(lon,lat){return [6378.137*lon*Math.PI/180,6378.137*Math.asinh(Math.tan(lat*Math.PI/180))];}
const origin=merc(...p.origin);
function xy(lon,lat){const q=merc(lon,lat);return [q[0]-origin[0],q[1]-origin[1]];}
const detailed=geo.maps.find(x=>x.elevation_m);
function elevation(lon,lat){
  if(!detailed)return 0;
  const [w,s,e,n]=detailed.bounds,[xl,yb]=merc(w,s),[xr,yt]=merc(e,n),[x,y]=merc(lon,lat);
  const u=(x-xl)/(xr-xl),v=(yt-y)/(yt-yb);
  if(u<0||u>1||v<0||v>1)return 0;
  const [cols,rows]=detailed.grid;
  const gx=u*(cols-1),gy=v*(rows-1),ix=Math.min(cols-2,Math.floor(gx)),iy=Math.min(rows-2,Math.floor(gy));
  const ax=gx-ix,ay=gy-iy,h=(i,j)=>detailed.elevation_m[j*cols+i];
  const z=(h(ix,iy)*(1-ax)+h(ix+1,iy)*ax)*(1-ay)+(h(ix,iy+1)*(1-ax)+h(ix+1,iy+1)*ax)*ay;
  return Math.max(0,z)*detailed.vertical_exaggeration/1000/Math.cos(p.origin[1]*Math.PI/180);
}
function world(point,lift=.15){return new THREE.Vector3(...xy(...point),elevation(...point)+lift);}
const textures=new THREE.TextureLoader();
for(const map of geo.maps){
  const [w,s,e,n]=map.bounds,[xl,yb]=xy(w,s),[xr,yt]=xy(e,n);
  const [cols,rows]=map.grid||[2,2],positions=[],uv=[],indices=[];
  for(let j=0;j<rows;j++)for(let i=0;i<cols;i++){
    const u=i/(cols-1),v=j/(rows-1);
    const z=map.elevation_m ? Math.max(0,map.elevation_m[j*cols+i])*map.vertical_exaggeration/1000/Math.cos(p.origin[1]*Math.PI/180):-.05;
    positions.push(xl+u*(xr-xl),yt-v*(yt-yb),z);uv.push(u,1-v);
    if(i<cols-1&&j<rows-1){const a=j*cols+i;indices.push(a,a+cols,a+1,a+1,a+cols,a+cols+1);}
  }
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
  geometry.setIndex(indices);geometry.computeVertexNormals();
  const texture=await textures.loadAsync('/project/'+map.texture);texture.colorSpace=THREE.SRGBColorSpace;
  const mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({map:texture,roughness:1,metalness:0,color:0xb9d5d5,side:THREE.DoubleSide}));
  scene.add(mesh);
}
const countryGroups=[];
for(const country of p.countries){
  const feature=geo.countries.find(x=>x.code===country.code);
  const group=new THREE.Group();scene.add(group);
  const polygons=feature.geometry.type==='Polygon'?[feature.geometry.coordinates]:feature.geometry.coordinates;
  for(const polygon of polygons){
    const shape=new THREE.Shape(polygon[0].map(q=>new THREE.Vector2(...xy(...q))));
    for(const ring of polygon.slice(1))shape.holes.push(new THREE.Path(ring.map(q=>new THREE.Vector2(...xy(...q)))));
    const geometry=new THREE.ShapeGeometry(shape);
    const pos=geometry.getAttribute('position');
    // Country highlight is an overlay at regional scale, hidden before the close terrain shot.
    for(let i=0;i<pos.count;i++)pos.setZ(i,.1);
    group.add(new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({color:p.colors.highlight,transparent:true,opacity:.40,depthTest:false,side:THREE.DoubleSide})));
    for(const ring of polygon){
      const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(ring.map(q=>world(q,.2))),
        new THREE.LineBasicMaterial({color:0xffd17b,transparent:true,opacity:.95,depthTest:false}));
      group.add(line);
    }
  }
  const label=document.createElement('div');label.className='anchor';
  const flag=document.createElement('img');flag.src=country.flag?'/project/'+country.flag:'/skill/assets/flags/'+country.code+'.svg';
  const text=document.createElement('span');text.textContent=country.name;
  label.append(flag,text);$('labels').append(label);
  countryGroups.push({country,group,label,flag});
}
const labels=p.labels.map(item=>{
  const el=document.createElement('div');el.className='anchor';el.textContent=item.text;$('labels').append(el);return{item,el};
});
const routes=p.routes.map(item=>{
  const geometry=new THREE.BufferGeometry().setFromPoints(item.points.map(q=>world(q,.25)));
  const line=new THREE.Line(geometry,new THREE.LineBasicMaterial({color:item.color||p.colors.route,depthTest:false}));
  line.renderOrder=10;scene.add(line);
  const head=document.createElement('img');head.className='object';head.src='/skill/assets/icons/arrow.svg';head.style.width='48px';$('labels').append(head);
  return {item,line,head};
});
const objects=p.objects.map(item=>{
  const el=document.createElement('img');el.className='object';el.src=item.asset?'/project/'+item.asset:'/skill/assets/icons/'+item.icon+'.svg';
  el.style.width=(item.width||100)+'px';$('labels').append(el);return{item,el};
});
function mix(a,b,t){return a+(b-a)*t;}function clamp(t){return Math.max(0,Math.min(1,t));}
function smooth(t){t=clamp(t);return t*t*(3-2*t);}
function track(points,progress){
  const projected=points.map(q=>xy(...q)),lengths=[0];
  for(let i=1;i<points.length;i++)lengths.push(lengths[i-1]+Math.hypot(projected[i][0]-projected[i-1][0],projected[i][1]-projected[i-1][1]));
  const d=clamp(progress)*lengths.at(-1);
  let i=1;while(i<lengths.length-1&&d>lengths[i])i++;
  const f=(d-lengths[i-1])/(lengths[i]-lengths[i-1]||1);
  return [mix(points[i-1][0],points[i][0],f),mix(points[i-1][1],points[i][1],f)];
}
function screen(q){const v=world(q).project(camera);return[(v.x+1)*base[0]/2,(1-v.y)*base[1]/2,v.z];}
function place(el,q,rotation=null){
  const [x,y,z]=screen(q);el.style.left=x+'px';el.style.top=y+'px';
  el.style.visibility=z< -1||z>1?'hidden':'visible';
  if(rotation!==null)el.style.transform='translate(-50%,-50%) rotate('+rotation+'deg)';
}
function direction(points,progress){
  const a=screen(track(points,Math.max(0,progress-.005))),b=screen(track(points,Math.min(1,progress+.005)));
  return Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI;
}
function cameraAt(t){
  let a=p.camera[0],b=a;
  for(const key of p.camera){b=key;if(t<=key.at)break;a=key;}
  const f=smooth((t-a.at)/(b.at-a.at||1));
  const lon=mix(a.center[0],b.center[0],f),lat=mix(a.center[1],b.center[1],f);
  const span=Math.exp(mix(Math.log(a.span_km),Math.log(b.span_km),f)),tilt=mix(a.tilt,b.tilt,f)*Math.PI/180,bearing=mix(a.bearing||0,b.bearing||0,f)*Math.PI/180;
  const target=world([lon,lat],0),distance=8000;
  camera.left=-span/2;camera.right=span/2;camera.top=span*base[1]/base[0]/2;camera.bottom=-camera.top;
  camera.position.set(target.x+Math.sin(bearing)*Math.sin(tilt)*distance,target.y-Math.cos(bearing)*Math.sin(tilt)*distance,target.z+Math.cos(tilt)*distance);
  camera.up.set(-Math.sin(bearing)*Math.cos(tilt),Math.cos(bearing)*Math.cos(tilt),Math.sin(tilt));
  camera.lookAt(target);camera.updateProjectionMatrix();camera.updateMatrixWorld();
}
const wm=p.watermark;
if(wm){$('watermark').src='/project/'+wm.file;$('watermark').style.cssText+=';left:'+wm.x*100+'%;top:'+wm.y*100+'%;width:'+wm.width*100+'%;opacity:'+wm.opacity;}
else $('watermark').style.display='none';
$('headline').textContent=p.title_screen;$('eyebrow').textContent=p.eyebrow||'';
$('credits').textContent=geo.credits.join('\n')+'\n'+p.route_note;
$('status').textContent=p.render_status==='final'?'':'ทดสอบภาพเคลื่อนไหว • ยังไม่มีเสียงพากย์';
await document.fonts.ready;
await Promise.all([...document.images].map(i=>i.decode().catch(()=>{throw Error('image failed: '+i.src);})));
window.setTime=async seconds=>{
  const t=seconds;cameraAt(t);
  for(const {country,group,label,flag} of countryGroups){
    group.visible=t>=country.start&&t<country.end;
    label.style.display=group.visible?'block':'none';flag.style.display=t>=country.flag_at?'block':'none';place(label,country.location);
  }
  for(const {item,el} of labels){el.style.display=t>=item.start&&t<item.end?'block':'none';place(el,item.location);}
  for(const {item,line,head} of routes){
    const progress=clamp((t-item.start)/(item.end-item.start));
    line.visible=t>=item.start;const count=Math.max(2,Math.ceil(progress*item.points.length));
    const partial=[item.points[0]];
    // Resample to 160 points for smooth, continuous route reveal.
    for(let i=1;i<=160;i++)partial.push(track(item.points,progress*i/160));
    line.geometry.dispose();line.geometry=new THREE.BufferGeometry().setFromPoints(partial.map(q=>world(q,.25)));
    head.style.display=t>=item.start?'block':'none';place(head,track(item.points,progress),direction(item.points,progress));
  }
  for(const {item,el} of objects){
    const route=p.routes.find(r=>r.id===item.route),progress=clamp((t-item.start)/(item.end-item.start));
    el.style.display=t>=item.start&&t<=item.end?'block':'none';place(el,track(route.points,progress),direction(route.points,progress));
  }
  const diagram=p.mechanism;
  const show=diagram&&(t>=diagram.start&&t<diagram.end||t<2.4);
  $('diagram').style.display=show?'block':'none';
  if(show){
    const f=t<2.4?smooth(t/2.4):smooth((t-diagram.start)/(diagram.end-diagram.start-1));
    const y=mix(265,130,f),d='M44 '+y+' H711 V304 H44 Z';
    $('water').setAttribute('d',d);$('ripple').setAttribute('d',d);
    $('lock-ship').setAttribute('y',y-103);
    $('flow').style.strokeDashoffset=String(-t*40);
  }
  const cue=(p.captions||[]).find(c=>seconds>=c.start&&seconds<c.end);
  $('subtitle').firstElementChild.textContent=cue?cue.text:'';
  $('subtitle').style.display=cue?'block':'none';
  $('headline').textContent=t>=22?p.answer_screen:p.title_screen;
  $('title').style.opacity=t>10&&t<21?'.65':'1';
  if(wm)$('watermark').style.display=seconds>=wm.start&&seconds<wm.end?'block':'none';
  renderer.render(scene,camera);
  const subtitle=$('subtitle').getBoundingClientRect();
  window.frameReport={time:seconds,terrainMode:detailed?'dem-mesh':'flat',
    renderer:renderer.getContext().getParameter(renderer.getContext().RENDERER),
    subtitleFits:!cue||(subtitle.left>=0&&subtitle.right<=window.innerWidth&&subtitle.bottom<=window.innerHeight),
    anchors:countryGroups.map(({country,label})=>({code:country.code,x:parseFloat(label.style.left),y:parseFloat(label.style.top)}))};
  return window.frameReport;
};
window.ready=true;await window.setTime(0);
