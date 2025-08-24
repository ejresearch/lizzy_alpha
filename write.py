#!/usr/bin/env python3
"""
Lizzy Alpha - Write Module (v3)
================================
Refactored to mirror the Brainstorm module's structure and UX, per spec:
- Processes ALL scenes automatically
- Requires an existing brainstorming session (brainstorming_log_vX)
- For each scene, pulls brainstorming responses for ALL buckets and blends them
- Injects bucket-specific guidance (books/scripts/plays) into the prompt
- Always includes continuity triad: previous scene text, outline snapshot, next scene outline
- Target length: 700–900 words; Golden-Era Romcom tone baked in
- Logs to versioned run table (write_runs_vX) + scene_drafts + finalized_scenes
- Auto-exports compiled .txt and .md on completion

Author: Lizzy AI Writing Framework
"""

import os
import re
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# LightRAG / LLM imports (for gpt_4o_mini wrapper)
LIGHTRAG_AVAILABLE = True
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm import gpt_4o_mini_complete
except ImportError:
    LIGHTRAG_AVAILABLE = False
    print("⚠️  LightRAG not installed. Install with: pip install lightrag")
    print("   This module requires LightRAG for AI-powered writing.")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GOLDEN_ERA_ROMCOM_TONE = (
    "You are writing a romantic comedy that revives the golden era of the genre—"
    "When Harry Met Sally, You've Got Mail, Pretty Woman, Sleepless in Seattle, Notting Hill.\n\n"
    "Principles:\n"
    "• Genuine emotional stakes and vulnerability\n"
    "• Witty, quotable dialogue that reveals character and advances plot\n"
    "• Earned romantic moments and clear \"why them\" chemistry\n"
    "• Universal yet specific conflicts (career vs love, timing, class, baggage)\n"
    "• Memorable set pieces; heart over hijinks; humor from truth, not humiliation\n"
    "Avoid: contrived misunderstandings solvable by one convo; cruelty; humiliation comedy; foundationless relationships."
)

BUCKET_GUIDANCE = {
    "books": (
        "You are an expert on screenwriting theory from acclaimed books."
        " Provide insights on structure, pacing, and character arcs."
        " Explain scene progression within three-act frameworks and how this scene serves the overall narrative."
    ),
    "scripts": (
        "You are an expert on top romantic comedy screenplays."
        " Compare to moments from successful romcoms."
        " Suggest use of romcom tropes (dialogue rhythm, humor, chemistry)."
        " Identify opportunities for comedic beats, romantic tension, and callbacks."
    ),
    "plays": (
        "You are an expert on Shakespearean comedy and drama."
        " Consider irony, elevated language, and universal themes."
        " Explore asides/soliloquy-like internal turns to heighten subtext where appropriate."
    ),
}

# -----------------------------
# Helpers to initialize buckets
# -----------------------------

def initialize_lightrag_buckets() -> Dict[str, "LightRAG"]:
    """Initialize LightRAG instances for standard buckets. (Not strictly required for write.)"""
    buckets: Dict[str, "LightRAG"] = {}
    if not LIGHTRAG_AVAILABLE:
        return buckets

    bucket_configs = {
        "books": "./lightrag_working_dir/books",
        "scripts": "./lightrag_working_dir/scripts",
        "plays": "./lightrag_working_dir/plays",
    }

    print("🔧 Initializing LightRAG buckets...")
    for name, root in bucket_configs.items():
        try:
            Path(root).mkdir(parents=True, exist_ok=True)
            buckets[name] = LightRAG(working_dir=root)
            print(f"  ✅ {name}: {root}")
        except Exception as e:
            print(f"  ⚠️  Skip {name}: {e}")

    return buckets


# -----------------------------
# Core Write Agent
# -----------------------------

