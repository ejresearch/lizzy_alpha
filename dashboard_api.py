#!/usr/bin/env python3
"""
Lizzy Alpha Dashboard API
========================
Flask backend that interfaces with the existing Lizzy Alpha modules
to provide real data integration for the web dashboard.
"""

import os
import sys
import sqlite3
import json
import asyncio
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path

# Add current directory to path for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import existing Lizzy Alpha modules
try:
    import start
    import intake
    import brainstorm
    import write
    from lightrag_helper import LightRAGManager, CreativeQueryBuilder
except ImportError as e:
    print(f"⚠️  Warning: Could not import module: {e}")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
CORS(app)

# Global LightRAG manager
lightrag_manager = None

def get_projects_list():
    """Get list of all projects from the projects directory."""
    projects_dir = Path("projects")
    if not projects_dir.exists():
        return []
    
    projects = []
    for project_path in projects_dir.iterdir():
        if project_path.is_dir():
            db_path = project_path / f"{project_path.name}.sqlite"
            if db_path.exists():
                # Get project metadata from database
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Get metadata as key-value pairs
                    cursor.execute("SELECT key, value FROM project_metadata")
                    metadata_rows = cursor.fetchall()
                    metadata = dict(metadata_rows) if metadata_rows else {}
                    
                    if metadata:
                        projects.append({
                            "name": project_path.name,
                            "title": metadata.get('title', project_path.name),
                            "genre": metadata.get('genre', 'Unknown'),
                            "tone": metadata.get('tone', 'Unknown'),
                            "created_date": metadata.get('created_date', 'Unknown'),
                            "status": "Active",
                            "path": str(project_path)
                        })
                    
                    conn.close()
                except Exception as e:
                    print(f"Error reading project {project_path.name}: {e}")
    
    return projects

def get_project_details(project_name):
    """Get detailed information about a specific project."""
    project_path = Path("projects") / project_name
    db_path = project_path / f"{project_name}.sqlite"
    
    if not db_path.exists():
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get project metadata as key-value pairs
        cursor.execute("SELECT key, value FROM project_metadata")
        metadata_rows = cursor.fetchall()
        metadata = dict(metadata_rows) if metadata_rows else {}
        
        # Get characters
        cursor.execute("SELECT * FROM characters")
        characters = []
        for row in cursor.fetchall():
            characters.append({
                "id": row[0],
                "name": row[1],
                "role": row[2] if len(row) > 2 else "",
                "gender": row[3] if len(row) > 3 else "",
                "age": row[4] if len(row) > 4 else None,
                "description": row[5] if len(row) > 5 else "",
                "personality_traits": row[6] if len(row) > 6 else "",
                "backstory": row[7] if len(row) > 7 else "",
                "goals": row[8] if len(row) > 8 else "",
                "conflicts": row[9] if len(row) > 9 else "",
                "arc": row[10] if len(row) > 10 else "",
                "romantic_challenge": row[11] if len(row) > 11 else "",
                "lovable_trait": row[12] if len(row) > 12 else "",
                "comedic_flaw": row[13] if len(row) > 13 else ""
            })
        
        # Get scenes
        cursor.execute("SELECT * FROM story_outline ORDER BY act, scene")
        scenes = []
        for row in cursor.fetchall():
            scenes.append({
                "id": row[0],
                "act": row[1],
                "scene": row[2],
                "scene_title": row[3] if len(row) > 3 else "",
                "characters_present": row[4] if len(row) > 4 else "",
                "key_events": row[5] if len(row) > 5 else "",
                "setting": row[6] if len(row) > 6 else "",
                "mood": row[7] if len(row) > 7 else "",
                "notes": row[8] if len(row) > 8 else ""
            })
        
        # Get brainstorming sessions
        cursor.execute("SELECT * FROM brainstorming_sessions ORDER BY created_at DESC LIMIT 10")
        brainstorm_sessions = []
        for row in cursor.fetchall():
            brainstorm_sessions.append({
                "id": row[0],
                "type": row[1] if len(row) > 1 else "general",
                "focus": row[2] if len(row) > 2 else "",
                "prompt": row[3] if len(row) > 3 else "",
                "output": row[4] if len(row) > 4 else "",
                "created_at": row[5] if len(row) > 5 else ""
            })
        
        # Get latest draft
        cursor.execute("SELECT * FROM drafts ORDER BY version DESC LIMIT 1")
        latest_draft = cursor.fetchone()
        
        conn.close()
        
        return {
            "metadata": {
                "name": project_name,
                "title": metadata.get('title', project_name),
                "genre": metadata.get('genre', 'Unknown'),
                "tone": metadata.get('tone', 'Unknown'),
                "created_date": metadata.get('created_date', 'Unknown')
            },
            "characters": characters,
            "scenes": scenes,
            "brainstorm_sessions": brainstorm_sessions,
            "latest_draft": {
                "version": latest_draft[1] if latest_draft else 0,
                "title": latest_draft[2] if latest_draft else "",
                "content": latest_draft[3] if latest_draft else "",
                "word_count": latest_draft[4] if latest_draft else 0,
                "created_at": latest_draft[5] if latest_draft else None
            } if latest_draft else None
        }
        
    except Exception as e:
        print(f"Error getting project details: {e}")
        return None

