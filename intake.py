#!/usr/bin/env python3
"""
Lizzy Alpha - Intake Module
===========================
Captures essential story elements and foundational metadata.
Builds the creative blueprint that informs all subsequent AI generation.

Author: Lizzy AI Writing Framework
"""

import os
import sqlite3
import sys
import json
from datetime import datetime
from pathlib import Path


class LizzyIntake:
    """
    The Intake module captures characters, story structure, and foundational elements.
    This creates the creative blueprint for AI-assisted brainstorming and writing.
    """
    
    def __init__(self, base_dir="projects"):
        self.base_dir = Path(base_dir)
        self.project_name = None
        self.db_path = None
        self.conn = None
    
    def run(self):
        """Main entry point for the Intake module."""
        print("📋 Lizzy Alpha - Intake Module")
        print("=" * 40)
        print("Capturing story elements and character details")
        print()
        
        try:
            self.select_project()
            self.connect_database()
            self.main_menu()
            
        except KeyboardInterrupt:
            print("\n\n⏸️  Intake session cancelled.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
        finally:
            if self.conn:
                self.conn.close()
    
    def select_project(self):
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
            choice = input("Enter project name: ").strip()
            
            if choice in projects:
                self.project_name = choice
                self.db_path = self.base_dir / self.project_name / f"{self.project_name}.sqlite"
                
                if not self.db_path.exists():
                    print(f"❌ Database not found for project '{choice}'. Run 'python3 start.py' first.")
                    continue
                    
                print(f"📝 Working with project: {choice}")
                break
            else:
                print("❌ Project not found. Please enter a valid project name.")
    
    def connect_database(self):
        """Connect to the project database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            print("✅ Connected to project database")
        except sqlite3.Error as e:
            print(f"❌ Database connection error: {e}")
            raise
    
    def main_menu(self):
        """Display main intake menu and handle user choices."""
        while True:
            print("\n📋 Intake Menu (Alpha):")
            print("  1. Manage Characters")
            print("  2. Manage Outline")
            print("  3. Project Summary")
            print("  4. Back")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                self.manage_characters()
            elif choice == "2":
                self.manage_outline()
            elif choice == "3":
                self.show_project_summary_tables()
            elif choice == "4":
                print("✅ Intake session complete!")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
    
    def manage_characters(self):
        """Character management - guided form for all fields."""
        while True:
            print("\n🧑‍🤝‍🧑 Character Management:")
            self.show_character_summary()
            print("\n  1. Add/Edit Character (Full Form)")
            print("  2. Delete Character")
            print("  3. Back to Main Menu")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == "1":
                self.character_full_form()
            elif choice == "2":
                self.delete_character()
            elif choice == "3":
                break
            else:
                print("❌ Invalid choice. Please select 1-3.")
    
    def show_character_summary(self):
        """Display current characters in the project."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, role, age, description FROM characters ORDER BY id")
        characters = cursor.fetchall()
        
        if characters:
            print("\nCurrent Characters:")
            for char in characters:
                role = char['role'] or 'Unknown role'
                age = f", age {char['age']}" if char['age'] else ""
                desc = f" - {char['description'][:50]}..." if char['description'] else ""
                print(f"  • {char['name']} ({role}{age}){desc}")
        else:
            print("\nNo characters added yet.")
    
    def character_full_form(self):
        """Comprehensive character form with all schema fields."""
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
            'gender': ("Gender", "Character's gender identity"),
            'age': ("Age", "Numeric age of the character"),
            'description': ("Physical Description", "Appearance, clothing, distinguishing features"),
            'personality_traits': ("Personality Traits", "Key personality characteristics"),
            'backstory': ("Backstory", "Character's history and background"),
            'goals': ("Goals", "What the character wants to achieve"),
            'conflicts': ("Conflicts", "Internal and external conflicts"),
            'arc': ("Character Arc", "How the character will change/develop"),
            'romantic_challenge': ("🎭 Romantic Challenge", "Essential Trinity: What prevents them from love?"),
            'lovable_trait': ("💝 Lovable Trait", "Essential Trinity: What makes them endearing?"),
            'comedic_flaw': ("😄 Comedic Flaw", "Essential Trinity: What makes them funny?"),
            'notes': ("Additional Notes", "Any other important information")
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
            
            # Handle age as integer
            if field == 'age' and value:
                if value.isdigit():
                    new_data[field] = int(value)
            elif value:  # Only update if value provided
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
                    cursor.execute(f"UPDATE characters SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
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
    
    def add_character(self):
        """Add a new character to the project."""
        print("\n✨ Adding New Character")
        
        name = input("Character name: ").strip()
        if not name:
            print("❌ Character name is required.")
            return
        
        # Check if character already exists
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM characters WHERE name = ?", (name,))
        if cursor.fetchone():
            print(f"❌ Character '{name}' already exists.")
            return
        
        print("\\nCharacter roles: protagonist, love_interest, antagonist, mentor, comic_relief, supporting, obstacle")
        role = input("Role: ").strip()
        
        gender = input("Gender: ").strip()
        
        age_str = input("Age (number): ").strip()
        age = None
        if age_str.isdigit():
            age = int(age_str)
        
        description = input("Brief description: ").strip()
        personality = input("Personality traits: ").strip()
        backstory = input("Backstory: ").strip()
        goals = input("Character goals: ").strip()
        conflicts = input("Internal/external conflicts: ").strip()
        arc = input("Character arc/development: ").strip()
        notes = input("Additional notes: ").strip()
        
        try:
            cursor.execute('''
                INSERT INTO characters 
                (name, role, gender, age, description, personality_traits, backstory, goals, conflicts, arc, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, role, gender, age, description, personality, backstory, goals, conflicts, arc, notes))
            
            self.conn.commit()
            print(f"✅ Added character: {name}")
            
        except sqlite3.Error as e:
            print(f"❌ Error adding character: {e}")
    
    def edit_character(self):
        """Edit an existing character."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM characters ORDER BY name")
        characters = cursor.fetchall()
        
        if not characters:
            print("No characters to edit.")
            return
        
        print("\\nSelect character to edit:")
        for i, char in enumerate(characters, 1):
            print(f"  {i}. {char['name']}")
        
        try:
            choice = int(input("Enter number: ")) - 1
            if 0 <= choice < len(characters):
                char_id = characters[choice]['id']
                char_name = characters[choice]['name']
                
                # Get current character data
                cursor.execute("SELECT * FROM characters WHERE id = ?", (char_id,))
                char_data = cursor.fetchone()
                
                print(f"\\nEditing: {char_name}")
                print("(Press Enter to keep current value)")
                
                # Update fields
                updates = {}
                fields = ['role', 'gender', 'age', 'description', 'personality_traits', 
                         'backstory', 'goals', 'conflicts', 'arc', 'notes']
                
                for field in fields:
                    current = char_data[field] or ""
                    prompt = f"{field.replace('_', ' ').title()} [{current}]: "
                    new_value = input(prompt).strip()
                    if new_value:
                        if field == 'age' and new_value.isdigit():
                            updates[field] = int(new_value)
                        else:
                            updates[field] = new_value
                
                if updates:
                    # Build update query
                    set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
                    values = list(updates.values()) + [char_id]
                    
                    cursor.execute(f"UPDATE characters SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
                    self.conn.commit()
                    print(f"✅ Updated character: {char_name}")
                else:
                    print("No changes made.")
            else:
                print("❌ Invalid selection.")
                
        except (ValueError, IndexError):
            print("❌ Invalid input.")
    
    def delete_character(self):
        """Delete a character."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM characters ORDER BY name")
        characters = cursor.fetchall()
        
        if not characters:
            print("No characters to delete.")
            return
        
        print("\\nSelect character to delete:")
        for i, char in enumerate(characters, 1):
            print(f"  {i}. {char['name']}")
        
        try:
            choice = int(input("Enter number: ")) - 1
            if 0 <= choice < len(characters):
                char_name = characters[choice]['name']
                char_id = characters[choice]['id']
                
                confirm = input(f"Delete '{char_name}'? (y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))
                    self.conn.commit()
                    print(f"✅ Deleted character: {char_name}")
                else:
                    print("Delete cancelled.")
            else:
                print("❌ Invalid selection.")
                
        except (ValueError, IndexError):
            print("❌ Invalid input.")
    
    def manage_outline(self):
        """Comprehensive outline management with guided form."""
        while True:
            print("\n📖 Story Outline Management:")
            self.show_outline_summary()
            print("\n  1. Add/Edit Scene (Full Form)")
            print("  2. Delete Scene")
            print("  3. Quick Three-Act Setup")
            print("  4. Back to Main Menu")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                self.scene_full_form()
            elif choice == "2":
                self.delete_scene()
            elif choice == "3":
                self.quick_three_act_setup()
            elif choice == "4":
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
    
    def scene_full_form(self):
        """Comprehensive scene form with all schema fields."""
        print("\n🎬 Scene Form (Complete All Fields)")
        print("=" * 40)
        
        cursor = self.conn.cursor()
        
        # Get act and scene numbers
        try:
            act = int(input("\nAct number: "))
            scene = int(input("Scene number: "))
        except ValueError:
            print("❌ Act and scene must be numbers.")
            return
        
        # Check if scene exists for editing
        cursor.execute("SELECT * FROM story_outline WHERE act = ? AND scene = ?", (act, scene))
        scene_data = cursor.fetchone()
        
        if scene_data:
            scene_data = dict(scene_data)
            print(f"\n📝 Editing: Act {act}, Scene {scene}")
            print("Press Enter to keep existing value")
        else:
            scene_data = {}
            print(f"\n✨ Creating: Act {act}, Scene {scene}")
        
        print("\n" + "=" * 40)
        print("Complete all fields for this scene")
        print("=" * 40 + "\n")
        
        # Get available characters for reference
        cursor.execute("SELECT name FROM characters ORDER BY name")
        char_names = [row['name'] for row in cursor.fetchall()]
        if char_names:
            print(f"Available characters: {', '.join(char_names)}\n")
        
        # Comprehensive field collection
        fields = {
            'scene_title': ("Scene Title", "Brief descriptive title for the scene"),
            'location': ("Location", "Where does this scene take place?"),
            'time_of_day': ("Time of Day", "morning/afternoon/evening/night"),
            'characters_present': ("Characters Present", "Comma-separated list of characters"),
            'scene_purpose': ("Scene Purpose", "setup/conflict/climax/resolution"),
            'key_events': ("Key Events", "What happens in this scene?"),
            'key_characters': ("Key Characters", "Legacy: Main characters in scene"),
            'beat': ("Beat", "Legacy Lizzy: Story beat/moment"),
            'nudge': ("Nudge", "Legacy Lizzy: Direction/guidance"),
            'emotional_beats': ("Emotional Beats", "Emotional journey in the scene"),
            'dialogue_notes': ("Dialogue Notes", "Key dialogue or conversation points"),
            'plot_threads': ("Plot Threads", "Which subplots are advanced?"),
            'notes': ("Additional Notes", "Any other important information")
        }
        
        new_data = {'act': act, 'scene': scene}
        
        for field, (label, help_text) in fields.items():
            print(f"\n{label}:")
            print(f"  ({help_text})")
            
            current = scene_data.get(field, '') if scene_data else ''
            if current:
                print(f"  Current: {current}")
            
            value = input("  > ").strip()
            
            if value:  # Only update if value provided
                new_data[field] = value
        
        # Save to database
        try:
            if scene_data:  # Update existing
                if len(new_data) > 2:  # More than just act and scene
                    set_clause = ", ".join([f"{field} = ?" for field in new_data.keys() if field not in ['act', 'scene']])
                    values = [v for k, v in new_data.items() if k not in ['act', 'scene']] + [act, scene]
                    cursor.execute(f"UPDATE story_outline SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE act = ? AND scene = ?", values)
                    self.conn.commit()
                    print(f"\n✅ Updated Act {act}, Scene {scene}")
                else:
                    print("\nNo changes made.")
            else:  # Insert new
                field_names = list(new_data.keys())
                placeholders = ", ".join(["?" for _ in field_names])
                fields_str = ", ".join(field_names)
                
                cursor.execute(f'''
                    INSERT INTO story_outline ({fields_str})
                    VALUES ({placeholders})
                ''', list(new_data.values()))
                
                self.conn.commit()
                print(f"\n✅ Added Act {act}, Scene {scene}")
                
        except sqlite3.IntegrityError:
            print(f"\n❌ Act {act}, Scene {scene} already exists. Please edit it instead.")
        except sqlite3.Error as e:
            print(f"\n❌ Database error: {e}")
    
    def build_story_outline(self):
        """Build or edit story structure."""
        while True:
            print("\\n📖 Story Outline:")
            self.show_outline_summary()
            print("\\n  1. Add Scene")
            print("  2. Edit Scene")
            print("  3. Delete Scene")
            print("  4. Quick Three-Act Setup")
            print("  5. Back to Main Menu")
            
            choice = input("\\nSelect option (1-5): ").strip()
            
            if choice == "1":
                self.add_scene()
            elif choice == "2":
                self.edit_scene()
            elif choice == "3":
                self.delete_scene()
            elif choice == "4":
                self.quick_three_act_setup()
            elif choice == "5":
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
    
    def show_outline_summary(self):
        """Display current story outline."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT act, scene, scene_title, scene_purpose FROM story_outline ORDER BY act, scene")
        scenes = cursor.fetchall()
        
        if scenes:
            print("\\nCurrent Outline:")
            current_act = None
            for scene in scenes:
                if scene['act'] != current_act:
                    current_act = scene['act']
                    print(f"\\n  Act {current_act}:")
                
                title = scene['scene_title'] or "Untitled"
                purpose = scene['scene_purpose'] or "No purpose set"
                print(f"    Scene {scene['scene']}: {title} ({purpose})")
        else:
            print("\\nNo scenes added yet.")
    
    def add_scene(self):
        """Add a new scene to the outline."""
        print("\\n🎬 Adding New Scene")
        
        try:
            act = int(input("Act number: "))
            scene = int(input("Scene number: "))
        except ValueError:
            print("❌ Act and scene must be numbers.")
            return
        
        # Check if scene already exists
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM story_outline WHERE act = ? AND scene = ?", (act, scene))
        if cursor.fetchone():
            print(f"❌ Act {act}, Scene {scene} already exists.")
            return
        
        title = input("Scene title: ").strip()
        location = input("Location: ").strip()
        time_of_day = input("Time of day: ").strip()
        
        # Get available characters for selection
        cursor.execute("SELECT name FROM characters ORDER BY name")
        char_names = [row['name'] for row in cursor.fetchall()]
        if char_names:
            print(f"\\nAvailable characters: {', '.join(char_names)}")
        
        characters_present = input("Characters present (comma-separated): ").strip()
        
        purpose = input("Scene purpose (setup/conflict/climax/resolution): ").strip()
        key_events = input("Key events: ").strip()
        emotional_beats = input("Emotional beats: ").strip()
        dialogue_notes = input("Dialogue notes: ").strip()
        plot_threads = input("Plot threads advanced: ").strip()
        notes = input("Additional notes: ").strip()
        
        try:
            cursor.execute('''
                INSERT INTO story_outline 
                (act, scene, scene_title, location, time_of_day, characters_present, 
                 scene_purpose, key_events, emotional_beats, dialogue_notes, plot_threads, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (act, scene, title, location, time_of_day, characters_present,
                  purpose, key_events, emotional_beats, dialogue_notes, plot_threads, notes))
            
            self.conn.commit()
            print(f"✅ Added Act {act}, Scene {scene}: {title}")
            
        except sqlite3.Error as e:
            print(f"❌ Error adding scene: {e}")
    
    def quick_three_act_setup(self):
        """Quick setup for standard three-act structure."""
        print("\\n🎭 Quick Three-Act Structure Setup")
        print("This will add basic scene placeholders for a three-act story.")
        
        confirm = input("Proceed? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            return
        
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
    
    def manage_world_building(self):
        """Manage world-building and setting elements."""
        print("\\n🌍 World Building & Setting")
        print("Add locations, cultures, rules, history, and other world elements.")
        
        # This is a simplified version - can be expanded
        category = input("Category (location/culture/rules/history/other): ").strip()
        name = input("Name: ").strip()
        description = input("Description: ").strip()
        importance = input("Importance (major/minor/background): ").strip()
        notes = input("Notes: ").strip()
        
        if name:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO world_building (category, name, description, importance, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (category, name, description, importance, notes))
            self.conn.commit()
            print(f"✅ Added world element: {name}")
    
    def manage_research(self):
        """Manage research and reference materials."""
        print("\\n📚 Research & References")
        
        category = input("Category (genre/historical/technical/other): ").strip()
        topic = input("Topic: ").strip()
        source = input("Source: ").strip()
        content = input("Content/Notes: ").strip()
        relevance = input("Relevance to story: ").strip()
        
        if topic:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO research (category, topic, source, content, relevance)
                VALUES (?, ?, ?, ?, ?)
            ''', (category, topic, source, content, relevance))
            self.conn.commit()
            print(f"✅ Added research item: {topic}")
    
    def set_project_goals(self):
        """Set project goals and themes."""
        print("\\n🎯 Project Goals & Themes")
        
        # Store in project_metadata
        cursor = self.conn.cursor()
        
        genre = input("Genre: ").strip()
        target_audience = input("Target audience: ").strip()
        word_count_goal = input("Target word count: ").strip()
        main_theme = input("Main theme: ").strip()
        tone = input("Tone (serious/humorous/dark/light): ").strip()
        
        if genre:
            cursor.execute('INSERT OR REPLACE INTO project_metadata (key, value) VALUES (?, ?)', ('genre', genre))
        if target_audience:
            cursor.execute('INSERT OR REPLACE INTO project_metadata (key, value) VALUES (?, ?)', ('target_audience', target_audience))
        if word_count_goal:
            cursor.execute('INSERT OR REPLACE INTO project_metadata (key, value) VALUES (?, ?)', ('word_count_goal', word_count_goal))
        if main_theme:
            cursor.execute('INSERT OR REPLACE INTO project_metadata (key, value) VALUES (?, ?)', ('main_theme', main_theme))
        if tone:
            cursor.execute('INSERT OR REPLACE INTO project_metadata (key, value) VALUES (?, ?)', ('tone', tone))
        
        self.conn.commit()
        print("✅ Project goals updated.")
    
    def show_project_summary_tables(self):
        """Display complete character and outline tables."""
        print("\n" + "=" * 60)
        print("📊 PROJECT SUMMARY - COMPLETE DATABASE TABLES")
        print("=" * 60)
        
        cursor = self.conn.cursor()
        
        # Display Characters Table
        print("\n🎭 CHARACTERS TABLE")
        print("-" * 60)
        cursor.execute("SELECT * FROM characters ORDER BY id")
        characters = cursor.fetchall()
        
        if characters:
            for char in characters:
                print(f"\n[Character #{char['id']}]")
                print(f"  Name: {char['name'] or 'N/A'}")
                print(f"  Role: {char['role'] or 'N/A'}")
                print(f"  Gender: {char['gender'] or 'N/A'}")
                print(f"  Age: {char['age'] or 'N/A'}")
                print(f"  Description: {char['description'] or 'N/A'}")
                print(f"  Personality: {char['personality_traits'] or 'N/A'}")
                print(f"  Backstory: {char['backstory'] or 'N/A'}")
                print(f"  Goals: {char['goals'] or 'N/A'}")
                print(f"  Conflicts: {char['conflicts'] or 'N/A'}")
                print(f"  Arc: {char['arc'] or 'N/A'}")
                print(f"  🎭 Romantic Challenge: {char['romantic_challenge'] or 'N/A'}")
                print(f"  💝 Lovable Trait: {char['lovable_trait'] or 'N/A'}")
                print(f"  😄 Comedic Flaw: {char['comedic_flaw'] or 'N/A'}")
                print(f"  Notes: {char['notes'] or 'N/A'}")
                print("-" * 40)
        else:
            print("  (No characters created yet)")
        
        # Display Story Outline Table
        print("\n📖 STORY OUTLINE TABLE")
        print("-" * 60)
        cursor.execute("SELECT * FROM story_outline ORDER BY act, scene")
        scenes = cursor.fetchall()
        
        if scenes:
            current_act = None
            for scene in scenes:
                if scene['act'] != current_act:
                    current_act = scene['act']
                    print(f"\n>>> ACT {current_act} <<<")
                
                print(f"\n[Scene {scene['scene']}]")
                print(f"  Title: {scene['scene_title'] or 'N/A'}")
                print(f"  Location: {scene['location'] or 'N/A'}")
                print(f"  Time: {scene['time_of_day'] or 'N/A'}")
                print(f"  Characters: {scene['characters_present'] or 'N/A'}")
                print(f"  Purpose: {scene['scene_purpose'] or 'N/A'}")
                print(f"  Key Events: {scene['key_events'] or 'N/A'}")
                print(f"  Key Characters: {scene['key_characters'] or 'N/A'}")
                print(f"  Beat: {scene['beat'] or 'N/A'}")
                print(f"  Nudge: {scene['nudge'] or 'N/A'}")
                print(f"  Emotional Beats: {scene['emotional_beats'] or 'N/A'}")
                print(f"  Dialogue Notes: {scene['dialogue_notes'] or 'N/A'}")
                print(f"  Plot Threads: {scene['plot_threads'] or 'N/A'}")
                print(f"  Notes: {scene['notes'] or 'N/A'}")
                print("-" * 40)
        else:
            print("  (No scenes created yet)")
        
        # Summary statistics
        print("\n📈 STATISTICS")
        print("-" * 60)
        print(f"  Total Characters: {len(characters)}")
        print(f"  Total Scenes: {len(scenes)}")
        
        # Count scenes by act
        act_counts = {}
        for scene in scenes:
            act = scene['act']
            act_counts[act] = act_counts.get(act, 0) + 1
        
        if act_counts:
            for act, count in sorted(act_counts.items()):
                print(f"    Act {act}: {count} scenes")
        
        print("\n" + "=" * 60)
        print("✨ End of Project Summary")
        print("=" * 60)
    
    def show_project_summary(self):
        """Display comprehensive project summary."""
        print("\\n📊 Project Summary")
        print("=" * 40)
        
        cursor = self.conn.cursor()
        
        # Project metadata
        cursor.execute("SELECT key, value FROM project_metadata")
        metadata = dict(cursor.fetchall())
        
        print(f"Project: {metadata.get('project_name', 'Unknown')}")
        print(f"Created: {metadata.get('created_date', 'Unknown')}")
        if 'genre' in metadata:
            print(f"Genre: {metadata['genre']}")
        if 'main_theme' in metadata:
            print(f"Theme: {metadata['main_theme']}")
        
        # Character count
        cursor.execute("SELECT COUNT(*) FROM characters")
        char_count = cursor.fetchone()[0]
        print(f"\\nCharacters: {char_count}")
        
        if char_count > 0:
            cursor.execute("SELECT name, role FROM characters ORDER BY id")
            for char in cursor.fetchall():
                role = char['role'] or 'Unknown role'
                print(f"  • {char['name']} ({role})")
        
        # Scene count
        cursor.execute("SELECT COUNT(*) FROM story_outline")
        scene_count = cursor.fetchone()[0]
        print(f"\\nScenes outlined: {scene_count}")
        
        # World building count
        cursor.execute("SELECT COUNT(*) FROM world_building")
        world_count = cursor.fetchone()[0]
        print(f"World elements: {world_count}")
        
        # Research count
        cursor.execute("SELECT COUNT(*) FROM research")
        research_count = cursor.fetchone()[0]
        print(f"Research items: {research_count}")
        
        print("\\n✨ Ready for brainstorming and writing!")


def main():
    """Entry point when running as a script."""
    intake_module = LizzyIntake()
    intake_module.run()


if __name__ == "__main__":
    main()