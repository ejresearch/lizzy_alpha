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
        """Initialize SQLite database with comprehensive schema for writing projects."""
        print("🗄️  Setting up project database...")
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Project metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Characters table - core story elements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    role TEXT,  -- protagonist, antagonist, supporting, etc.
                    gender TEXT,
                    age INTEGER,
                    description TEXT,
                    personality_traits TEXT,
                    backstory TEXT,
                    goals TEXT,
                    conflicts TEXT,
                    arc TEXT,  -- character development arc
                    romantic_challenge TEXT,  -- from legacy Miranda system
                    lovable_trait TEXT,       -- from legacy Miranda system  
                    comedic_flaw TEXT,        -- from legacy Miranda system
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Story structure/outline table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS story_outline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    act INTEGER NOT NULL,
                    scene INTEGER NOT NULL,
                    scene_title TEXT,
                    location TEXT,
                    time_of_day TEXT,
                    characters_present TEXT,  -- JSON or comma-separated
                    scene_purpose TEXT,  -- setup, conflict, resolution, etc.
                    key_events TEXT,
                    key_characters TEXT,  -- from legacy systems
                    beat TEXT,            -- from legacy Lizzy system
                    nudge TEXT,           -- from legacy Lizzy system
                    emotional_beats TEXT,
                    dialogue_notes TEXT,
                    plot_threads TEXT,  -- subplots being advanced
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(act, scene)
                )
            ''')
            
            # World-building/setting table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS world_building (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,  -- location, culture, rules, history, etc.
                    name TEXT NOT NULL,
                    description TEXT,
                    importance TEXT,  -- major, minor, background
                    related_characters TEXT,
                    related_scenes TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Brainstorming sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS brainstorming_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT,
                    prompt TEXT,
                    context_buckets TEXT,  -- LightRAG buckets used
                    tone_preset TEXT,
                    ai_response TEXT,
                    user_notes TEXT,
                    quality_rating INTEGER,  -- 1-5 scale
                    used_in_draft BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Ideas and inspiration table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ideas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,  -- dialogue, scene, character, plot, theme, etc.
                    title TEXT,
                    content TEXT,
                    source TEXT,  -- brainstorming, research, inspiration, etc.
                    tags TEXT,  -- searchable keywords
                    priority TEXT,  -- high, medium, low
                    status TEXT,  -- new, in_progress, used, discarded
                    related_elements TEXT,  -- links to characters, scenes, etc.
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Draft versions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS drafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL,
                    title TEXT,
                    content TEXT,
                    word_count INTEGER,
                    summary TEXT,
                    completion_status TEXT,  -- outline, first_draft, revision, final
                    notes TEXT,
                    brainstorm_session_ids TEXT,  -- references to brainstorming used
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Research and reference materials
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS research (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,  -- genre_conventions, historical_facts, technical_details, etc.
                    topic TEXT,
                    source TEXT,
                    content TEXT,
                    relevance TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Legacy-compatible scene drafts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scene_drafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    act INTEGER NOT NULL,
                    scene INTEGER NOT NULL,
                    draft_id INTEGER,  -- for legacy compatibility
                    draft_text TEXT,
                    feedback TEXT,
                    version INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Legacy-compatible finalized scenes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS finalized_scenes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    act INTEGER NOT NULL,
                    scene INTEGER NOT NULL,
                    final_text TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(act, scene)
                )
            ''')
            
            # Legacy brainstorming log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS brainstorming_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    user_response TEXT NOT NULL,
                    act INTEGER,
                    scene INTEGER,
                    bucket_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Legacy brainstorming synthesis
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS brainstorming_synthesis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    user_response TEXT NOT NULL,
                    synthesis TEXT NOT NULL,
                    act INTEGER,
                    scene INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Writing goals and progress tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progress_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT CURRENT_DATE,
                    words_written INTEGER DEFAULT 0,
                    scenes_completed INTEGER DEFAULT 0,
                    characters_developed INTEGER DEFAULT 0,
                    goals_met TEXT,
                    challenges_faced TEXT,
                    next_session_plan TEXT,
                    mood_rating INTEGER,  -- 1-5 scale
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert initial project metadata
            cursor.execute('''
                INSERT OR REPLACE INTO project_metadata (key, value, updated_at)
                VALUES ('project_name', ?, CURRENT_TIMESTAMP)
            ''', (self.project_name,))
            
            cursor.execute('''
                INSERT OR REPLACE INTO project_metadata (key, value, updated_at)
                VALUES ('created_date', ?, CURRENT_TIMESTAMP)
            ''', (datetime.now().isoformat(),))
            
            cursor.execute('''
                INSERT OR REPLACE INTO project_metadata (key, value, updated_at)
                VALUES ('lizzy_version', ?, CURRENT_TIMESTAMP)
            ''', ('alpha_1.0',))
            
            # Create useful indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_story_outline_act_scene ON story_outline(act, scene)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_brainstorming_sessions_date ON brainstorming_sessions(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ideas_category ON ideas(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_drafts_version ON drafts(version)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scene_drafts_act_scene ON scene_drafts(act, scene)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_brainstorming_log_act_scene ON brainstorming_log(act, scene)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_finalized_scenes_act_scene ON finalized_scenes(act, scene)')
            
            self.conn.commit()
            print("✅ Database schema initialized successfully")
            
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise
    
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
        
        cursor.execute('SELECT COUNT(*) FROM drafts')
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
        start_module.db_path = project_dir / f"{sanitized_name}.db"
        
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