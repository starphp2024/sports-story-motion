#!/usr/bin/env python3
"""Validate provider manifests against current official schemas and skill frontmatter."""
import json
from pathlib import Path
from urllib.request import urlopen
import jsonschema
import yaml
ROOT=Path(__file__).resolve().parents[1]
def run():
    records=[]
    for file,url in [
        ("plugin.json","https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"),
        (".antigravity-plugin/plugin.json","https://antigravity.google/schemas/v1/plugin.json")]:
        with urlopen(url,timeout=45) as response:schema=json.load(response)
        jsonschema.validate(json.loads((ROOT/file).read_text(encoding="utf-8")),schema)
        records.append({"file":file,"schema":url,"result":"pass","scope":"official JSON schema; not an app installation"})
    skill=ROOT/"skills/sports-story-motion/SKILL.md"
    front=yaml.safe_load(skill.read_text(encoding="utf-8").split("---",2)[1])
    assert front["name"]==skill.parent.name and isinstance(front["description"],str) and front["description"].strip()
    manifest=json.loads((ROOT/".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"]==front["name"]
    assert len(json.loads((ROOT/"plugin.json").read_text(encoding="utf-8"))["extensions"]["com.openai"]["interface"]["shortDescription"])<=30
    records.append({"file":str(skill.relative_to(ROOT)),"result":"pass","scope":"YAML parsing, name/description and manifest identity"})
    print(json.dumps(records,ensure_ascii=False,indent=2))
    return records
if __name__=="__main__":run()
