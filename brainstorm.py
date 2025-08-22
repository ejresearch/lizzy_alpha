#!/usr/bin/env python3
"""
Lizzy Alpha - Brainstorm Module
================================
Generates creative ideas and thematic content for each scene using LightRAG.
Queries multiple knowledge buckets to provide diverse perspectives.

Author: Lizzy AI Writing Framework
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime

# Import LightRAG and its query parameters
try:
    from lightrag import LightRAG, QueryParam
except ImportError:
    print("⚠️  LightRAG not installed. Install with: pip install lightrag")
    print("   This module requires LightRAG for AI-powered brainstorming.")
    exit(1)


# Define the golden era romcom tone for all brainstorming
GOLDEN_ERA_ROMCOM_TONE = """You are brainstorming a romantic comedy that will revive the golden era of the genre—think When Harry Met Sally, You've Got Mail, Pretty Woman, Sleepless in Seattle, and Notting Hill. 

This means crafting scenes with:
• **Genuine emotional stakes** - Characters we deeply care about facing real vulnerabilities, not just manufactured obstacles
• **Witty, quotable dialogue** - Sharp, intelligent banter that reveals character while advancing the story, not just filler jokes
• **Earned romantic moments** - Chemistry that builds through meaningful interaction, not just physical attraction or coincidence
• **Universal yet specific conflicts** - Problems that feel both deeply personal and widely relatable (career vs. love, timing, class differences, emotional baggage)
• **The "why them?" factor** - Clear reasons why THESE TWO PEOPLE specifically need each other to become their best selves
• **Memorable set pieces** - Iconic scenes that become cultural touchstones (the deli scene, the Empire State Building, the bookshop)
• **Heart over hijinks** - Comedy arising from character truth and situation, not slapstick or embarrassment
• **The yearning** - That delicious tension where the audience desperately wants them together but understands exactly why they're apart

Avoid modern romcom pitfalls: manufactured misunderstandings that could be solved with one conversation, protagonists who are horrible to each other, comedy based on humiliation, or relationships with no foundation beyond "hot people in proximity."

