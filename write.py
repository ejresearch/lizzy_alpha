#!/usr/bin/env python3
"""
Lizzy Alpha - Write Module
=========================
Synthesizes brainstorming sessions and project elements into polished drafts.
Provides structured writing workflows with AI assistance and iterative refinement.

Author: Lizzy AI Writing Framework
"""

import os
import sqlite3
import sys
import json
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from lightrag.llm import gpt_4o_mini_complete
    OPENAI_AVAILABLE = True
except ImportError:
    print("⚠️  OpenAI integration not available. Some features will be limited.")
    OPENAI_AVAILABLE = False


class LizzyWrite:
    """
    The Write module synthesizes brainstorming sessions and project elements
    into structured drafts with AI assistance and iterative refinement.
    """
    
    def __init__(self, base_dir="projects"):
        self.base_dir = Path(base_dir)
        self.project_name = None
        self.db_path = None
        self.conn = None
        
        # Writing templates and styles
        self.writing_styles = {
            "1": {
                "name": "Detailed Narrative",
                "description": "Rich prose with full scene descriptions and internal thoughts",
                "approach": "comprehensive storytelling with deep character development"
            },
            "2": {
                "name": "Dialogue-Heavy",
                "description": "Focus on character interactions and conversations",
                "approach": "character-driven through speech and dialogue exchanges"
            },
            "3": {
                "name": "Action-Oriented",
                "description": "Fast-paced with emphasis on events and movement",
                "approach": "plot-driven with dynamic pacing and clear action"
            },
            "4": {
                "name": "Atmospheric",
                "description": "Mood and setting-focused with rich sensory details",
                "approach": "immersive world-building and emotional atmosphere"
            },
            "5": {
                "name": "Minimalist",
                "description": "Clean, spare prose with precise word choice",
                "approach": "economical language with maximum impact"
            },
            "6": {
                "name": "Stream of Consciousness",
                "description": "Internal character perspective with flowing thoughts",
                "approach": "character's mental journey and internal experience"
            }
        }
        
        # Draft types
        self.draft_types = {
            "scene": "Individual scene draft",
            "chapter": "Complete chapter",
            "act": "Full act or major section",
            "synopsis": "Story synopsis or treatment",
            "character_study": "Character development piece",
            "dialogue_only": "Pure dialogue draft"
        }
    
    def run(self):
        """Main entry point for the Write module."""
        print("✍️  Lizzy Alpha - Write Module")
        print("=" * 40)
        print("AI-assisted draft synthesis and iterative writing")
        print()
        
        try:
            self.setup_project()
            self.main_menu()
            
        except KeyboardInterrupt:
            print("\n\n⏸️  Writing session cancelled.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
        finally:
            if self.conn:
                self.conn.close()
    
    def setup_project(self):
        """Select an existing project to work with."""
        print("📂 Available Projects:")
        projects = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        
        if not projects:
            print("❌ No projects found. Run 'python3 start.py' first to create a project.")
            sys.exit(1)
        
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project}")
        
        print()
        
        while True:
            try:
                choice = input("Select project number: ").strip()
                project_index = int(choice) - 1
                
                if 0 <= project_index < len(projects):
                    self.project_name = projects[project_index]
                    break
                else:
                    print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        self.db_path = self.base_dir / self.project_name / f"{self.project_name}.sqlite"
        
        if not self.db_path.exists():
            print(f"❌ Database not found for project '{self.project_name}'")
            print("💡 Initialize the project first by running: python3 start.py")
            sys.exit(1)
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        print(f"📝 Writing for project: {self.project_name}")
    
    def main_menu(self):
        """Display main writing menu."""
        while True:
            print("\n✍️  Writing Menu:")
            print("  1. Write New Scene")
            print("  2. Write Chapter/Act")
            print("  3. Synthesize from Brainstorming")
            print("  4. Create Character Study")
            print("  5. Write Synopsis/Treatment")
            print("  6. Edit Existing Draft")
            print("  7. Review/Compare Drafts")
            print("  8. Export Final Draft")
            print("  9. Exit")
            
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == "1":
                self.write_scene()
            elif choice == "2":
                self.write_chapter()
            elif choice == "3":
                self.synthesize_brainstorming()
            elif choice == "4":
                self.write_character_study()
            elif choice == "5":
                self.write_synopsis()
            elif choice == "6":
                self.edit_draft()
            elif choice == "7":
                self.review_drafts()
            elif choice == "8":
                self.export_draft()
            elif choice == "9":
                print("✅ Writing session complete!")
                break
            else:
                print("❌ Invalid choice. Please select 1-9.")
    
    def write_scene(self):
        """Write a new scene draft."""
        print("\n🎬 Write New Scene")
        
        # Show available scenes from outline
        cursor = self.conn.cursor()
        cursor.execute("SELECT act, scene, scene_title, key_events FROM story_outline ORDER BY act, scene")
        scenes = cursor.fetchall()
        
        if not scenes:
            print("❌ No scenes found in story outline. Add scenes in the Intake module first.")
            return
        
        print("\nAvailable scenes:")
        for i, scene in enumerate(scenes, 1):
            title = scene['scene_title'] or "Untitled"
            print(f"  {i}. Act {scene['act']}, Scene {scene['scene']}: {title}")
        
        print("  0. Write custom scene (not in outline)")
        
        try:
            choice = int(input("Select scene number: "))
            
            if choice == 0:
                self.write_custom_scene()
            elif 1 <= choice <= len(scenes):
                selected_scene = scenes[choice - 1]
                self.write_outlined_scene(selected_scene['act'], selected_scene['scene'])
            else:
                print("❌ Invalid selection.")
        except ValueError:
            print("❌ Invalid input.")
    
    def write_outlined_scene(self, act, scene):
        """Write a scene that exists in the story outline."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM story_outline WHERE act = ? AND scene = ?", (act, scene))
        scene_data = cursor.fetchone()
        
        if not scene_data:
            print(f"❌ Scene not found: Act {act}, Scene {scene}")
            return
        
        print(f"\n📋 Writing Scene: Act {act}, Scene {scene}")
        print(f"Title: {scene_data['scene_title'] or 'Untitled'}")
        print(f"Purpose: {scene_data['scene_purpose'] or 'Not specified'}")
        print(f"Key Events: {scene_data['key_events'] or 'Not specified'}")
        
        # Get project context
        project_context = self.get_comprehensive_context()
        
        # Select writing style
        writing_style = self.select_writing_style()
        
        # Check for relevant brainstorming sessions
        brainstorm_sessions = self.get_relevant_brainstorming(f"scene act {act} scene {scene}")
        
        # Generate the scene
        self.generate_scene_draft(scene_data, project_context, writing_style, brainstorm_sessions)
    
    def write_custom_scene(self):
        """Write a scene not in the current outline."""
        print("\n✨ Write Custom Scene")
        
        scene_title = input("Scene title: ").strip()
        scene_description = input("Brief scene description: ").strip()
        characters_present = input("Characters in this scene: ").strip()
        
        if not scene_title:
            print("❌ Scene title required.")
            return
        
        # Create custom scene data
        custom_scene = {
            'scene_title': scene_title,
            'scene_purpose': scene_description,
            'characters_present': characters_present,
            'key_events': scene_description,
            'act': 0,  # Custom scene
            'scene': 0
        }
        
        project_context = self.get_comprehensive_context()
        writing_style = self.select_writing_style()
        brainstorm_sessions = self.get_relevant_brainstorming(scene_title)
        
        self.generate_scene_draft(custom_scene, project_context, writing_style, brainstorm_sessions)
    
    def write_chapter(self):
        """Write a complete chapter or act."""
        print("\n📚 Write Chapter/Act")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT act FROM story_outline ORDER BY act")
        acts = [row['act'] for row in cursor.fetchall()]
        
        if not acts:
            print("❌ No acts found in story outline.")
            return
        
        print("\nAvailable acts:")
        for act in acts:
            cursor.execute("SELECT COUNT(*) as scene_count FROM story_outline WHERE act = ?", (act,))
            scene_count = cursor.fetchone()['scene_count']
            print(f"  {act}. Act {act} ({scene_count} scenes)")
        
        try:
            choice = int(input("Select act number: "))
            if choice in acts:
                self.write_act(choice)
            else:
                print("❌ Invalid selection.")
        except ValueError:
            print("❌ Invalid input.")
    
    def write_act(self, act_number):
        """Write a complete act."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM story_outline WHERE act = ? ORDER BY scene", (act_number,))
        scenes = cursor.fetchall()
        
        print(f"\n📖 Writing Act {act_number} ({len(scenes)} scenes)")
        
        project_context = self.get_comprehensive_context()
        writing_style = self.select_writing_style()
        
        # Generate cohesive act draft
        self.generate_act_draft(act_number, scenes, project_context, writing_style)
    
    def synthesize_brainstorming(self):
        """Create a draft by synthesizing brainstorming sessions."""
        print("\n🧠 Synthesize from Brainstorming")
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, session_name, prompt, created_at, quality_rating
            FROM brainstorming_sessions 
            ORDER BY created_at DESC LIMIT 20
        ''')
        sessions = cursor.fetchall()
        
        if not sessions:
            print("❌ No brainstorming sessions found. Run brainstorm.py first.")
            return
        
        print("\nRecent brainstorming sessions:")
        for i, session in enumerate(sessions, 1):
            rating = f"⭐{session['quality_rating']}" if session['quality_rating'] else "Not rated"
            print(f"  {i}. {session['session_name']} ({rating})")
        
        print("\nSelect sessions to synthesize (comma-separated numbers):")
        selection = input("Session numbers: ").strip()
        
        try:
            selected_indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_sessions = [sessions[i] for i in selected_indices if 0 <= i < len(sessions)]
            
            if selected_sessions:
                self.create_synthesis_draft(selected_sessions)
            else:
                print("❌ No valid sessions selected.")
        except (ValueError, IndexError):
            print("❌ Invalid selection.")
    
    def write_character_study(self):
        """Write a character development piece."""
        print("\n👤 Write Character Study")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, role, description FROM characters")
        characters = cursor.fetchall()
        
        if not characters:
            print("❌ No characters found. Add characters in the Intake module first.")
            return
        
        print("\nSelect character:")
        for i, char in enumerate(characters, 1):
            role = char['role'] or "Unknown role"
            print(f"  {i}. {char['name']} ({role})")
        
        try:
            choice = int(input("Select character number: ")) - 1
            if 0 <= choice < len(characters):
                character = characters[choice]
                self.generate_character_study(character)
            else:
                print("❌ Invalid selection.")
        except ValueError:
            print("❌ Invalid input.")
    
    def write_synopsis(self):
        """Write a story synopsis or treatment."""
        print("\n📋 Write Synopsis/Treatment")
        
        synopsis_types = [
            "Short synopsis (1-2 paragraphs)",
            "Medium synopsis (1-2 pages)",
            "Detailed treatment (5+ pages)",
            "Character-focused synopsis",
            "Plot-focused synopsis"
        ]
        
        print("\nSynopsis types:")
        for i, stype in enumerate(synopsis_types, 1):
            print(f"  {i}. {stype}")
        
        try:
            choice = int(input("Select synopsis type: ")) - 1
            if 0 <= choice < len(synopsis_types):
                synopsis_type = synopsis_types[choice]
                self.generate_synopsis(synopsis_type)
            else:
                print("❌ Invalid selection.")
        except ValueError:
            print("❌ Invalid input.")
    
    def edit_draft(self):
        """Edit an existing draft."""
        print("\n✏️  Edit Existing Draft")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, version, completion_status, created_at FROM drafts ORDER BY created_at DESC LIMIT 10")
        drafts = cursor.fetchall()
        
        if not drafts:
            print("❌ No drafts found. Create a draft first.")
            return
        
        print("\nRecent drafts:")
        for i, draft in enumerate(drafts, 1):
            title = draft['title'] or "Untitled"
            status = draft['completion_status'] or "unknown"
            print(f"  {i}. {title} (v{draft['version']}, {status})")
        
        try:
            choice = int(input("Select draft number: ")) - 1
            if 0 <= choice < len(drafts):
                selected_draft = drafts[choice]
                self.edit_existing_draft(selected_draft['id'])
            else:
                print("❌ Invalid selection.")
        except ValueError:
            print("❌ Invalid input.")
    
    def review_drafts(self):
        """Review and compare drafts."""
        print("\n📊 Review/Compare Drafts")
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, title, version, word_count, completion_status, created_at
            FROM drafts 
            ORDER BY title, version
        ''')
        drafts = cursor.fetchall()
        
        if not drafts:
            print("❌ No drafts found.")
            return
        
        # Group by title for version comparison
        draft_groups = {}
        for draft in drafts:
            title = draft['title'] or "Untitled"
            if title not in draft_groups:
                draft_groups[title] = []
            draft_groups[title].append(draft)
        
        print("\nDraft versions by title:")
        for title, versions in draft_groups.items():
            print(f"\n📄 {title}:")
            for version in versions:
                word_count = version['word_count'] or 0
                status = version['completion_status'] or "unknown"
                print(f"  v{version['version']}: {word_count} words ({status}) - {version['created_at']}")
        
        draft_id = input("\nEnter draft ID to view details: ").strip()
        if draft_id.isdigit():
            self.show_draft_details(int(draft_id))
    
    def export_draft(self):
        """Export a final draft."""
        print("\n📤 Export Final Draft")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, version, completion_status FROM drafts WHERE completion_status = 'final' ORDER BY created_at DESC")
        final_drafts = cursor.fetchall()
        
        if not final_drafts:
            print("❌ No final drafts found. Mark a draft as 'final' first.")
            return
        
        print("\nFinal drafts:")
        for i, draft in enumerate(final_drafts, 1):
            title = draft['title'] or "Untitled"
            print(f"  {i}. {title} (v{draft['version']})")
        
        try:
            choice = int(input("Select draft to export: ")) - 1
            if 0 <= choice < len(final_drafts):
                selected_draft = final_drafts[choice]
                self.export_to_file(selected_draft['id'])
            else:
                print("❌ Invalid selection.")
        except ValueError:
            print("❌ Invalid input.")
    
    def get_comprehensive_context(self):
        """Gather all relevant project context."""
        cursor = self.conn.cursor()
        
        # Project metadata
        cursor.execute("SELECT key, value FROM project_metadata")
        metadata = dict(cursor.fetchall())
        
        # Characters with full details
        cursor.execute("SELECT * FROM characters")
        characters = cursor.fetchall()
        
        # Story structure
        cursor.execute("SELECT * FROM story_outline ORDER BY act, scene")
        outline = cursor.fetchall()
        
        # Recent ideas
        cursor.execute("SELECT category, title, content FROM ideas WHERE status != 'discarded' ORDER BY created_at DESC LIMIT 10")
        ideas = cursor.fetchall()
        
        context = f"""
PROJECT: {metadata.get('project_name', 'Unknown')}
CREATED: {metadata.get('created_date', 'Unknown')}

CHARACTERS:
"""
        
        for char in characters:
            context += f"""
{char['name']} ({char['role'] or 'Unknown role'}):
  Description: {char['description'] or 'No description'}
  Personality: {char['personality_traits'] or 'Not specified'}
  Goals: {char['goals'] or 'Not specified'}
  Conflicts: {char['conflicts'] or 'Not specified'}
  Arc: {char['arc'] or 'Not specified'}
"""
        
        if outline:
            context += "\nSTORY STRUCTURE:\n"
            current_act = None
            for scene in outline:
                if scene['act'] != current_act:
                    current_act = scene['act']
                    context += f"\nAct {current_act}:\n"
                
                title = scene['scene_title'] or 'Untitled'
                purpose = scene['scene_purpose'] or 'No purpose'
                events = scene['key_events'] or 'No events'
                
                context += f"  Scene {scene['scene']}: {title}\n"
                context += f"    Purpose: {purpose}\n"
                context += f"    Events: {events}\n"
        
        if ideas:
            context += "\nRECENT IDEAS:\n"
            for idea in ideas[:5]:  # Limit to top 5
                context += f"- {idea['title']}: {idea['content'][:100]}...\n"
        
        return context
    
    def select_writing_style(self):
        """Let user select a writing style."""
        print("\n🎨 Select Writing Style:")
        for key, style in self.writing_styles.items():
            print(f"  {key}. {style['name']} - {style['description']}")
        
        while True:
            choice = input("\nSelect style (1-6): ").strip()
            if choice in self.writing_styles:
                selected = self.writing_styles[choice]
                print(f"✅ Selected: {selected['name']}")
                return selected
            else:
                print("❌ Invalid choice. Please select 1-6.")
    
    def get_relevant_brainstorming(self, search_term):
        """Find brainstorming sessions relevant to the current writing task."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT session_name, ai_response, quality_rating
            FROM brainstorming_sessions 
            WHERE session_name LIKE ? OR prompt LIKE ?
            ORDER BY quality_rating DESC, created_at DESC
            LIMIT 5
        ''', (f'%{search_term}%', f'%{search_term}%'))
        
        return cursor.fetchall()
    
    def generate_scene_draft(self, scene_data, project_context, writing_style, brainstorm_sessions):
        """Generate a scene draft using AI assistance."""
        print(f"\n🤖 Generating scene draft...")
        
        # Build comprehensive prompt
        prompt = f"""
