#!/usr/bin/env python3
"""
Lizzy Alpha - Intake Module
===========================
Interactive story outline and character development tool for romantic comedies.
Creates project database with characters, scenes, and metadata for use by other modules.

Features:
- Project setup and metadata collection
- Character creation with romcom-specific traits
- Scene outline with three-act structure
- Database schema setup for downstream modules
- Export capabilities

Author: Lizzy AI Writing Framework
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

class IntakeAgent:
    def __init__(self, base_dir: str = "projects"):
        self.base_dir = Path(base_dir)
        self.project_name: Optional[str] = None
        self.db_path: Optional[Path] = None
        self.conn: Optional[sqlite3.Connection] = None
        
    def setup_project(self) -> bool:
        """Setup or connect to a project."""
        print("🎬 Lizzy Alpha - Project Setup")
        print("=" * 40)
        
        # Create base directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # List existing projects
        existing_projects = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        if existing_projects:
            print("📂 Existing projects:")
            for project in existing_projects:
                print(f"  - {project}")
            print()
        
        while True:
            project_name = input("Enter project name (new or existing): ").strip()
            if not project_name:
                print("❌ Project name cannot be empty.")
                continue
                
            # Sanitize project name
            safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            
            if safe_name != project_name:
                print(f"📝 Using sanitized name: {safe_name}")
            
            self.project_name = safe_name
            project_dir = self.base_dir / safe_name
            project_dir.mkdir(parents=True, exist_ok=True)
            
            self.db_path = project_dir / f"{safe_name}.sqlite"
            
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.conn.row_factory = sqlite3.Row
                print(f"✅ Connected to project: {safe_name}")
                return True
            except sqlite3.Error as e:
                print(f"❌ Database connection error: {e}")
                return False
    
    def create_schema(self):
        """Create database tables for the project."""
        cursor = self.conn.cursor()
        
        # Project metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Characters
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                role TEXT,
                description TEXT,
                personality_traits TEXT,
                backstory TEXT,
                goals TEXT,
                conflicts TEXT,
                romantic_challenge TEXT,
                lovable_trait TEXT,
                comedic_flaw TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Story outline
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_outline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                act INTEGER NOT NULL,
                scene INTEGER NOT NULL,
                scene_title TEXT,
                location TEXT,
                time_of_day TEXT,
                characters_present TEXT,
                scene_purpose TEXT,
                key_events TEXT,
                key_characters TEXT,
                beat TEXT,
                nudge TEXT,
                emotional_beats TEXT,
                dialogue_notes TEXT,
                plot_threads TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(act, scene)
            )
        """)
        
        # Scene drafts (for writing module)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scene_drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                act INTEGER NOT NULL,
                scene INTEGER NOT NULL,
                draft_id TEXT,
                draft_text TEXT,
                version INTEGER DEFAULT 1,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Finalized scenes (for writing module)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS finalized_scenes (
                act INTEGER NOT NULL,
                scene INTEGER NOT NULL,
                final_text TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (act, scene)
            )
        """)
        
        self.conn.commit()
        print("📝 Database schema created successfully")
    
    def collect_metadata(self):
        """Collect project metadata."""
        print("\n📋 Project Information")
        print("=" * 30)
        
        metadata = {}
        
        # Basic info
        metadata["project_name"] = input("Project title: ").strip() or self.project_name
        metadata["genre"] = input("Genre [default: Romantic Comedy]: ").strip() or "Romantic Comedy"
        metadata["logline"] = input("Logline (one sentence summary): ").strip()
        metadata["theme"] = input("Central theme: ").strip()
        
        # Technical specs
        print("\n🎭 Writing Style")
        metadata["pov"] = self.select_option("Point of view", 
            ["third-person limited", "third-person omniscient", "first-person"], 
            "third-person limited")
        metadata["tense"] = self.select_option("Tense", ["past", "present"], "past")
        
        # Save metadata
        cursor = self.conn.cursor()
        for key, value in metadata.items():
            cursor.execute("""
                INSERT OR REPLACE INTO project_metadata (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
        
        self.conn.commit()
        print("✅ Project metadata saved")
        
    def select_option(self, prompt: str, options: List[str], default: str) -> str:
        """Helper for multiple choice selection."""
        print(f"\n{prompt}:")
        for i, option in enumerate(options, 1):
            marker = " (default)" if option == default else ""
            print(f"  {i}) {option}{marker}")
        
        while True:
            choice = input(f"Select (1-{len(options)}, default {options.index(default)+1}): ").strip()
            if not choice:
                return default
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
            except ValueError:
                pass
            print("❌ Invalid selection. Please try again.")
    
    def create_characters(self):
        """Interactive character creation."""
        print("\n👥 Character Development")
        print("=" * 30)
        print("Let's create the main characters for your romantic comedy.")
        print("Typically you'll want:")
        print("  • Protagonist (lead romantic interest)")
        print("  • Love Interest (other romantic lead)")
        print("  • Best Friend/Confidant")
        print("  • Antagonist or Obstacle character")
        print()
        
        while True:
            self.create_character()
            
            if not self.yes_no("Add another character?", default=True):
                break
        
        print("✅ Character creation complete")
    
    def create_character(self):
        """Create a single character with comprehensive form."""
        print("\n✨ Character Form (Complete All Fields)")
        print("=" * 40)
        
        cursor = self.conn.cursor()
        
        # Check if editing existing character
        cursor.execute("SELECT id, name FROM characters ORDER BY name")
        characters = cursor.fetchall()
        
        char_id = None
        char_data = {}
        
        if characters:
            print("\nExisting characters:")
            for i, char in enumerate(characters, 1):
                print(f"  {i}. {char['name']}")
            print(f"  {len(characters) + 1}. Create new character")
            
            try:
                choice = int(input("\nSelect option: "))
                if 1 <= choice <= len(characters):
                    char_id = characters[choice - 1]['id']
                    cursor.execute("SELECT * FROM characters WHERE id = ?", (char_id,))
                    char_data = dict(cursor.fetchone())
                    print(f"\n📝 Editing: {char_data['name']}")
            except (ValueError, IndexError):
                pass
        
        print("\n" + "=" * 40)
        print("Press Enter to keep existing value (if editing)")
        print("=" * 40 + "\n")
        
        # Comprehensive field collection
        fields = {
            'name': ("Character Name", "Required - The character's full name"),
            'role': ("Role", "protagonist/love_interest/antagonist/mentor/comic_relief/supporting"),
            'description': ("Physical Description", "Appearance, clothing, distinguishing features"),
            'personality_traits': ("Personality Traits", "Key personality characteristics"),
            'backstory': ("Backstory", "Character's history and background"),
            'goals': ("Goals", "What the character wants to achieve"),
            'conflicts': ("Conflicts", "Internal and external conflicts"),
            'romantic_challenge': ("🎭 Romantic Challenge", "Essential Trinity: What prevents them from love?"),
            'lovable_trait': ("💝 Lovable Trait", "Essential Trinity: What makes them endearing?"),
            'comedic_flaw': ("😄 Comedic Flaw", "Essential Trinity: What makes them funny?"),
        }
        
        new_data = {}
        
        for field, (label, help_text) in fields.items():
            print(f"\n{label}:")
            print(f"  ({help_text})")
            
            current = char_data.get(field, '') if char_data else ''
            if current:
                print(f"  Current: {current}")
            
            value = input("  > ").strip()
            
            # For new characters, name is required
            if not char_id and field == 'name' and not value:
                print("❌ Character name is required for new characters.")
                return
            
            if value:  # Only update if value provided
                new_data[field] = value
            elif not char_id and field == 'name':  # New character needs name
                print("❌ Character name is required.")
                return
        
        # Save to database
        try:
            if char_id:  # Update existing
                if new_data:
                    set_clause = ", ".join([f"{field} = ?" for field in new_data.keys()])
                    values = list(new_data.values()) + [char_id]
                    cursor.execute(f"UPDATE characters SET {set_clause} WHERE id = ?", values)
                    self.conn.commit()
                    print(f"\n✅ Updated character: {char_data['name']}")
                else:
                    print("\nNo changes made.")
            else:  # Insert new
                # Check if character name already exists
                cursor.execute("SELECT name FROM characters WHERE name = ?", (new_data.get('name', ''),))
                if cursor.fetchone():
                    print(f"\n❌ Character '{new_data['name']}' already exists.")
                    return
                
                # Prepare insert with all fields
                field_names = list(new_data.keys())
                placeholders = ", ".join(["?" for _ in field_names])
                fields_str = ", ".join(field_names)
                
                cursor.execute(f'''
                    INSERT INTO characters ({fields_str})
                    VALUES ({placeholders})
                ''', list(new_data.values()))
                
                self.conn.commit()
                print(f"\n✅ Added character: {new_data['name']}")
                
        except sqlite3.Error as e:
            print(f"\n❌ Database error: {e}")
    
    def create_outline(self):
        """Interactive scene outline creation with quick setup option."""
        print("\n📖 Story Outline")
        print("=" * 30)
        print("Let's create your three-act structure.")
        print("Typical romantic comedy structure:")
        print("  • Act 1: Setup, meet-cute, initial conflict (25%)")
        print("  • Act 2: Development, obstacles, complications (50%)")  
        print("  • Act 3: Crisis, resolution, happy ending (25%)")
        print()
        
        # Check if quick setup is wanted
        if self.yes_no("Use Quick Three-Act Setup with standard scenes?", default=False):
            self.quick_three_act_setup()
            return
        
        # Get target length
        total_scenes = self.get_number("How many total scenes? [default: 30]: ", 30, 10, 100)
        
        act1_scenes = max(1, int(total_scenes * 0.25))
        act2_scenes = max(1, int(total_scenes * 0.50))  
        act3_scenes = total_scenes - act1_scenes - act2_scenes
        
        print(f"\n📊 Suggested breakdown:")
        print(f"  Act 1: {act1_scenes} scenes")
        print(f"  Act 2: {act2_scenes} scenes")
        print(f"  Act 3: {act3_scenes} scenes")
        
        if self.yes_no("Use this breakdown?", default=True):
            acts = [(1, act1_scenes), (2, act2_scenes), (3, act3_scenes)]
        else:
            acts = []
            for act in [1, 2, 3]:
                count = self.get_number(f"Act {act} scenes: ", 10, 1, 50)
                acts.append((act, count))
        
        # Create scenes for each act
        for act, scene_count in acts:
            print(f"\n🎬 Act {act} Scenes")
            print("-" * 20)
            self.create_act_scenes(act, scene_count)
        
        print("✅ Story outline complete")
    
    def quick_three_act_setup(self):
        """Quick setup for standard three-act structure."""
        print("\n🎭 Quick Three-Act Structure Setup")
        print("This will add basic scene placeholders for a three-act story.")
        
        # Standard three-act structure
        scenes = [
            (1, 1, "Opening Image", "setup"),
            (1, 2, "Inciting Incident", "setup"),
            (1, 3, "Plot Point 1", "setup"),
            (2, 1, "First Obstacle", "conflict"),
            (2, 2, "Midpoint", "conflict"),
            (2, 3, "All Is Lost", "conflict"),
            (2, 4, "Plot Point 2", "conflict"),
            (3, 1, "Climax", "climax"),
            (3, 2, "Resolution", "resolution"),
            (3, 3, "Final Image", "resolution"),
        ]
        
        cursor = self.conn.cursor()
        added_count = 0
        
        for act, scene, title, purpose in scenes:
            # Check if scene already exists
            cursor.execute("SELECT * FROM story_outline WHERE act = ? AND scene = ?", (act, scene))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO story_outline (act, scene, scene_title, scene_purpose)
                    VALUES (?, ?, ?, ?)
                ''', (act, scene, title, purpose))
                added_count += 1
        
        self.conn.commit()
        print(f"✅ Added {added_count} scene placeholders.")
        print("You can now edit each scene to add details.")
    
    def create_act_scenes(self, act: int, scene_count: int):
        """Create scenes for a specific act."""
        for scene_num in range(1, scene_count + 1):
            print(f"\nScene {act}.{scene_num}:")
            
            scene = {
                "act": act,
                "scene": scene_num,
                "scene_title": input("  Scene title: ").strip(),
                "location": input("  Location: ").strip(),
                "time_of_day": input("  Time of day: ").strip(),
                "characters_present": input("  Characters present: ").strip(),
                "scene_purpose": input("  Scene purpose (what it accomplishes): ").strip(),
                "key_events": input("  Key events: ").strip(),
                "emotional_beats": input("  Emotional journey: ").strip(),
                "dialogue_notes": input("  Dialogue notes: ").strip(),
                "plot_threads": input("  Plot threads (setup/payoff): ").strip(),
                "notes": input("  Additional notes: ").strip()
            }
            
            # Add some helpful prompts based on act
            if act == 1:
                scene["beat"] = "Setup/Inciting Incident"
            elif act == 2:
                scene["beat"] = "Complication/Development" 
            else:
                scene["beat"] = "Climax/Resolution"
            
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO story_outline (act, scene, scene_title, location, time_of_day,
                                             characters_present, scene_purpose, key_events,
                                             emotional_beats, dialogue_notes, plot_threads, 
                                             notes, beat)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(scene[key] for key in [
                    "act", "scene", "scene_title", "location", "time_of_day",
                    "characters_present", "scene_purpose", "key_events", 
                    "emotional_beats", "dialogue_notes", "plot_threads",
                    "notes", "beat"
                ]))
                self.conn.commit()
                print(f"  ✅ Scene {act}.{scene_num} saved")
                
            except sqlite3.IntegrityError:
                print(f"  ❌ Scene {act}.{scene_num} already exists")
    
    def yes_no(self, prompt: str, default: bool = True) -> bool:
        """Simple yes/no prompt."""
        suffix = " [Y/n]: " if default else " [y/N]: "
        while True:
            response = input(prompt + suffix).strip().lower()
            if not response:
                return default
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            print("❌ Please enter y/yes or n/no")
    
    def get_number(self, prompt: str, default: int, min_val: int = 1, max_val: int = 999) -> int:
        """Get a number within range."""
        while True:
            response = input(prompt).strip()
            if not response:
                return default
            try:
                num = int(response)
                if min_val <= num <= max_val:
                    return num
                print(f"❌ Please enter a number between {min_val} and {max_val}")
            except ValueError:
                print("❌ Please enter a valid number")
    
    def show_summary(self):
        """Show project summary."""
        print("\n📊 Project Summary")
        print("=" * 30)
        
        # Metadata
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, value FROM project_metadata")
        metadata = dict(cursor.fetchall())
        
        print("📋 Project Info:")
        for key in ["project_name", "genre", "logline", "theme"]:
            value = metadata.get(key, "Not set")
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Characters
        cursor.execute("SELECT name, role FROM characters ORDER BY role, name")
        characters = cursor.fetchall()
        print(f"\n👥 Characters ({len(characters)}):")
        for name, role in characters:
            print(f"  • {name} ({role})")
        
        # Scenes
        cursor.execute("SELECT act, COUNT(*) as scene_count FROM story_outline GROUP BY act ORDER BY act")
        acts = cursor.fetchall()
        total_scenes = sum(count for _, count in acts)
        print(f"\n📖 Story Outline ({total_scenes} scenes):")
        for act, count in acts:
            print(f"  Act {act}: {count} scenes")
    
    def export_summary(self):
        """Export project summary to a text file."""
        if not self.project_name:
            return
        
        desktop = Path.home() / "Desktop"
        if not desktop.exists():
            desktop = self.base_dir
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = desktop / f"{self.project_name}_summary_{timestamp}.txt"
        
        cursor = self.conn.cursor()
        
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(f"PROJECT SUMMARY: {self.project_name.upper()}\n")
            f.write("=" * 50 + "\n\n")
            
            # Metadata
            cursor.execute("SELECT key, value FROM project_metadata")
            metadata = dict(cursor.fetchall())
            
            f.write("PROJECT INFORMATION:\n")
            f.write("-" * 20 + "\n")
            for key in ["project_name", "genre", "logline", "theme", "pov", "tense"]:
                value = metadata.get(key, "Not specified")
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            
            # Characters
            cursor.execute("""
                SELECT name, role, description, personality_traits, backstory, goals, 
                       conflicts, romantic_challenge, lovable_trait, comedic_flaw
                FROM characters ORDER BY role, name
            """)
            characters = cursor.fetchall()
            
            f.write(f"\n\nCHARACTERS ({len(characters)}):\n")
            f.write("-" * 20 + "\n")
            
            for char in characters:
                f.write(f"\n• {char['name']} ({char['role']})\n")
                if char['description']:
                    f.write(f"  Description: {char['description']}\n")
                if char['personality_traits']:
                    f.write(f"  Personality: {char['personality_traits']}\n")
                if char['goals']:
                    f.write(f"  Goals: {char['goals']}\n")
                if char['romantic_challenge']:
                    f.write(f"  Romantic Challenge: {char['romantic_challenge']}\n")
                if char['lovable_trait']:
                    f.write(f"  Lovable Trait: {char['lovable_trait']}\n")
                if char['comedic_flaw']:
                    f.write(f"  Comedy: {char['comedic_flaw']}\n")
            
            # Story outline
            cursor.execute("""
                SELECT act, scene, scene_title, location, time_of_day, characters_present,
                       scene_purpose, key_events, emotional_beats, plot_threads
                FROM story_outline ORDER BY act, scene
            """)
            scenes = cursor.fetchall()
            
            f.write(f"\n\nSTORY OUTLINE ({len(scenes)} scenes):\n")
            f.write("-" * 20 + "\n")
            
            current_act = None
            for scene in scenes:
                if scene['act'] != current_act:
                    current_act = scene['act']
                    f.write(f"\nACT {current_act}:\n")
                
                f.write(f"\nScene {scene['act']}.{scene['scene']}")
                if scene['scene_title']:
                    f.write(f": {scene['scene_title']}")
                f.write("\n")
                
                if scene['location'] or scene['time_of_day']:
                    f.write(f"  Setting: {scene['location']} - {scene['time_of_day']}\n")
                if scene['characters_present']:
                    f.write(f"  Characters: {scene['characters_present']}\n")
                if scene['scene_purpose']:
                    f.write(f"  Purpose: {scene['scene_purpose']}\n")
                if scene['key_events']:
                    f.write(f"  Events: {scene['key_events']}\n")
                if scene['emotional_beats']:
                    f.write(f"  Emotional Journey: {scene['emotional_beats']}\n")
        
        print(f"✅ Project summary exported to: {export_path}")
    
    def run(self):
        """Main workflow."""
        try:
            if not self.setup_project():
                return
            
            self.create_schema()
            
            # Check if project already has content
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM characters")
            char_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM story_outline") 
            scene_count = cursor.fetchone()[0]
            
            if char_count > 0 or scene_count > 0:
                print(f"\n📁 Project already has content:")
                print(f"  Characters: {char_count}")
                print(f"  Scenes: {scene_count}")
                
                if not self.yes_no("Continue editing this project?", default=True):
                    return
            
            # Main workflow
            print("\n🚀 Starting intake process...")
            
            self.collect_metadata()
            
            if char_count == 0:
                self.create_characters()
            elif self.yes_no("Add/edit characters?", default=False):
                self.create_characters()
            
            if scene_count == 0:
                self.create_outline()
            elif self.yes_no("Add/edit scenes?", default=False):
                self.create_outline()
            
            # Summary and export
            self.show_summary()
            
            if self.yes_no("Export project summary?", default=True):
                self.export_summary()
            
            print(f"\n🎉 Project '{self.project_name}' is ready!")
            print("Next steps:")
            print("  • Run 'python3 brainstorm.py' to generate creative ideas")
            print("  • Run 'python3 write.py' to write your scenes")
            
        except KeyboardInterrupt:
            print("\n\n⏸️  Intake cancelled.")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.conn:
                self.conn.close()
            print("\n👋 Intake session ended.")

def main():
    """Entry point."""
    print("🎬 Lizzy Alpha - Intake Module")
    print("=" * 40)
    print("Interactive story development for romantic comedies")
    print()
    
    agent = IntakeAgent()
    agent.run()

if __name__ == "__main__":
    main()