import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/"skills/sports-story-motion"
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,file);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
ssm=module("ssm",SKILL/"scripts/ssm.py")
geo=module("geo",SKILL/"scripts/prepare_geo.py")
legacy=module("legacy",SKILL/"scripts/render.py")
pack=module("pack",ROOT/"scripts/build_packages.py")
class ToolkitTests(unittest.TestCase):
    def setUp(self):
        self.project=json.loads((SKILL/"assets/panama/project.json").read_text(encoding="utf-8"))
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.path=self.root/"project.json"
    def tearDown(self):self.temp.cleanup()
    def validate(self,preview=True):
        ssm.write(self.path,self.project);return ssm.validate(self.path,preview)
    def test_demo_requires_real_narration(self):
        self.validate()
        with self.assertRaisesRegex(ValueError,"Google AI Studio"):self.validate(False)
    def test_flag_must_precede_zoom(self):
        self.project["countries"][0]["flag_at"]=7
        with self.assertRaisesRegex(ValueError,"locate"):self.validate()
    def test_country_flag_has_reading_hold(self):
        self.project["countries"][0]["flag_at"]=5.8
        with self.assertRaisesRegex(ValueError,"one second"):self.validate()
    def test_actual_route_needs_provenance(self):
        self.project["routes"][0]["kind"]="actual"
        with self.assertRaisesRegex(ValueError,"verified source"):self.validate()
    def test_no_unrequested_watermark(self):
        (self.root/"logo.png").write_bytes(b"test")
        self.project["watermark"]={"file":"logo.png","start":0,"end":26,"width":.1,"opacity":.5}
        with self.assertRaisesRegex(ValueError,"explicit user request"):self.validate()
    def test_caption_must_fit_audio(self):
        self.project["captions"]=[{"start":25,"end":29,"text":"ทดสอบ"}]
        with self.assertRaisesRegex(ValueError,"cue outside"):self.validate()
    def test_srt_retains_thai_marks_and_milliseconds(self):
        path=self.root/"thai.srt";path.write_text("1\n00:00:01,025 --> 00:00:02,700\nเรือกำลังสูงขึ้น\n",encoding="utf-8")
        self.assertEqual(ssm.parse_srt(path),[{"start":1.025,"end":2.7,"text":"เรือกำลังสูงขึ้น"}])
    def test_local_path_cannot_escape_project(self):
        with self.assertRaises(ValueError):ssm.local(self.root,"../secret.txt")
    def test_dem_decodes_terrarium_before_interpolation(self):
        from PIL import Image
        import io
        image=Image.new("RGB",(256,256),(128,26,128));buf=io.BytesIO();image.save(buf,format="PNG")
        with patch.object(geo,"fetch",return_value=buf.getvalue()):
            dem=geo.mosaic([-80,8,-79,10],8,geo.DEM,self.root,[],(3,3),True)
        self.assertAlmostEqual(dem.getpixel((1,1)),26.5,places=3)
    def test_legacy_timeline_and_raqm_still_work(self):
        path=SKILL/"assets/demo/timeline.json";job=json.loads(path.read_text(encoding="utf-8"))
        legacy.validate(job,path.parent,30)
        image=legacy.Renderer(job,path.parent,(270,480),30).frame(291)
        self.assertEqual(image.size,(270,480))
    def test_platform_packages_and_no_runtime_cache(self):
        packages=pack.build(self.root/"dist")
        self.assertEqual(len(packages),4)
        self.assertTrue(all(p["bytes"]>10000 for p in packages))
if __name__=="__main__":unittest.main()