Instead, create something audiences will rewatch for decades—where every scene either deepens character, advances the relationship, or ideally both. Make us laugh, make us cry, make us believe in love again."""


class BrainstormingAgent:
    """
    The Brainstorming Agent generates creative content for each scene
    by querying different LightRAG knowledge buckets.
    """
    
    def __init__(self, lightrag_instances=None, base_dir="projects"):
        """
        Initialize the BrainstormingAgent.
        
        Args:
            lightrag_instances: Dictionary mapping bucket names to LightRAG instances
            base_dir: Directory containing project folders
        """
        self.lightrag = lightrag_instances or {}
        self.base_dir = Path(base_dir)
        self.project_name = None
        self.db_path = None
        self.conn = None
        self.easter_egg = ""
        self.table_name = None
        
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
    
    
    def input_easter_egg(self):
        """Optional creative twist or constraint for the brainstorming."""
        print("\n✨ Easter Egg (Optional Creative Twist)")
        print("  Add a unique element, constraint, or theme to weave through all scenes")
        print("  Examples: 'includes a running gag about coffee', 'set during a heatwave'")
        print("  Press Enter to skip")
        
        idea = input("\n  > ").strip()
        self.easter_egg = idea
        
        if idea:
            print(f"✅ Easter egg added: {idea}")
    
    def get_next_table_name(self):
        """Find the next available version number for brainstorming log table."""
        cursor = self.conn.cursor()
        
        # Look for existing versioned tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'brainstorming_log_v%'
        """)
        tables = cursor.fetchall()
        
        # Extract version numbers
        versions = []
        for table in tables:
            name = table['name']
            if '_v' in name:
                try:
                    version = int(name.split('_v')[-1])
                    versions.append(version)
                except ValueError:
                    continue
        
        # Determine next version
        next_version = max(versions) + 1 if versions else 1
        return f"brainstorming_log_v{next_version}"
    
    def setup_table(self):
        """Create a new versioned table for this brainstorming session."""
        self.table_name = self.get_next_table_name()
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                act INTEGER NOT NULL,
                scene INTEGER NOT NULL,
                scene_description TEXT NOT NULL,
                bucket_name TEXT NOT NULL,
                response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Also record this session in the main brainstorming_sessions table
        cursor.execute("""
            INSERT INTO brainstorming_sessions 
            (session_name, prompt, tone_preset, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            f"Session {self.table_name}",
            self.easter_egg or "No easter egg",
            "golden-era-romcom"
        ))
        
        self.conn.commit()
        print(f"📝 Created brainstorming table: {self.table_name}")
    
    def fetch_all_scenes(self):
        """Fetch all scenes from story_outline table and synthesize descriptions."""
        cursor = self.conn.cursor()
        
        # Get all scenes with their details
        cursor.execute("""
            SELECT act, scene, scene_title, location, time_of_day,
                   characters_present, scene_purpose, key_events,
                   emotional_beats, dialogue_notes, plot_threads
            FROM story_outline 
            ORDER BY act, scene
        """)
        
        scenes = []
        for row in cursor.fetchall():
            # Synthesize a scene description from available fields
            description_parts = []
            
            if row['scene_title']:
                description_parts.append(f"Title: {row['scene_title']}")
            
            if row['location']:
                description_parts.append(f"Location: {row['location']}")
                
            if row['time_of_day']:
                description_parts.append(f"Time: {row['time_of_day']}")
            
            if row['characters_present']:
                description_parts.append(f"Characters: {row['characters_present']}")
            
            if row['scene_purpose']:
                description_parts.append(f"Purpose: {row['scene_purpose']}")
            
            if row['key_events']:
                description_parts.append(f"Key Events: {row['key_events']}")
            
            if row['emotional_beats']:
                description_parts.append(f"Emotional Beats: {row['emotional_beats']}")
            
            if row['dialogue_notes']:
                description_parts.append(f"Dialogue Notes: {row['dialogue_notes']}")
            
            if row['plot_threads']:
                description_parts.append(f"Plot Threads: {row['plot_threads']}")
            
            # Only include scenes that have some content
            if description_parts:
                description = "\n".join(description_parts)
                scenes.append((row['act'], row['scene'], description))
        
        return scenes
    
    def create_prompt(self, bucket_name, scene_description):
        """Generate a tailored prompt for each bucket and scene."""
        # Start with the golden era romcom tone
        intro = GOLDEN_ERA_ROMCOM_TONE
        
        # Add easter egg if provided
        if self.easter_egg:
            intro += f"\n\n🎁 Writer twist: {self.easter_egg}"
        
        # Define bucket-specific expertise
        bucket_guidance = {
            "books": """
You are an expert on screenwriting theory, drawing from acclaimed screenwriting books.
Provide insights on **structure, pacing, and character arcs**.
Explain **scene progression within a three-act structure** based on established principles.
Consider how this scene serves the overall narrative architecture.
Reference relevant storytelling frameworks and techniques.""",
            
            "scripts": """
You are an expert in romantic comedy screenplays, knowledgeable of the top 100 romcom scripts.
Compare this scene to **moments from successful romcoms**.
Suggest effective use of **romcom tropes** with a focus on dialogue, humor, and pacing.
Identify opportunities for comedic beats, romantic tension, and character chemistry.
Draw parallels to iconic scenes that achieved similar narrative goals.""",
            
            "plays": """
You are an expert in Shakespearean drama and comedy, deeply familiar with Shakespeare's complete works.
Analyze the scene through a **Shakespearean lens**, focusing on **character dynamics, irony, heightened language, and themes**.
Consider how dramatic irony, soliloquies, or asides might enhance the scene.
Explore universal themes and the interplay between comedy and tragedy.
Suggest how elevated language could intensify emotional moments."""
        }
        
        # Get the expertise for this bucket
        expertise = bucket_guidance.get(bucket_name, "Provide creative insights for this scene.")
        
        # Construct the full prompt
        return f"""
{intro}

### Scene Description:
{scene_description}

### Task:
{expertise.strip()}

Please provide specific, actionable suggestions for this scene.
"""
    
    def query_bucket(self, bucket_name, prompt):
        """Query a specific LightRAG bucket with the prompt."""
        if bucket_name not in self.lightrag:
            return f"Bucket '{bucket_name}' not configured."
        
        try:
            print(f"  🔍 Querying {bucket_name} bucket...")
            response = self.lightrag[bucket_name].query(
                prompt, 
                param=QueryParam(mode="mix")
            )
            return response
        except Exception as e:
            print(f"  ❌ Error querying {bucket_name}: {e}")
            return f"Error querying {bucket_name}: {str(e)}"
    
    def save_response(self, act, scene, description, bucket_name, response):
        """Save the brainstorming response to the database."""
        cursor = self.conn.cursor()
        
        cursor.execute(f"""
            INSERT INTO {self.table_name}
            (act, scene, scene_description, bucket_name, response)
            VALUES (?, ?, ?, ?, ?)
        """, (act, scene, description, bucket_name, response))
        
        self.conn.commit()
    
    def run(self):
        """Main workflow: process each scene through all buckets."""
        scenes = self.fetch_all_scenes()
        
        if not scenes:
            print("❌ No scenes found in story outline.")
            print("   Run 'python3 intake.py' first to add scenes.")
            return
        
        print(f"\n📚 Found {len(scenes)} scenes to brainstorm")
        print(f"🎯 Will query {len(self.lightrag)} knowledge buckets per scene")
        print("=" * 60)
        
        # Process each scene
        for act, scene_num, description in scenes:
            print(f"\n🎬 Act {act}, Scene {scene_num}")
            print("-" * 40)
            
            # Query each bucket for this scene
            for bucket_name in self.lightrag.keys():
                # Create tailored prompt
                prompt = self.create_prompt(bucket_name, description)
                
                # Query the bucket
                response = self.query_bucket(bucket_name, prompt)
                
                # Save to database
                self.save_response(act, scene_num, description, bucket_name, response)
                
                # Display the result
                print(f"\n🧠 Brainstorm ({bucket_name.capitalize()}):")
                print(response[:500] + "..." if len(response) > 500 else response)
                print()
        
        print("\n" + "=" * 60)
        print(f"✅ Brainstorming complete!")
        print(f"📊 Generated {len(scenes) * len(self.lightrag)} creative responses")
        print(f"💾 Saved to table: {self.table_name}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def initialize_lightrag_buckets():
    """Initialize LightRAG instances for each knowledge bucket."""
    buckets = {}
    
    # Define bucket configurations
    bucket_configs = {
        "books": "./lightrag_working_dir/books",
        "scripts": "./lightrag_working_dir/scripts", 
        "plays": "./lightrag_working_dir/plays"
    }
    
    print("🔧 Initializing LightRAG buckets...")
    
    for bucket_name, working_dir in bucket_configs.items():
        try:
            # Create directory if it doesn't exist
            Path(working_dir).mkdir(parents=True, exist_ok=True)
            
            # Initialize LightRAG instance
            buckets[bucket_name] = LightRAG(working_dir=working_dir)
            print(f"  ✅ {bucket_name}: {working_dir}")
            
        except Exception as e:
            print(f"  ⚠️  {bucket_name}: Failed to initialize - {e}")
            print(f"      The {bucket_name} bucket will be skipped during brainstorming.")
    
    if not buckets:
        print("\n❌ No LightRAG buckets could be initialized.")
        print("   Please check your LightRAG installation and configuration.")
        return None
    
    return buckets


def main():
    """Entry point for the brainstorming module."""
    print("🧠 Lizzy Alpha - Brainstorm Module")
    print("=" * 40)
    print("AI-powered creative brainstorming for your scenes")
    print()
    
    # Initialize LightRAG buckets
    lightrag_instances = initialize_lightrag_buckets()
    
    if not lightrag_instances:
        print("Cannot proceed without LightRAG buckets.")
        return
    
    print()
    
    # Create brainstorming agent
    agent = BrainstormingAgent(lightrag_instances)
    
    try:
        # Setup workflow
        if not agent.setup_project():
            return
        
        agent.input_easter_egg()
        agent.setup_table()
        
        # Run brainstorming
        print("\n🚀 Starting brainstorming process...")
        agent.run()
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Brainstorming cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        agent.close()
        print("\n👋 Brainstorming session ended.")


if __name__ == "__main__":
    main()