class WriteAgent:
    def __init__(self, lightrag_instances: Optional[Dict[str, "LightRAG"]] = None, base_dir: str = "projects"):
        self.base_dir = Path(base_dir)
        self.project_name: Optional[str] = None
        self.db_path: Optional[Path] = None
        self.conn: Optional[sqlite3.Connection] = None

        self.lightrag = lightrag_instances or {}

        # Authoring controls
        self.style = "cinematic"              # cinematic | literary | commercial | minimalist | screenplay
        self.tone = "engaging"
        self.goal = "Write polished, production-ready scenes with vivid prose and authentic dialogue."
        self.easter_egg = ""
        self.format = "prose"                 # prose | screenplay

        # Session table
        self.table_name: Optional[str] = None  # write_runs_vX

        # Hard requirement per spec
        self.require_brainstorm = True

    # -------------
    # Setup & Schema
    # -------------
    def setup_project(self) -> bool:
        print("📂 Available Projects:")
        projects = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        if not projects:
            print("❌ No projects found. Run 'python3 start.py' first to create a project.")
            return False
        for p in projects:
            print(f"  - {p}")
        print()
        while True:
            name = input("Enter project name: ").strip()
            if name in projects:
                self.project_name = name
                self.db_path = self.base_dir / name / f"{name}.sqlite"
                if not self.db_path.exists():
                    print(f"❌ Database not found for project '{name}'.")
                    continue
                try:
                    self.conn = sqlite3.connect(self.db_path)
                    self.conn.row_factory = sqlite3.Row
                    print(f"✅ Connected to project: {name}")
                    return True
                except sqlite3.Error as e:
                    print(f"❌ Database connection error: {e}")
                    return False
            else:
                print("❌ Project not found. Please enter a valid project name.")

    def ensure_support_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS write_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                style TEXT,
                tone TEXT,
                goal TEXT,
                easter_egg TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def get_next_table_name(self) -> str:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE 'write_runs_v%'
            """
        )
        tables = [r[0] for r in cursor.fetchall()]
        versions: List[int] = []
        for t in tables:
            m = re.search(r"_v(\d+)$", t)
            if m:
                versions.append(int(m.group(1)))
        next_v = max(versions) + 1 if versions else 1
        return f"write_runs_v{next_v}"

    def setup_session_table(self):
        self.ensure_support_tables()
        self.table_name = self.get_next_table_name()
        cursor = self.conn.cursor()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                act INTEGER NOT NULL,
                scene INTEGER NOT NULL,
                scene_title TEXT,
                prompt TEXT NOT NULL,
                output TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            INSERT INTO write_sessions (session_name, style, tone, goal, easter_egg)
            VALUES (?, ?, ?, ?, ?)
            """,
            (f"Session {self.table_name} ({self.format})", self.style, self.tone, self.goal, self.easter_egg or "None"),
        )
        self.conn.commit()
        print(f"📝 Created writing table: {self.table_name}")

    # --------------------
    # Authoring Experience
    # --------------------
    def input_style_and_tone(self):
        print("\n✍️  Authoring Presets")
        print("=" * 40)
        
        # Format selection first
        print("FORMAT:")
        print("1) Prose      — Traditional narrative format")
        print("2) Screenplay — Movie script format")
        format_choice = input("\nSelect format (1-2, default 1): ").strip() or "1"
        format_mapping = {"1": "prose", "2": "screenplay"}
        self.format = format_mapping.get(format_choice, "prose")
        print(f"✅ Format: {self.format.capitalize()}")
        
        # Style selection (modified for screenplay)
        if self.format == "screenplay":
            print("\nSTYLE (for screenplay):")
            print("1) Commercial — Fast-paced, dialogue-forward")
            print("2) Character-driven — Deep character focus")
            print("3) Visual — Action and visual emphasis")
            choice = input("\nSelect style (1-3, default 1): ").strip() or "1"
            mapping = {"1": "commercial", "2": "character-driven", "3": "visual"}
            self.style = mapping.get(choice, "commercial")
        else:
            print("\nSTYLE (for prose):")
            print("1) Cinematic  — Visual, action-focused prose")
            print("2) Literary   — Rich description, interiority")
            print("3) Commercial — Fast-paced, dialogue-forward")
            print("4) Minimalist — Lean prose, subtext heavy")
            choice = input("\nSelect style (1-4, default 1): ").strip() or "1"
            mapping = {"1": "cinematic", "2": "literary", "3": "commercial", "4": "minimalist"}
            self.style = mapping.get(choice, "cinematic")
        
        print(f"✅ Selected: {self.style.capitalize()}")
        
        t = input("\nTone (e.g., witty, heartfelt, dramatic) [default: engaging]: ").strip()
        if t:
            self.tone = t
        print(f"✅ Tone: {self.tone}")
        
        g = input("\nGoal override (Enter to keep default): ").strip()
        if g:
            self.goal = g
            
        egg = input("\nOptional motif / Easter egg (Enter to skip): ").strip()
        if egg:
            self.easter_egg = egg
            print(f"✅ Easter egg added: {self.easter_egg}")

    # ------------------
    # Data Fetch Helpers
    # ------------------
    def get_project_metadata(self) -> Dict[str, str]:
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT key, value FROM project_metadata")
            return dict(cursor.fetchall())
        except sqlite3.OperationalError:
            return {}

    def fetch_characters(self) -> List[Dict]:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                SELECT name, role, description, personality_traits, backstory,
                       goals, conflicts, romantic_challenge, lovable_trait, comedic_flaw
                FROM characters ORDER BY name
                """
            )
            return [dict(r) for r in cursor.fetchall()]
        except sqlite3.OperationalError:
            return []

    def fetch_scenes(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, act, scene, scene_title, location, time_of_day,
                   characters_present, scene_purpose, key_events,
                   key_characters, beat, nudge, emotional_beats,
                   dialogue_notes, plot_threads, notes
            FROM story_outline ORDER BY act, scene
            """
        )
        return [dict(r) for r in cursor.fetchall()]

    def get_latest_brainstorm_table(self) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE 'brainstorming_log_v%'
            """
        )
        tables = [r[0] for r in cursor.fetchall()]
        if not tables:
            return None
        def ver(t: str) -> int:
            m = re.search(r"_v(\d+)$", t)
            return int(m.group(1)) if m else 0
        tables.sort(key=ver, reverse=True)
        return tables[0]

    def get_brainstorm_by_bucket(self, table: str, act: int, scene: int) -> Dict[str, str]:
        """Return a dict of bucket_name -> concatenated response for this scene."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                f"SELECT bucket_name, response FROM {table} WHERE act=? AND scene=? ORDER BY id",
                (act, scene),
            )
            rows = cursor.fetchall()
            bucket_map: Dict[str, List[str]] = {}
            for r in rows:
                b = r["bucket_name"].strip()
                bucket_map.setdefault(b, []).append(r["response"])
            return {b: "\n\n".join(txts) for b, txts in bucket_map.items()} if bucket_map else {}
        except sqlite3.OperationalError:
            return {}

    def verify_brainstorm_coverage(self, table: str, scenes: List[Dict]) -> None:
        """Ensure every scene has at least one brainstorm row; raise if any are missing."""
        missing: List[Tuple[int, int]] = []
        for s in scenes:
            act, sc = s["act"], s["scene"]
            by_bucket = self.get_brainstorm_by_bucket(table, act, sc)
            if not by_bucket:
                missing.append((act, sc))
        if missing:
            lines = ", ".join([f"Act {a}, Scene {b}" for a, b in missing])
            raise RuntimeError(
                f"❌ Brainstorming context is required but missing for: {lines}.\n"
                "   Run the brainstorming module to populate these scenes before writing."
            )

    # -------------
    # Prompt Builder
    # -------------
    def build_prompt(
        self,
        metadata: Dict[str, str],
        characters: List[Dict],
        scene: Dict,
        brainstorm_by_bucket: Dict[str, str],
        outline_snapshot: str,
        prev_text: str,
        next_desc: str,
        min_words: int = 700,
        max_words: int = 900,
    ) -> str:
        title = metadata.get("project_name", self.project_name or "Untitled Project")
        genre = metadata.get("genre", "Romantic Comedy")
        pov = metadata.get("pov", "third-person limited")
        tense = metadata.get("tense", "past")

        # Character summaries
        char_lines: List[str] = []
        for c in characters:
            name = c.get("name", "")
            role = c.get("role", "")
            desc = c.get("description", "")
            bits: List[str] = []
            if c.get("romantic_challenge"): bits.append(f"Challenge: {c['romantic_challenge']}")
            if c.get("lovable_trait"): bits.append(f"Lovable: {c['lovable_trait']}")
            if c.get("comedic_flaw"): bits.append(f"Comedy: {c['comedic_flaw']}")
            tag = f" - {name}"
            if role: tag += f" ({role})"
            if desc: tag += f": {desc}"
            if bits: tag += f" [{'; '.join(bits)}]"
            char_lines.append(tag)

        # Scene context
        def ctx(scene: Dict) -> str:
            parts: List[str] = []
            if scene.get('scene_title'): parts.append(f"Title: {scene['scene_title']}")
            if scene.get('location'): parts.append(f"Location: {scene['location']}")
            if scene.get('time_of_day'): parts.append(f"Time: {scene['time_of_day']}")
            if scene.get('characters_present'): parts.append(f"Characters: {scene['characters_present']}")
            if scene.get('scene_purpose'): parts.append(f"Purpose: {scene['scene_purpose']}")
            if scene.get('key_events'): parts.append(f"Key Events: {scene['key_events']}")
            if scene.get('emotional_beats'): parts.append(f"Emotional Journey: {scene['emotional_beats']}")
            if scene.get('dialogue_notes'): parts.append(f"Dialogue Notes: {scene['dialogue_notes']}")
            if scene.get('beat'): parts.append(f"Story Beat: {scene['beat']}")
            if scene.get('nudge'): parts.append(f"Direction: {scene['nudge']}")
            if scene.get('plot_threads'): parts.append(f"Plot Threads: {scene['plot_threads']}")
            if scene.get('notes'): parts.append(f"Notes: {scene['notes']}")
            return "\n".join(parts)

        # Build bucket guidance and context blocks (only for buckets present in brainstorm rows)
        present_buckets = list(brainstorm_by_bucket.keys())
        guidance_lines: List[str] = []
        for b in present_buckets:
            g = BUCKET_GUIDANCE.get(b, "Provide creative insights for this scene.")
            guidance_lines.append(f"- {b}: {g}")

        bucket_context_lines: List[str] = []
        for b in present_buckets:
            bucket_context_lines.append(f"[{b.upper()}]\n{brainstorm_by_bucket[b].strip()}")

        style_blend = self.style
        egg = f"\n- Easter egg to weave in: {self.easter_egg}" if self.easter_egg else ""

        if self.format == "screenplay":
            format_instructions = f"""
FORMAT: SCREENPLAY
Write in proper screenplay format with:
- Scene headings: INT./EXT. LOCATION - TIME OF DAY
- Character names in ALL CAPS when speaking
- Dialogue centered under character names
- Action lines in present tense, left-aligned
- Parentheticals sparingly (only when essential)
- NO camera directions or editing notes
- Standard screenplay conventions throughout

EXAMPLE FORMAT:
INT. COFFEE SHOP - MORNING

ROSIE stands behind the counter, steam rising from the espresso machine. The morning rush creates a symphony of clinking cups and muffled conversations.

                    ROSIE
          (to customer)
     One cappuccino, extra foam.

She slides the cup across the counter with practiced ease.

TARGET: {min_words}-{max_words} words in screenplay format{egg}
"""
            task_instruction = "Make a brief internal plan, then write ONE complete scene in proper screenplay format that advances stakes and arcs while honoring all locks and continuity. Output the screenplay scene only."
            no_headers_instruction = "- Use proper screenplay scene headings (INT./EXT. LOCATION - TIME)."
        else:
            format_instructions = f"""
STYLE & TARGET
- Style: {style_blend}
- Tone: {self.tone}
- Target length: {min_words}-{max_words} words{egg}
"""
            task_instruction = "Make a brief internal plan, then write ONE continuous, production-ready scene in polished prose that advances stakes and arcs while honoring all locks and continuity. Output the scene text only."
            no_headers_instruction = "- No scene headers or lists; output prose only."

        prompt = f"""
TONE PRESET
{GOLDEN_ERA_ROMCOM_TONE}

PROJECT: {title}
GENRE: {genre}

CONTINUITY LOCKS (must not change):
- POV: {pov} | Tense: {tense}
- Names & spelling: Use exactly as in CHARACTERS.
- Setting/time for this scene must match SCENE CONTEXT.

CHARACTERS
{chr(10).join(char_lines) if char_lines else '(No characters defined)'}

SCENE CONTEXT
Act {scene['act']}, Scene {scene['scene']}
{ctx(scene)}

CONTINUITY CONTEXT
- Previous Scene Text (for tone/voice/emotional carry-over):
{prev_text}

- Outline Snapshot (full structure, current marked with ">>"):
{outline_snapshot}

- Next Scene Description (for pacing/foreshadowing alignment):
{next_desc if next_desc else '(No next scene listed.)'}

BUCKET GUIDANCE (apply all)
{chr(10).join(guidance_lines) if guidance_lines else '- (no bucket guidance present)'}

BRAINSTORM CONTEXT BY BUCKET (inspiration; do not copy verbatim)
{chr(10).join(bucket_context_lines) if bucket_context_lines else '(No brainstorming context available)'}

{format_instructions}

DO
- Keep POV/tense and SCENE CONTEXT facts invariant.
- Maintain continuity with the previous scene's emotional and dialogue tone.
- Build toward the next scene (subtle foreshadowing, preserve open threads).
- Use distinct character voices, subtext, and concrete action.
- Structure beats implicitly: Objective → Obstacle → Turn → Decision → Button.

DON'T
{no_headers_instruction}
- Do not quote or closely paraphrase brainstorm text. Synthesize.
- Do not introduce new named characters or revise canon facts.

TASK
{task_instruction}
""".strip()
        return prompt

    # --------------
    # Generation & Persist
    # --------------
    def generate(self, prompt: str) -> str:
        # Per spec: we do not fan out one draft per bucket; we blend all buckets then generate once.
        # Use direct OpenAI API call instead of LightRAG's async wrapper
        if LIGHTRAG_AVAILABLE:
            try:
                import openai
                client = openai.OpenAI()
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert screenwriter and novelist specializing in romantic comedies."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                return f"[Error generating scene: {e}]"
        return "[Scene generation unavailable - LightRAG not installed]"

    def save_run_row(self, act: int, scene: int, title: str, prompt: str, output: str):
        cursor = self.conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO {self.table_name} (act, scene, scene_title, prompt, output)
            VALUES (?, ?, ?, ?, ?)
            """,
            (act, scene, title, prompt, output),
        )
        self.conn.commit()

    def save_draft_and_final(self, act: int, scene: int, output: str, style_note: str):
        cursor = self.conn.cursor()
        # Draft
        cursor.execute(
            """
            INSERT INTO scene_drafts (act, scene, draft_id, draft_text, version, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'draft', CURRENT_TIMESTAMP)
            """,
            (
                act,
                scene,
                f"write_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                output,
                1,
            ),
        )
        # Finalized
        cursor.execute(
            """
            INSERT OR REPLACE INTO finalized_scenes (act, scene, final_text, notes, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (act, scene, output, style_note),
        )
        self.conn.commit()

    # -------
    # Export
    # -------
    def export_full_script(self, scenes: List[Dict], metadata: Dict[str, str]):
        cursor = self.conn.cursor()
        cursor.execute("SELECT act, scene, final_text FROM finalized_scenes ORDER BY act, scene")
        rows = cursor.fetchall()
        if not rows:
            print("⚠️  No finalized scenes to export")
            return
        desktop = Path.home() / "Desktop"
        if not desktop.exists():
            outdir = self.base_dir / (self.project_name or "") / "outputs"
            outdir.mkdir(parents=True, exist_ok=True)
            desktop = outdir
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        title = metadata.get("project_name", self.project_name or "Untitled Project")
        
        # Format-specific export
        if self.format == "screenplay":
            # Screenplay format - use .fountain extension for screenplay software compatibility
            screenplay_parts: List[str] = []
            for (act, scene, text) in rows:
                screenplay_parts.append(text or "[empty scene]")
            full_screenplay = "\n\n".join(screenplay_parts)
            
            # Main screenplay file (.fountain format)
            fountain_path = desktop / f"{self.project_name}_screenplay_{ts}.fountain"
            with open(fountain_path, "w", encoding="utf-8") as f:
                f.write(f"Title: {title}\n")
                f.write(f"Credit: Written by\n")
                f.write(f"Author: Lizzy Alpha AI Framework\n")
                if metadata.get("genre"):
                    f.write(f"Genre: {metadata['genre']}\n")
                f.write(f"Format: Feature Film\n\n")
                f.write("FADE IN:\n\n")
                f.write(full_screenplay)
                f.write("\n\nFADE OUT.")
            
            # Also create a .txt version for easy reading
            txt_path = desktop / f"{self.project_name}_screenplay_{ts}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"{title}\n{'='*len(title)}\n")
                if metadata.get("genre"):
                    f.write(f"Genre: {metadata['genre']}\n")
                f.write(f"Format: Screenplay\n\n")
                f.write(full_screenplay)
                
            print("\n✅ 📄 Screenplay automatically saved to Desktop:")
            print(f"  Screenplay: {fountain_path.name} (Fountain format)")
            print(f"  Text: {txt_path.name}")
            print(f"  Location: {desktop}")
        else:
            # Traditional prose format
            text_parts: List[str] = []
            for (act, scene, text) in rows:
                hdr = f"\n{'='*60}\nAct {act}, Scene {scene}\n{'='*60}\n"
                text_parts.append(hdr + (text or "[empty]"))
            full_text = "\n\n".join(text_parts)
            txt_path = desktop / f"{self.project_name}_full_script_{ts}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"{title}\n{'='*len(title)}\n\n")
                f.write(full_text)
            # Markdown index
            md_path = desktop / f"{self.project_name}_script_{ts}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                if metadata.get("genre"):
                    f.write(f"**Genre:** {metadata['genre']}\n\n")
                f.write("## Scenes\n\n")
                finals = {(r[0], r[1]) for r in rows}
                for s in scenes:
                    if (s['act'], s['scene']) in finals:
                        f.write(f"### Act {s['act']}, Scene {s['scene']} — {s.get('scene_title','Untitled')}\n")
                        if s.get('location') or s.get('time_of_day'):
                            f.write(f"- **Setting:** {s.get('location','')} / {s.get('time_of_day','')}\n")
                        f.write("\n")
            print("\n✅ 📄 Script automatically saved to Desktop:")
            print(f"  Text: {txt_path.name}")
            print(f"  Markdown: {md_path.name}")
            print(f"  Location: {desktop}")

    # ----
    # Run
    # ----
    def run(self):
        if not self.conn:
            print("❌ No database connection")
            return

        metadata = self.get_project_metadata()
        characters = self.fetch_characters()
        scenes = self.fetch_scenes()
        if not scenes:
            print("❌ No scenes found in story outline. Run 'python3 intake.py' first to add scenes.")
            return

        brainstorm_table = self.get_latest_brainstorm_table()
        if self.require_brainstorm and not brainstorm_table:
            print("❌ Required brainstorming table not found. Run 'python3 brainstorm.py' first.")
            return

        if self.require_brainstorm:
            try:
                self.verify_brainstorm_coverage(brainstorm_table, scenes)  # raises on missing
            except RuntimeError as e:
                print(str(e))
                return
            print(f"📚 Using brainstorming context from: {brainstorm_table}")
        else:
            if brainstorm_table:
                print(f"📚 Using brainstorming context from: {brainstorm_table}")
            else:
                print("📚 No brainstorming context table found; proceeding without it.")

        print(f"\n🎬 Found {len(scenes)} scenes to write; blending all buckets per scene where available")
        print("=" * 60)

        written = 0
        for scene in scenes:
            act, scene_num = scene['act'], scene['scene']
            title = scene.get('scene_title', 'Untitled')
            print(f"\n✍️  Writing Act {act}, Scene {scene_num}: {title}")

            # Gather per-scene brainstorm blocks by bucket
            brainstorm_by_bucket = self.get_brainstorm_by_bucket(brainstorm_table, act, scene_num) if brainstorm_table else {}

            prev_raw = self.get_prev_scene_text(act, scene_num)
            prev = self.summarize_prev_if_long(prev_raw)
            outline_snap = self.make_outline_snapshot(scenes, act, scene_num)
            next_desc = self.get_next_scene_outline_desc(act, scene_num)

            prompt = self.build_prompt(
                metadata, characters, scene, brainstorm_by_bucket,
                outline_snapshot=outline_snap,
                prev_text=prev,
                next_desc=next_desc,
                min_words=700, max_words=900,
            )

            output = self.generate(prompt)
            self.save_run_row(act, scene_num, title, prompt, output)
            self.save_draft_and_final(
                act, scene_num, output,
                style_note=f"Generated with {self.style} style, {self.tone} tone, {self.format} format; Golden-Era Romcom tone preset",
            )
            written += 1
            print(f"  ✅ Done Act {act}, Scene {scene_num} ({len(output)} characters)")

        if written:
            print(f"\n🎉 Writing session complete!")
            print(f"📊 Wrote {written} of {len(scenes)} scenes")
            print("\n📝 Automatically exporting to Desktop...")
            self.export_full_script(scenes, metadata)
        else:
            print("\n❌ No scenes were successfully written.")

    # Continuity helpers
    def get_prev_scene_text(self, act: int, scene: int) -> str:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT final_text FROM finalized_scenes
            WHERE act=? AND scene=? LIMIT 1
            """,
            (act, scene - 1),
        )
        r = cursor.fetchone()
        if r and r[0]:
            return r[0]
        if scene == 1 and act > 1:
            cursor.execute(
                """
                SELECT final_text FROM finalized_scenes
                WHERE act=? ORDER BY scene DESC LIMIT 1
                """,
                (act - 1,),
            )
            r = cursor.fetchone()
            if r and r[0]:
                return r[0]
        return ""

    def get_next_scene_outline_desc(self, act: int, scene: int) -> str:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT scene_title, location, time_of_day, characters_present, scene_purpose,
                   key_events, emotional_beats, dialogue_notes, beat, nudge, plot_threads, notes
            FROM story_outline WHERE act=? AND scene=? LIMIT 1
            """,
            (act, scene + 1),
        )
        r = cursor.fetchone()
        if not r and act:
            cursor.execute(
                """
                SELECT scene_title, location, time_of_day, characters_present, scene_purpose,
                       key_events, emotional_beats, dialogue_notes, beat, nudge, plot_threads, notes
                FROM story_outline WHERE act=? ORDER BY scene ASC LIMIT 1
                """,
                (act + 1,),
            )
            r = cursor.fetchone()
        if not r:
            return ""
        parts: List[str] = []
        for key in [
            "scene_title","location","time_of_day","characters_present","scene_purpose",
            "key_events","emotional_beats","dialogue_notes","beat","nudge","plot_threads","notes"
        ]:
            val = r[key]
            if val:
                label = key.replace('_', ' ').title()
                parts.append(f"{label}: {val}")
        return "\n".join(parts)

    def make_outline_snapshot(self, scenes: List[Dict], current_act: int, current_scene: int, max_chars: int = 1200) -> str:
        lines: List[str] = []
        for s in scenes:
            tag = ">>" if (s["act"] == current_act and s["scene"] == current_scene) else "  "
            title = s.get("scene_title") or "Untitled"
            lines.append(f"{tag} Act {s['act']}, Scene {s['scene']} — {title}")
        snap = "\n".join(lines)
        if len(snap) > max_chars:
            snap = snap[:max_chars] + "\n...[truncated]"
        return snap

    def summarize_prev_if_long(self, text: str, max_chars: int = 2500) -> str:
        if not text:
            return "(No previous scene available.)"
        return text[:max_chars] + ("..." if len(text) > max_chars else "")

    def close(self):
        if self.conn:
            self.conn.close()


# -------------
# Entrypoint
# -------------

def main():
    print("✍️  Lizzy Alpha - Write Module (v3)")
    print("=" * 40)
    print("Production-grade scene writing with brainstorm-like flow")
    print()

    if not LIGHTRAG_AVAILABLE:
        print("⚠️  Warning: LightRAG not available. Some features will be limited.")
        print()

    lightrag_instances = initialize_lightrag_buckets()
    agent = WriteAgent(lightrag_instances=lightrag_instances)

    try:
        if not agent.setup_project():
            return
        agent.input_style_and_tone()
        agent.setup_session_table()

        print("\n🚀 Starting writing process...")
        agent.run()

    except KeyboardInterrupt:
        print("\n\n⏸️  Session cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        agent.close()
        print("\n👋 Writing session ended.")


if __name__ == "__main__":
    main()