# API Routes

@app.route('/')
def serve_dashboard():
    """Serve the main dashboard."""
    return send_from_directory('.', 'real_dashboard.html')

@app.route('/api/projects', methods=['GET'])
def api_get_projects():
    """Get list of all projects."""
    projects = get_projects_list()
    return jsonify({"projects": projects})

@app.route('/api/projects/<project_name>', methods=['GET'])
def api_get_project(project_name):
    """Get detailed information about a specific project."""
    project_details = get_project_details(project_name)
    if project_details:
        return jsonify(project_details)
    else:
        return jsonify({"error": "Project not found"}), 404

@app.route('/api/projects', methods=['POST'])
def api_create_project():
    """Create a new project using start.py."""
    data = request.json
    project_name = data.get('name')
    title = data.get('title', project_name)
    genre = data.get('genre', 'Romance')
    tone = data.get('tone', 'Romantic Comedy')
    
    try:
        # Use the start module to create the project
        success = start.create_new_project(project_name, title, genre, tone)
        
        if success:
            return jsonify({
                "message": "Project created successfully",
                "project_name": project_name
            })
        else:
            return jsonify({"error": "Failed to create project"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Error creating project: {str(e)}"}), 500

@app.route('/api/projects/<project_name>/characters', methods=['POST'])
def api_add_character(project_name):
    """Add a character to a project."""
    data = request.json
    
    try:
        # Use intake module functionality
        project_path = Path("projects") / project_name
        db_path = project_path / f"{project_name}.sqlite"
        
        if not db_path.exists():
            return jsonify({"error": "Project not found"}), 404
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO characters (name, role, romantic_challenge, lovable_trait, comedic_flaw, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get('name'),
            data.get('role'),
            data.get('romantic_challenge'),
            data.get('lovable_trait'),
            data.get('comedic_flaw'),
            data.get('description', '')
        ))
        
        conn.commit()
        character_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            "message": "Character added successfully",
            "character_id": character_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Error adding character: {str(e)}"}), 500

@app.route('/api/projects/<project_name>/brainstorm', methods=['POST'])
def api_brainstorm(project_name):
    """Generate brainstorming content."""
    data = request.json
    
    try:
        # Initialize LightRAG if needed
        global lightrag_manager
        if lightrag_manager is None:
            lightrag_manager = LightRAGManager()
            asyncio.run(lightrag_manager.initialize())
        
        # Get project details for context
        project_details = get_project_details(project_name)
        if not project_details:
            return jsonify({"error": "Project not found"}), 404
        
        # Build query based on brainstorm type
        brainstorm_type = data.get('type', 'general')
        tone = data.get('tone', 'romantic comedy')
        custom_query = data.get('query', '')
        
        if brainstorm_type == 'character' and data.get('character_data'):
            query = CreativeQueryBuilder.build_character_query(
                data['character_data'], tone
            )
        elif brainstorm_type == 'scene' and data.get('scene_data'):
            query = CreativeQueryBuilder.build_scene_query(
                data['scene_data'], tone
            )
        elif brainstorm_type == 'plot':
            context = f"Project: {project_details['metadata']['title']}\nGenre: {project_details['metadata']['genre']}"
            query = CreativeQueryBuilder.build_plot_query(
                'story development', context, tone
            )
        else:
            query = custom_query or f"Generate creative ideas for a {tone} story"
        
        # Query LightRAG
        results = asyncio.run(lightrag_manager.query_all_buckets(query))
        
        # Combine results
        combined_output = ""
        for bucket, result in results.items():
            if not result.startswith("Error:"):
                combined_output += f"### From {bucket.title()} Knowledge:\n{result}\n\n"
        
        # Store in database
        project_path = Path("projects") / project_name
        db_path = project_path / f"{project_name}.sqlite"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO brainstorming_log (type, tone, query, output, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            brainstorm_type,
            tone,
            query,
            combined_output,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            "session_id": session_id,
            "output": combined_output,
            "query": query
        })
        
    except Exception as e:
        return jsonify({"error": f"Error during brainstorming: {str(e)}"}), 500

