import {chromium} from 'playwright';
const browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage();
 console.log(JSON.stringify(await page.evaluate(()=>{
   const gl=document.createElement('canvas').getContext('webgl2');
   if(!gl)throw Error('WebGL2 unavailable');
   return {webgl2:true,renderer:gl.getParameter(gl.RENDERER),version:gl.getParameter(gl.VERSION),thaiShaper:'Chromium HarfBuzz; visual inspection still required'};
 }),null,2));
}finally{await browser.close();}
