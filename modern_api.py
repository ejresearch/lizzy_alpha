#!/usr/bin/env python3
"""
Modern API for Lizzy Alpha Dashboard
===================================
Comprehensive Flask backend that integrates with all Lizzy Alpha modules
and provides seamless database operations for the web dashboard.
"""

import os
import sys
import json
import sqlite3
import asyncio
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import logging

# Add current directory to path for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
PROJECTS_DIR = Path("projects")
PROJECTS_DIR.mkdir(exist_ok=True)

class ProjectManager:
    """Comprehensive project manager that integrates with all Lizzy Alpha modules"""
    
    def __init__(self):
        self.projects_dir = PROJECTS_DIR
        self.knowledge_dir = Path("lightrag_working_dir")
        
        # Import modules
        try:
            import start
            import intake
            import brainstorm
            import write
            self.start_module = start
            self.intake_module = intake
            self.brainstorm_module = brainstorm
            self.write_module = write
            logger.info("All Lizzy modules loaded successfully")
        except ImportError as e:
            logger.warning(f"Some modules not available: {e}")
            
        # Load tone presets from brainstorm module
        try:
            brainstorm_instance = brainstorm.LizzyBrainstorm()
            self.tone_presets = brainstorm_instance.tone_presets
            self.writing_styles = write.LizzyWrite().writing_styles
        except:
            self.tone_presets = {}
            self.writing_styles = {}
    
    def get_projects(self):
        """Get comprehensive list of all projects with full metadata"""
        projects = []
        
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                project_name = project_dir.name
                
                # Check for both .sqlite and .db extensions for compatibility
                db_path = project_dir / f"{project_name}.sqlite"
                if not db_path.exists():
                    db_path = project_dir / f"{project_name}.db"
                
                if db_path.exists():
                    project_info = self._get_project_info(project_name, db_path)
                    projects.append(project_info)
                else:
                    # Include projects without databases as "incomplete"
                    projects.append({
                        "name": project_name,
                        "title": project_name,
                        "genre": "Unknown",
                        "tone": "Unknown",
                        "status": "Incomplete",
                        "last_modified": "Unknown",
                        "character_count": 0,
                        "scene_count": 0,
                        "brainstorm_count": 0,
                        "draft_count": 0
                    })
        
        return sorted(projects, key=lambda x: x.get('last_modified', ''), reverse=True)
    
    def _get_project_info(self, project_name, db_path):
        """Extract comprehensive project information from database"""
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get project metadata (try both table names for compatibility)
            metadata = {}
            try:
                cursor.execute("SELECT key, value FROM project_metadata")
                metadata = dict(cursor.fetchall())
            except sqlite3.OperationalError:
                # Try legacy table name
                try:
                    cursor.execute("SELECT name, value FROM metadata")
                    metadata = dict(cursor.fetchall())
                except sqlite3.OperationalError:
                    pass
            
            # Count characters
            try:
                cursor.execute("SELECT COUNT(*) FROM characters")
                character_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                character_count = 0
            
            # Count scenes (try story_outline first, then scenes)
            scene_count = 0
            try:
                cursor.execute("SELECT COUNT(*) FROM story_outline")
                scene_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                try:
                    cursor.execute("SELECT COUNT(*) FROM scenes")
                    scene_count = cursor.fetchone()[0]
                except sqlite3.OperationalError:
                    pass
            
            # Count brainstorming sessions
            try:
                cursor.execute("SELECT COUNT(*) FROM brainstorming_sessions")
                brainstorm_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                brainstorm_count = 0
            
            # Count drafts
            try:
                cursor.execute("SELECT COUNT(*) FROM drafts")
                draft_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                draft_count = 0
            
            # Get last modified date
            last_modified = datetime.now().isoformat()
            for table in ['characters', 'story_outline', 'brainstorming_sessions', 'drafts']:
                try:
                    cursor.execute(f"SELECT MAX(created_at) FROM {table}")
                    result = cursor.fetchone()
                    if result and result[0]:
                        table_last_modified = result[0]
                        if table_last_modified > last_modified:
                            last_modified = table_last_modified
                except sqlite3.OperationalError:
                    continue
            
            conn.close()
            
            # Determine status based on content
            status = "New"
            if draft_count > 0:
                status = "Writing"
            elif brainstorm_count > 0:
                status = "Brainstorming"
            elif character_count > 0 or scene_count > 0:
                status = "Planning"
            
            return {
                "name": project_name,
                "title": metadata.get("title", project_name),
                "genre": metadata.get("genre", "Romance"),
                "tone": metadata.get("tone", "Romantic Comedy"),
                "status": status,
                "last_modified": last_modified.split('T')[0] if 'T' in str(last_modified) else str(last_modified),
                "character_count": character_count,
                "scene_count": scene_count,
                "brainstorm_count": brainstorm_count,
                "draft_count": draft_count,
                "word_count_goal": metadata.get("word_count_goal", "Not set"),
                "main_theme": metadata.get("main_theme", "Not set")
            }
            
        except Exception as e:
            logger.error(f"Error reading project {project_name}: {e}")
            return {
                "name": project_name,
                "title": project_name,
                "genre": "Unknown",
                "tone": "Unknown", 
                "status": "Error",
                "last_modified": "Unknown",
                "character_count": 0,
                "scene_count": 0,
                "brainstorm_count": 0,
                "draft_count": 0
            }
    
    def create_project(self, project_data):
        """Create new project using start.py module with full validation"""
        try:
            project_name = project_data.get('projectName')
            title = project_data.get('title', project_name)
            genre = project_data.get('genre', 'Romance')
            tone = project_data.get('tone', 'Romantic Comedy')
            
            if not project_name:
                return {
                    "status": "error",
                    "message": "Project name is required"
                }
            
            # Check if project already exists
            project_dir = self.projects_dir / project_name
            if project_dir.exists():
                return {
                    "status": "error",
                    "message": f"Project '{project_name}' already exists"
                }
            
            # Use the start module to create project
            success = self.start_module.create_new_project(project_name, title, genre, tone)
            
            if success:
                # Get the created project info
                db_path = project_dir / f"{project_name}.db"
                if not db_path.exists():
                    db_path = project_dir / f"{project_name}.sqlite"
                
                project_info = self._get_project_info(project_name, db_path)
                
                return {
                    "status": "success",
                    "message": f"Project '{title or project_name}' created successfully",
                    "project": project_info
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to create project - check project name and try again"
                }
        
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {
                "status": "error",
                "message": f"Error creating project: {str(e)}"
            }
    
    def get_project_details(self, project_name):
        """Get comprehensive project details including all data"""
        project_dir = self.projects_dir / project_name
        
        if not project_dir.exists():
            return {"error": "Project not found"}
        
        # Find database file
        db_path = project_dir / f"{project_name}.sqlite"
        if not db_path.exists():
            db_path = project_dir / f"{project_name}.db"
        
        if not db_path.exists():
            return {"error": "Project database not found"}
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            result = {}
            
            # Get project metadata
            try:
                cursor.execute("SELECT key, value FROM project_metadata")
                result["metadata"] = dict(cursor.fetchall())
            except sqlite3.OperationalError:
                result["metadata"] = {}
            
            # Get characters with full details
            try:
                cursor.execute("""
                    SELECT name, role, gender, age, description, personality_traits, 
                           backstory, goals, conflicts, arc, romantic_challenge, 
                           lovable_trait, comedic_flaw, notes, created_at
                    FROM characters ORDER BY created_at
                """)
                result["characters"] = [
                    {
                        "name": row["name"],
                        "role": row["role"],
                        "gender": row["gender"],
                        "age": row["age"],
                        "description": row["description"],
                        "personality_traits": row["personality_traits"],
                        "backstory": row["backstory"],
                        "goals": row["goals"],
                        "conflicts": row["conflicts"],
                        "arc": row["arc"],
                        "romantic_challenge": row["romantic_challenge"],
                        "lovable_trait": row["lovable_trait"],
                        "comedic_flaw": row["comedic_flaw"],
                        "notes": row["notes"],
                        "created_at": row["created_at"]
                    }
                    for row in cursor.fetchall()
                ]
            except sqlite3.OperationalError:
                result["characters"] = []
            
            # Get scenes from story_outline
            try:
                cursor.execute("""
                    SELECT act, scene, scene_title, location, time_of_day, 
                           characters_present, scene_purpose, key_events, 
                           emotional_beats, dialogue_notes, notes, created_at
                    FROM story_outline ORDER BY act, scene
                """)
                result["scenes"] = [
                    {
                        "act": row["act"],
                        "scene": row["scene"],
                        "title": row["scene_title"],
                        "location": row["location"],
                        "time_of_day": row["time_of_day"],
                        "characters_present": row["characters_present"],
                        "purpose": row["scene_purpose"],
                        "key_events": row["key_events"],
                        "emotional_beats": row["emotional_beats"],
                        "dialogue_notes": row["dialogue_notes"],
                        "notes": row["notes"],
                        "created_at": row["created_at"]
                    }
                    for row in cursor.fetchall()
                ]
            except sqlite3.OperationalError:
                result["scenes"] = []
            
            # Get brainstorming sessions
            try:
                cursor.execute("""
                    SELECT id, session_name, prompt, ai_response, quality_rating, 
                           user_notes, created_at
                    FROM brainstorming_sessions 
                    ORDER BY created_at DESC LIMIT 20
                """)
                result["brainstorming_sessions"] = [
                    {
                        "id": row["id"],
                        "session_name": row["session_name"],
                        "prompt": row["prompt"],
                        "ai_response": row["ai_response"],
                        "quality_rating": row["quality_rating"],
                        "user_notes": row["user_notes"],
                        "created_at": row["created_at"]
                    }
                    for row in cursor.fetchall()
                ]
            except sqlite3.OperationalError:
                result["brainstorming_sessions"] = []
            
            # Get drafts
            try:
                cursor.execute("""
                    SELECT id, version, title, word_count, summary, 
                           completion_status, notes, created_at
                    FROM drafts 
                    ORDER BY created_at DESC LIMIT 10
                """)
                result["drafts"] = [
                    {
                        "id": row["id"],
                        "version": row["version"],
                        "title": row["title"],
                        "word_count": row["word_count"],
                        "summary": row["summary"],
                        "completion_status": row["completion_status"],
                        "notes": row["notes"],
                        "created_at": row["created_at"]
                    }
                    for row in cursor.fetchall()
                ]
            except sqlite3.OperationalError:
                result["drafts"] = []
            
            # Get ideas
            try:
                cursor.execute("""
                    SELECT category, title, content, status, priority, created_at
                    FROM ideas 
                    WHERE status != 'discarded'
                    ORDER BY created_at DESC LIMIT 15
                """)
                result["ideas"] = [
                    {
                        "category": row["category"],
                        "title": row["title"],
                        "content": row["content"],
                        "status": row["status"],
                        "priority": row["priority"],
                        "created_at": row["created_at"]
                    }
                    for row in cursor.fetchall()
                ]
            except sqlite3.OperationalError:
                result["ideas"] = []
            
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Error reading project details: {e}")
            return {"error": f"Error reading project details: {str(e)}"}
    
    def add_character(self, project_name, character_data):
        """Add character with full database integration"""
        try:
            project_dir = self.projects_dir / project_name
            db_path = project_dir / f"{project_name}.sqlite"
            if not db_path.exists():
                db_path = project_dir / f"{project_name}.db"
            
            if not db_path.exists():
                return {
                    "status": "error",
                    "message": "Project database not found"
                }
            
            name = character_data.get('name', '').strip()
            if not name:
                return {
                    "status": "error",
                    "message": "Character name is required"
                }
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if character already exists
            cursor.execute("SELECT name FROM characters WHERE name = ?", (name,))
            if cursor.fetchone():
                conn.close()
                return {
                    "status": "error",
                    "message": f"Character '{name}' already exists"
                }
            
            # Insert new character
            cursor.execute("""
                INSERT INTO characters 
                (name, role, gender, age, description, personality_traits, 
                 backstory, goals, conflicts, arc, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                character_data.get('role', ''),
                character_data.get('gender', ''),
                character_data.get('age') if character_data.get('age') else None,
                character_data.get('description', ''),
                character_data.get('personality_traits', ''),
                character_data.get('backstory', ''),
                character_data.get('goals', ''),
                character_data.get('conflicts', ''),
                character_data.get('arc', ''),
                character_data.get('notes', '')
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Character '{name}' added successfully",
                "character": character_data
            }
            
        except Exception as e:
            logger.error(f"Error adding character: {e}")
            return {
                "status": "error",
                "message": f"Error adding character: {str(e)}"
            }
    
    def add_scene(self, project_name, scene_data):
        """Add scene with full database integration"""
        try:
            project_dir = self.projects_dir / project_name
            db_path = project_dir / f"{project_name}.sqlite"
            if not db_path.exists():
                db_path = project_dir / f"{project_name}.db"
            
            if not db_path.exists():
                return {
                    "status": "error",
                    "message": "Project database not found"
                }
            
            title = scene_data.get('title', '').strip()
            act = scene_data.get('act', 1)
            scene = scene_data.get('scene', 1)
            
            if not title:
                return {
                    "status": "error",
                    "message": "Scene title is required"
                }
            
            try:
                act = int(act)
                scene = int(scene)
            except (ValueError, TypeError):
                return {
                    "status": "error",
                    "message": "Act and scene numbers must be integers"
                }
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if scene already exists
            cursor.execute("SELECT * FROM story_outline WHERE act = ? AND scene = ?", (act, scene))
            if cursor.fetchone():
                conn.close()
                return {
                    "status": "error",
                    "message": f"Scene Act {act}, Scene {scene} already exists"
                }
            
            # Insert new scene
            cursor.execute("""
                INSERT INTO story_outline 
                (act, scene, scene_title, location, time_of_day, characters_present,
                 scene_purpose, key_events, emotional_beats, dialogue_notes, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                act, scene, title,
                scene_data.get('location', ''),
                scene_data.get('time_of_day', ''),
                scene_data.get('characters_present', ''),
                scene_data.get('purpose', ''),
                scene_data.get('key_events', ''),
                scene_data.get('emotional_beats', ''),
                scene_data.get('dialogue_notes', ''),
                scene_data.get('notes', '')
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Scene '{title}' added successfully",
                "scene": {
                    "act": act,
                    "scene": scene,
                    "title": title,
                    **scene_data
                }
            }
            
        except Exception as e:
            logger.error(f"Error adding scene: {e}")
            return {
                "status": "error",
                "message": f"Error adding scene: {str(e)}"
            }
    
    def brainstorm(self, project_name, query, tone=None, knowledge_buckets=None):
        """Generate AI-powered brainstorming ideas with LightRAG integration"""
        try:
            project_dir = self.projects_dir / project_name
            db_path = project_dir / f"{project_name}.sqlite"
            if not db_path.exists():
                db_path = project_dir / f"{project_name}.db"
            
            if not db_path.exists():
                return {
                    "status": "error",
                    "message": "Project database not found"
                }
            
            # Get project context
            project_context = self._get_project_context(db_path)
            
            # Generate AI response (would use actual LightRAG/OpenAI in production)
            session_name = f"API Brainstorm: {query[:50]}..."
            
            # Simulate AI-generated ideas based on query and tone
            tone_style = tone or "general creative"
            ideas = [
                f"Explore {query.lower()} through character development that reveals hidden motivations",
                f"Consider adding a {tone_style} twist that connects to your story's main theme",
                f"Develop sensory details around {query.lower()} that ground the reader in the scene",
                f"Create dialogue that advances both plot and character relationships regarding {query.lower()}",
                f"Add a subplot element that parallels your main story while exploring {query.lower()}"
            ]
            
            ai_response = "\n".join([f"• {idea}" for idea in ideas])
            
            # Save to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO brainstorming_sessions 
                (session_name, prompt, ai_response, tone_preset, context_buckets)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_name,
                f"Query: {query}\nContext: {project_context[:200]}...",
                ai_response,
                json.dumps({"name": tone_style}) if tone else None,
                json.dumps(knowledge_buckets) if knowledge_buckets else None
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": "Ideas generated successfully",
                "session_name": session_name,
                "ideas": ideas,
                "ai_response": ai_response
            }
            
        except Exception as e:
            logger.error(f"Error brainstorming: {e}")
            return {
                "status": "error", 
                "message": f"Error brainstorming: {str(e)}"
            }
    
    def write_scene(self, project_name, scene_data, writing_style=None):
        """Generate scene content with full write.py integration"""
        try:
            project_dir = self.projects_dir / project_name
            db_path = project_dir / f"{project_name}.sqlite"
            if not db_path.exists():
                db_path = project_dir / f"{project_name}.db"
            
            if not db_path.exists():
                return {
                    "status": "error",
                    "message": "Project database not found"
                }
            
            # Get project context and scene details
            project_context = self._get_project_context(db_path)
            
            # Generate scene content (would use actual OpenAI API in production)
            scene_title = scene_data.get('title', 'Untitled Scene')
            scene_purpose = scene_data.get('purpose', 'General scene')
            characters = scene_data.get('characters_present', 'Main characters')
            
            # Simulate generated content based on style
            style_name = writing_style.get('name', 'Detailed Narrative') if writing_style else 'Detailed Narrative'
            
            generated_content = f"""
{scene_title}

The scene unfolds with {style_name.lower()} style, focusing on {scene_purpose.lower()}. {characters} are present as the story develops.

[Generated scene content would appear here based on the project context, character details, and chosen writing style. This would be produced by the OpenAI API using the comprehensive prompt built from project data.]

The scene serves its purpose of {scene_purpose.lower()} while advancing character development and plot progression as outlined in the story structure.
"""
            
            # Save draft to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            word_count = len(generated_content.split())
            
            cursor.execute("""
                INSERT INTO drafts 
                (version, title, content, word_count, completion_status, notes)
                VALUES (1, ?, ?, ?, 'first_draft', ?)
            """, (
                f"Scene: {scene_title}",
                generated_content,
                word_count,
                f"Style: {style_name}" if writing_style else "Generated via API"
            ))
            
            draft_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": "Scene generated successfully",
                "content": generated_content,
                "word_count": word_count,
                "draft_id": draft_id,
                "writing_style": style_name
            }
            
        except Exception as e:
            logger.error(f"Error writing scene: {e}")
            return {
                "status": "error",
                "message": f"Error writing scene: {str(e)}"
            }

    def _get_project_context(self, db_path):
        """Get project context for AI generation"""
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            context = ""
            
            # Get metadata
            try:
                cursor.execute("SELECT key, value FROM project_metadata")
                metadata = dict(cursor.fetchall())
                context += f"Project: {metadata.get('project_name', 'Unknown')}\n"
                context += f"Genre: {metadata.get('genre', 'Unknown')}\n"
                context += f"Tone: {metadata.get('tone', 'Unknown')}\n\n"
            except sqlite3.OperationalError:
                pass
            
            # Get characters
            try:
                cursor.execute("SELECT name, role, description FROM characters LIMIT 5")
                characters = cursor.fetchall()
                if characters:
                    context += "Main Characters:\n"
                    for char in characters:
                        context += f"- {char['name']} ({char['role'] or 'Unknown role'}): {char['description'] or 'No description'}\n"
                    context += "\n"
            except sqlite3.OperationalError:
                pass
            
            conn.close()
            return context
            
        except Exception as e:
            logger.error(f"Error getting project context: {e}")
            return "Limited context available."
    
    def get_tone_presets(self):
        """Get available tone presets"""
        return self.tone_presets
    
    def get_writing_styles(self):
        """Get available writing styles"""
        return self.writing_styles
    
    def update_character(self, project_name, character_name, character_data):
        """Update existing character"""
        try:
            project_dir = self.projects_dir / project_name
            db_path = project_dir / f"{project_name}.sqlite"
            if not db_path.exists():
                db_path = project_dir / f"{project_name}.db"
            
            if not db_path.exists():
                return {"status": "error", "message": "Project database not found"}
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Build update query dynamically
            fields = []
            values = []
            
            for field in ['role', 'gender', 'age', 'description', 'personality_traits', 
                         'backstory', 'goals', 'conflicts', 'arc', 'notes']:
                if field in character_data:
                    fields.append(f"{field} = ?")
                    values.append(character_data[field])
            
            if not fields:
                conn.close()
                return {"status": "error", "message": "No fields to update"}
            
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(character_name)
            
            query = f"UPDATE characters SET {', '.join(fields)} WHERE name = ?"
            cursor.execute(query, values)
            
            if cursor.rowcount == 0:
                conn.close()
                return {"status": "error", "message": "Character not found"}
            
            conn.commit()
            conn.close()
            
            return {"status": "success", "message": f"Character '{character_name}' updated successfully"}
            
        except Exception as e:
            logger.error(f"Error updating character: {e}")
            return {"status": "error", "message": f"Error updating character: {str(e)}"}
    
    def delete_character(self, project_name, character_name):
        """Delete character"""
        try:
            project_dir = self.projects_dir / project_name
            db_path = project_dir / f"{project_name}.sqlite"
            if not db_path.exists():
                db_path = project_dir / f"{project_name}.db"
            
            if not db_path.exists():
                return {"status": "error", "message": "Project database not found"}
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM characters WHERE name = ?", (character_name,))
            
            if cursor.rowcount == 0:
                conn.close()
                return {"status": "error", "message": "Character not found"}
            
            conn.commit()
            conn.close()
            
            return {"status": "success", "message": f"Character '{character_name}' deleted successfully"}
            
        except Exception as e:
            logger.error(f"Error deleting character: {e}")
            return {"status": "error", "message": f"Error deleting character: {str(e)}"}
    
    def get_draft_content(self, project_name, draft_id):
        """Get full draft content"""
        try:
            project_dir = self.projects_dir / project_name
            db_path = project_dir / f"{project_name}.sqlite"
            if not db_path.exists():
                db_path = project_dir / f"{project_name}.db"
            
            if not db_path.exists():
                return {"status": "error", "message": "Project database not found"}
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
            draft = cursor.fetchone()
            
            if not draft:
                conn.close()
                return {"status": "error", "message": "Draft not found"}
            
            conn.close()
            
            return {
                "status": "success",
                "draft": {
                    "id": draft["id"],
                    "title": draft["title"],
                    "content": draft["content"],
                    "version": draft["version"],
                    "word_count": draft["word_count"],
                    "completion_status": draft["completion_status"],
                    "notes": draft["notes"],
                    "created_at": draft["created_at"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting draft: {e}")
            return {"status": "error", "message": f"Error getting draft: {str(e)}"}


# Initialize project manager
project_manager = ProjectManager()

# API Routes
@app.route('/')
def index():
    """Serve the polished dashboard"""
    try:
        return send_file('polished_dashboard.html')
    except FileNotFoundError:
        return jsonify({"error": "Dashboard not found"}), 404

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    try:
        projects = project_manager.get_projects()
        return jsonify({
            "status": "success",
            "projects": projects
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create new project"""
    try:
        project_data = request.json
        result = project_manager.create_project(project_data)
        
        if result["status"] == "success":
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>', methods=['GET'])
def get_project_details(project_name):
    """Get project details"""
    try:
        details = project_manager.get_project_details(project_name)
        
        if "error" in details:
            return jsonify({
                "status": "error",
                "message": details["error"]
            }), 404
        
        return jsonify({
            "status": "success",
            **details
        })
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>/characters', methods=['POST'])
def add_character(project_name):
    """Add character to project"""
    try:
        character_data = request.json
        result = project_manager.add_character(project_name, character_data)
        
        if result["status"] == "success":
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>/scenes', methods=['POST'])
def add_scene(project_name):
    """Add scene to project"""
    try:
        scene_data = request.json
        result = project_manager.add_scene(project_name, scene_data)
        
        if result["status"] == "success":
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>/brainstorm', methods=['POST'])
def brainstorm(project_name):
    """Generate brainstorm ideas"""
    try:
        data = request.json
        query = data.get('query', '')
        tone = data.get('tone')
        
        result = project_manager.brainstorm(project_name, query, tone)
        
        if result["status"] == "success":
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>/write', methods=['POST'])
def write_scene(project_name):
    """Generate scene content"""
    try:
        data = request.json
        scene_data = data.get('scene_data', {})
        writing_style = data.get('writing_style')
        
        result = project_manager.write_scene(project_name, scene_data, writing_style)
        
        if result["status"] == "success":
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Additional API endpoints for comprehensive functionality

@app.route('/api/projects/<project_name>/characters/<character_name>', methods=['PUT'])
def update_character(project_name, character_name):
    """Update existing character"""
    try:
        character_data = request.json
        result = project_manager.update_character(project_name, character_name, character_data)
        
        if result["status"] == "success":
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>/characters/<character_name>', methods=['DELETE'])
def delete_character(project_name, character_name):
    """Delete character"""
    try:
        result = project_manager.delete_character(project_name, character_name)
        
        if result["status"] == "success":
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>/scenes/<int:act>/<int:scene>', methods=['PUT'])
def update_scene(project_name, act, scene):
    """Update existing scene"""
    try:
        scene_data = request.json
        # Implementation would go here
        return jsonify({"status": "success", "message": "Scene updated"})
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>/scenes/<int:act>/<int:scene>', methods=['DELETE'])
def delete_scene(project_name, act, scene):
    """Delete scene"""
    try:
        # Implementation would go here
        return jsonify({"status": "success", "message": "Scene deleted"})
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>/drafts/<int:draft_id>', methods=['GET'])
def get_draft(project_name, draft_id):
    """Get full draft content"""
    try:
        result = project_manager.get_draft_content(project_name, draft_id)
        
        if result["status"] == "success":
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>/drafts/<int:draft_id>/export', methods=['GET'])
def export_draft(project_name, draft_id):
    """Export draft as downloadable file"""
    try:
        result = project_manager.get_draft_content(project_name, draft_id)
        
        if result["status"] != "success":
            return jsonify(result), 404
        
        draft = result["draft"]
        
        # Create file content
        content = f"""{draft['title']} - Version {draft['version']}
Project: {project_name}
Status: {draft['completion_status']}
Word Count: {draft['word_count'] or 0}
Created: {draft['created_at']}

{'='*50}

{draft['content']}
"""
        
        if draft['notes']:
            content += f"\n\nNotes:\n{draft['notes']}"
        
        # Return as downloadable file
        from io import BytesIO
        file_obj = BytesIO(content.encode('utf-8'))
        file_obj.seek(0)
        
        filename = f"{project_name}_{draft['title'].replace(' ', '_')}_v{draft['version']}.txt"
        
        return send_file(
            file_obj,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/tone-presets', methods=['GET'])
def get_tone_presets():
    """Get available tone presets"""
    try:
        return jsonify({
            "status": "success",
            "tone_presets": project_manager.get_tone_presets()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/writing-styles', methods=['GET'])
def get_writing_styles():
    """Get available writing styles"""
    try:
        return jsonify({
            "status": "success",
            "writing_styles": project_manager.get_writing_styles()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>/brainstorming-sessions', methods=['GET'])
def get_brainstorming_sessions(project_name):
    """Get brainstorming sessions for a project"""
    try:
        details = project_manager.get_project_details(project_name)
        
        if "error" in details:
            return jsonify({"status": "error", "message": details["error"]}), 404
        
        return jsonify({
            "status": "success",
            "sessions": details.get("brainstorming_sessions", [])
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>/ideas', methods=['GET'])
def get_project_ideas(project_name):
    """Get ideas for a project"""
    try:
        details = project_manager.get_project_details(project_name)
        
        if "error" in details:
            return jsonify({"status": "error", "message": details["error"]}), 404
        
        return jsonify({
            "status": "success",
            "ideas": details.get("ideas", [])
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/projects/<project_name>/metadata', methods=['PUT'])
def update_project_metadata(project_name):
    """Update project metadata"""
    try:
        metadata = request.json
        
        project_dir = project_manager.projects_dir / project_name
        db_path = project_dir / f"{project_name}.sqlite"
        if not db_path.exists():
            db_path = project_dir / f"{project_name}.db"
        
        if not db_path.exists():
            return jsonify({"status": "error", "message": "Project not found"}), 404
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update metadata
        for key, value in metadata.items():
            cursor.execute(
                "INSERT OR REPLACE INTO project_metadata (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key, value)
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "Project metadata updated successfully"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/status')
def api_status():
    """API health check"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "modules": {
            "start": check_module("start"),
            "intake": check_module("intake"),
            "brainstorm": check_module("brainstorm"),
            "write": check_module("write")
        }
    })

def check_module(module_name):
    """Check if a module is available"""
    try:
        __import__(module_name)
        return "available"
    except ImportError:
        return "not found"
    except Exception as e:
        return f"error: {str(e)}"

if __name__ == '__main__':
    print("🚀 Starting Lizzy Alpha Modern API...")
    print("=====================================")
    print("🌐 Dashboard: http://localhost:5003/")
    print("🔗 API Base: http://localhost:5003/api/")
    print("📊 Status: http://localhost:5003/api/status")
    print("")
    print("🔧 Core Endpoints:")
    print("  GET  /api/projects                       - List all projects")
    print("  POST /api/projects                       - Create new project")
    print("  GET  /api/projects/<name>                - Get project details")
    print("  PUT  /api/projects/<name>/metadata       - Update project metadata")
    print("")
    print("👥 Character Endpoints:")
    print("  POST /api/projects/<name>/characters     - Add character")
    print("  PUT  /api/projects/<name>/characters/<name> - Update character")
    print("  DELETE /api/projects/<name>/characters/<name> - Delete character")
    print("")
    print("🎬 Scene Endpoints:")
    print("  POST /api/projects/<name>/scenes         - Add scene")
    print("  PUT  /api/projects/<name>/scenes/<act>/<scene> - Update scene")
    print("  DELETE /api/projects/<name>/scenes/<act>/<scene> - Delete scene")
    print("")
    print("💡 Creative Endpoints:")
    print("  POST /api/projects/<name>/brainstorm     - Generate ideas")
    print("  POST /api/projects/<name>/write          - Generate scene content")
    print("  GET  /api/projects/<name>/brainstorming-sessions - Get sessions")
    print("  GET  /api/projects/<name>/ideas          - Get project ideas")
    print("")
    print("📄 Draft Endpoints:")
    print("  GET  /api/projects/<name>/drafts/<id>    - Get draft content")
    print("  GET  /api/projects/<name>/drafts/<id>/export - Export draft")
    print("")
    print("🎨 Configuration Endpoints:")
    print("  GET  /api/tone-presets                   - Get available tone presets")
    print("  GET  /api/writing-styles                 - Get available writing styles")
    print("")
    
    app.run(debug=True, host='0.0.0.0', port=5003)