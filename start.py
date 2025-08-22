#!/usr/bin/env python3
"""
Lizzy Alpha - Start Module
=========================
Initializes new writing projects with proper database schema.
This module establishes the foundation for all subsequent creative work.

Author: Lizzy AI Writing Framework
"""

import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


class LizzyStart:
    """
    The Start module initializes writing projects with isolated SQLite databases.
    Creates the foundation for the entire Lizzy AI-assisted writing workflow.
    """
    
    def __init__(self, base_dir="projects"):
        self.base_dir = Path(base_dir)
        self.project_name = None
        self.db_path = None
        self.conn = None
        
        # Ensure base directory exists
        self.base_dir.mkdir(exist_ok=True)
    
    def run(self):
        """Main entry point for the Start module."""
        print("🚀 Lizzy Alpha - Start Module")
        print("=" * 40)
        print("Initializing your writing project with AI-powered workflow")
        print()
        
        try:
            self.setup_project()
            self.setup_database()
            print(f"✅ Project '{self.project_name}' is ready!")
            print(f"📁 Database: {self.db_path}")
            print()
            print("Next Steps:")
            print("  1. Run: python3 intake.py    # Add characters and story elements")
            print("  2. Run: python3 brainstorm.py # Generate creative ideas")
            print("  3. Run: python3 write.py     # Create your draft")
            
        except KeyboardInterrupt:
            print("\n\n⏸️  Project setup cancelled.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
        finally:
            if self.conn:
                self.conn.close()
    
    def setup_project(self):
        """Handle project selection/creation with user interaction."""
        print("📂 Available Projects:")
        projects = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        
        if projects:
            for i, project in enumerate(projects, 1):
                print(f"  {i}. {project}")
        else:
            print("  (No existing projects)")
        
        print()
        
        while True:
            project_name = input("Enter project name (or create new): ").strip()
            
            if not project_name:
                print("❌ Project name cannot be empty.")
                continue
                
            # Sanitize project name
            project_name = "".join(c for c in project_name if c.isalnum() or c in "._- ").strip()
            project_name = project_name.replace(" ", "_")
            
            if not project_name:
                print("❌ Invalid project name. Use letters, numbers, spaces, hyphens, or underscores.")
                continue
            
            self.project_name = project_name
            project_dir = self.base_dir / self.project_name
            self.db_path = project_dir / f"{self.project_name}.sqlite"
            
            if project_name in projects:
                print(f"📝 Opening existing project: {project_name}")
                break
            else:
                create = input(f"'{project_name}' doesn't exist. Create it? (y/N): ").strip().lower()
                if create in ['y', 'yes']:
                    project_dir.mkdir(exist_ok=True)
                    print(f"✨ Created new project: {project_name}")
                    break
                else:
                    continue
    
    def setup_database(self):
        """Initialize ONLY the tables needed by brainstorm.py and write.py."""
        print("🗄️  Setting up project database...")

        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")

            # 1) Project metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2) Characters (only fields write.py reads)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    role TEXT,
                    description TEXT,
                    personality_traits TEXT,
                    backstory TEXT,
                    goals TEXT,
                    conflicts TEXT,
                    romantic_challenge TEXT,
                    lovable_trait TEXT,
                    comedic_flaw TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3) Story outline (expanded for 30-scene structure)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS story_outline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    act INTEGER NOT NULL,
                    scene INTEGER NOT NULL,
                    beat TEXT,
                    scene_title TEXT,
                    location TEXT,
                    time_of_day TEXT,
                    characters_present TEXT,
                    scene_purpose TEXT,
                    key_events TEXT,
                    key_characters TEXT,
                    nudge TEXT,
                    emotional_beats TEXT,
                    dialogue_notes TEXT,
                    plot_threads TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(act, scene)
                )
            """)

            # 4) Brainstorming sessions (minimal columns actually written)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS brainstorming_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT,
                    prompt TEXT,
                    tone_preset TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 5) Scene drafts (draft_id must be TEXT to match write.py)
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

            # 6) Finalized scenes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finalized_scenes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    act INTEGER NOT NULL,
                    scene INTEGER NOT NULL,
                    final_text TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(act, scene)
                )
            """)

            # Minimal indexes used by access patterns
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_story_outline_act_scene ON story_outline(act, scene)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scene_drafts_act_scene ON scene_drafts(act, scene)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_finalized_scenes_act_scene ON finalized_scenes(act, scene)")

            # Seed metadata
            cursor.execute("""
                INSERT OR REPLACE INTO project_metadata (key, value, updated_at)
                VALUES ('project_name', ?, CURRENT_TIMESTAMP)
            """, (self.project_name,))

            cursor.execute("""
                INSERT OR REPLACE INTO project_metadata (key, value, updated_at)
                VALUES ('created_date', ?, CURRENT_TIMESTAMP)
            """, (datetime.now().isoformat(),))

            cursor.execute("""
                INSERT OR REPLACE INTO project_metadata (key, value, updated_at)
                VALUES ('lizzy_version', ?, CURRENT_TIMESTAMP)
            """, ('alpha_1.0',))

            self.conn.commit()
            print("✅ Database schema initialized successfully")
            
            # Populate 30-scene professional structure
            self.populate_30_scene_template(cursor)

        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise
    
    def populate_30_scene_template(self, cursor):
        """Populate the story_outline table with the professional 30-scene structure."""
        print("📝 Populating 30-scene professional template...")
        
        # Complete 30-scene romantic comedy structure from professional template
        template_scenes = [
            # Act 1 (12 scenes)
            (1, 1, "Opening Image", "Chemical Equation", "Establish the world and protagonist starting point"),
            (1, 2, "Theme Stated", "Emotional Baseline", "Introduce the theme through dialogue or action"),
            (1, 3, "Set-Up", "Meet Cute", "The moment when romantic leads first encounter each other"),
            (1, 4, "Set-Up", "Meet Cute", "Initial romantic spark that creates future romantic momentum"),
            (1, 5, "Catalyst", "Stacsis", "Show the characters need to leave their normal routines"),
            (1, 6, "Catalyst", "Get Out", "Show an event that disrupts the normal routines"),
            (1, 7, "Debate", "Romantic Complication", "Why they can't and won't fall for each other (or legendary)"),
            (1, 8, "Debate", "Romantic Complication", "One of the main characters denies their feelings (legendary)"),
            (1, 9, "Break Into Two", "Best Bet", "Dramatic pressure at deadline (imminent)"),
            (1, 10, "Break Into Two", "Best Bet", "The most obvious solution to the deadline (imminent)"),
            (1, 11, "B Story", "Complication/Tension Rise", "Second lead's reveal (in romantic comedies imminent)"),
            (1, 12, "B Story", "First Revelation", "Characters begin seeing how things (love actually) work"),
            
            # Act 2 (12 scenes)  
            (2, 13, "Fun & Games / Falling in", "Messages or series of bonding moments", "Main characters learning about their charged past things"),
            (2, 14, "Fun & Games / Falling in", "Subplot Hero", "Subplot characters learn about bonding moments"),
            (2, 15, "Fun & Games / Falling in", "Magicful Heart", "The sense of connection or about their charged and thing"),
            (2, 16, "Fun & Games / Falling in", "Magicful Heart", "Making realizations or about their charged and thing"),
            (2, 17, "Midpoint/Romantic Turning Rise", "Relationship Pause Day", "Obvious realizations or relationship appears destined"),
            (2, 18, "Midpoint/Romantic Turning Rise", "Extraordinary Turning Rise", "Characters being about their feelings - false"),
            (2, 19, "Lost Soul", "Lost Soul", "All seems lost - the relationship appears doomed"),
            (2, 20, "Lost Soul", "Lost Soul", "A misstatement - about their charged and thing (internal)"),
            (2, 21, "Self-Revelation", "Self-Revelation", "Confronting an awful moment (or hero's worst things)"),
            (2, 22, "Self-Revelation", "Self-Revelation", "New understanding of love and what charged message"),
            (2, 23, "Psychological Turning Rise", "Fun", "Putting the new understanding (or love) into theory"),
            (2, 24, "Break into Three", "Extraordinary Turning Rise", "New understanding of love and what charged message"),
            
            # Act 3 (6 scenes)
            (3, 25, "Finale", "Climatic Interaction", "The characters seem back together destined"),
            (3, 26, "Finale", "New High, New Higher, New High", "New challenging information or series about destined"),
            (3, 27, "Finale", "Proof & Revelation", "The breakthrough romantic scene that paid changed"),
            (3, 28, "Finale", "Proof & Revelation", "Confronting romantic issue that they paid charged"),
            (3, 29, "Final Image", "Final Chemical Equation", "Any ending note - image, line, hit text book charged"),
            (3, 30, "Final Image", "Final Chemical Equation", "The final note closing out what we've about/witnessed")
        ]
        
        for act, scene, beat, scene_title, description in template_scenes:
            cursor.execute("""
                INSERT OR REPLACE INTO story_outline 
                (act, scene, beat, scene_title, scene_purpose, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (act, scene, beat, scene_title, description, "Professional 30-scene template"))
        
        print("✅ 30-scene template populated successfully")
    
    def get_project_info(self):
        """Return basic project information."""
        if not self.conn:
            return None
            
        cursor = self.conn.cursor()
        cursor.execute('SELECT key, value FROM project_metadata')
        metadata = dict(cursor.fetchall())
        
        cursor.execute('SELECT COUNT(*) FROM characters')
        char_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM story_outline')
        scene_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM brainstorming_sessions')
        brainstorm_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM scene_drafts')
        draft_count = cursor.fetchone()[0]
        
        return {
            'metadata': metadata,
            'characters': char_count,
            'scenes': scene_count,
            'brainstorm_sessions': brainstorm_count,
            'drafts': draft_count
        }


def create_new_project(project_name, title=None, genre="Romance", tone="Romantic Comedy"):
    """
    Programmatic function to create a new project for API use.
    
    Args:
        project_name (str): The project directory name
        title (str): Human-readable project title
        genre (str): Project genre
        tone (str): Project tone/style
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Sanitize project name
        sanitized_name = "".join(c for c in project_name if c.isalnum() or c in "._- ").strip()
        sanitized_name = sanitized_name.replace(" ", "_")
        
        if not sanitized_name:
            raise ValueError("Invalid project name")
        
        # Create start module instance
        start_module = LizzyStart()
        start_module.project_name = sanitized_name
        
        # Create project directory
        project_dir = start_module.base_dir / sanitized_name
        project_dir.mkdir(exist_ok=True)
        
        # Set database path
        start_module.db_path = project_dir / f"{sanitized_name}.sqlite"
        
        # Initialize database
        start_module.setup_database()
        
        # Add additional metadata
        if start_module.conn:
            cursor = start_module.conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO project_metadata (key, value, updated_at)
                VALUES ('title', ?, CURRENT_TIMESTAMP)
            ''', (title or project_name,))
            
            cursor.execute('''
                INSERT OR REPLACE INTO project_metadata (key, value, updated_at)
                VALUES ('genre', ?, CURRENT_TIMESTAMP)
            ''', (genre,))
            
            cursor.execute('''
                INSERT OR REPLACE INTO project_metadata (key, value, updated_at)
                VALUES ('tone', ?, CURRENT_TIMESTAMP)
            ''', (tone,))
            
            start_module.conn.commit()
            start_module.conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error creating project: {e}")
        return False


def main():
    """Entry point when running as a script."""
    start_module = LizzyStart()
    start_module.run()


if __name__ == "__main__":
    main()