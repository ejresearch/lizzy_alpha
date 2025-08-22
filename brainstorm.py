#!/usr/bin/env python3
"""
Lizzy Alpha - Brainstorm Module
===============================
Generates creative ideas and thematic content using LightRAG knowledge retrieval.
Utilizes tone presets and contextual source materials for rich creative ideation.

Author: Lizzy AI Writing Framework
"""

import os
import sqlite3
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm import openai_complete_if_cache, openai_embedding
    LIGHTRAG_AVAILABLE = True
except ImportError:
    print("⚠️  LightRAG not available. Some features will be limited.")
    LIGHTRAG_AVAILABLE = False


class LizzyBrainstorm:
    """
    The Brainstorm module generates creative ideas using AI and knowledge retrieval.
    Integrates project context with external knowledge sources for rich inspiration.
    """
    
    def __init__(self, base_dir="projects", knowledge_dir="lightrag_working_dir"):
        self.base_dir = Path(base_dir)
        self.knowledge_dir = Path(knowledge_dir)
        self.project_name = None
        self.db_path = None
        self.conn = None
        self.lightrag_instances = {}
        
        # Tone presets for different writing styles
        self.tone_presets = {
            "1": {
                "name": "Romantic Comedy",
                "description": "Light, humorous, with romantic tension and witty dialogue",
                "style": "upbeat, charming, with comedic mishaps and romantic misunderstandings"
            },
            "2": {
                "name": "Dramatic Romance", 
                "description": "Emotionally rich, serious romantic themes with depth",
                "style": "emotionally resonant, character-driven, with meaningful conflicts"
            },
            "3": {
                "name": "Literary Fiction",
                "description": "Character-focused, literary style with thematic depth",
                "style": "thoughtful, nuanced, with rich character development and themes"
            },
            "4": {
                "name": "Thriller/Suspense",
                "description": "Fast-paced, tension-filled, with mystery elements",
                "style": "suspenseful, action-oriented, with plot twists and urgency"
            },
            "5": {
                "name": "Fantasy/Sci-Fi",
                "description": "Imaginative world-building with fantastical elements",
                "style": "creative, world-building focused, with unique concepts and magic/tech"
            },
            "6": {
                "name": "Historical Fiction",
                "description": "Period-appropriate, historically grounded narrative",
                "style": "authentic to period, research-based, with historical context"
            }
        }
    
    def run(self):
        """Main entry point for the Brainstorm module."""
        print("💡 Lizzy Alpha - Brainstorm Module")
        print("=" * 40)
        print("AI-powered creative ideation with contextual knowledge")
        print()
        
        try:
            self.select_project()
            self.connect_database()
            self.initialize_knowledge_base()
            self.main_menu()
            
        except KeyboardInterrupt:
            print("\\n\\n⏸️  Brainstorming session cancelled.")
            sys.exit(0)
        except Exception as e:
            print(f"\\n❌ Error: {e}")
            sys.exit(1)
        finally:
            if self.conn:
                self.conn.close()
    
    def select_project(self):
        """Select an existing project to brainstorm for."""
        print("📂 Available Projects:")
        projects = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        
        if not projects:
            print("❌ No projects found. Run 'python3 start.py' first to create a project.")
            sys.exit(1)
        
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project}")
        
        print()
        
        while True:
            choice = input("Enter project name: ").strip()
            
            if choice in projects:
                self.project_name = choice
                self.db_path = self.base_dir / self.project_name / f"{self.project_name}.sqlite"
                
                if not self.db_path.exists():
                    print(f"❌ Database not found for project '{choice}'. Run 'python3 start.py' first.")
                    continue
                    
                print(f"🎯 Brainstorming for project: {choice}")
                break
            else:
                print("❌ Project not found. Please enter a valid project name.")
    
    def connect_database(self):
        """Connect to the project database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            print("✅ Connected to project database")
        except sqlite3.Error as e:
            print(f"❌ Database connection error: {e}")
            raise
    
    def initialize_knowledge_base(self):
        """Initialize LightRAG knowledge base instances."""
        if not LIGHTRAG_AVAILABLE:
            print("⚠️  Knowledge base features disabled (LightRAG not available)")
            return
        
        print("🧠 Initializing knowledge base...")
        
        # Use the local LightRAG knowledge buckets
        main_knowledge_dir = self.knowledge_dir
        
        if not main_knowledge_dir.exists():
            print("⚠️  Knowledge directory not found. Using limited mode.")
            return
        
        # Get available knowledge buckets from directory structure
        bucket_dirs = [d for d in main_knowledge_dir.iterdir() 
                      if d.is_dir() and not d.name.startswith('.') and not d.name.startswith('_')]
        
        # Filter out non-bucket directories and check for required files
        valid_buckets = []
        for d in bucket_dirs:
            if d.name in ['books', 'plays', 'scripts']:
                # Check if bucket has required LightRAG files
                required_files = ['vdb_entities.json', 'vdb_relationships.json']
                has_all_files = all((d / f).exists() for f in required_files)
                if has_all_files:
                    valid_buckets.append(d)
                else:
                    print(f"  ⚠️  Skipping {d.name}: Missing required files")
        
        bucket_dirs = valid_buckets
        
        print(f"Found {len(bucket_dirs)} knowledge buckets:")
        for bucket in bucket_dirs:
            print(f"  • {bucket.name}")
        
        # Initialize LightRAG instances for each bucket
        for bucket_dir in bucket_dirs:
            try:
                rag = LightRAG(
                    working_dir=str(bucket_dir),
                    llm_model_func=openai_complete_if_cache,
                    embedding_func=openai_embedding
                )
                self.lightrag_instances[bucket_dir.name] = rag
                print(f"  ✅ Loaded: {bucket_dir.name}")
            except Exception as e:
                print(f"  ⚠️  Failed to load {bucket_dir.name}: {e}")
        
        print(f"✅ Knowledge base ready with {len(self.lightrag_instances)} buckets")
    
    def main_menu(self):
        """Display main brainstorming menu."""
        while True:
            print("\\n💡 Brainstorming Menu:")
            print("  1. Scene-Specific Brainstorming")
            print("  2. Character Development Ideas")
            print("  3. Plot Development & Twists")
            print("  4. Dialogue & Voice Exploration")
            print("  5. Theme & Symbolism Ideas")
            print("  6. World Building Expansion")
            print("  7. Free-Form Creative Session")
            print("  8. Review Previous Sessions")
            print("  9. Exit")
            
            choice = input("\\nSelect option (1-9): ").strip()
            
            if choice == "1":
                self.scene_brainstorming()
            elif choice == "2":
                self.character_brainstorming()
            elif choice == "3":
                self.plot_brainstorming()
            elif choice == "4":
                self.dialogue_brainstorming()
            elif choice == "5":
                self.theme_brainstorming()
            elif choice == "6":
                self.world_building_brainstorming()
            elif choice == "7":
                self.free_form_brainstorming()
            elif choice == "8":
                self.review_sessions()
            elif choice == "9":
                print("✅ Brainstorming session complete!")
                break
            else:
                print("❌ Invalid choice. Please select 1-9.")
    
    def scene_brainstorming(self):
        """Brainstorm ideas for specific scenes."""
        print("\\n🎬 Scene-Specific Brainstorming")
        
        # Show available scenes
        cursor = self.conn.cursor()
        cursor.execute("SELECT act, scene, scene_title FROM story_outline ORDER BY act, scene")
        scenes = cursor.fetchall()
        
        if not scenes:
            print("No scenes found. Add scenes in the Intake module first.")
            return
        
        print("\\nAvailable scenes:")
        for i, scene in enumerate(scenes, 1):
            title = scene['scene_title'] or "Untitled"
            print(f"  {i}. Act {scene['act']}, Scene {scene['scene']}: {title}")
        
        try:
            choice = int(input("Select scene number: ")) - 1
            if 0 <= choice < len(scenes):
                selected_scene = scenes[choice]
                self.brainstorm_for_scene(selected_scene['act'], selected_scene['scene'])
            else:
                print("❌ Invalid selection.")
        except ValueError:
            print("❌ Invalid input.")
    
    def brainstorm_for_scene(self, act, scene):
        """Generate ideas for a specific scene."""
        # Get scene context from database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM story_outline WHERE act = ? AND scene = ?", (act, scene))
        scene_data = cursor.fetchone()
        
        if not scene_data:
            print(f"Scene not found: Act {act}, Scene {scene}")
            return
        
        # Get project context
        project_context = self.get_project_context()
        
        # Select tone preset
        tone_preset = self.select_tone_preset()
        
        # Select knowledge buckets
        knowledge_context = self.select_knowledge_buckets()
        
        # Build brainstorming prompt
        prompt = self.build_scene_prompt(scene_data, project_context, tone_preset)
        
        # Generate and save brainstorming session
        self.run_brainstorming_session(
            f"Scene Brainstorming: Act {act}, Scene {scene}",
            prompt,
            knowledge_context,
            tone_preset
        )
    
    def character_brainstorming(self):
        """Brainstorm character development ideas."""
        print("\\n🧑‍🤝‍🧑 Character Development Brainstorming")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, role FROM characters ORDER BY name")
        characters = cursor.fetchall()
        
        if not characters:
            print("No characters found. Add characters in the Intake module first.")
            return
        
        print("\\nSelect character:")
        for i, char in enumerate(characters, 1):
            role = char['role'] or "Unknown"
            print(f"  {i}. {char['name']} ({role})")
        
        try:
            choice = int(input("Select character number: ")) - 1
            if 0 <= choice < len(characters):
                char_name = characters[choice]['name']
                self.brainstorm_for_character(char_name)
            else:
                print("❌ Invalid selection.")
        except ValueError:
            print("❌ Invalid input.")
    
    def brainstorm_for_character(self, character_name):
        """Generate character development ideas."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE name = ?", (character_name,))
        char_data = cursor.fetchone()
        
        project_context = self.get_project_context()
        tone_preset = self.select_tone_preset()
        knowledge_context = self.select_knowledge_buckets()
        
        prompt = self.build_character_prompt(char_data, project_context, tone_preset)
        
        self.run_brainstorming_session(
            f"Character Development: {character_name}",
            prompt,
            knowledge_context,
            tone_preset
        )
    
    def plot_brainstorming(self):
        """Brainstorm plot development and twists."""
        print("\\n📚 Plot Development Brainstorming")
        
        focus_areas = [
            "Plot twists and surprises",
            "Subplot development", 
            "Conflict escalation",
            "Rising action ideas",
            "Climax alternatives",
            "Resolution options"
        ]
        
        print("\\nFocus areas:")
        for i, area in enumerate(focus_areas, 1):
            print(f"  {i}. {area}")
        
        try:
            choice = int(input("Select focus area: ")) - 1
            if 0 <= choice < len(focus_areas):
                focus_area = focus_areas[choice]
                self.brainstorm_plot_element(focus_area)
            else:
                print("❌ Invalid selection.")
        except ValueError:
            print("❌ Invalid input.")
    
    def brainstorm_plot_element(self, focus_area):
        """Brainstorm specific plot elements."""
        project_context = self.get_project_context()
        tone_preset = self.select_tone_preset()
        knowledge_context = self.select_knowledge_buckets()
        
        prompt = f"""
        PROJECT CONTEXT:
        {project_context}
        
        FOCUS AREA: {focus_area}
        
        Generate creative ideas for {focus_area.lower()} that would enhance this story.
        Consider the existing characters, plot elements, and tone.
        Provide multiple distinct options with brief explanations.
        """
        
        self.run_brainstorming_session(
            f"Plot Development: {focus_area}",
            prompt,
            knowledge_context,
            tone_preset
        )
    
    def dialogue_brainstorming(self):
        """Brainstorm dialogue and character voice."""
        print("\\n💬 Dialogue & Voice Brainstorming")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM characters ORDER BY name")
        characters = [row['name'] for row in cursor.fetchall()]
        
        if not characters:
            print("No characters found. Add characters first.")
            return
        
        print(f"\\nAvailable characters: {', '.join(characters)}")
        char_input = input("Enter character name(s) for dialogue (comma-separated): ").strip()
        
        if not char_input:
            return
        
        selected_chars = [name.strip() for name in char_input.split(',')]
        
        project_context = self.get_project_context()
        tone_preset = self.select_tone_preset()
        knowledge_context = self.select_knowledge_buckets()
        
        prompt = f"""
        PROJECT CONTEXT:
        {project_context}
        
        DIALOGUE FOCUS: {', '.join(selected_chars)}
        
        Generate dialogue ideas, character voice development, and conversation starters
        for the specified character(s). Consider their personalities, relationships,
        and current story situation.
        """
        
        self.run_brainstorming_session(
            f"Dialogue: {', '.join(selected_chars)}",
            prompt,
            knowledge_context,
            tone_preset
        )
    
    def theme_brainstorming(self):
        """Brainstorm themes and symbolism."""
        print("\\n🎭 Theme & Symbolism Brainstorming")
        
        project_context = self.get_project_context()
        tone_preset = self.select_tone_preset()
        knowledge_context = self.select_knowledge_buckets()
        
        prompt = f"""
        PROJECT CONTEXT:
        {project_context}
        
        Explore themes, symbolism, and deeper meanings that could enhance this story.
        Consider metaphors, recurring motifs, and thematic elements that would
        add depth and resonance to the narrative.
        """
        
        self.run_brainstorming_session(
            "Themes & Symbolism",
            prompt,
            knowledge_context,
            tone_preset
        )
    
    def world_building_brainstorming(self):
        """Brainstorm world-building elements."""
        print("\\n🌍 World Building Brainstorming")
        
        project_context = self.get_project_context()
        tone_preset = self.select_tone_preset()
        knowledge_context = self.select_knowledge_buckets()
        
        prompt = f"""
        PROJECT CONTEXT:
        {project_context}
        
        Develop world-building elements including settings, locations, cultural details,
        social structures, and environmental factors that would enrich the story world.
        Consider how these elements support the plot and character development.
        """
        
        self.run_brainstorming_session(
            "World Building",
            prompt,
            knowledge_context,
            tone_preset
        )
    
    def free_form_brainstorming(self):
        """Free-form creative brainstorming session."""
        print("\\n✨ Free-Form Creative Session")
        
        custom_prompt = input("Enter your creative prompt or question: ").strip()
        if not custom_prompt:
            return
        
        project_context = self.get_project_context()
        tone_preset = self.select_tone_preset()
        knowledge_context = self.select_knowledge_buckets()
        
        full_prompt = f"""
        PROJECT CONTEXT:
        {project_context}
        
        CREATIVE PROMPT:
        {custom_prompt}
        
        Provide creative ideas, suggestions, and inspiration related to this prompt
        in the context of the current project.
        """
        
        self.run_brainstorming_session(
            f"Free-form: {custom_prompt[:50]}...",
            full_prompt,
            knowledge_context,
            tone_preset
        )
    
    def get_project_context(self):
        """Gather comprehensive project context."""
        cursor = self.conn.cursor()
        
        # Project metadata
        cursor.execute("SELECT key, value FROM project_metadata")
        metadata = dict(cursor.fetchall())
        
        # Characters
        cursor.execute("SELECT name, role, description FROM characters")
        characters = cursor.fetchall()
        
        # Story outline
        cursor.execute("SELECT act, scene, scene_title, scene_purpose FROM story_outline ORDER BY act, scene")
        outline = cursor.fetchall()
        
        context = f"""
        PROJECT: {metadata.get('project_name', 'Unknown')}
        GENRE: {metadata.get('genre', 'Not specified')}
        THEME: {metadata.get('main_theme', 'Not specified')}
        TONE: {metadata.get('tone', 'Not specified')}
        
        CHARACTERS:
        """
        
        for char in characters:
            role = char['role'] or 'Unknown'
            desc = char['description'] or 'No description'
            context += f"- {char['name']} ({role}): {desc}\\n"
        
        if outline:
            context += "\\nSTORY OUTLINE:\\n"
            current_act = None
            for scene in outline:
                if scene['act'] != current_act:
                    current_act = scene['act']
                    context += f"\\nAct {current_act}:\\n"
                title = scene['scene_title'] or 'Untitled'
                purpose = scene['scene_purpose'] or 'No purpose'
                context += f"  Scene {scene['scene']}: {title} ({purpose})\\n"
        
        return context
    
    def select_tone_preset(self):
        """Let user select a tone preset."""
        print("\\n🎨 Select Writing Tone:")
        for key, preset in self.tone_presets.items():
            print(f"  {key}. {preset['name']} - {preset['description']}")
        
        while True:
            choice = input("\\nSelect tone (1-6): ").strip()
            if choice in self.tone_presets:
                selected = self.tone_presets[choice]
                print(f"✅ Selected: {selected['name']}")
                return selected
            else:
                print("❌ Invalid choice. Please select 1-6.")
    
    def select_knowledge_buckets(self):
        """Let user select knowledge buckets for context."""
        if not self.lightrag_instances:
            print("⚠️  No knowledge buckets available.")
            return []
        
        print("\\n🧠 Available Knowledge Buckets:")
        bucket_names = list(self.lightrag_instances.keys())
        
        for i, bucket in enumerate(bucket_names, 1):
            print(f"  {i}. {bucket}")
        
        print("  0. Skip knowledge context")
        
        selected_buckets = []
        
        while True:
            choice = input("\\nSelect bucket number (or 'done' to finish): ").strip().lower()
            
            if choice == 'done' or choice == '0':
                break
            
            try:
                bucket_idx = int(choice) - 1
                if 0 <= bucket_idx < len(bucket_names):
                    bucket_name = bucket_names[bucket_idx]
                    if bucket_name not in selected_buckets:
                        selected_buckets.append(bucket_name)
                        print(f"✅ Added: {bucket_name}")
                    else:
                        print(f"Already selected: {bucket_name}")
                else:
                    print("❌ Invalid bucket number.")
            except ValueError:
                print("❌ Invalid input.")
        
        if selected_buckets:
            print(f"Selected buckets: {', '.join(selected_buckets)}")
        
        return selected_buckets
    
    def build_scene_prompt(self, scene_data, project_context, tone_preset):
        """Build a comprehensive prompt for scene brainstorming."""
        return f"""
        {project_context}
        
        SCENE FOCUS:
        Act {scene_data['act']}, Scene {scene_data['scene']}: {scene_data['scene_title'] or 'Untitled'}
        Location: {scene_data['location'] or 'Not specified'}
        Characters: {scene_data['characters_present'] or 'Not specified'}
        Purpose: {scene_data['scene_purpose'] or 'Not specified'}
        Key Events: {scene_data['key_events'] or 'Not specified'}
        
        TONE: {tone_preset['style']}
        
        Generate creative ideas for this scene including:
        - Specific dialogue snippets or exchanges
        - Physical actions and staging
        - Emotional beats and character moments
        - Sensory details and atmosphere
        - Potential complications or surprises
        - Ways to advance character development
        - Connection to overall story themes
        """
    
    def build_character_prompt(self, char_data, project_context, tone_preset):
        """Build a comprehensive prompt for character brainstorming."""
        return f"""
        {project_context}
        
        CHARACTER FOCUS: {char_data['name']}
        Role: {char_data['role'] or 'Not specified'}
        Description: {char_data['description'] or 'Not specified'}
        Personality: {char_data['personality_traits'] or 'Not specified'}
        Goals: {char_data['goals'] or 'Not specified'}
        Conflicts: {char_data['conflicts'] or 'Not specified'}
        
        TONE: {tone_preset['style']}
        
        Generate character development ideas including:
        - Specific mannerisms and habits
        - Dialogue voice and speech patterns
        - Internal motivations and fears
        - Relationship dynamics with other characters
        - Character growth opportunities
        - Backstory elements that could be revealed
        - Moments that showcase their personality
        """
    
    def run_brainstorming_session(self, session_name, prompt, knowledge_buckets, tone_preset):
        """Execute the brainstorming session with AI generation."""
        print(f"\\n🤖 Generating ideas for: {session_name}")
        print("=" * 50)
        
        # Enhance prompt with knowledge context if available
        enhanced_prompt = prompt
        
        if knowledge_buckets and self.lightrag_instances:
            print("🔍 Gathering relevant knowledge...")
            knowledge_context = self.gather_knowledge_context(prompt, knowledge_buckets)
            if knowledge_context:
                enhanced_prompt = f"""
                RELEVANT KNOWLEDGE CONTEXT:
                {knowledge_context}
                
                {prompt}
                
                Use the knowledge context above to inform and enrich your creative suggestions.
                """
        
        # For now, simulate AI response (in real implementation, call OpenAI API)
        ai_response = self.simulate_ai_response(session_name, enhanced_prompt, tone_preset)
        
        print("\\n💡 Generated Ideas:")
        print("-" * 30)
        print(ai_response)
        print("-" * 30)
        
        # Save to database
        self.save_brainstorming_session(session_name, prompt, knowledge_buckets, ai_response, tone_preset)
        
        # Ask for user rating and notes
        self.collect_user_feedback()
    
    def gather_knowledge_context(self, prompt, bucket_names):
        """Query LightRAG buckets for relevant context."""
        if not LIGHTRAG_AVAILABLE:
            return ""
        
        context_snippets = []
        
        for bucket_name in bucket_names:
            if bucket_name in self.lightrag_instances:
                try:
                    rag = self.lightrag_instances[bucket_name]
                    # Create a query based on the prompt
                    query = f"creative writing ideas related to: {prompt[:200]}"
                    
                    # Query the RAG system (this would be async in real implementation)
                    result = "Sample knowledge context from " + bucket_name
                    context_snippets.append(f"From {bucket_name}: {result}")
                    
                except Exception as e:
                    print(f"⚠️  Error querying {bucket_name}: {e}")
        
        return "\\n\\n".join(context_snippets)
    
    def simulate_ai_response(self, session_name, prompt, tone_preset):
        """Simulate AI response for demonstration."""
        return f"""
        Based on your {tone_preset['name'].lower()} tone and project context, here are some creative ideas:
        
        1. **Character Moment**: A subtle gesture or habit that reveals deeper personality
        2. **Dialogue Hook**: An unexpected line that shifts the conversation's direction  
        3. **Sensory Detail**: A specific smell, sound, or texture that grounds the scene
        4. **Emotional Beat**: A moment where the character's guard drops, revealing vulnerability
        5. **Plot Element**: A small complication that creates new story possibilities
        
        [This is a simulated response. In the full implementation, this would be generated by OpenAI's API using the enhanced prompt with knowledge context.]
        """
    
    def save_brainstorming_session(self, session_name, prompt, knowledge_buckets, ai_response, tone_preset):
        """Save the brainstorming session to the database."""
        cursor = self.conn.cursor()
        
        buckets_json = json.dumps(knowledge_buckets) if knowledge_buckets else None
        tone_json = json.dumps(tone_preset)
        
        cursor.execute('''
            INSERT INTO brainstorming_sessions 
            (session_name, prompt, context_buckets, tone_preset, ai_response)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_name, prompt, buckets_json, tone_json, ai_response))
        
        self.conn.commit()
        print("\\n💾 Session saved to database")
    
    def collect_user_feedback(self):
        """Collect user rating and notes for the session."""
        try:
            rating = int(input("\\nRate this session (1-5): "))
            if 1 <= rating <= 5:
                notes = input("Additional notes (optional): ").strip()
                
                cursor = self.conn.cursor()
                cursor.execute('''
                    UPDATE brainstorming_sessions 
                    SET quality_rating = ?, user_notes = ?
                    WHERE id = (SELECT MAX(id) FROM brainstorming_sessions)
                ''', (rating, notes))
                self.conn.commit()
                print("✅ Feedback saved")
            else:
                print("❌ Rating must be 1-5")
        except ValueError:
            print("❌ Invalid rating")
    
    def review_sessions(self):
        """Review previous brainstorming sessions."""
        print("\\n📚 Previous Brainstorming Sessions")
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT session_name, created_at, quality_rating, user_notes
            FROM brainstorming_sessions 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        sessions = cursor.fetchall()
        
        if not sessions:
            print("No previous sessions found.")
            return
        
        for i, session in enumerate(sessions, 1):
            rating = f"⭐{session['quality_rating']}" if session['quality_rating'] else "Not rated"
            print(f"{i}. {session['session_name']} - {session['created_at']} ({rating})")
            if session['user_notes']:
                print(f"   Notes: {session['user_notes']}")
        
        print("\\nEnter session number to view details, or press Enter to continue.")
        choice = input().strip()
        
        if choice.isdigit():
            try:
                session_idx = int(choice) - 1
                if 0 <= session_idx < len(sessions):
                    self.show_session_details(sessions[session_idx]['session_name'])
            except (ValueError, IndexError):
                pass
    
    def show_session_details(self, session_name):
        """Show detailed view of a brainstorming session."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM brainstorming_sessions 
            WHERE session_name = ?
            ORDER BY created_at DESC LIMIT 1
        ''', (session_name,))
        session = cursor.fetchone()
        
        if session:
            print(f"\\n📋 Session: {session['session_name']}")
            print(f"Date: {session['created_at']}")
            print(f"Tone: {session['tone_preset']}")
            print(f"Knowledge Used: {session['context_buckets']}")
            print(f"\\nAI Response:\\n{session['ai_response']}")
            if session['user_notes']:
                print(f"\\nYour Notes: {session['user_notes']}")


def main():
    """Entry point when running as a script."""
    brainstorm_module = LizzyBrainstorm()
    brainstorm_module.run()


if __name__ == "__main__":
    main()