import {chromium} from 'playwright';
import {createServer} from 'node:http';
import {readFile,writeFile,mkdir,stat,rename} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {spawn,spawnSync} from 'node:child_process';
import {once} from 'node:events';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const argv=process.argv.slice(2),pos=argv.filter(x=>!x.startsWith('--'));
if(pos.length!==2){console.error('node render.mjs project.json output.mp4 [--preview] [--animation-only]');process.exit(1);}
const input=path.resolve(pos[0]),output=path.resolve(pos[1]),root=path.dirname(input);
const skill=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const p=JSON.parse(await readFile(input,'utf8')),animationOnly=argv.includes('--animation-only');
if(!output.endsWith('.mp4'))throw Error('output must end in .mp4');
const python=process.env.SSM_PYTHON|| (process.platform==='win32'?'python':'python3');
const validation=spawnSync(python,[path.join(skill,'scripts','ssm.py'),'validate',input,...(animationOnly?['--animation-only']:[])],{encoding:'utf8'});
if(validation.status!==0)throw Error(validation.stderr||validation.stdout||'project validation failed');
p.render_status=animationOnly?'animation-only':'final';
await mkdir(path.dirname(output),{recursive:true});
const mime={'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.json':'application/json','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.ttf':'font/ttf','.wav':'audio/wav'};
const server=createServer(async(req,res)=>{
  try{
    const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    if(pathname==='/project/project.json'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(p));return;}
    const prefix=pathname.startsWith('/skill/')?'/skill/':'/project/';
    if(!pathname.startsWith(prefix)){res.writeHead(404).end();return;}
    const base=prefix==='/skill/'?skill:root,target=path.resolve(base,pathname.slice(prefix.length));
    if(!target.startsWith(base+path.sep)){res.writeHead(403).end();return;}
    res.setHeader('Content-Type',mime[path.extname(target)]||'application/octet-stream');
    res.end(await readFile(target));
  }catch(e){res.writeHead(404).end(String(e));}
});
server.listen(0,'127.0.0.1');await once(server,'listening');
const width=argv.includes('--preview')?(p.aspect==='16:9'?960:540):(p.aspect==='16:9'?1920:1080);
const height=Math.round(width*(p.aspect==='16:9'?9/16:16/9));
const frames=Math.ceil(p.duration*p.fps),reports=[],errors=[];
let browser,encoder;const temporary=output.replace(/\.mp4$/,'.partial.mp4');
try{
  browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:'+server.address().port+'/skill/renderer/index.html');
  await page.waitForFunction(()=>window.ready===true,{},{timeout:60000});
  const command=['-hide_banner','-loglevel','error','-y','-f','image2pipe','-vcodec','png','-framerate',String(p.fps),'-i','pipe:0'];
  if(!animationOnly)command.push('-i',path.resolve(root,p.audio.file),'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','192k');
  command.push('-t',String(p.duration),'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',temporary);
  encoder=spawn('ffmpeg',command,{stdio:['pipe','ignore','pipe']});
  const encodingDone=new Promise((resolve,reject)=>{
    encoder.once('error',reject);encoder.once('close',code=>code===0?resolve():reject(Error('FFmpeg exit '+code)));
  });
  // Prevent an unhandled rejection while a failed encoder interrupts the screenshot loop.
  encodingDone.catch(()=>{});
  let ffmpegError='';encoder.stderr.on('data',b=>ffmpegError=(ffmpegError+b).slice(-12000));
  encoder.stdin.on('error',()=>{});
  const samples=new Set([0,Math.round(frames*.18),Math.round(frames*.32),Math.round(frames*.50),Math.round(frames*.72),frames-1]);
  for(let frame=0;frame<frames;frame++){
    const report=await page.evaluate(t=>window.setTime(t),frame/p.fps);
    if(errors.length)throw Error(errors.join('\n'));
    if(!report.subtitleFits)throw Error('caption outside frame at '+frame/p.fps);
    const png=await page.screenshot({type:'png'});
    if(samples.has(frame)){await writeFile(output.replace('.mp4','-frame-'+String(frame).padStart(4,'0')+'.png'),png);reports.push(report);}
    if(!encoder.stdin.write(png))await Promise.race([once(encoder.stdin,'drain'),encodingDone.then(()=>{throw Error('encoder ended early '+ffmpegError);})]);
    if(frame%p.fps===0)console.log('frame '+frame+'/'+frames);
  }
  encoder.stdin.end();await encodingDone;
  await rename(temporary,output);
  const probe=spawnSync('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',output],{encoding:'utf8'});
  if(probe.status!==0)throw Error('ffprobe failed: '+probe.stderr);
  const info=JSON.parse(probe.stdout),video=info.streams.find(s=>s.codec_type==='video');
  if(Number(video.nb_read_frames)!==frames||video.width!==width||video.height!==height)throw Error('encoded frame count/size mismatch');
  if(!animationOnly&&!info.streams.some(s=>s.codec_type==='audio'))throw Error('missing audio stream');
  const decode=spawnSync('ffmpeg',['-v','error','-i',output,'-f','null','-'],{encoding:'utf8'});
  if(decode.status!==0||decode.stderr.trim())throw Error('decode errors: '+decode.stderr);
  const formatTime=t=>{let ms=Math.round(t*1000),h=Math.floor(ms/3600000);ms%=3600000;const m=Math.floor(ms/60000);ms%=60000;return [h,m,Math.floor(ms/1000)].map(x=>String(x).padStart(2,'0')).join(':')+','+String(ms%1000).padStart(3,'0');};
  await writeFile(output.replace('.mp4','.srt'),p.captions.map((c,i)=>(i+1)+'\n'+formatTime(c.start)+' --> '+formatTime(c.end)+'\n'+c.text).join('\n\n')+'\n','utf8');
  await writeFile(output.replace('.mp4','.qa.json'),JSON.stringify({
    status:animationOnly?'animation-preview-incomplete':'encoded-awaiting-human-review',
    complete:false,reason:animationOnly?'Google AI Studio narration unavailable':'human visual/audio review still required',
    sha256:createHash('sha256').update(await readFile(output)).digest('hex'),
    terrain_mode:'dem-mesh',vertical_exaggeration:p.terrain.vertical_exaggeration,dimensions:[width,height],fps:p.fps,
    scope:['frame count','full FFmpeg decode','streams','caption container bounds','six frame reports'],
    not_checked:['Thai pronunciation by listening','Thai marks by visual inspection','reference video similarity','subjective audio balance'],
    stream_info:info,reports
  },null,2));
  console.log(output);
}finally{
  if(encoder&&encoder.exitCode===null)encoder.kill();
  if(browser)await browser.close();
  await new Promise(resolve=>server.close(resolve));
}