You are a skilled creative writer working on a story. Generate a complete scene draft based on the following information:

PROJECT CONTEXT:
{project_context}

SCENE DETAILS:
Title: {scene_data['scene_title'] or 'Untitled'}
Act: {scene_data['act']}, Scene: {scene_data['scene']}
Purpose: {scene_data['scene_purpose'] or 'Not specified'}
Characters Present: {scene_data['characters_present'] or 'Not specified'}
Key Events: {scene_data['key_events'] or 'Not specified'}
Location: {scene_data.get('location', 'Not specified')}

WRITING STYLE: {writing_style['name']} - {writing_style['approach']}

RELEVANT BRAINSTORMING IDEAS:
"""
        
        for session in brainstorm_sessions:
            prompt += f"\n- {session['session_name']}: {session['ai_response'][:200]}...\n"
        
        prompt += """

INSTRUCTIONS:
1. Write a complete, polished scene that fits the specified style
2. Include vivid descriptions, natural dialogue, and character development
3. Ensure the scene serves its stated purpose in the story
4. Incorporate the key events naturally into the narrative
5. Show character personalities through actions and dialogue
6. Create a scene that feels complete and satisfying

Write the scene now:
"""
        
        if OPENAI_AVAILABLE:
            try:
                ai_response = gpt_4o_mini_complete(prompt)
                self.save_scene_draft(scene_data, ai_response, writing_style, prompt)
                self.display_and_refine_draft(ai_response)
            except Exception as e:
                print(f"❌ AI generation failed: {e}")
                print("💡 You can still write manually or try again later.")
        else:
            print("⚠️  AI generation not available. Saving scene outline for manual writing.")
            manual_draft = f"""
