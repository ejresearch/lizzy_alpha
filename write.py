#!/usr/bin/env python3
"""
Lizzy Alpha - Write Module
===========================
Synthesizes brainstorming sessions and project elements into polished drafts.
Integrates with story_outline and brainstorming_log_vX tables to generate scenes.

Author: Lizzy AI Writing Framework
"""

import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import LightRAG and OpenAI integration
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm import gpt_4o_mini_complete
    LIGHTRAG_AVAILABLE = True
except ImportError:
    print("⚠️  LightRAG not installed. Install with: pip install lightrag")
    print("   This module requires LightRAG for AI-powered writing.")
    LIGHTRAG_AVAILABLE = False
    
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class LizzyWrite:
    """
    The Write module generates production-ready scene drafts by:
    - Reading characters and story outline from your schema
    - Pulling latest brainstorming context per scene
    - Using LightRAG buckets for informed scene generation
    - Saving versioned drafts to existing schema tables
    """
    
    def __init__(self, base_dir="projects"):
        self.base_dir = Path(base_dir)
        self.project_name = None
        self.db_path = None
        self.conn = None
        
        # Writing configuration
        self.tone = ""
        self.goal = "Write polished, production-ready scenes with vivid prose and authentic dialogue."
        self.easter_egg = ""
        self.writing_style = "cinematic"
        
        # LightRAG integration
        self.selected_buckets = []
        self.bucket_guidance = {}
        self.lightrag_instances = {}
        
    def setup_project(self):
        """Select and connect to a project database."""
        print("📂 Available Projects:")
        projects = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        
        if not projects:
            print("❌ No projects found. Run 'python3 start.py' first to create a project.")
            return False
            
        for project in projects:
            print(f"  - {project}")
        
        print()
        while True:
            project = input("Enter project name: ").strip()
            
            if project in projects:
                self.project_name = project
                self.db_path = self.base_dir / project / f"{project}.sqlite"
                
                if not self.db_path.exists():
                    print(f"❌ Database not found for project '{project}'.")
                    continue
                    
                try:
                    self.conn = sqlite3.connect(self.db_path)
                    self.conn.row_factory = sqlite3.Row
                    print(f"✅ Connected to project: {project}")
                    return True
                except sqlite3.Error as e:
                    print(f"❌ Database connection error: {e}")
                    return False
            else:
                print("❌ Project not found. Please enter a valid project name.")
    
    def select_buckets(self):
        """Select LightRAG knowledge buckets to use for writing."""
        if not LIGHTRAG_AVAILABLE:
            print("⚠️  LightRAG not available. Proceeding without bucket context.")
            return
            
        buckets_dir = Path("./lightrag_working_dir")
        if not buckets_dir.exists():
            print("⚠️  No LightRAG buckets found. Proceeding without bucket context.")
            return
            
        available_buckets = [
            d.name for d in buckets_dir.iterdir() 
            if d.is_dir() and not d.name.startswith(".")
        ]
        
        if not available_buckets:
            print("⚠️  No LightRAG buckets configured. Proceeding without bucket context.")
            return
            
        print("\\n📚 Available LightRAG Buckets:")
        for i, bucket in enumerate(available_buckets, 1):
            print(f"  {i}. {bucket}")
        
        print("\\nBucket Selection:")
        print("  - Enter numbers (e.g., '1,3')")
        print("  - Enter 'all' for all buckets")
        print("  - Press Enter to skip buckets")
        
        choice = input("\\nSelect buckets: ").strip()
        
        if not choice:
            self.selected_buckets = []
        elif choice.lower() == "all":
            self.selected_buckets = available_buckets
        else:
            selected = []
            for c in choice.split(","):
                c = c.strip()
                if c.isdigit() and 1 <= int(c) <= len(available_buckets):
                    selected.append(available_buckets[int(c) - 1])
            self.selected_buckets = selected
        
        # Initialize LightRAG instances for selected buckets
        if self.selected_buckets:
            print("\\n🔧 Initializing selected buckets...")
            for bucket in self.selected_buckets:
                try:
                    bucket_path = buckets_dir / bucket
                    self.lightrag_instances[bucket] = LightRAG(working_dir=str(bucket_path))
                    
                    # Get guidance for this bucket
                    guidance = input(f"  Guidance for '{bucket}' (how should it inform writing?): ").strip()
                    self.bucket_guidance[bucket] = guidance or f"Use {bucket} knowledge to enhance the scene"
                    
                    print(f"  ✅ {bucket} initialized")
                except Exception as e:
                    print(f"  ⚠️  Failed to initialize {bucket}: {e}")
        
        if self.lightrag_instances:
            print(f"\\n✅ Using {len(self.lightrag_instances)} LightRAG buckets for context")
        else:
            print("\\n📝 Proceeding without LightRAG bucket context")
    
    def configure_writing(self):
        """Configure writing style and authoring controls."""
        print("\\n✍️  Writing Configuration")
        print("=" * 40)
        
        # Writing style selection
        styles = {
            "1": ("Cinematic", "Visual, action-focused prose like a screenplay in narrative form"),
            "2": ("Literary", "Rich, descriptive prose with deep character interiority"),
            "3": ("Commercial", "Fast-paced, dialogue-heavy, accessible storytelling"),
            "4": ("Minimalist", "Lean, Hemingway-esque prose focused on subtext")
        }
        
        print("\\nWriting Styles:")
        for key, (name, desc) in styles.items():
            print(f"  {key}. {name}: {desc}")
        
        while True:
            style_choice = input("\\nSelect writing style (1-4): ").strip()
            if style_choice in styles:
                self.writing_style = styles[style_choice][0].lower()
                print(f"✅ Selected: {styles[style_choice][0]}")
                break
            print("❌ Please enter 1, 2, 3, or 4")
        
        # Tone and approach
        self.tone = input("\\nWriting tone (e.g., witty, heartfelt, dramatic): ").strip() or "engaging"
        
        # Custom writing goal
        print(f"\\nCurrent goal: {self.goal}")
        custom_goal = input("Custom writing goal (Enter to keep current): ").strip()
        if custom_goal:
            self.goal = custom_goal
        
        # Easter egg/motif
        self.easter_egg = input("\\nOptional motif/easter egg to weave throughout: ").strip()
        
        print("\\n✅ Writing configuration complete")
    
    def get_project_metadata(self) -> Dict[str, str]:
        """Retrieve project metadata."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("SELECT key, value FROM project_metadata")
            return dict(cursor.fetchall())
        except sqlite3.OperationalError:
            return {}
    
    def get_characters(self) -> List[Dict]:
        """Retrieve all characters with their details."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                SELECT name, role, description, personality_traits, backstory,
                       goals, conflicts, romantic_challenge, lovable_trait, comedic_flaw
                FROM characters 
                ORDER BY name
            """)
            
            characters = []
            for row in cursor.fetchall():
                char = dict(row)
                characters.append(char)
            
            return characters
        except sqlite3.OperationalError:
            return []
    
    def get_story_outline(self) -> List[Dict]:
        """Retrieve story outline with scene details."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT id, act, scene, scene_title, location, time_of_day,
                   characters_present, scene_purpose, key_events,
                   key_characters, beat, nudge, emotional_beats,
                   dialogue_notes, plot_threads, notes
            FROM story_outline 
            ORDER BY act, scene
        """)
        
        scenes = []
        for row in cursor.fetchall():
            scene = dict(row)
            scenes.append(scene)
        
        return scenes
    
    def get_latest_brainstorm_table(self) -> Optional[str]:
        """Find the most recent brainstorming_log_vX table."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'brainstorming_log_v%'
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            return None
        
        # Extract version numbers and get the highest
        def get_version(table_name):
            match = re.search(r'_v(\d+)$', table_name)
            return int(match.group(1)) if match else 0
        
        tables.sort(key=get_version, reverse=True)
        return tables[0]
    
    def get_brainstorm_for_scene(self, brainstorm_table: str, act: int, scene: int) -> Optional[str]:
        """Get brainstorming responses for a specific scene."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(f"""
                SELECT response, bucket_name 
                FROM {brainstorm_table}
                WHERE act = ? AND scene = ?
                ORDER BY id
            """, (act, scene))
            
            responses = cursor.fetchall()
            
            if not responses:
                return None
            
            # Combine all bucket responses
            brainstorm_parts = []
            for response in responses:
                bucket = response['bucket_name']
                text = response['response']
                brainstorm_parts.append(f"[{bucket.upper()}]: {text}")
            
            return "\\n\\n".join(brainstorm_parts)
            
        except sqlite3.OperationalError:
            return None
    
    def synthesize_scene_context(self, scene: Dict) -> str:
        """Combine scene fields into a cohesive description."""
        context_parts = []
        
        if scene.get('scene_title'):
            context_parts.append(f"Title: {scene['scene_title']}")
        
        if scene.get('location'):
            context_parts.append(f"Location: {scene['location']}")
        
        if scene.get('time_of_day'):
            context_parts.append(f"Time: {scene['time_of_day']}")
        
        if scene.get('characters_present'):
            context_parts.append(f"Characters: {scene['characters_present']}")
        
        if scene.get('scene_purpose'):
            context_parts.append(f"Purpose: {scene['scene_purpose']}")
        
        if scene.get('key_events'):
            context_parts.append(f"Key Events: {scene['key_events']}")
        
        if scene.get('emotional_beats'):
            context_parts.append(f"Emotional Journey: {scene['emotional_beats']}")
        
        if scene.get('dialogue_notes'):
            context_parts.append(f"Dialogue Notes: {scene['dialogue_notes']}")
        
        if scene.get('beat'):
            context_parts.append(f"Story Beat: {scene['beat']}")
        
        if scene.get('nudge'):
            context_parts.append(f"Direction: {scene['nudge']}")
        
        if scene.get('plot_threads'):
            context_parts.append(f"Plot Threads: {scene['plot_threads']}")
        
        if scene.get('notes'):
            context_parts.append(f"Notes: {scene['notes']}")
        
        return "\\n".join(context_parts)
    
    def get_prev_scene_text(self, act: int, scene: int) -> str:
        """Return finalized text for previous scene (or empty)."""
        cursor = self.conn.cursor()
        # Same act, previous scene
        cursor.execute("""
            SELECT final_text FROM finalized_scenes
            WHERE act = ? AND scene = ?
            LIMIT 1
        """, (act, scene - 1))
        row = cursor.fetchone()
        if row and row[0]:
            return row[0]

        # If first scene of act, try last scene of previous act
        if scene == 1 and act > 1:
            cursor.execute("""
                SELECT final_text FROM finalized_scenes
                WHERE act = ?
                ORDER BY scene DESC
                LIMIT 1
            """, (act - 1,))
            row = cursor.fetchone()
            if row and row[0]:
                return row[0]

        return ""

    def get_next_scene_outline_desc(self, act: int, scene: int) -> str:
        """Return outline description for next scene (or empty)."""
        cursor = self.conn.cursor()

        # Same act, next scene
        cursor.execute("""
            SELECT scene_title, location, time_of_day, characters_present, scene_purpose,
                   key_events, emotional_beats, dialogue_notes, beat, nudge, plot_threads, notes
            FROM story_outline
            WHERE act = ? AND scene = ?
            LIMIT 1
        """, (act, scene + 1))
        row = cursor.fetchone()
        if not row and act:  # first scene of next act
            cursor.execute("""
                SELECT scene_title, location, time_of_day, characters_present, scene_purpose,
                       key_events, emotional_beats, dialogue_notes, beat, nudge, plot_threads, notes
                FROM story_outline
                WHERE act = ?
                ORDER BY scene ASC
                LIMIT 1
            """, (act + 1,))
            row = cursor.fetchone()

        if not row:
            return ""

        # Build description from row data
        parts = []
        if row['scene_title']: parts.append(f"Title: {row['scene_title']}")
        if row['location']: parts.append(f"Location: {row['location']}")
        if row['time_of_day']: parts.append(f"Time: {row['time_of_day']}")
        if row['characters_present']: parts.append(f"Characters: {row['characters_present']}")
        if row['scene_purpose']: parts.append(f"Purpose: {row['scene_purpose']}")
        if row['key_events']: parts.append(f"Key Events: {row['key_events']}")
        if row['emotional_beats']: parts.append(f"Emotional Beats: {row['emotional_beats']}")
        if row['dialogue_notes']: parts.append(f"Dialogue Notes: {row['dialogue_notes']}")
        if row['beat']: parts.append(f"Story Beat: {row['beat']}")
        if row['nudge']: parts.append(f"Direction: {row['nudge']}")
        if row['plot_threads']: parts.append(f"Plot Threads: {row['plot_threads']}")
        if row['notes']: parts.append(f"Notes: {row['notes']}")
        return "\\n".join(parts)

    def make_outline_snapshot(self, scenes: List[Dict], current_act: int, current_scene: int, max_chars: int = 1200) -> str:
        """
        Return a compact 'full outline' snapshot (one line per scene), 
        highlighting the current scene. Truncate to max_chars.
        """
        lines = []
        for s in scenes:
            tag = ">>" if (s["act"] == current_act and s["scene"] == current_scene) else "  "
            title = s.get("scene_title") or "Untitled"
            lines.append(f"{tag} Act {s['act']}, Scene {s['scene']} — {title}")
        snapshot = "\\n".join(lines)
        if len(snapshot) > max_chars:
            snapshot = snapshot[:max_chars] + "\\n...[truncated]"
        return snapshot

    def summarize_prev_if_long(self, text: str, max_chars: int = 2500) -> str:
        """Hard truncate to stay token-safe for Claude; optionally replace with a short note if empty."""
        if not text:
            return "(No previous scene available.)"
        return text[:max_chars] + ("..." if len(text) > max_chars else "")
    
    def build_scene_prompt(self, metadata: Dict, characters: List[Dict], 
                          scene: Dict, brainstorm_context: Optional[str],
                          outline_snapshot: str = "", prev_scene_text: str = "", 
                          next_scene_desc: str = "",
                          style_primary: str = None, style_secondary: str = None,
                          min_words: int = 700, max_words: int = 900) -> str:
        """Build comprehensive prompt for scene generation with full continuity context."""
        
        # Project context
        title = metadata.get('project_name', self.project_name or 'Untitled Project')
        genre = metadata.get('genre', 'Romantic Comedy')
        
        # Character summaries
        char_summaries = []
        for char in characters:
            name = char.get('name', '')
            role = char.get('role', '')
            desc = char.get('description', '')
            
            summary = f"- {name}"
            if role:
                summary += f" ({role})"
            if desc:
                summary += f": {desc}"
            
            # Add Essential Trinity if available
            traits = []
            if char.get('romantic_challenge'):
                traits.append(f"Challenge: {char['romantic_challenge']}")
            if char.get('lovable_trait'):
                traits.append(f"Lovable: {char['lovable_trait']}")
            if char.get('comedic_flaw'):
                traits.append(f"Comedy: {char['comedic_flaw']}")
            
            if traits:
                summary += f" [{'; '.join(traits)}]"
            
            char_summaries.append(summary)
        
        # Scene context
        scene_context = self.synthesize_scene_context(scene)
        
        # Style configuration
        style_primary = style_primary or self.writing_style
        style_secondary = style_secondary or ""
        style_blend = f"{style_primary}" + (f" + {style_secondary}" if style_secondary else "")
        
        # Continuity locks from metadata
        pov = metadata.get("pov", "third-person limited")
        tense = metadata.get("tense", "past")
        
        # Easter egg
        easter_egg_line = f"\\n- Easter egg to weave in: {self.easter_egg}" if self.easter_egg else ""
        
        prompt = f"""PROJECT: {title}
