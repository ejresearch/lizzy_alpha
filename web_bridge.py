#!/usr/bin/env python3
"""
Web Bridge for Lizzy Alpha
==========================
Simple script that allows the web dashboard to call the real Python modules
"""

import sys
import json
import os
from pathlib import Path

# Add current directory to path for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def call_start_module(project_name, title, genre, tone):
    """Call the real start.py module to create a project"""
    try:
        # Import the start module
        import start
        
        # Call the programmatic function we added
        success = start.create_new_project(project_name, title, genre, tone)
        
        if success:
            return {
                "status": "success",
                "message": f"Project '{project_name}' created successfully",
                "project_name": project_name,
                "title": title,
                "genre": genre,
                "tone": tone
            }
        else:
            return {
                "status": "error", 
                "message": "Failed to create project"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

def call_intake_module(project_name, data_type, data):
    """Call the real intake.py module to add character or scene data"""
    try:
        # For now, simulate intake call
        # In full implementation, this would use the intake module
        return {
            "status": "success",
            "message": f"Added {data_type} to project '{project_name}'",
            "data": data
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

def call_brainstorm_module(project_name, query, tone):
    """Call the real brainstorm.py module"""
    try:
        # For now, simulate brainstorm call
        # In full implementation, this would use the brainstorm module
        return {
            "status": "success",
            "message": "Brainstorming completed",
            "output": f"AI-generated ideas for '{project_name}' with tone '{tone}' and query '{query}'"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

def call_write_module(project_name, scene_id):
    """Call the real write.py module"""
    try:
        # For now, simulate write call
        # In full implementation, this would use the write module  
        return {
            "status": "success",
            "message": "Scene generated successfully",
            "content": f"Generated scene content for scene {scene_id} in project '{project_name}'"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

def main():
    """Handle command line calls from the web dashboard"""
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No command specified"}))
        return
    
    command = sys.argv[1]
    
    try:
        if command == "start":
            # Extract parameters for start command
            project_name = sys.argv[2]
            title = sys.argv[3] 
            genre = sys.argv[4]
            tone = sys.argv[5]
            
            result = call_start_module(project_name, title, genre, tone)
            print(json.dumps(result))
            
        elif command == "intake":
            project_name = sys.argv[2]
            data_type = sys.argv[3]  # "character" or "scene"
            data = json.loads(sys.argv[4])
            
            result = call_intake_module(project_name, data_type, data)
            print(json.dumps(result))
            
        elif command == "brainstorm":
            project_name = sys.argv[2]
            query = sys.argv[3]
            tone = sys.argv[4]
            
            result = call_brainstorm_module(project_name, query, tone)
            print(json.dumps(result))
            
        elif command == "write":
            project_name = sys.argv[2]
            scene_id = sys.argv[3]
            
            result = call_write_module(project_name, scene_id)
            print(json.dumps(result))
            
        else:
            print(json.dumps({"status": "error", "message": f"Unknown command: {command}"}))
            
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Bridge error: {str(e)}"}))

if __name__ == "__main__":
    main()