SCENE OUTLINE FOR MANUAL WRITING:

Title: {scene_data['scene_title'] or 'Untitled'}
Purpose: {scene_data['scene_purpose'] or 'Not specified'}
Characters: {scene_data['characters_present'] or 'Not specified'}
Key Events: {scene_data['key_events'] or 'Not specified'}

Writing Style: {writing_style['name']}
Approach: {writing_style['approach']}

[Write your scene here based on the outline above]
"""
            self.save_scene_draft(scene_data, manual_draft, writing_style, prompt)
            print("📝 Scene outline saved. You can edit it manually.")
    
    def generate_act_draft(self, act_number, scenes, project_context, writing_style):
        """Generate a complete act draft."""
        print(f"\n🤖 Generating Act {act_number} draft...")
        
        scene_summaries = []
        for scene in scenes:
            scene_summaries.append(f"Scene {scene['scene']}: {scene['scene_title'] or 'Untitled'} - {scene['key_events'] or 'No events'}")
        
        prompt = f"""
You are writing Act {act_number} of a story. Create a cohesive, well-paced act that includes all the specified scenes.

PROJECT CONTEXT:
{project_context}

ACT {act_number} SCENES:
{chr(10).join(scene_summaries)}

WRITING STYLE: {writing_style['name']} - {writing_style['approach']}