GENRE: {genre}

CONTINUITY LOCKS (must not change):
- POV: {pov} | Tense: {tense}
- Names & spelling: Use exactly as in CHARACTERS.
- Setting/time for this scene must match SCENE CONTEXT.

CHARACTERS
{chr(10).join(char_summaries) if char_summaries else '(No characters defined)'}

SCENE CONTEXT
Act {scene['act']}, Scene {scene['scene']}
{scene_context}

CONTINUITY CONTEXT
- Previous Scene Text (for tone/voice/emotional carry-over):
{prev_scene_text}

- Outline Snapshot (full structure, current marked with ">>"):
{outline_snapshot}

- Next Scene Description (for pacing/foreshadowing alignment):
{next_scene_desc if next_scene_desc else '(No next scene listed.)'}

BRAINSTORMING CONTEXT (for inspiration, do not copy verbatim):
{brainstorm_context or '(No brainstorming context available)'}

STYLE & TARGET
- Style blend: {style_blend}
- Tone: {self.tone or 'engaging'}
- Target length: {min_words}-{max_words} words{easter_egg_line}

DO
- Keep POV/tense and SCENE CONTEXT facts invariant.
- Maintain continuity with the previous scene's emotional and dialogue tone.
- Build toward the next scene (subtle foreshadowing, preserve open threads).
- Use distinct character voices, subtext, and concrete action.
- Structure beats implicitly in prose: Objective → Obstacle → Turn → Decision → Button.