@app.route('/api/projects/<project_name>/write', methods=['POST'])
def api_write_scene(project_name):
    """Generate a scene draft."""
    data = request.json
    
    try:
        # Get project details
        project_details = get_project_details(project_name)
        if not project_details:
            return jsonify({"error": "Project not found"}), 404
        
        scene_id = data.get('scene_id')
        if not scene_id:
            return jsonify({"error": "Scene ID required"}), 400
        
        # Find the scene
        scene_data = None
        for scene in project_details['scenes']:
            if scene['id'] == scene_id:
                scene_data = scene
                break
        
        if not scene_data:
            return jsonify({"error": "Scene not found"}), 400
        
        # Use write module to generate draft
        # This would integrate with the actual write.py module
        # For now, simulate the process
        
        project_path = Path("projects") / project_name
        db_path = project_path / f"{project_name}.sqlite"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get latest brainstorming content for context
        cursor.execute("""
            SELECT output FROM brainstorming_log 
            WHERE type IN ('scene', 'general') 
            ORDER BY timestamp DESC LIMIT 3
        """)
        brainstorm_content = [row[0] for row in cursor.fetchall()]
        
        # Simulate scene generation (in real implementation, this would use write.py)
        scene_content = f"""
# {scene_data['scene_title']}

*Act {scene_data['act']}, Scene {scene_data['scene']}*

Characters Present: {scene_data['characters_present']}

{scene_data['key_events']}

[This would be the AI-generated scene content based on brainstorming data]

---
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        """.strip()
        
        # Get next version number
        cursor.execute("SELECT MAX(version) FROM final_drafts")
        max_version = cursor.fetchone()[0] or 0
        new_version = max_version + 1
        
        # Store draft
        cursor.execute("""
            INSERT INTO final_drafts (version, content, timestamp)
            VALUES (?, ?, ?)
        """, (
            new_version,
            scene_content,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "version": new_version,
            "content": scene_content,
            "message": "Scene draft generated successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"Error generating scene: {str(e)}"}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Get system status."""
    try:
        # Check LightRAG status
        lightrag_status = "Not initialized"
        if lightrag_manager and lightrag_manager.initialized:
            lightrag_status = f"Active ({len(lightrag_manager.instances)} buckets)"
        
        # Check API key
        api_key_status = "Not configured"
        if os.getenv("OPENAI_API_KEY") and not os.getenv("OPENAI_API_KEY").startswith("your_"):
            api_key_status = "Configured"
        
        # Count projects
        projects_count = len(get_projects_list())
        
        return jsonify({
            "lightrag_status": lightrag_status,
            "api_key_status": api_key_status,
            "projects_count": projects_count,
            "working_directory": os.getcwd()
        })
        
    except Exception as e:
        return jsonify({"error": f"Error getting status: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Starting Lizzy Alpha Dashboard API...")
    print("=" * 50)
    
    # Initialize LightRAG in background
    try:
        lightrag_manager = LightRAGManager()
        print("🧠 LightRAG manager created")
    except Exception as e:
        print(f"⚠️  LightRAG initialization warning: {e}")
    
    print("🌐 Starting Flask server...")
    print("📱 Dashboard will be available at: http://localhost:5001")
    print("🔗 API endpoints ready")
    
    app.run(debug=True, host='0.0.0.0', port=5001)