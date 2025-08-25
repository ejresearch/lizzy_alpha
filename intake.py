#!/usr/bin/env python3
"""
Lizzy Alpha - Rich Terminal Intake Module
=========================================
Beautiful command-line interface for editing story elements.

Author: Lizzy AI Writing Framework
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import print as rprint


class RichIntake:
    """Rich terminal interface for story editing."""
    
    def __init__(self, base_dir: str = "projects"):
        self.base_dir = Path(base_dir)
        self.project_name = None
        self.db_path = None
        self.conn = None
        self.console = Console()
    
    def setup_project(self) -> bool:
        """Connect to existing project."""
        self.console.clear()
        self.console.print(Panel("📖 Lizzy Alpha - Story Editor", style="bold blue"))
        
        # Create base directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # List existing projects
        existing_projects = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        if not existing_projects:
            self.console.print("[red]❌ No projects found. Run 'python start.py' first to create a project.[/red]")
            return False
        
        self.console.print("📂 Available projects:")
        for i, project in enumerate(existing_projects, 1):
            self.console.print(f"  {i}. {project}")
        
        choice = Prompt.ask("Select project number", choices=[str(i+1) for i in range(len(existing_projects))])
        try:
            idx = int(choice) - 1
            self.project_name = existing_projects[idx]
        except (ValueError, IndexError):
            return False
        
        # Connect to database
        project_dir = self.base_dir / self.project_name
        self.db_path = project_dir / f"{self.project_name}.sqlite"
        
        if not self.db_path.exists():
            self.console.print(f"[red]❌ Database not found for {self.project_name}. Run 'python start.py' first.[/red]")
            return False
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.console.print(f"[green]✅ Connected to project: {self.project_name}[/green]")
            return True
        except sqlite3.Error as e:
            self.console.print(f"[red]❌ Database connection error: {e}[/red]")
            return False
    
    def show_status(self):
        """Show current project status."""
        cursor = self.conn.cursor()
        
        # Logline
        cursor.execute("SELECT logline FROM project_logline LIMIT 1")
        row = cursor.fetchone()
        logline = row[0] if row else "No logline set"
        
        self.console.print(Panel(f"📝 Current Logline\n[italic]{logline}[/italic]", style="cyan"))
        
        # Characters summary
        cursor.execute("SELECT name, role FROM characters WHERE name NOT LIKE '%(EDIT%' ORDER BY role")
        real_characters = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM characters WHERE name LIKE '%(EDIT%'")
        template_count = cursor.fetchone()[0]
        
        char_panel = "👥 Characters\n"
        if real_characters:
            for name, role in real_characters:
                char_panel += f"• {name} ({role})\n"
        if template_count > 0:
            char_panel += f"📝 {template_count} templates ready to customize"
        
        self.console.print(Panel(char_panel.strip(), style="green"))
        
        # Scenes summary
        cursor.execute("""
            SELECT act, COUNT(*) as count,
                   COUNT(CASE WHEN location IS NOT NULL AND location != '' THEN 1 END) as filled
            FROM story_outline 
            GROUP BY act 
            ORDER BY act
        """)
        acts = cursor.fetchall()
        
        if acts:
            scene_panel = "📖 Story Outline\n"
            total_scenes = sum(row[1] for row in acts)
            filled_scenes = sum(row[2] for row in acts)
            scene_panel += f"{total_scenes} scenes total, {filled_scenes} customized\n"
            for act, count, filled in acts:
                status = f"{filled}/{count} customized" if filled > 0 else "templates only"
                scene_panel += f"Act {act}: {count} scenes ({status})\n"
        else:
            scene_panel = "📖 No scenes found"
        
        self.console.print(Panel(scene_panel.strip(), style="yellow"))
    
    def edit_logline(self):
        """Edit the logline."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT logline FROM project_logline LIMIT 1")
        row = cursor.fetchone()
        current = row[0] if row else ""
        
        self.console.print(Panel("📝 Edit Logline", style="bold cyan"))
        self.console.print(f"Current: [italic]{current}[/italic]")
        
        new_logline = Prompt.ask("Enter new logline", default=current)
        
        if new_logline != current:
            cursor.execute("""
                INSERT OR REPLACE INTO project_logline (id, logline, notes, updated_at)
                VALUES (1, ?, 'User-defined logline', CURRENT_TIMESTAMP)
            """, (new_logline,))
            self.conn.commit()
            self.console.print("[green]✅ Logline updated![/green]")
        
        input("Press Enter to continue...")
    
    def edit_characters(self):
        """Character editing interface."""
        cursor = self.conn.cursor()
        
        while True:
            # Show current characters
            cursor.execute("SELECT id, name, role, romantic_challenge, lovable_trait, comedic_flaw FROM characters ORDER BY role")
            characters = cursor.fetchall()
            
            self.console.clear()
            self.console.print(Panel("👥 Characters Editor", style="bold green"))
            
            if characters:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("#", style="dim", width=3)
                table.add_column("Name", style="cyan", width=20)
                table.add_column("Role", style="green", width=15)
                table.add_column("Romantic Challenge", width=30)
                table.add_column("Lovable Trait", width=25)
                
                for i, char in enumerate(characters, 1):
                    table.add_row(
                        str(i),
                        char[1] or "",
                        char[2] or "",
                        (char[3][:27] + "...") if char[3] and len(char[3]) > 30 else (char[3] or ""),
                        (char[4][:22] + "...") if char[4] and len(char[4]) > 25 else (char[4] or "")
                    )
                
                self.console.print(table)
            else:
                self.console.print("[yellow]No characters found[/yellow]")
            
            self.console.print("\n[bold]Options:[/bold]")
            self.console.print("1. Edit character")
            self.console.print("2. Add new character") 
            self.console.print("3. Delete character")
            self.console.print("4. Return to main menu")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="4")
            
            if choice == "1" and characters:
                char_num = Prompt.ask(f"Edit character (1-{len(characters)})", default="1")
                try:
                    char_idx = int(char_num) - 1
                    if 0 <= char_idx < len(characters):
                        self.edit_single_character(characters[char_idx])
                except ValueError:
                    pass
            elif choice == "2":
                self.add_new_character()
            elif choice == "3" and characters:
                char_num = Prompt.ask(f"Delete character (1-{len(characters)})")
                try:
                    char_idx = int(char_num) - 1
                    if 0 <= char_idx < len(characters):
                        char_id = characters[char_idx][0]
                        if Confirm.ask(f"Delete '{characters[char_idx][1]}'?"):
                            cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))
                            self.conn.commit()
                            self.console.print("[green]✅ Character deleted[/green]")
                            input("Press Enter to continue...")
                except ValueError:
                    pass
            elif choice == "4":
                break
    
    def edit_single_character(self, character):
        """Edit a single character."""
        cursor = self.conn.cursor()
        char_id, name, role, romantic_challenge, lovable_trait, comedic_flaw = character
        
        self.console.print(Panel(f"Editing: {name}", style="bold yellow"))
        
        new_name = Prompt.ask("Name", default=name or "")
        new_role = Prompt.ask("Role", choices=["protagonist", "love_interest", "supporting", "antagonist"], default=role or "protagonist")
        new_challenge = Prompt.ask("Romantic Challenge", default=romantic_challenge or "")
        new_trait = Prompt.ask("Lovable Trait", default=lovable_trait or "")
        new_flaw = Prompt.ask("Comedic Flaw", default=comedic_flaw or "")
        
        cursor.execute("""
            UPDATE characters 
            SET name = ?, role = ?, romantic_challenge = ?, lovable_trait = ?, comedic_flaw = ?
            WHERE id = ?
        """, (new_name, new_role, new_challenge, new_trait, new_flaw, char_id))
        
        self.conn.commit()
        self.console.print("[green]✅ Character updated![/green]")
        input("Press Enter to continue...")
    
    def add_new_character(self):
        """Add a new character."""
        cursor = self.conn.cursor()
        
        self.console.print(Panel("Add New Character", style="bold green"))
        
        name = Prompt.ask("Name")
        role = Prompt.ask("Role", choices=["protagonist", "love_interest", "supporting", "antagonist"], default="supporting")
        romantic_challenge = Prompt.ask("Romantic Challenge", default="")
        lovable_trait = Prompt.ask("Lovable Trait", default="")
        comedic_flaw = Prompt.ask("Comedic Flaw", default="")
        
        cursor.execute("""
            INSERT INTO characters (name, role, romantic_challenge, lovable_trait, comedic_flaw)
            VALUES (?, ?, ?, ?, ?)
        """, (name, role, romantic_challenge, lovable_trait, comedic_flaw))
        
        self.conn.commit()
        self.console.print("[green]✅ Character added![/green]")
        input("Press Enter to continue...")
    
    def edit_outline(self):
        """Story outline editing interface."""
        cursor = self.conn.cursor()
        
        while True:
            self.console.clear()
            self.console.print(Panel("📖 Story Outline Editor (30 Scenes)", style="bold blue"))
            
            # Show scenes by act
            for act in [1, 2, 3]:
                cursor.execute("SELECT scene, scene_title, scene_purpose FROM story_outline WHERE act = ? ORDER BY scene", (act,))
                scenes = cursor.fetchall()
                
                if scenes:
                    self.console.print(f"\n[bold cyan]Act {act}:[/bold cyan]")
                    table = Table(show_header=True, header_style="bold magenta", box=None)
                    table.add_column("Scene", width=5)
                    table.add_column("Title", width=25)
                    table.add_column("Purpose", width=50)
                    
                    for scene, title, purpose in scenes:
                        table.add_row(
                            str(scene),
                            (title[:22] + "...") if title and len(title) > 25 else (title or "[dim]Untitled[/dim]"),
                            (purpose[:47] + "...") if purpose and len(purpose) > 50 else (purpose or "[dim]No purpose set[/dim]")
                        )
                    
                    self.console.print(table)
            
            self.console.print("\n[bold]Options:[/bold]")
            self.console.print("1. Edit scene")
            self.console.print("2. Jump to act")
            self.console.print("3. Return to main menu")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3"], default="3")
            
            if choice == "1":
                scene_num = Prompt.ask("Edit scene number (1-30)")
                try:
                    scene_int = int(scene_num)
                    if 1 <= scene_int <= 30:
                        self.edit_single_scene(scene_int)
                except ValueError:
                    pass
            elif choice == "2":
                act_num = Prompt.ask("Jump to act", choices=["1", "2", "3"])
                # Show just that act (implementation)
                pass
            elif choice == "3":
                break
    
    def edit_single_scene(self, scene_num):
        """Edit a single scene."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM story_outline WHERE scene = ?", (scene_num,))
        scene = cursor.fetchone()
        
        if not scene:
            self.console.print("[red]Scene not found[/red]")
            return
        
        act = scene['act']
        self.console.print(Panel(f"Editing: Act {act}, Scene {scene_num}", style="bold yellow"))
        
        title = Prompt.ask("Scene Title", default=scene['scene_title'] or "")
        location = Prompt.ask("Location", default=scene['location'] or "")
        characters = Prompt.ask("Characters Present", default=scene['characters_present'] or "")
        purpose = Prompt.ask("Scene Purpose", default=scene['scene_purpose'] or "")
        key_events = Prompt.ask("Key Events", default=scene['key_events'] or "")
        
        cursor.execute("""
            UPDATE story_outline 
            SET scene_title = ?, location = ?, characters_present = ?, scene_purpose = ?, key_events = ?
            WHERE scene = ?
        """, (title, location, characters, purpose, key_events, scene_num))
        
        self.conn.commit()
        self.console.print("[green]✅ Scene updated![/green]")
        input("Press Enter to continue...")
    
    def run(self):
        """Main workflow."""
        try:
            if not self.setup_project():
                return
            
            # Initialize empty tables if needed
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_logline (
                    id INTEGER PRIMARY KEY,
                    logline TEXT,
                    notes TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("SELECT COUNT(*) FROM project_logline")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO project_logline (logline, notes) 
                    VALUES ('Write your one-sentence story summary here...', 'The logline should capture the essence of your romantic comedy')
                """)
            
            self.conn.commit()
            
            while True:
                self.console.clear()
                self.show_status()
                
                self.console.print("\n🎯 [bold]What would you like to do?[/bold]")
                self.console.print("1. 📝 Edit Logline")
                self.console.print("2. 👥 Edit Characters") 
                self.console.print("3. 📖 Edit Story Outline")
                self.console.print("4. 🔄 Refresh Status")
                self.console.print("5. 🚪 Exit")
                
                choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="5")
                
                if choice == "1":
                    self.edit_logline()
                elif choice == "2":
                    self.edit_characters()
                elif choice == "3":
                    self.edit_outline()
                elif choice == "4":
                    continue  # Just refresh
                elif choice == "5":
                    self.console.print("👋 [green]Story editing complete![/green]")
                    break
        
        except KeyboardInterrupt:
            self.console.print("\n\n⏸️  [yellow]Cancelled.[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]❌ Error: {e}[/red]")
        finally:
            if self.conn:
                self.conn.close()


def main():
    """Entry point."""
    intake = RichIntake()
    intake.run()


if __name__ == "__main__":
    main()