DON'T
- No scene headers or lists; output prose only.
- Do not quote or closely paraphrase brainstorm text.
- Do not introduce new named characters or revise canon facts.

TASK
Silently make a brief internal plan, then write ONE continuous, production-ready scene in polished prose that advances stakes and arcs while honoring all locks and continuity. Output the scene text only.
"""
        
        return prompt.strip()
    
    def generate_scene_text(self, prompt: str) -> str:
        """Generate scene text using LightRAG buckets or direct LLM."""
        
        if self.lightrag_instances:
            # Use LightRAG with selected buckets
            try:
                # Pick first available bucket for generation
                bucket_name = list(self.lightrag_instances.keys())[0]
                response = self.lightrag_instances[bucket_name].query(
                    prompt, 
                    param=QueryParam(mode="mix")
                )
                return str(response).strip()
            except Exception as e:
                print(f"  ⚠️  LightRAG generation failed: {e}")
                print("  Falling back to direct LLM...")
        
        # Fallback to direct LLM
        if LIGHTRAG_AVAILABLE:
            try:
                response = gpt_4o_mini_complete(prompt)
                return str(response).strip()
            except Exception as e:
                print(f"  ❌ LLM generation failed: {e}")
                return f"[Error generating scene: {e}]"
        else:
            return "[Scene generation unavailable - LightRAG not installed]"
    
    def save_scene_draft(self, scene: Dict, prompt: str, scene_text: str, version: int = 1):
        """Save scene draft to scene_drafts table."""
        cursor = self.conn.cursor()
        
        # Use existing scene_drafts table from start.py schema
        cursor.execute("""
            INSERT INTO scene_drafts 
            (act, scene, draft_id, draft_text, version, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'draft', CURRENT_TIMESTAMP)
        """, (
            scene['act'], 
            scene['scene'],
            f"write_v{version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            scene_text,
            version
        ))
        
        self.conn.commit()
    
    def save_finalized_scene(self, scene: Dict, scene_text: str):
        """Save finalized scene to finalized_scenes table."""
        cursor = self.conn.cursor()
        
        # Use existing finalized_scenes table from start.py schema
        cursor.execute("""
            INSERT OR REPLACE INTO finalized_scenes
            (act, scene, final_text, notes, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            scene['act'],
            scene['scene'], 
            scene_text,
            f"Generated with {self.writing_style} style, {self.tone} tone"
        ))
        
        self.conn.commit()
    
    def export_full_script(self, scenes: List[Dict], metadata: Dict):
        """Export complete script to text and markdown files."""
        # Get all finalized scenes
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT act, scene, final_text 
            FROM finalized_scenes 
            ORDER BY act, scene
        """)
        
        finalized = cursor.fetchall()
        
        if not finalized:
            print("⚠️  No finalized scenes to export")
            return
        
        # Export to Desktop
        desktop_path = Path.home() / "Desktop"
        if not desktop_path.exists():
            # Fallback to project directory if Desktop doesn't exist
            desktop_path = self.base_dir / self.project_name / "outputs"
            desktop_path.mkdir(exist_ok=True)
        
        # Generate timestamp for version
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title = metadata.get('project_name', self.project_name)
        
        # Create full text
        full_text_parts = []
        for row in finalized:
            act, scene, text = row
            scene_header = f"\\n{'='*60}\\nAct {act}, Scene {scene}\\n{'='*60}\\n"
            full_text_parts.append(scene_header + text)
        
        full_text = "\\n\\n".join(full_text_parts)
        
        # Export text file to Desktop
        txt_file = desktop_path / f"{self.project_name}_full_script_{timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"{title}\\n{'='*len(title)}\\n\\n")
            f.write(full_text)
        
        # Export markdown file with outline to Desktop
        md_file = desktop_path / f"{self.project_name}_script_{timestamp}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\\n\\n")
            
            if metadata.get('genre'):
                f.write(f"**Genre:** {metadata['genre']}\\n\\n")
            
            f.write("## Scenes\\n\\n")
            for scene in scenes:
                if any(row[0] == scene['act'] and row[1] == scene['scene'] for row in finalized):
                    f.write(f"### Act {scene['act']}, Scene {scene['scene']} — {scene.get('scene_title', 'Untitled')}\\n")
                    if scene.get('location') or scene.get('time_of_day'):
                        f.write(f"- **Setting:** {scene.get('location', '')} / {scene.get('time_of_day', '')}\\n")
                    f.write("\\n")
        
        print(f"\\n✅ 📄 Script automatically saved to Desktop:")
        print(f"  Text: {txt_file.name}")
        print(f"  Markdown: {md_file.name}")
        print(f"  Location: {desktop_path}")
    
    def run(self):
        """Main writing workflow."""
        if not self.conn:
            print("❌ No database connection")
            return
        
        # Get project data
        metadata = self.get_project_metadata()
        characters = self.get_characters()
        scenes = self.get_story_outline()
        
        if not scenes:
            print("❌ No scenes found in story outline.")
            print("   Run 'python3 intake.py' first to add scenes.")
            return
        
        # Get brainstorming context
        brainstorm_table = self.get_latest_brainstorm_table()
        if brainstorm_table:
            print(f"📚 Using brainstorming context from: {brainstorm_table}")
        else:
            print("📚 No brainstorming context found (run brainstorm.py first for richer context)")
        
        print(f"\\n🎬 Found {len(scenes)} scenes to write")
        print(f"👥 Using {len(characters)} characters")
        print("=" * 60)
        
        # Process each scene
        scenes_written = 0
        for scene in scenes:
            act, scene_num = scene['act'], scene['scene']
            scene_title = scene.get('scene_title', 'Untitled')
            
            print(f"\\n✍️  Writing Act {act}, Scene {scene_num}: {scene_title}")
            
            # Get brainstorming context for this scene
            brainstorm_context = None
            if brainstorm_table:
                brainstorm_context = self.get_brainstorm_for_scene(brainstorm_table, act, scene_num)
            
            # Get continuity context
            prev_text_raw = self.get_prev_scene_text(act, scene_num)
            prev_text = self.summarize_prev_if_long(prev_text_raw)
            
            outline_snap = self.make_outline_snapshot(scenes, act, scene_num)
            next_desc = self.get_next_scene_outline_desc(act, scene_num)
            
            # Build prompt with full continuity
            prompt = self.build_scene_prompt(
                metadata, characters, scene, brainstorm_context,
                outline_snapshot=outline_snap,
                prev_scene_text=prev_text,
                next_scene_desc=next_desc,
                style_primary=self.writing_style,
                style_secondary=None,
                min_words=700, max_words=900
            )
            
            # Generate scene
            try:
                scene_text = self.generate_scene_text(prompt)
                
                # Save draft
                self.save_scene_draft(scene, prompt, scene_text)
                
                # Save as finalized
                self.save_finalized_scene(scene, scene_text)
                
                scenes_written += 1
                print(f"✅ Act {act}, Scene {scene_num} complete ({len(scene_text)} characters)")
                
            except Exception as e:
                print(f"❌ Error writing Act {act}, Scene {scene_num}: {e}")
        
        # Automatically export complete script to Desktop
        if scenes_written > 0:
            print(f"\\n🎉 Writing session complete!")
            print(f"📊 Wrote {scenes_written} of {len(scenes)} scenes")
            
            # Auto-export to Desktop
            print("\\n📝 Automatically exporting to Desktop...")
            self.export_full_script(scenes, metadata)
        else:
            print("\\n❌ No scenes were successfully written")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    """Entry point for the write module."""
    print("✍️  Lizzy Alpha - Write Module")
    print("=" * 40)
    print("AI-powered scene writing with contextual brainstorming")
    print()
    
    if not LIGHTRAG_AVAILABLE:
        print("⚠️  Warning: LightRAG not available. Some features will be limited.")
        print()
    
    writer = LizzyWrite()
    
    try:
        # Setup workflow
        if not writer.setup_project():
            return
        
        writer.select_buckets()
        writer.configure_writing()
        
        # Run writing process
        print("\\n🚀 Starting writing process...")
        writer.run()
        
    except KeyboardInterrupt:
        print("\\n\\n⏸️  Writing session cancelled.")
    except Exception as e:
        print(f"\\n❌ Error: {e}")
    finally:
        writer.close()
        print("\\n👋 Writing session ended.")


if __name__ == "__main__":
    main()