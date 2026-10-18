"""Template loader and renderer using stdlib string.Template (Phase 1, Task T1.05)."""
from __future__ import annotations

import datetime
from pathlib import Path
from string import Template
from typing import Any, Dict

from skillfactory.spec import SkillSpec
from skillfactory.yaml_util import dump_frontmatter

TEMPLATES_ROOT = Path(__file__).resolve().parent

MIT_LICENSE = """MIT License

Copyright (c) $year $author

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

APACHE_LICENSE = """                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
Copyright $year $author

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

UNLICENSE = """This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
"""


def build_template_context(spec: SkillSpec) -> Dict[str, str]:
    """Build variable substitution map from a SkillSpec."""
    # Frontmatter dictionary
    fm_dict: Dict[str, Any] = {
        "name": spec.name,
        "description": spec.description,
    }
    if spec.compatibility:
        fm_dict["compatibility"] = spec.compatibility
    if spec.metadata:
        fm_dict["metadata"] = spec.metadata

    frontmatter_yaml = dump_frontmatter(fm_dict).rstrip("\r\n")

    # Format steps
    if spec.steps:
        steps_md = "\n".join(f"{i+1}. {step}" for i, step in enumerate(spec.steps))
    else:
        steps_md = (
            "1. Clarify expected inputs and outputs.\n"
            "2. Inspect available files without modifying them.\n"
            "3. Plan and execute the core task logic.\n"
            "4. Verify the output and report any limitations."
        )

    # Format examples
    if spec.examples:
        example_lines = []
        for ex in spec.examples:
            if isinstance(ex, dict):
                inp = ex.get("input", "")
                out = ex.get("output", "")
                desc = ex.get("description", "")
                if desc:
                    example_lines.append(f"**{desc}**")
                if inp:
                    example_lines.append(f"Input: `{inp}`")
                if out:
                    example_lines.append(f"Output: `{out}`")
            else:
                example_lines.append(f"- {ex}")
        examples_md = "\n".join(example_lines)
    else:
        examples_md = f"Run `{spec.name}` to achieve: {spec.description}."

    year = str(datetime.datetime.now().year)
    author = spec.author or "Skill Author"

    return {
        "name": spec.name,
        "description": spec.description,
        "frontmatter_yaml": frontmatter_yaml,
        "steps_md": steps_md,
        "examples_md": examples_md,
        "license": spec.license,
        "author": author,
        "year": year,
        "version": spec.version,
    }


def render_template_family(spec: SkillSpec) -> Dict[str, str]:
    """Render all template files for the spec's template family into a {rel_path: content} dict."""
    family_dir = TEMPLATES_ROOT / spec.template_family
    if not family_dir.exists():
        raise ValueError(
            f"Template family '{spec.template_family}' not found at {family_dir}"
        )

    context = build_template_context(spec)
    rendered_files: Dict[str, str] = {}

    for path in sorted(family_dir.rglob("*.tmpl")):
        rel_tmpl = path.relative_to(family_dir)
        # Strip .tmpl suffix: e.g. SKILL.md.tmpl -> SKILL.md
        rel_out = rel_tmpl.as_posix()[:-5]
        template_text = path.read_text(encoding="utf-8")
        rendered = Template(template_text).safe_substitute(context)
        # Normalize to LF endings
        rendered_files[rel_out] = rendered.replace("\r\n", "\n")

    # Add LICENSE file if requested
    license_choice = (spec.license or "").upper()
    license_content: str | None = None
    if license_choice == "MIT":
        license_content = Template(MIT_LICENSE).safe_substitute(context)
    elif license_choice in ("APACHE-2.0", "APACHE 2.0", "APACHE"):
        license_content = Template(APACHE_LICENSE).safe_substitute(context)
    elif license_choice in ("UNLICENSE", "PUBLIC DOMAIN"):
        license_content = UNLICENSE

    if license_content:
        rendered_files["LICENSE"] = license_content.replace("\r\n", "\n")

    return rendered_files
