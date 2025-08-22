#!/usr/bin/env python3
"""
Lizzy Alpha - Enhanced Intake Module
====================================
Enhanced navigation for 30-scene structure with beats, quick jumps, and templates.
Improved user experience for managing large story outlines.

Author: Lizzy AI Writing Framework
"""

import os
import sqlite3
import sys
import json
from datetime import datetime
from pathlib import Path

# Import the base intake functionality
from intake import LizzyIntake


class LizzyIntakeEnhanced(LizzyIntake):
    """
    Enhanced intake with 30-scene navigation and advanced character management.
    """
    
    def manage_characters(self):
        """Enhanced character management with role-based navigation and templates."""
        while True:
            print("\\n🧑‍🤝‍🧑 Character Management (Enhanced):")
            self.show_enhanced_character_summary()
            print("\\n  1. Add/Edit Character (Full Form)")
            print("  2. Navigate by Role")
            print("  3. Search Characters")
            print("  4. Generate Romcom Character Templates")
            print("  5. Character Relationship Map")
            print("  6. Delete Character")
            print("  7. Back to Main Menu")
            
            choice = input("\\nSelect option (1-7): ").strip()
            
            if choice == "1":
                self.character_full_form()
            elif choice == "2":
                self.navigate_by_role()
            elif choice == "3":
                self.search_characters()
            elif choice == "4":
                self.generate_romcom_character_templates()
            elif choice == "5":
                self.show_character_relationships()
            elif choice == "6":
                self.delete_character()
            elif choice == "7":
                break
            else:
                print("❌ Invalid choice. Please select 1-7.")
    
    def show_enhanced_character_summary(self):
        """Display enhanced character summary with roles and completion status."""
        cursor = self.conn.cursor()
        cursor.execute("""SELECT name, role, description, personality_traits, romantic_challenge, 
                                 lovable_trait, comedic_flaw FROM characters ORDER BY 
                                 CASE role 
                                     WHEN 'protagonist' THEN 1
                                     WHEN 'love_interest' THEN 2
                                     WHEN 'supporting' THEN 3
                                     WHEN 'antagonist' THEN 4
                                     ELSE 5
                                 END, name""")
        characters = cursor.fetchall()
        
        if characters:
            print("\\n📊 Character Overview:")
            print(f"   Total Characters: {len(characters)}")
            print("   " + "="*70)
            
            # Group by role
            role_groups = {}
            for char in characters:
                role = char['role'] or 'undefined'
                if role not in role_groups:
                    role_groups[role] = []
                role_groups[role].append(char)
            
            # Display by role priority
            role_order = ['protagonist', 'love_interest', 'supporting', 'antagonist', 'undefined']
            role_icons = {
                'protagonist': '🌟',
                'love_interest': '💕', 
                'supporting': '👥',
                'antagonist': '⚡',
                'undefined': '❓'
            }
            
            for role in role_order:
                if role in role_groups:
                    chars = role_groups[role]
                    print(f"\\n   {role_icons[role]} {role.replace('_', ' ').title()} ({len(chars)}):")
                    
                    for char in chars:
                        # Calculate completion score
                        fields = [char['description'], char['personality_traits'], 
                                char['romantic_challenge'], char['lovable_trait'], char['comedic_flaw']]
                        completed = sum(1 for field in fields if field and field.strip())
                        completion = "✅" if completed >= 4 else "⚠️" if completed >= 2 else "❌"
                        
                        desc = char['description'][:30] + "..." if char['description'] else "No description"
                        print(f"      {completion} {char['name']:<15} | {desc}")
                        
                        # Show essential trinity status
                        trinity = []
                        if char['romantic_challenge']: trinity.append("Challenge✓")
                        if char['lovable_trait']: trinity.append("Lovable✓") 
                        if char['comedic_flaw']: trinity.append("Comedy✓")
                        if trinity:
                            print(f"          Trinity: {', '.join(trinity)}")
            
            # Show missing essentials
            missing_roles = []
            if 'protagonist' not in role_groups: missing_roles.append("Protagonist")
            if 'love_interest' not in role_groups: missing_roles.append("Love Interest")
            
            if missing_roles:
                print(f"\\n   ⚠️  Missing essential roles: {', '.join(missing_roles)}")
        else:
            print("\\n⚪ No characters added yet. Use option 4 to generate romcom templates.")
    
    def navigate_by_role(self):
        """Navigate characters by their roles."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT role FROM characters WHERE role IS NOT NULL ORDER BY role")
        roles = [row['role'] for row in cursor.fetchall()]
        
        if not roles:
            print("\\n⚪ No character roles defined yet.")
            return
        
        print("\\n🎭 Navigate by Character Role:")
        role_display = {
            'protagonist': '🌟 Protagonist',
            'love_interest': '💕 Love Interest',
            'supporting': '👥 Supporting',
            'antagonist': '⚡ Antagonist'
        }
        
        for i, role in enumerate(roles, 1):
            display_name = role_display.get(role, f"📝 {role.title()}")
            print(f"  {i}. {display_name}")
        
        try:
            choice = int(input(f"\\nSelect role (1-{len(roles)}): ")) - 1
            if 0 <= choice < len(roles):
                selected_role = roles[choice]
                cursor.execute("SELECT name, description, romantic_challenge, lovable_trait, comedic_flaw FROM characters WHERE role = ? ORDER BY name", (selected_role,))
                role_chars = cursor.fetchall()
                
                print(f"\\n🎭 {selected_role.replace('_', ' ').title()} Characters:")
                for char in role_chars:
                    print(f"\\n  📝 {char['name']}:")
                    if char['description']:
                        print(f"     Description: {char['description']}")
                    if char['romantic_challenge']:
                        print(f"     🎭 Challenge: {char['romantic_challenge']}")
                    if char['lovable_trait']:
                        print(f"     💝 Lovable: {char['lovable_trait']}")
                    if char['comedic_flaw']:
                        print(f"     😄 Comedy: {char['comedic_flaw']}")
                
                # Quick edit option
                edit_char = input(f"\\nEnter character name to edit or press Enter to go back: ").strip()
                if edit_char:
                    self.edit_character_by_name(edit_char)
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def search_characters(self):
        """Search characters by name, description, or traits."""
        print("\\n🔍 Character Search")
        search_term = input("Enter search term (name, description, trait): ").strip()
        if not search_term:
            return
        
        cursor = self.conn.cursor()
        cursor.execute("""SELECT name, role, description, personality_traits, romantic_challenge, 
                                 lovable_trait, comedic_flaw FROM characters 
                          WHERE name LIKE ? OR description LIKE ? OR personality_traits LIKE ? 
                             OR romantic_challenge LIKE ? OR lovable_trait LIKE ? OR comedic_flaw LIKE ?
                          ORDER BY name""", 
                      (f"%{search_term}%",) * 6)
        results = cursor.fetchall()
        
        if results:
            print(f"\\n🔍 Found {len(results)} matching characters:")
            for char in results:
                role = char['role'] or 'undefined'
                desc = char['description'][:40] + "..." if char['description'] else "No description"
                print(f"\\n  📝 {char['name']} ({role})")
                print(f"     {desc}")
                
                # Show which field matched
                fields_to_check = {
                    'description': char['description'],
                    'personality': char['personality_traits'],
                    'challenge': char['romantic_challenge'],
                    'lovable trait': char['lovable_trait'],
                    'comedic flaw': char['comedic_flaw']
                }
                
                matches = []
                for field_name, field_value in fields_to_check.items():
                    if field_value and search_term.lower() in field_value.lower():
                        matches.append(field_name)
                
                if matches:
                    print(f"     Matches in: {', '.join(matches)}")
            
            # Edit option
            edit_choice = input("\\nEnter character name to edit or press Enter to go back: ").strip()
            if edit_choice:
                self.edit_character_by_name(edit_choice)
        else:
            print(f"\\n❌ No characters found matching '{search_term}'")
    
    def generate_romcom_character_templates(self):
        """Generate romantic comedy character archetypes."""
        print("\\n✨ Romantic Comedy Character Templates")
        print("Generate professional romcom archetypes with essential trinity traits.")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM characters")
        existing_chars = [row['name'] for row in cursor.fetchall()]
        
        print(f"\\nCurrent characters: {len(existing_chars)}")
        if existing_chars:
            print(f"  Existing: {', '.join(existing_chars)}")
        
        print("\\nAvailable Templates:")
        print("  1. Generate Core Duo (Protagonist + Love Interest)")
        print("  2. Generate Supporting Cast (Best Friend + Rival)")
        print("  3. Generate Full Ensemble (All 4 archetypes)")
        print("  4. Custom Single Character")
        print("  5. Back")
        
        choice = input("\\nSelect template (1-5): ").strip()
        
        if choice == "1":
            self.create_core_duo_templates()
        elif choice == "2":
            self.create_supporting_templates()
        elif choice == "3":
            self.create_full_ensemble_templates()
        elif choice == "4":
            self.create_custom_character_template()
    
    def create_core_duo_templates(self):
        """Create protagonist and love interest templates."""
        templates = [
            {
                'name': 'Sarah',
                'role': 'protagonist',
                'description': 'Determined career woman with expressive eyes and impeccable style',
                'personality_traits': 'ambitious, organized, secretly vulnerable, perfectionist',
                'backstory': 'Youngest of three sisters, always felt need to prove herself. Lost her father young, drove her to succeed.',
                'goals': 'Wants to make partner at law firm, but really needs to learn to trust others',
                'conflicts': 'External: competing for promotion. Internal: fear of being vulnerable after past heartbreak',
                'romantic_challenge': 'believes vulnerability equals weakness',
                'lovable_trait': 'remembers everyone\'s coffee orders and birthdays',
                'comedic_flaw': 'catastrophically overthinks everything'
            },
            {
                'name': 'Jake',
                'role': 'love_interest', 
                'description': 'Charming entrepreneur with warm smile and casual confidence',
                'personality_traits': 'spontaneous, empathetic, optimistic, slightly disorganized',
                'backstory': 'Grew up in small town, moved to city to start food truck business. Values experiences over possessions.',
                'goals': 'Wants to open restaurant, but really needs to learn it\'s okay to plan ahead',
                'conflicts': 'External: struggling to secure restaurant funding. Internal: fear of being tied down',
                'romantic_challenge': 'avoids commitment because thinks it kills spontaneity',
                'lovable_trait': 'stops to help strangers and always tips generously',
                'comedic_flaw': 'magnetically attracts minor disasters'
            }
        ]
        
        self.insert_character_templates(templates)
    
    def create_supporting_templates(self):
        """Create best friend and rival templates."""
        templates = [
            {
                'name': 'Maya',
                'role': 'supporting',
                'description': 'Vivacious best friend with infectious laugh and bold fashion choices',
                'personality_traits': 'loyal, brutally honest, fun-loving, wise beyond her years',
                'backstory': 'Childhood friend who stayed local. Owns vintage boutique. Been through her own heartbreak.',
                'goals': 'Wants to expand business, but really wants to see her friend happy',
                'conflicts': 'External: competing boutiques. Internal: worried about being left behind',
                'romantic_challenge': 'gives great advice but terrible at taking it',
                'lovable_trait': 'drops everything to help friends in crisis',
                'comedic_flaw': 'speaks in movie quotes when emotional'
            },
            {
                'name': 'Victoria',
                'role': 'antagonist',
                'description': 'Polished rival with sharp wit and designer everything',
                'personality_traits': 'competitive, intelligent, insecure beneath surface, surprisingly principled',
                'backstory': 'Grew up wealthy but emotionally neglected. Uses success to prove worth to absent parents.',
                'goals': 'Wants recognition and respect, but really needs genuine connection',
                'conflicts': 'External: competing for same opportunities. Internal: fear of being truly known',
                'romantic_challenge': 'believes love is weakness in competitive world',
                'lovable_trait': 'secretly mentors younger colleagues',
                'comedic_flaw': 'completely helpless with anything domestic'
            }
        ]
        
        self.insert_character_templates(templates)
    
    def create_full_ensemble_templates(self):
        """Create all four main character archetypes."""
        self.create_core_duo_templates()
        self.create_supporting_templates()
        print("\\n✨ Full ensemble created! You now have all four essential romcom archetypes.")
    
    def create_custom_character_template(self):
        """Create a custom character with guided prompts."""
        print("\\n🎭 Custom Character Creator")
        
        roles = {
            '1': 'protagonist',
            '2': 'love_interest', 
            '3': 'supporting',
            '4': 'antagonist',
            '5': 'mentor'
        }
        
        print("\\nSelect character role:")
        for key, role in roles.items():
            print(f"  {key}. {role.replace('_', ' ').title()}")
        
        role_choice = input("\\nEnter choice: ").strip()
        if role_choice not in roles:
            print("❌ Invalid choice")
            return
        
        selected_role = roles[role_choice]
        
        # Get basic info
        name = input(f"\\nCharacter name for {selected_role}: ").strip()
        if not name:
            print("❌ Name required")
            return
        
        # Check if exists
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM characters WHERE name = ?", (name,))
        if cursor.fetchone():
            print(f"❌ Character '{name}' already exists")
            return
        
        # Quick template generation
        template = {
            'name': name,
            'role': selected_role,
            'description': f'[Generated {selected_role.replace("_", " ")} - customize as needed]',
            'personality_traits': '[Add 3-4 key personality traits]',
            'backstory': '[Add formative background and history]',
            'goals': '[What they want vs what they need]',
            'conflicts': '[External and internal obstacles]',
            'romantic_challenge': '[What prevents them from love]',
            'lovable_trait': '[What makes them endearing]',
            'comedic_flaw': '[What makes them funny]'
        }
        
        self.insert_character_templates([template])
        print(f"\\n✅ Created template for {name}. Use 'Edit Character' to customize details.")
    
    def insert_character_templates(self, templates):
        """Insert character templates into database."""
        cursor = self.conn.cursor()
        added_count = 0
        skipped = []
        
        for template in templates:
            # Check if character already exists
            cursor.execute("SELECT name FROM characters WHERE name = ?", (template['name'],))
            if cursor.fetchone():
                skipped.append(template['name'])
                continue
            
            cursor.execute("""
                INSERT INTO characters (name, role, description, personality_traits, 
                                      backstory, goals, conflicts, romantic_challenge,
                                      lovable_trait, comedic_flaw)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template['name'], template['role'], template['description'],
                template['personality_traits'], template['backstory'], template['goals'],
                template['conflicts'], template['romantic_challenge'],
                template['lovable_trait'], template['comedic_flaw']
            ))
            added_count += 1
        
        self.conn.commit()
        
        print(f"\\n✅ Added {added_count} character templates")
        if skipped:
            print(f"⚠️  Skipped existing characters: {', '.join(skipped)}")
    
    def show_character_relationships(self):
        """Display character relationship map."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, role, description FROM characters ORDER BY role, name")
        characters = cursor.fetchall()
        
        if len(characters) < 2:
            print("\\n⚪ Need at least 2 characters to show relationships")
            return
        
        print("\\n🌐 Character Relationship Map")
        print("=" * 50)
        
        # Group characters by role
        role_groups = {}
        for char in characters:
            role = char['role'] or 'undefined'
            if role not in role_groups:
                role_groups[role] = []
            role_groups[role].append(char)
        
        # Show potential relationships
        if 'protagonist' in role_groups and 'love_interest' in role_groups:
            protag = role_groups['protagonist'][0]['name']
            love = role_groups['love_interest'][0]['name']
            print(f"💕 Central Romance: {protag} ↔ {love}")
        
        if 'protagonist' in role_groups and 'supporting' in role_groups:
            protag = role_groups['protagonist'][0]['name']
            support = role_groups['supporting'][0]['name']
            print(f"👯 Best Friends: {protag} ↔ {support}")
        
        if 'protagonist' in role_groups and 'antagonist' in role_groups:
            protag = role_groups['protagonist'][0]['name']
            antag = role_groups['antagonist'][0]['name']
            print(f"⚡ Rivalry: {protag} ↔ {antag}")
        
        # Show all characters with descriptions
        print(f"\\n📝 Cast Overview ({len(characters)} characters):")
        for char in characters:
            role_icon = {'protagonist': '🌟', 'love_interest': '💕', 
                        'supporting': '👥', 'antagonist': '⚡'}.get(char['role'], '📝')
            desc = char['description'][:40] + "..." if char['description'] else "No description"
            print(f"  {role_icon} {char['name']}: {desc}")
    
    def edit_character_by_name(self, name: str):
        """Edit a character by name with enhanced form."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE name LIKE ?", (f"%{name}%",))
        matches = cursor.fetchall()
        
        if not matches:
            print(f"❌ No character found matching '{name}'")
            return
        elif len(matches) > 1:
            print(f"\\n🔍 Multiple matches found:")
            for i, char in enumerate(matches, 1):
                print(f"  {i}. {char['name']} ({char['role'] or 'no role'})")
            
            try:
                choice = int(input(f"\\nSelect character (1-{len(matches)}): ")) - 1
                if 0 <= choice < len(matches):
                    selected_char = matches[choice]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                print("❌ Please enter a valid number")
                return
        else:
            selected_char = matches[0]
        
        # Show current character info
        print(f"\\n📝 Editing: {selected_char['name']}")
        print(f"   Role: {selected_char['role'] or 'No role set'}")
        if selected_char['description']:
            print(f"   Description: {selected_char['description'][:50]}...")
        
        # Use the existing character_full_form but pre-populate with this character
        print("\\nOpening character editor...")
        self.character_full_form()
    
    def manage_outline(self):
        """Enhanced 30-scene outline management with easy navigation."""
        while True:
            print("\\n📖 Story Outline Management (30-Scene Structure):")
            self.show_enhanced_outline_summary()
            print("\\n  1. Add/Edit Scene (Full Form)")
            print("  2. Quick Jump to Scene")
            print("  3. Navigate by Beat")
            print("  4. Delete Scene")
            print("  5. Generate 30-Scene Template")
            print("  6. Back to Main Menu")
            
            choice = input("\\nSelect option (1-6): ").strip()
            
            if choice == "1":
                self.scene_full_form()
            elif choice == "2":
                self.quick_jump_to_scene()
            elif choice == "3":
                self.navigate_by_beat()
            elif choice == "4":
                self.delete_scene()
            elif choice == "5":
                self.generate_30_scene_template()
            elif choice == "6":
                break
            else:
                print("❌ Invalid choice. Please select 1-6.")
    
    def show_enhanced_outline_summary(self):
        """Display enhanced story outline with beats and progress."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT act, scene, beat, scene_title, scene_purpose FROM story_outline ORDER BY act, scene")
        scenes = cursor.fetchall()
        
        if scenes:
            print("\\n📊 Current 30-Scene Outline:")
            print(f"   Progress: {len(scenes)}/30 scenes created")
            print("   " + "="*60)
            
            current_act = None
            act_counts = {1: 0, 2: 0, 3: 0}
            
            for scene in scenes:
                act_counts[scene['act']] += 1
                
                if scene['act'] != current_act:
                    current_act = scene['act']
                    expected = {1: 12, 2: 16, 3: 8}[current_act]
                    actual = act_counts[current_act] if current_act <= 3 else 0
                    print(f"\\n   🎬 ACT {current_act} ({actual}/{expected} scenes):")
                
                title = scene['scene_title'] or "Untitled"
                beat = scene['beat'] or "No beat"
                purpose = scene['scene_purpose'] or "No purpose"
                
                # Visual indicator for completion
                status = "✅" if title != "Untitled" else "⚪"
                print(f"      {status} Scene {scene['scene']:2d}: {beat:<20} | {title:<25} ({purpose})")
                
            # Show missing scenes
            expected_total = {1: 12, 2: 16, 3: 8}
            for act_num in [1, 2, 3]:
                missing = expected_total[act_num] - act_counts.get(act_num, 0)
                if missing > 0:
                    print(f"\\n   ⚠️  Act {act_num} missing {missing} scenes")
        else:
            print("\\n⚪ No scenes added yet. Use option 5 to generate 30-scene template.")
    
    def quick_jump_to_scene(self):
        """Quick navigation to specific scenes."""
        print("\\n🎯 Quick Scene Navigation")
        print("\\nJump Options:")
        print("  1. Go to specific scene (e.g., 'Act 2, Scene 15')")
        print("  2. Go to specific act")
        print("  3. Find scene by title")
        print("  4. Back")
        
        choice = input("\\nSelect option: ").strip()
        
        if choice == "1":
            try:
                act = int(input("Enter Act (1-3): "))
                scene = int(input("Enter Scene: "))
                if 1 <= act <= 3:
                    self.edit_specific_scene(act, scene)
                else:
                    print("❌ Act must be 1, 2, or 3")
            except ValueError:
                print("❌ Please enter valid numbers")
        elif choice == "2":
            try:
                act = int(input("Enter Act (1-3): "))
                if 1 <= act <= 3:
                    self.show_act_scenes(act)
                else:
                    print("❌ Act must be 1, 2, or 3")
            except ValueError:
                print("❌ Please enter valid number")
        elif choice == "3":
            self.find_scene_by_title()
    
    def navigate_by_beat(self):
        """Navigate scenes organized by story beat."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT beat FROM story_outline WHERE beat IS NOT NULL ORDER BY beat")
        beats = [row['beat'] for row in cursor.fetchall()]
        
        if not beats:
            print("\\n⚪ No beats defined yet. Generate 30-scene template first.")
            return
        
        print("\\n🎵 Navigate by Story Beat:")
        for i, beat in enumerate(beats, 1):
            print(f"  {i}. {beat}")
        
        try:
            choice = int(input(f"\\nSelect beat (1-{len(beats)}): ")) - 1
            if 0 <= choice < len(beats):
                selected_beat = beats[choice]
                cursor.execute("SELECT act, scene, scene_title FROM story_outline WHERE beat = ? ORDER BY act, scene", (selected_beat,))
                scenes = cursor.fetchall()
                
                print(f"\\n📝 Scenes for '{selected_beat}':")
                for scene in scenes:
                    title = scene['scene_title'] or "Untitled"
                    print(f"  Act {scene['act']}, Scene {scene['scene']}: {title}")
                
                # Option to edit one of these scenes
                edit_choice = input("\\nEnter Act,Scene to edit (e.g., '2,15') or press Enter to go back: ").strip()
                if edit_choice:
                    try:
                        act, scene_num = map(int, edit_choice.split(','))
                        self.edit_specific_scene(act, scene_num)
                    except ValueError:
                        print("❌ Invalid format. Use 'Act,Scene' like '2,15'")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def show_act_scenes(self, act: int):
        """Show all scenes in a specific act."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT scene, beat, scene_title, scene_purpose FROM story_outline WHERE act = ? ORDER BY scene", (act,))
        scenes = cursor.fetchall()
        
        expected_count = {1: 12, 2: 16, 3: 8}[act]
        print(f"\\n🎬 Act {act} Scenes ({len(scenes)}/{expected_count}):")
        
        if scenes:
            for scene in scenes:
                title = scene['scene_title'] or "Untitled"
                beat = scene['beat'] or "No beat"
                purpose = scene['scene_purpose'] or "No purpose"
                status = "✅" if title != "Untitled" else "⚪"
                print(f"  {status} Scene {scene['scene']:2d}: {beat:<20} | {title} ({purpose})")
        else:
            print(f"  ⚪ No scenes in Act {act} yet")
        
        # Quick edit option
        edit_scene = input(f"\\nEnter scene number to edit (1-{expected_count}) or press Enter to go back: ").strip()
        if edit_scene.isdigit():
            scene_num = int(edit_scene)
            self.edit_specific_scene(act, scene_num)
    
    def find_scene_by_title(self):
        """Search for scenes by title."""
        search = input("\\nEnter part of scene title to search: ").strip()
        if not search:
            return
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT act, scene, scene_title, beat FROM story_outline WHERE scene_title LIKE ? ORDER BY act, scene", (f"%{search}%",))
        results = cursor.fetchall()
        
        if results:
            print(f"\\n🔍 Found {len(results)} matching scenes:")
            for result in results:
                title = result['scene_title'] or "Untitled"
                beat = result['beat'] or "No beat"
                print(f"  Act {result['act']}, Scene {result['scene']}: {title} ({beat})")
            
            # Option to edit
            edit_choice = input("\\nEnter Act,Scene to edit (e.g., '2,15') or press Enter to go back: ").strip()
            if edit_choice:
                try:
                    act, scene_num = map(int, edit_choice.split(','))
                    self.edit_specific_scene(act, scene_num)
                except ValueError:
                    print("❌ Invalid format. Use 'Act,Scene' like '2,15'")
        else:
            print(f"\\n❌ No scenes found matching '{search}'")
    
    def edit_specific_scene(self, act: int, scene: int):
        """Edit a specific scene by act and scene number."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, act, scene, beat, scene_title, location, time_of_day, characters_present, scene_purpose, key_events, key_characters, nudge, emotional_beats, dialogue_notes, plot_threads, notes FROM story_outline WHERE act = ? AND scene = ?", (act, scene))
        row = cursor.fetchone()
        
        if row:
            # Convert tuple to dictionary for easier access
            scene_data = {
                'id': row[0], 'act': row[1], 'scene': row[2], 'beat': row[3],
                'scene_title': row[4], 'location': row[5], 'time_of_day': row[6],
                'characters_present': row[7], 'scene_purpose': row[8], 'key_events': row[9],
                'key_characters': row[10], 'nudge': row[11], 'emotional_beats': row[12],
                'dialogue_notes': row[13], 'plot_threads': row[14], 'notes': row[15]
            }
            
            print(f"\\n📝 Editing Act {act}, Scene {scene}")
            if scene_data['beat']:
                print(f"   Beat: {scene_data['beat']}")
            if scene_data['scene_title']:
                print(f"   Current Title: {scene_data['scene_title']}")
            print()
            # Call the existing scene form with pre-filled act/scene
            self.scene_full_form_with_preset(act, scene)
        else:
            print(f"\\n⚪ Act {act}, Scene {scene} doesn't exist. Would you like to create it?")
            create = input("Create scene? (y/N): ").strip().lower()
            if create in ['y', 'yes']:
                self.scene_full_form_with_preset(act, scene)
    
    def scene_full_form_with_preset(self, preset_act: int = None, preset_scene: int = None):
        """Scene form with optional preset act/scene."""
        cursor = self.conn.cursor()
        
        # Get act and scene numbers (with presets)
        if preset_act and preset_scene:
            act, scene = preset_act, preset_scene
            print(f"Editing Act {act}, Scene {scene}")
        else:
            try:
                act = int(input("\\nAct number: "))
                scene = int(input("Scene number: "))
            except ValueError:
                print("❌ Act and scene must be numbers.")
                return
        
        # Check for existing scene
        cursor.execute("SELECT id, act, scene, beat, scene_title, location, time_of_day, characters_present, scene_purpose, key_events, key_characters, nudge, emotional_beats, dialogue_notes, plot_threads, notes FROM story_outline WHERE act = ? AND scene = ?", (act, scene))
        row = cursor.fetchone()
        
        if row:
            # Convert tuple to dictionary for easier access
            scene_data = {
                'id': row[0], 'act': row[1], 'scene': row[2], 'beat': row[3],
                'scene_title': row[4], 'location': row[5], 'time_of_day': row[6],
                'characters_present': row[7], 'scene_purpose': row[8], 'key_events': row[9],
                'key_characters': row[10], 'nudge': row[11], 'emotional_beats': row[12],
                'dialogue_notes': row[13], 'plot_threads': row[14], 'notes': row[15]
            }
            print(f"\\n📝 Editing: Act {act}, Scene {scene}")
            if scene_data.get('beat'):
                print(f"   Story Beat: {scene_data['beat']}")
            print("Press Enter to keep existing value")
        else:
            scene_data = {}
            print(f"\\n✨ Creating: Act {act}, Scene {scene}")
        
        print("\\n" + "=" * 40)
        print("Complete all fields for this scene")
        print("=" * 40 + "\\n")
        
        # Get available characters for reference
        cursor.execute("SELECT name FROM characters ORDER BY name")
        char_names = [row[0] for row in cursor.fetchall()]  # row[0] = name
        if char_names:
            print(f"Available characters: {', '.join(char_names)}\\n")
        
        # Comprehensive field collection
        fields = {
            'scene_title': ("Scene Title", "Brief descriptive title for the scene"),
            'location': ("Location", "Where does this scene take place?"),
            'time_of_day': ("Time of Day", "morning/afternoon/evening/night"),
            'characters_present': ("Characters Present", "Comma-separated list of characters"),
            'scene_purpose': ("Scene Purpose", "setup/conflict/climax/resolution"),
            'key_events': ("Key Events", "What happens in this scene?"),
            'emotional_beats': ("Emotional Beats", "Emotional journey in the scene"),
            'dialogue_notes': ("Dialogue Notes", "Key dialogue or conversation points"),
            'plot_threads': ("Plot Threads", "Which subplots are advanced?"),
            'notes': ("Additional Notes", "Any other important information")
        }
        
        new_data = {'act': act, 'scene': scene}
        
        for field, (label, help_text) in fields.items():
            print(f"\\n{label}:")
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
                    print(f"\\n✅ Updated Act {act}, Scene {scene}")
                else:
                    print("\\nNo changes made.")
            else:  # Insert new
                field_names = list(new_data.keys())
                placeholders = ", ".join(["?" for _ in field_names])
                fields_str = ", ".join(field_names)
                
                cursor.execute(f'''
                    INSERT INTO story_outline ({fields_str})
                    VALUES ({placeholders})
                ''', list(new_data.values()))
                
                self.conn.commit()
                print(f"\\n✅ Added Act {act}, Scene {scene}")
                
        except sqlite3.IntegrityError:
            print(f"\\n❌ Act {act}, Scene {scene} already exists. Please edit it instead.")
        except sqlite3.Error as e:
            print(f"\\n❌ Database error: {e}")
    
    def generate_30_scene_template(self):
        """Generate complete 30-scene template with beats."""
        print("\\n🎭 Generate 30-Scene Template")
        print("This will create all 30 scene placeholders with proper beats.")
        print("⚠️  This will not overwrite existing scenes.")
        
        confirm = input("\\nProceed? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            return
        
        # 30-scene template with beats
        template_scenes = [
            # Act 1 (12 scenes)
            (1, 1, "Opening Image", "Chemical Equation", "setup"),
            (1, 2, "Opening Image", "Emotional Baseline", "setup"),
            (1, 3, "Meet Cute", "First Encounter", "setup"),
            (1, 4, "Meet Cute", "Memorable Meeting", "setup"),
            (1, 5, "Reaction", "First Impressions", "setup"),
            (1, 6, "Reaction", "Processing", "setup"),
            (1, 7, "Romantic Complication", "The Obstacle", "setup"),
            (1, 8, "Romantic Complication", "Why Not Together", "setup"),
            (1, 9, "Raise Stakes", "What Matters", "setup"),
            (1, 10, "Raise Stakes", "Time Pressure", "setup"),
            (1, 11, "Break into Act II", "Commitment", "setup"),
            (1, 12, "Break into Act II", "New Territory", "setup"),
            
            # Act 2 (16 scenes)
            (2, 13, "Fun & Games", "Romance Promise", "conflict"),
            (2, 14, "Fun & Games", "Bonding Montage", "conflict"),
            (2, 15, "Midpoint Hook", "Game Changer", "conflict"),
            (2, 16, "Midpoint Hook", "Raised Stakes", "conflict"),
            (2, 17, "External/Internal Tensions", "First Cracks", "conflict"),
            (2, 18, "External/Internal Tensions", "Growing Problems", "conflict"),
            (2, 19, "Lose Beat", "All Seems Lost", "conflict"),
            (2, 20, "Lose Beat", "Lowest Point", "conflict"),
            (2, 21, "Self-Revelation", "What Must Change", "conflict"),
            (2, 22, "Self-Revelation", "True Feelings", "conflict"),
            
            # Act 3 (8 scenes) - Note: scenes 23-30 map to scenes 1-8 in Act 3
            (3, 1, "Grand Gesture", "Big Romantic Action", "climax"),
            (3, 2, "Grand Gesture", "Proof of Change", "climax"),
            (3, 3, "Reunion", "Coming Together", "resolution"),
            (3, 4, "Reunion", "Understanding", "resolution"),
            (3, 5, "Happy Ending", "Resolution", "resolution"),
            (3, 6, "Happy Ending", "Celebration", "resolution"),
            (3, 7, "Final Image", "Transformation", "resolution"),
            (3, 8, "Final Image", "New Equilibrium", "resolution"),
        ]
        
        cursor = self.conn.cursor()
        added_count = 0
        
        for act, scene, beat, title, purpose in template_scenes:
            # Check if scene already exists
            cursor.execute("SELECT * FROM story_outline WHERE act = ? AND scene = ?", (act, scene))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO story_outline (act, scene, beat, scene_title, scene_purpose)
                    VALUES (?, ?, ?, ?, ?)
                ''', (act, scene, beat, title, purpose))
                added_count += 1
        
        self.conn.commit()
        print(f"\\n✅ Added {added_count} scene templates.")
        print("✨ You now have the complete 30-scene structure!")
        print("   Use navigation options to fill in details for each scene.")


def main():
    """Entry point for the enhanced intake module."""
    intake_module = LizzyIntakeEnhanced()
    intake_module.run()


if __name__ == "__main__":
    main()