INSTRUCTIONS:
1. Write smooth transitions between scenes
2. Maintain consistent character voices throughout
3. Build tension and momentum across the act
4. Ensure each scene serves the overall act structure
5. Create a satisfying act conclusion that propels the story forward

Write Act {act_number}:
"""
        
        if OPENAI_AVAILABLE:
            try:
                ai_response = gpt_4o_mini_complete(prompt)
                self.save_act_draft(act_number, ai_response, writing_style)
                self.display_and_refine_draft(ai_response)
            except Exception as e:
                print(f"❌ AI generation failed: {e}")
        else:
            manual_draft = f"ACT {act_number} OUTLINE - Write based on scenes above"
            self.save_act_draft(act_number, manual_draft, writing_style)
    
    def generate_character_study(self, character):
        """Generate a character development piece."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE name = ?", (character['name'],))
        char_data = cursor.fetchone()
        
        project_context = self.get_comprehensive_context()
        writing_style = self.select_writing_style()
        
        prompt = f"""
Write a character study for {character['name']} that reveals their personality, motivations, and inner world.

CHARACTER DETAILS:
Name: {char_data['name']}
Role: {char_data['role'] or 'Not specified'}
Description: {char_data['description'] or 'Not specified'}
Personality: {char_data['personality_traits'] or 'Not specified'}
Goals: {char_data['goals'] or 'Not specified'}
Conflicts: {char_data['conflicts'] or 'Not specified'}
Arc: {char_data['arc'] or 'Not specified'}

WRITING STYLE: {writing_style['name']} - {writing_style['approach']}

Write a character study that:
1. Shows the character in a revealing moment or situation
2. Explores their internal thoughts and motivations
3. Demonstrates their personality through actions and choices
4. Hints at their backstory and future development
5. Connects to the larger story context

Character Study:
"""
        
        if OPENAI_AVAILABLE:
            try:
                ai_response = gpt_4o_mini_complete(prompt)
                self.save_character_study(character['name'], ai_response, writing_style)
                self.display_and_refine_draft(ai_response)
            except Exception as e:
                print(f"❌ AI generation failed: {e}")
        else:
            print("⚠️  Manual character study outline saved.")
    
    def create_synthesis_draft(self, brainstorm_sessions):
        """Create a draft by synthesizing multiple brainstorming sessions."""
        print(f"\n🧠 Synthesizing {len(brainstorm_sessions)} brainstorming sessions...")
        
        # Get full session details
        cursor = self.conn.cursor()
        session_contents = []
        
        for session in brainstorm_sessions:
            cursor.execute("SELECT * FROM brainstorming_sessions WHERE id = ?", (session['id'],))
            full_session = cursor.fetchone()
            session_contents.append(full_session)
        
        project_context = self.get_comprehensive_context()
        writing_style = self.select_writing_style()
        
        # Build synthesis prompt
        brainstorm_text = "\n\n".join([
            f"SESSION: {session['session_name']}\nPROMPT: {session['prompt']}\nRESPONSE: {session['ai_response']}"
            for session in session_contents
        ])
        
        prompt = f"""
Create a cohesive draft by synthesizing insights from multiple brainstorming sessions.

PROJECT CONTEXT:
{project_context}

BRAINSTORMING SESSIONS TO SYNTHESIZE:
{brainstorm_text}

WRITING STYLE: {writing_style['name']} - {writing_style['approach']}

INSTRUCTIONS:
1. Identify the strongest ideas from all sessions
2. Weave them together into a coherent narrative piece
3. Eliminate contradictions and enhance complementary ideas
4. Create smooth flow between synthesized elements
5. Maintain consistent voice and style throughout

Synthesized Draft:
"""
        
        if OPENAI_AVAILABLE:
            try:
                ai_response = gpt_4o_mini_complete(prompt)
                self.save_synthesis_draft(session_contents, ai_response, writing_style)
                self.display_and_refine_draft(ai_response)
            except Exception as e:
                print(f"❌ AI generation failed: {e}")
        else:
            print("⚠️  Manual synthesis outline saved.")
    
    def generate_synopsis(self, synopsis_type):
        """Generate a story synopsis."""
        project_context = self.get_comprehensive_context()
        
        prompt = f"""
Write a {synopsis_type.lower()} for this story based on the project information.

PROJECT CONTEXT:
{project_context}

SYNOPSIS TYPE: {synopsis_type}

INSTRUCTIONS:
1. Capture the essence of the story and its appeal
2. Include main characters, central conflict, and stakes
3. Show the story's unique elements and themes
4. Write in present tense with engaging, professional tone
5. Match the length and detail level for the specified type

Synopsis:
"""
        
        if OPENAI_AVAILABLE:
            try:
                ai_response = gpt_4o_mini_complete(prompt)
                self.save_synopsis(synopsis_type, ai_response)
                self.display_and_refine_draft(ai_response)
            except Exception as e:
                print(f"❌ AI generation failed: {e}")
        else:
            print("⚠️  Manual synopsis outline saved.")
    
    def display_and_refine_draft(self, draft_content):
        """Display draft and offer refinement options."""
        print("\n📄 Generated Draft:")
        print("=" * 50)
        print(draft_content)
        print("=" * 50)
        
        while True:
            print("\n✨ Draft Options:")
            print("  1. Accept and save")
            print("  2. Request revisions")
            print("  3. Edit manually")
            print("  4. Regenerate completely")
            print("  5. Cancel")
            
            choice = input("Select option (1-5): ").strip()
            
            if choice == "1":
                print("✅ Draft accepted and saved!")
                break
            elif choice == "2":
                revision_notes = input("What revisions would you like? ")
                if revision_notes.strip():
                    self.request_revisions(draft_content, revision_notes)
                    break
            elif choice == "3":
                self.manual_edit_session(draft_content)
                break
            elif choice == "4":
                print("🔄 Regenerating...")
                # Would regenerate with slightly different prompt
                break
            elif choice == "5":
                print("❌ Draft cancelled.")
                break
            else:
                print("❌ Invalid choice.")
    
    def save_scene_draft(self, scene_data, content, writing_style, original_prompt):
        """Save a scene draft to the database."""
        cursor = self.conn.cursor()
        
        fallback_title = f"Act {scene_data['act']}, Scene {scene_data['scene']}"
        title = f"Scene: {scene_data['scene_title'] or fallback_title}"
        word_count = len(content.split())
        
        cursor.execute('''
            INSERT INTO drafts (version, title, content, word_count, completion_status, notes)
            VALUES (1, ?, ?, ?, 'first_draft', ?)
        ''', (title, content, word_count, f"Style: {writing_style['name']}"))
        
        self.conn.commit()
        print(f"💾 Scene draft saved ({word_count} words)")
    
    def save_act_draft(self, act_number, content, writing_style):
        """Save an act draft to the database."""
        cursor = self.conn.cursor()
        
        title = f"Act {act_number}"
        word_count = len(content.split())
        
        cursor.execute('''
            INSERT INTO drafts (version, title, content, word_count, completion_status, notes)
            VALUES (1, ?, ?, ?, 'first_draft', ?)
        ''', (title, content, word_count, f"Style: {writing_style['name']}"))
        
        self.conn.commit()
        print(f"💾 Act draft saved ({word_count} words)")
    
    def save_character_study(self, character_name, content, writing_style):
        """Save a character study to the database."""
        cursor = self.conn.cursor()
        
        title = f"Character Study: {character_name}"
        word_count = len(content.split())
        
        cursor.execute('''
            INSERT INTO drafts (version, title, content, word_count, completion_status, notes)
            VALUES (1, ?, ?, ?, 'character_study', ?)
        ''', (title, content, word_count, f"Style: {writing_style['name']}"))
        
        self.conn.commit()
        print(f"💾 Character study saved ({word_count} words)")
    
    def save_synthesis_draft(self, brainstorm_sessions, content, writing_style):
        """Save a synthesis draft to the database."""
        cursor = self.conn.cursor()
        
        session_names = [session['session_name'] for session in brainstorm_sessions]
        title = f"Synthesis: {', '.join(session_names[:2])}{'...' if len(session_names) > 2 else ''}"
        word_count = len(content.split())
        session_ids = json.dumps([str(session['id']) for session in brainstorm_sessions])
        
        cursor.execute('''
            INSERT INTO drafts (version, title, content, word_count, completion_status, notes, brainstorm_session_ids)
            VALUES (1, ?, ?, ?, 'synthesis', ?, ?)
        ''', (title, content, word_count, f"Style: {writing_style['name']}", session_ids))
        
        self.conn.commit()
        print(f"💾 Synthesis draft saved ({word_count} words)")
    
    def save_synopsis(self, synopsis_type, content):
        """Save a synopsis to the database."""
        cursor = self.conn.cursor()
        
        title = f"Synopsis: {synopsis_type}"
        word_count = len(content.split())
        
        cursor.execute('''
            INSERT INTO drafts (version, title, content, word_count, completion_status, notes)
            VALUES (1, ?, ?, ?, 'synopsis', ?)
        ''', (title, content, word_count, f"Type: {synopsis_type}"))
        
        self.conn.commit()
        print(f"💾 Synopsis saved ({word_count} words)")
    
    def request_revisions(self, original_content, revision_notes):
        """Request specific revisions to a draft."""
        if not OPENAI_AVAILABLE:
            print("⚠️  AI revisions not available. Edit manually instead.")
            return
        
        revision_prompt = f"""
Revise the following draft based on the user's feedback:

ORIGINAL DRAFT:
{original_content}

REVISION REQUESTS:
{revision_notes}

INSTRUCTIONS:
1. Address all the specific feedback points
2. Maintain the overall style and voice
3. Improve the draft while keeping its core strengths
4. Make changes that enhance rather than completely rewrite

REVISED DRAFT:
"""
        
        try:
            revised_content = gpt_4o_mini_complete(revision_prompt)
            print("\n🔄 Revised Draft:")
            print("=" * 50)
            print(revised_content)
            print("=" * 50)
            
            # Update the database with the revision
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE drafts 
                SET content = ?, notes = notes || ? 
                WHERE id = (SELECT MAX(id) FROM drafts)
            ''', (revised_content, f"\n\nRevision: {revision_notes}"))
            self.conn.commit()
            
        except Exception as e:
            print(f"❌ Revision failed: {e}")
    
    def manual_edit_session(self, draft_content):
        """Start a manual editing session."""
        print("\n✏️  Manual Edit Session")
        print("Current draft will be displayed. Edit as needed:")
        print("(Type 'SAVE' on a new line when finished)")
        print("-" * 50)
        
        lines = draft_content.split('\n')
        edited_lines = []
        
        for i, line in enumerate(lines, 1):
            print(f"{i:3}: {line}")
            new_line = input(f"     ").strip()
            if new_line.upper() == 'SAVE':
                break
            elif new_line == '':
                edited_lines.append(line)  # Keep original
            else:
                edited_lines.append(new_line)  # Use edited version
        
        edited_content = '\n'.join(edited_lines)
        
        # Save the edited version
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE drafts 
            SET content = ?, notes = notes || ?
            WHERE id = (SELECT MAX(id) FROM drafts)
        ''', (edited_content, "\n\nManually edited"))
        self.conn.commit()
        
        print("✅ Manual edits saved!")
    
    def edit_existing_draft(self, draft_id):
        """Edit an existing draft."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
        draft = cursor.fetchone()
        
        if not draft:
            print("❌ Draft not found.")
            return
        
        print(f"\n✏️  Editing: {draft['title']} (v{draft['version']})")
        print(f"Current word count: {draft['word_count'] or 0}")
        print(f"Status: {draft['completion_status']}")
        
        print("\nEdit options:")
        print("  1. View and edit content")
        print("  2. Change status")
        print("  3. Add notes")
        print("  4. Create new version")
        print("  5. Cancel")
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == "1":
            self.manual_edit_session(draft['content'])
        elif choice == "2":
            self.change_draft_status(draft_id)
        elif choice == "3":
            self.add_draft_notes(draft_id)
        elif choice == "4":
            self.create_new_version(draft)
        elif choice == "5":
            return
        else:
            print("❌ Invalid choice.")
    
    def change_draft_status(self, draft_id):
        """Change the status of a draft."""
        statuses = ["outline", "first_draft", "revision", "final"]
        
        print("\nAvailable statuses:")
        for i, status in enumerate(statuses, 1):
            print(f"  {i}. {status}")
        
        try:
            choice = int(input("Select new status: ")) - 1
            if 0 <= choice < len(statuses):
                new_status = statuses[choice]
                
                cursor = self.conn.cursor()
                cursor.execute("UPDATE drafts SET completion_status = ? WHERE id = ?", (new_status, draft_id))
                self.conn.commit()
                
                print(f"✅ Status changed to: {new_status}")
            else:
                print("❌ Invalid selection.")
        except ValueError:
            print("❌ Invalid input.")
    
    def add_draft_notes(self, draft_id):
        """Add notes to a draft."""
        notes = input("Add notes: ").strip()
        if notes:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE drafts SET notes = notes || ? WHERE id = ?", (f"\n{notes}", draft_id))
            self.conn.commit()
            print("✅ Notes added.")
    
    def create_new_version(self, original_draft):
        """Create a new version of an existing draft."""
        cursor = self.conn.cursor()
        
        # Get the highest version number for this title
        cursor.execute("SELECT MAX(version) FROM drafts WHERE title = ?", (original_draft['title'],))
        max_version = cursor.fetchone()[0] or 0
        new_version = max_version + 1
        
        # Create new version
        cursor.execute('''
            INSERT INTO drafts (version, title, content, word_count, completion_status, notes, brainstorm_session_ids)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            new_version,
            original_draft['title'],
            original_draft['content'],
            original_draft['word_count'],
            'revision',
            f"Version {new_version} - copied from v{original_draft['version']}",
            original_draft['brainstorm_session_ids']
        ))
        
        self.conn.commit()
        print(f"✅ Created version {new_version}")
    
    def show_draft_details(self, draft_id):
        """Show detailed view of a draft."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
        draft = cursor.fetchone()
        
        if not draft:
            print("❌ Draft not found.")
            return
        
        print(f"\n📄 Draft Details")
        print(f"Title: {draft['title']}")
        print(f"Version: {draft['version']}")
        print(f"Word Count: {draft['word_count'] or 0}")
        print(f"Status: {draft['completion_status']}")
        print(f"Created: {draft['created_at']}")
        print(f"Notes: {draft['notes'] or 'None'}")
        
        show_content = input("\nShow full content? (y/N): ").strip().lower()
        if show_content == 'y':
            print("\n" + "="*50)
            print(draft['content'])
            print("="*50)
    
    def export_to_file(self, draft_id):
        """Export a draft to a text file."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
        draft = cursor.fetchone()
        
        if not draft:
            print("❌ Draft not found.")
            return
        
        # Create export filename
        title = draft['title'].replace(' ', '_').replace(':', '_')
        filename = f"{self.project_name}_{title}_v{draft['version']}.txt"
        export_path = self.base_dir / self.project_name / filename
        
        # Write to file
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(f"{draft['title']} - Version {draft['version']}\n")
                f.write(f"Project: {self.project_name}\n")
                f.write(f"Status: {draft['completion_status']}\n")
                f.write(f"Word Count: {draft['word_count'] or 0}\n")
                f.write(f"Created: {draft['created_at']}\n")
                f.write("\n" + "="*50 + "\n\n")
                f.write(draft['content'])
                if draft['notes']:
                    f.write(f"\n\nNotes:\n{draft['notes']}")
            
            print(f"✅ Draft exported to: {export_path}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")


def main():
    """Entry point when running as a script."""
    write_module = LizzyWrite()
    write_module.run()


if __name__ == "__main__":
    main()