#!/usr/bin/env python3
"""
Lizzy Alpha - Simple Intake Module
=================================
Streamlined story development focusing on logline and 30-scene outline.

Author: Lizzy AI Writing Framework
"""

import sqlite3
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import print as rprint


class SimpleIntake:
    """Simplified intake focused on logline and scene outline."""
    
    def __init__(self, base_dir: str = "projects"):
        self.base_dir = Path(base_dir)
        self.project_name = None
        self.db_path = None
        self.conn = None
        self.console = Console()
        self.rich_available = True
    
    def check_visidata(self) -> bool:
        """Check if VisiData is available."""
        try:
            subprocess.run(['vd', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def setup_project(self) -> bool:
        """Connect to existing project (must run start.py first)."""
        print("📖 Lizzy Alpha - Simple Story Intake")
        print("=" * 40)
        
        # Create base directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # List existing projects
        existing_projects = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        if not existing_projects:
            print("❌ No projects found. Run 'python start.py' first to create a project.")
            return False
        
        print("📂 Available projects:")
        for i, project in enumerate(existing_projects, 1):
            print(f"  {i}. {project}")
        print()
        
        while True:
            try:
                choice = input("Select project number: ").strip()
                if not choice:
                    continue
                
                idx = int(choice) - 1
                if 0 <= idx < len(existing_projects):
                    self.project_name = existing_projects[idx]
                    break
                else:
                    print("❌ Invalid selection.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Connect to database
        project_dir = self.base_dir / self.project_name
        self.db_path = project_dir / f"{self.project_name}.sqlite"
        
        if not self.db_path.exists():
            print(f"❌ Database not found for {self.project_name}. Run 'python start.py' first.")
            return False
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            print(f"✅ Connected to project: {self.project_name}")
            return True
        except sqlite3.Error as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def setup_tables(self):
        """Ensure we have the essential tables."""
        cursor = self.conn.cursor()
        
        # Simple logline table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_logline (
                id INTEGER PRIMARY KEY,
                logline TEXT,
                notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default logline if empty
        cursor.execute("SELECT COUNT(*) FROM project_logline")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO project_logline (logline, notes) 
                VALUES ('Write your one-sentence story summary here...', 'The logline should capture the essence of your romantic comedy')
            """)
        
        # Add character templates if characters table is empty
        cursor.execute("SELECT COUNT(*) FROM characters")
        if cursor.fetchone()[0] == 0:
            self.setup_character_templates()
        
        # Add 30-scene template if story_outline table is empty
        cursor.execute("SELECT COUNT(*) FROM story_outline")
        if cursor.fetchone()[0] == 0:
            self.setup_30_scene_template()
        
        self.conn.commit()
    
    def setup_character_templates(self):
        """Add basic character templates."""
        cursor = self.conn.cursor()
        
        templates = [
            {
                'name': 'Protagonist (EDIT NAME)',
                'role': 'protagonist', 
                'description': 'Main character - the one we root for',
                'romantic_challenge': 'What prevents them from opening their heart?',
                'lovable_trait': 'What makes audiences fall in love with them?',
                'comedic_flaw': 'What creates funny situations?'
            },
            {
                'name': 'Love Interest (EDIT NAME)',
                'role': 'love_interest',
                'description': 'The romantic counterpart',
                'romantic_challenge': 'What keeps them from committing?',
                'lovable_trait': 'What draws the protagonist to them?',
                'comedic_flaw': 'Their amusing weakness'
            },
            {
                'name': 'Best Friend (EDIT NAME)', 
                'role': 'supporting',
                'description': 'Voice of wisdom (or chaos)',
                'comedic_flaw': 'Over-the-top personality quirk'
            }
        ]
        
        for template in templates:
            columns = ', '.join(template.keys())
            placeholders = ', '.join(['?' for _ in template])
            
            cursor.execute(f'''
                INSERT INTO characters ({columns})
                VALUES ({placeholders})
            ''', list(template.values()))
    
    def setup_30_scene_template(self):
        """Add the 30-scene professional template."""
        cursor = self.conn.cursor()
        
        # Professional 30-scene romantic comedy structure
        template_scenes = [
            # Act 1 (12 scenes)
            (1, 1, "Opening Image", "Chemical Equation", "Establish the world and protagonist starting point"),
            (1, 2, "Theme Stated", "Emotional Baseline", "Introduce the theme through dialogue or action"),
            (1, 3, "Set-Up", "Meet Cute", "The moment when romantic leads first encounter each other"),
            (1, 4, "Set-Up", "Meet Cute", "Initial romantic spark that creates future romantic momentum"),
            (1, 5, "Catalyst", "Status Quo", "Show the characters need to leave their normal routines"),
            (1, 6, "Catalyst", "Get Out", "Show an event that disrupts the normal routines"),
            (1, 7, "Debate", "Romantic Complication", "Why they can't and won't fall for each other"),
            (1, 8, "Debate", "Romantic Complication", "One of the main characters denies their feelings"),
            (1, 9, "Break Into Two", "Best Bet", "Dramatic pressure at deadline"),
            (1, 10, "Break Into Two", "Best Bet", "The most obvious solution to the deadline"),
            (1, 11, "B Story", "Complication/Tension Rise", "Second lead's reveal"),
            (1, 12, "B Story", "First Revelation", "Characters begin seeing how love works"),
            
            # Act 2 (12 scenes)  
            (2, 13, "Fun & Games", "Romance Develops", "Main characters bonding and falling in love"),
            (2, 14, "Fun & Games", "Subplot Development", "Subplot characters learn about bonding moments"),
            (2, 15, "Fun & Games", "Deepening Connection", "The sense of connection grows stronger"),
            (2, 16, "Fun & Games", "Realizations", "Making realizations about their relationship"),
            (2, 17, "Midpoint", "Relationship Peak", "Relationship appears destined to succeed"),
            (2, 18, "Midpoint", "Turning Point", "Major shift - false victory or defeat"),
            (2, 19, "Bad Guys Close In", "External Pressure", "External forces threaten the relationship"),
            (2, 20, "Bad Guys Close In", "Internal Doubt", "Internal conflicts create problems"),
            (2, 21, "All Is Lost", "Rock Bottom", "All seems lost - the relationship appears doomed"),
            (2, 22, "All Is Lost", "Lowest Point", "Characters at their absolute lowest point"),
            (2, 23, "Dark Night of Soul", "Self-Revelation", "Confronting their worst fears about love"),
            (2, 24, "Break into Three", "New Understanding", "New understanding of what love requires"),
            
            # Act 3 (6 scenes)
            (3, 25, "Finale", "Grand Gesture", "Big romantic action to win back love"),
            (3, 26, "Finale", "Proof of Change", "Demonstrating real growth and change"),
            (3, 27, "Finale", "Climactic Choice", "The final choice between old and new self"),
            (3, 28, "Finale", "Resolution", "Resolution of the central conflict"),
            (3, 29, "Final Image", "New World", "Characters in their new reality"),
            (3, 30, "Final Image", "Transformation Complete", "Final image showing complete transformation")
        ]
        
        for act, scene, beat, scene_title, description in template_scenes:
            cursor.execute("""
                INSERT INTO story_outline 
                (act, scene, beat, scene_title, scene_purpose, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (act, scene, beat, scene_title, description, "Professional 30-scene template"))
        
        print("✅ Added 30-scene professional template")
    
    def edit_with_visidata(self, table_name: str, title: str) -> bool:
        """Launch VisiData to edit a specific table."""
        if not self.visidata_available:
            print("⚠️  VisiData not available. Install with: pip install visidata")
            return False
        
        print(f"\n📊 {title}")
        print("=" * 50)
        print("VisiData Controls:")
        print("  • Navigate: Arrow keys")
        print("  • Edit cell: Enter, then type")
        print("  • Save: Ctrl+S")
        print("  • Quit: 'q'")
        print()
        input("Press Enter to launch VisiData...")
        
        try:
            cmd = ['vd', str(self.db_path), '-S', table_name]
            subprocess.run(cmd, check=False)
            print("✅ Editing complete")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def show_current_outline(self):
        """Show data in proper table format."""
        cursor = self.conn.cursor()
        
        # Show logline table
        print(f"\n📝 LOGLINE TABLE")
        print("=" * 80)
        cursor.execute("SELECT id, logline, notes FROM project_logline")
        loglines = cursor.fetchall()
        if loglines:
            print(f"{'ID':<3} {'LOGLINE':<50} {'NOTES':<25}")
            print("-" * 80)
            for row in loglines:
                logline = (row[1][:47] + "...") if len(row[1]) > 50 else row[1]
                notes = (row[2][:22] + "...") if row[2] and len(row[2]) > 25 else (row[2] or "")
                print(f"{row[0]:<3} {logline:<50} {notes:<25}")
        else:
            print("No logline data")
        
        # Show characters table
        print(f"\n👥 CHARACTERS TABLE")
        print("=" * 100)
        cursor.execute("SELECT id, name, role, romantic_challenge, lovable_trait, comedic_flaw FROM characters ORDER BY role")
        characters = cursor.fetchall()
        if characters:
            print(f"{'ID':<3} {'NAME':<20} {'ROLE':<15} {'ROMANTIC CHALLENGE':<25} {'LOVABLE TRAIT':<20} {'COMEDIC FLAW':<15}")
            print("-" * 100)
            for row in characters:
                name = (row[1][:17] + "...") if len(row[1]) > 20 else row[1]
                role = (row[2][:12] + "...") if row[2] and len(row[2]) > 15 else (row[2] or "")
                challenge = (row[3][:22] + "...") if row[3] and len(row[3]) > 25 else (row[3] or "")
                trait = (row[4][:17] + "...") if row[4] and len(row[4]) > 20 else (row[4] or "")
                flaw = (row[5][:12] + "...") if row[5] and len(row[5]) > 15 else (row[5] or "")
                print(f"{row[0]:<3} {name:<20} {role:<15} {challenge:<25} {trait:<20} {flaw:<15}")
        else:
            print("No character data")
        
        # Show story outline table (first 10 scenes to avoid overwhelming)
        print(f"\n📖 STORY OUTLINE TABLE (showing first 10 scenes)")
        print("=" * 120)
        cursor.execute("SELECT act, scene, beat, scene_title, location, characters_present, scene_purpose FROM story_outline ORDER BY act, scene LIMIT 10")
        scenes = cursor.fetchall()
        if scenes:
            print(f"{'ACT':<3} {'SC':<3} {'BEAT':<15} {'TITLE':<20} {'LOCATION':<15} {'CHARACTERS':<20} {'PURPOSE':<35}")
            print("-" * 120)
            for row in scenes:
                beat = (row[2][:12] + "...") if row[2] and len(row[2]) > 15 else (row[2] or "")
                title = (row[3][:17] + "...") if row[3] and len(row[3]) > 20 else (row[3] or "")
                location = (row[4][:12] + "...") if row[4] and len(row[4]) > 15 else (row[4] or "")
                chars = (row[5][:17] + "...") if row[5] and len(row[5]) > 20 else (row[5] or "")
                purpose = (row[6][:32] + "...") if row[6] and len(row[6]) > 35 else (row[6] or "")
                print(f"{row[0]:<3} {row[1]:<3} {beat:<15} {title:<20} {location:<15} {chars:<20} {purpose:<35}")
            
            # Show count of remaining scenes
            cursor.execute("SELECT COUNT(*) FROM story_outline")
            total = cursor.fetchone()[0]
            if total > 10:
                print(f"\n... and {total - 10} more scenes (use VisiData to see/edit all)")
        else:
            print("No scene data")
    
    def run(self):
        """Main workflow - just logline and outline editing."""
        try:
            if not self.setup_project():
                return
            
            self.setup_tables()
            self.show_current_outline()
            
            print("\n🎯 What would you like to do?")
            print("  1. 📝 Edit Logline")
            print("  2. 👥 Edit Characters (spreadsheet)")
            print("  3. 📖 Edit Story Outline (spreadsheet)")
            print("  4. 👀 View Tables (preview)")
            print("  5. 🔍 Browse All Data (full tables)")
            print("  6. 🚪 Exit")
            
            while True:
                choice = input("\nSelect option (1-6): ").strip()
                
                if choice == '1':
                    # Edit logline
                    if self.visidata_available:
                        self.edit_with_visidata('project_logline', 'Edit Story Logline')
                    else:
                        self.edit_logline_cli()
                    
                elif choice == '2':
                    # Edit characters
                    if self.visidata_available:
                        self.edit_with_visidata('characters', 'Edit Characters (Spreadsheet)')
                    else:
                        print("💡 VisiData not available. Install with: pip install visidata")
                    
                elif choice == '3':
                    # Edit outline
                    if self.visidata_available:
                        self.edit_with_visidata('story_outline', 'Edit 30-Scene Story Outline (Spreadsheet)')
                    else:
                        print("💡 VisiData not available. Install with: pip install visidata")
                    
                elif choice == '4':
                    # Show preview
                    self.show_current_outline()
                    
                elif choice == '5':
                    # Browse all data with VisiData
                    if self.visidata_available:
                        self.browse_all_data()
                    else:
                        print("💡 VisiData not available. Install with: pip install visidata")
                    
                elif choice == '6':
                    print("👋 Intake complete!")
                    break
                    
                else:
                    print("❌ Please select 1-6")
                    continue
                
                # Show updated status after each edit
                self.show_current_outline()
        
        except KeyboardInterrupt:
            print("\n\n⏸️  Cancelled.")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if self.conn:
                self.conn.close()
    
    def edit_logline_cli(self):
        """Simple CLI logline editing."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT logline FROM project_logline LIMIT 1")
        row = cursor.fetchone()
        current = row[0] if row else ""
        
        print(f"\nCurrent logline:")
        print(f"  {current}")
        print()
        new_logline = input("Enter new logline (or press Enter to keep current): ").strip()
        
        if new_logline:
            cursor.execute("""
                INSERT OR REPLACE INTO project_logline (id, logline, notes, updated_at)
                VALUES (1, ?, 'User-defined logline', CURRENT_TIMESTAMP)
            """, (new_logline,))
            self.conn.commit()
            print("✅ Logline updated!")
    
    def browse_all_data(self):
        """Launch VisiData to browse all tables."""
        print(f"\n🔍 Browse All Project Data")
        print("=" * 50)
        print("VisiData Navigation:")
        print("  • Switch tables: Ctrl+H (show all sheets)")
        print("  • Navigate: Arrow keys, PgUp/PgDn")
        print("  • Search: '/' then type search term")
        print("  • Filter: '|' then type condition")
        print("  • Sort: '^' (ascending) or 'z^' (descending)")
        print("  • Edit mode: Enter, then type")
        print("  • Help: F1 or '?'")
        print("  • Quit: 'q'")
        print()
        input("Press Enter to launch VisiData with all tables...")
        
        try:
            cmd = ['vd', str(self.db_path)]
            subprocess.run(cmd, check=False)
            print("✅ Browse session complete")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


def main():
    """Entry point."""
    intake = SimpleIntake()
    intake.run()


if __name__ == "__main__":
    main()