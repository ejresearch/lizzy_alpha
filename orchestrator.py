# IN DEVELOPMENT 
#!/usr/bin/env python3
"""
Lizzy Alpha - Orchestrator Agent
=================================
Automated end-to-end romantic comedy generation with unique, detailed stories.
Runs the complete pipeline: Start → Intake → Brainstorm → Write → Desktop

Author: Lizzy AI Writing Framework
"""

import os
import sys
import sqlite3
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Import all Lizzy modules
from start import LizzyStart
from intake_enhanced import LizzyIntakeEnhanced
from brainstorm import BrainstormingAgent, initialize_lightrag_buckets
from write import LizzyWrite

# Story concept generators for unique ideas
UNIQUE_PREMISES = [
    ("A perfectionist wedding planner", "discovers her soulmate is the disaster-prone food truck owner", "who keeps crashing the upscale events she organizes"),
    ("A by-the-book NASA engineer", "falls for a chaotic astrologer", "who's hired to boost team morale during a critical Mars mission"),
    ("A minimalist professional organizer", "meets her match in a maximalist vintage shop owner", "when they're forced to share a workspace"),
    ("A cynical divorce lawyer", "starts receiving love letters from the optimistic baker next door", "hidden in fortune cookies meant for other customers"),
    ("A night-shift ER doctor", "and a morning radio DJ", "keep missing each other but fall in love through voicemails"),
    ("A competitive food critic", "anonymously battles online with a chef", "not knowing they're already best friends in real life"),
    ("A billionaire trying to live normally", "hires a no-nonsense budget coach", "who has no idea about the fortune hidden in offshore accounts"),
    ("A professional bridesmaid", "keeps encountering the same bitter wedding videographer", "who's documenting why love doesn't last"),
    ("A social media influencer afraid of flying", "gets stuck on a cross-country train", "with a tech-phobic nature photographer"),
    ("A Broadway understudy", "switches lives with a Fortune 500 CEO", "after a fortune teller's blessing goes hilariously wrong"),
]

CHARACTER_DEPTH_TRAITS = {
    "fears": [
        "abandonment after parents' bitter divorce",
        "success because they don't feel worthy",
        "vulnerability due to past betrayal",
        "commitment after seeing too many failures",
        "being ordinary in an extraordinary family",
        "letting people see their real self",
        "heights but dreams of being a pilot",
        "making the same mistakes as their parents",
    ],
    "secrets": [
        "writes romance novels under a pen name",
        "is actually the heir to a fortune",
        "failed spectacularly at their dream career",
        "has synesthesia and sees emotions as colors",
        "was almost married three times before",
        "is ghost-writing their ex's autobiography",
        "won the lottery but gave it all away",
        "is terrified of the dark but runs a haunted house",
    ],
    "quirks": [
        "names all their plants and talks to them",
        "can only think clearly while doing puzzles",
        "collects fortune cookie fortunes obsessively",
        "speaks in movie quotes when nervous",
        "reorganizes things when stressed",
        "makes up elaborate backstories for strangers",
        "has a different coffee order for each day",
        "practices acceptance speeches in the shower",
    ],
    "skills": [
        "can read body language like a book",
        "remembers every conversation verbatim",
        "makes the world's best grilled cheese",
        "can fix anything with duct tape",
        "speaks four languages fluently",
        "has a photographic memory for faces",
        "can juggle while solving math problems",
        "knows every constellation's mythology",
    ]
}

STORY_COMPLICATIONS = [
    "a meddling but well-meaning grandmother who's also a tech mogul",
    "a rival who turns out to be their new roommate",
    "a company merger that puts them on opposite sides",
    "a viral social media misunderstanding",
    "an inherited bed & breakfast they must run together",
    "a witness protection program mishap",
    "competing for the same promotion",
    "a reality TV show they didn't know they signed up for",
    "an AI dating app that keeps sabotaging them",
    "a time capsule that reveals an old connection",
]


class LizzyOrchestrator:
    """
    Orchestrates the entire Lizzy pipeline automatically with creative generation.
    """
    
    def __init__(self):
        self.project_name = None
        self.project_title = None
        self.db_path = None
        self.conn = None
        self.base_dir = Path("projects")
        
    def generate_unique_concept(self) -> Dict:
        """Generate a unique, detailed story concept."""
        premise = random.choice(UNIQUE_PREMISES)
        complication = random.choice(STORY_COMPLICATIONS)
        
        concept = {
            "protagonist_type": premise[0],
            "love_interest_type": premise[1],
            "meet_cute": premise[2],
            "major_complication": complication,
            "title": self.generate_title(premise),
            "logline": f"{premise[0]} {premise[1]} {premise[2]}, but things get complicated when {complication}.",
        }
        
        return concept
    
    def generate_title(self, premise: Tuple) -> str:
        """Generate a catchy romantic comedy title."""
        title_templates = [
            f"Love and {premise[0].split()[-1].title()}",
            f"The {premise[1].split()[-1].title()} Next Door",
            f"Unexpectedly {random.choice(['Yours', 'Mine', 'Ours', 'Us'])}",
            f"The {random.choice(['Perfect', 'Impossible', 'Unlikely', 'Inevitable'])} Match",
            f"Hearts and {premise[0].split()[-1].title()}s",
        ]
        return random.choice(title_templates)
    
    def generate_detailed_character(self, name: str, role: str, char_type: str) -> Dict:
        """Generate a detailed, unique character."""
        return {
            "name": name,
            "role": role,
            "description": f"A {random.choice(['charming', 'witty', 'endearing', 'brilliant'])} {char_type} with {random.choice(['expressive eyes', 'an infectious laugh', 'graceful movements', 'distinctive style'])}",
            "personality_traits": f"{random.choice(['optimistic', 'pragmatic', 'spontaneous', 'methodical'])}, {random.choice(['empathetic', 'analytical', 'creative', 'determined'])}, secretly {random.choice(['romantic', 'vulnerable', 'insecure', 'hopeful'])}",
            "backstory": f"Grew up {random.choice(['in a small town', 'moving constantly', 'in the city', 'abroad'])}, {random.choice(['youngest of five', 'only child', 'raised by grandparents', 'middle child'])}. {random.choice(['Changed careers twice', 'Lost someone important', 'Achieved early success', 'Started over at 30'])}.",
            "goals": f"Wants to {random.choice(['prove themselves', 'find belonging', 'make a difference', 'build something lasting'])}, but really needs to {random.choice(['learn to trust', 'forgive themselves', 'slow down', 'open their heart'])}",
            "conflicts": f"External: {random.choice(['career crisis', 'family pressure', 'financial struggles', 'reputation at stake'])}. Internal: {random.choice(CHARACTER_DEPTH_TRAITS['fears'])}",
            "romantic_challenge": random.choice([
                "believes they're too broken for love",
                "always puts others first, never themselves",
                "terrified of becoming their parents",
                "convinced love is just chemical reactions",
                "has built walls that seem insurmountable",
            ]),
            "lovable_trait": random.choice([
                "leaves encouraging notes for strangers",
                "remembers everyone's birthday",
                "adopts every stray animal they find",
                "secretly pays for people's coffee",
                "makes people feel truly seen",
            ]),
            "comedic_flaw": random.choice([
                "catastrophically bad at technology",
                "interprets everything literally",
                "compulsively makes puns",
                "accidentally speaks thoughts aloud",
                "magnetically attracts chaos",
            ]),
            "secret": random.choice(CHARACTER_DEPTH_TRAITS["secrets"]),
            "quirk": random.choice(CHARACTER_DEPTH_TRAITS["quirks"]),
            "special_skill": random.choice(CHARACTER_DEPTH_TRAITS["skills"]),
        }
    
    def generate_compelling_outline(self, concept: Dict) -> List[Dict]:
        """Generate a complete 30-scene three-act outline with detailed beats."""
        outline = []
        
        # Act 1 - Setup (12 scenes)
        act1_scenes = [
            {"act": 1, "scene": 1, "beat": "Opening Image", "scene_title": "Chemical Equation", "scene_purpose": "setup", "key_events": "Establish the world and protagonist's starting point", "emotional_beats": "Status quo establishment"},
            {"act": 1, "scene": 2, "beat": "Opening Image", "scene_title": "Emotional Baseline", "scene_purpose": "setup", "key_events": "Set up the emotional/romantic baseline", "emotional_beats": "Longing or emptiness revealed"},
            {"act": 1, "scene": 3, "beat": "Meet Cute", "scene_title": "First Encounter", "scene_purpose": "setup", "key_events": f"The moment when romantic leads first encounter: {concept['meet_cute']}", "emotional_beats": "Instant chemistry or conflict"},
            {"act": 1, "scene": 4, "beat": "Meet Cute", "scene_title": "Memorable Meeting", "scene_purpose": "setup", "key_events": "Initial spark or conflict that makes the meeting memorable", "emotional_beats": "Attraction mixed with resistance"},
            {"act": 1, "scene": 5, "beat": "Reaction", "scene_title": "First Impressions", "scene_purpose": "setup", "key_events": "How the characters react to their first meeting", "emotional_beats": "Confusion and interest"},
            {"act": 1, "scene": 6, "beat": "Reaction", "scene_title": "Processing", "scene_purpose": "setup", "key_events": "Internal processing and initial attraction/repulsion", "emotional_beats": "Can't stop thinking about them"},
            {"act": 1, "scene": 7, "beat": "Romantic Complication", "scene_title": "The Obstacle", "scene_purpose": "setup", "key_events": f"The obstacle that prevents easy romance: {concept['major_complication']}", "emotional_beats": "Frustration and longing"},
            {"act": 1, "scene": 8, "beat": "Romantic Complication", "scene_title": "Why Not Together", "scene_purpose": "setup", "key_events": "Why they can't just be together", "emotional_beats": "Resignation masking hope"},
            {"act": 1, "scene": 9, "beat": "Raise Stakes", "scene_title": "What Matters", "scene_purpose": "setup", "key_events": "Why this relationship matters to the characters", "emotional_beats": "Recognition of deeper need"},
            {"act": 1, "scene": 10, "beat": "Raise Stakes", "scene_title": "Time Pressure", "scene_purpose": "setup", "key_events": "External pressure or deadline introduced", "emotional_beats": "Urgency and determination"},
            {"act": 1, "scene": 11, "beat": "Break into Act II", "scene_title": "Commitment", "scene_purpose": "setup", "key_events": "Commitment to pursue the relationship despite obstacles", "emotional_beats": "Courage overcoming fear"},
            {"act": 1, "scene": 12, "beat": "Break into Act II", "scene_title": "New Territory", "scene_purpose": "setup", "key_events": "Crossing the threshold into new territory", "emotional_beats": "Excitement mixed with terror"},
        ]
        
        # Act 2 - Confrontation (16 scenes)
        act2_scenes = [
            {"act": 2, "scene": 13, "beat": "Fun & Games", "scene_title": "Romance Promise", "scene_purpose": "conflict", "key_events": "The promise of the premise - romance develops", "emotional_beats": "Joy and discovery"},
            {"act": 2, "scene": 14, "beat": "Fun & Games", "scene_title": "Bonding Montage", "scene_purpose": "conflict", "key_events": "Montage or series of bonding moments", "emotional_beats": "Falling deeper"},
            {"act": 2, "scene": 15, "beat": "Midpoint Hook", "scene_title": "Game Changer", "scene_purpose": "conflict", "key_events": "Major revelation or event that changes everything", "emotional_beats": "Shock and realization"},
            {"act": 2, "scene": 16, "beat": "Midpoint Hook", "scene_title": "Raised Stakes", "scene_purpose": "conflict", "key_events": "Stakes are raised, relationship deepens or is threatened", "emotional_beats": "Intensity and fear"},
            {"act": 2, "scene": 17, "beat": "External/Internal Tensions", "scene_title": "First Cracks", "scene_purpose": "conflict", "key_events": "Character flaws create problems", "emotional_beats": "Doubt creeping in"},
            {"act": 2, "scene": 18, "beat": "External/Internal Tensions", "scene_title": "Growing Problems", "scene_purpose": "conflict", "key_events": "Character flaws create bigger problems", "emotional_beats": "Frustration building"},
            {"act": 2, "scene": 19, "beat": "Lose Beat", "scene_title": "All Seems Lost", "scene_purpose": "conflict", "key_events": "All seems lost - the relationship appears doomed", "emotional_beats": "Despair and heartbreak"},
            {"act": 2, "scene": 20, "beat": "Lose Beat", "scene_title": "Lowest Point", "scene_purpose": "conflict", "key_events": "Characters at their lowest point", "emotional_beats": "Rock bottom despair"},
            {"act": 2, "scene": 21, "beat": "Self-Revelation", "scene_title": "What Must Change", "scene_purpose": "conflict", "key_events": "Characters realize what they must change", "emotional_beats": "Painful self-awareness"},
            {"act": 2, "scene": 22, "beat": "Self-Revelation", "scene_title": "True Feelings", "scene_purpose": "conflict", "key_events": "Understanding of true feelings and priorities", "emotional_beats": "Clarity through pain"},
        ]
        
        # Act 3 - Resolution (8 scenes)
        act3_scenes = [
            {"act": 3, "scene": 23, "beat": "Grand Gesture", "scene_title": "Big Romantic Action", "scene_purpose": "climax", "key_events": "Big romantic action to win back love", "emotional_beats": "Vulnerability and courage"},
            {"act": 3, "scene": 24, "beat": "Grand Gesture", "scene_title": "Proof of Change", "scene_purpose": "climax", "key_events": "Demonstration of growth and change", "emotional_beats": "Authentic transformation"},
            {"act": 3, "scene": 25, "beat": "Reunion", "scene_title": "Coming Together", "scene_purpose": "resolution", "key_events": "Coming back together after growth", "emotional_beats": "Tentative hope"},
            {"act": 3, "scene": 26, "beat": "Reunion", "scene_title": "Understanding", "scene_purpose": "resolution", "key_events": "Forgiveness and understanding", "emotional_beats": "Relief and reconciliation"},
            {"act": 3, "scene": 27, "beat": "Happy Ending", "scene_title": "Resolution", "scene_purpose": "resolution", "key_events": "Resolution of all conflicts", "emotional_beats": "Peace and satisfaction"},
            {"act": 3, "scene": 28, "beat": "Happy Ending", "scene_title": "Celebration", "scene_purpose": "resolution", "key_events": "Celebration of love achieved", "emotional_beats": "Joy and triumph"},
            {"act": 3, "scene": 29, "beat": "Final Image", "scene_title": "Transformation", "scene_purpose": "resolution", "key_events": "Mirror of opening showing transformation", "emotional_beats": "Growth demonstrated"},
            {"act": 3, "scene": 30, "beat": "Final Image", "scene_title": "New Equilibrium", "scene_purpose": "resolution", "key_events": "New equilibrium established", "emotional_beats": "Earned happiness"},
        ]
        
        return act1_scenes + act2_scenes + act3_scenes
    
    def run_complete_pipeline(self):
        """Execute the entire Lizzy pipeline automatically."""
        print("🎬 Lizzy Alpha - Enhanced Automated Story Generation")
        print("=" * 50)
        print("Creating a unique romantic comedy from scratch...\n")
        
        # Step 1: Generate unique concept
        print("💡 Step 1: Generating unique story concept...")
        concept = self.generate_unique_concept()
        self.project_title = concept["title"]
        self.project_name = concept["title"].lower().replace(" ", "_").replace("'", "")
        
        print(f"   Title: {concept['title']}")
        print(f"   Logline: {concept['logline']}\n")
        
        # Step 2: Create project with start.py
        print("📁 Step 2: Creating project structure...")
        start = LizzyStart()
        start.project_name = self.project_name
        start.base_dir.mkdir(exist_ok=True)
        project_dir = start.base_dir / self.project_name
        project_dir.mkdir(exist_ok=True)
        start.db_path = project_dir / f"{self.project_name}.sqlite"
        start.setup_database()
        
        # Add metadata
        if start.conn:
            cursor = start.conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO project_metadata (key, value) VALUES (?, ?)", 
                          ('title', self.project_title))
            cursor.execute("INSERT OR REPLACE INTO project_metadata (key, value) VALUES (?, ?)", 
                          ('genre', 'Romantic Comedy'))
            cursor.execute("INSERT OR REPLACE INTO project_metadata (key, value) VALUES (?, ?)", 
                          ('tone', 'Golden Era Romcom'))
            cursor.execute("INSERT OR REPLACE INTO project_metadata (key, value) VALUES (?, ?)", 
                          ('logline', concept['logline']))
            start.conn.commit()
            start.conn.close()
        
        print(f"   ✅ Project '{self.project_name}' created\n")
        
        # Step 3: Generate characters and outline using enhanced intake
        print("👥 Step 3: Creating professional character templates...")
        self.conn = sqlite3.connect(start.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        
        # Use enhanced intake to generate professional templates
        enhanced_intake = LizzyIntakeEnhanced()
        enhanced_intake.project_name = self.project_name
        enhanced_intake.db_path = start.db_path
        enhanced_intake.conn = self.conn
        
        # Generate full romcom ensemble
        print("   🎭 Generating core romcom archetypes...")
        enhanced_intake.create_full_ensemble_templates()
        
        # Note: 30-scene structure is now automatically populated by start.py
        print("   📖 Using professional 30-scene structure from start.py...")
        
        # Update character names in scenes with generated characters
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, role FROM characters ORDER BY role")
        chars_by_role = {}
        for row in cursor.fetchall():
            chars_by_role[row[1]] = row[0]  # row[1] = role, row[0] = name
        
        protagonist_name = chars_by_role.get('protagonist', 'Protagonist')
        love_interest_name = chars_by_role.get('love_interest', 'Love Interest')
        supporting_name = chars_by_role.get('supporting', 'Best Friend')
        
        # Update specific scenes with character assignments
        key_scenes = [
            (1, 1, protagonist_name),  # Opening
            (1, 3, f"{protagonist_name}, {love_interest_name}"),  # Meet cute
            (2, 13, f"{protagonist_name}, {love_interest_name}"),  # Fun & Games
            (2, 15, f"{protagonist_name}, {love_interest_name}, {supporting_name}"),  # Midpoint
            (3, 1, f"{protagonist_name}, {love_interest_name}"),  # Grand gesture
        ]
        
        for act, scene, characters in key_scenes:
            cursor.execute("""
                UPDATE story_outline SET characters_present = ? 
                WHERE act = ? AND scene = ?
            """, (characters, act, scene))
        
        self.conn.commit()
        
        # Get counts for reporting
        cursor.execute("SELECT COUNT(*) FROM characters")
        char_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM story_outline")
        scene_count = cursor.fetchone()[0]
        
        print(f"   ✅ Created {char_count} professional character archetypes")
        print(f"   ✅ Created {scene_count} scene structure with beats")
        print(f"      - Cast: {protagonist_name}, {love_interest_name}, {supporting_name}, and more\n")
        
        # Step 4: Run brainstorming
        print("🧠 Step 4: Running AI brainstorming for all 30 scenes...")
        
        # Initialize LightRAG if available
        try:
            lightrag_instances = initialize_lightrag_buckets()
            if lightrag_instances:
                brainstorm = BrainstormingAgent(lightrag_instances)
                brainstorm.project_name = self.project_name
                brainstorm.db_path = start.db_path
                brainstorm.conn = self.conn
                brainstorm.easter_egg = random.choice([
                    "recurring joke about mismatched socks",
                    "ongoing metaphor about coffee temperatures",
                    "running gag about autocorrect fails",
                    "repeated references to 90s rom-coms",
                ])
                brainstorm.setup_table()
                
                # Process scenes
                scenes_data = brainstorm.fetch_all_scenes()
                for act, scene_num, description in scenes_data:
                    print(f"   Processing Act {act}, Scene {scene_num}...")
                    for bucket_name in lightrag_instances.keys():
                        prompt = brainstorm.create_prompt(bucket_name, description)
                        response = brainstorm.query_bucket(bucket_name, prompt)
                        brainstorm.save_response(act, scene_num, description, bucket_name, response)
                
                print(f"   ✅ Brainstorming complete\n")
            else:
                print("   ⚠️  Skipping brainstorming (LightRAG not available)\n")
        except Exception as e:
            print(f"   ⚠️  Brainstorming skipped: {e}\n")
        
        # Step 5: Write scenes
        print("✍️  Step 5: Writing complete 30-scene manuscript with continuity...")
        writer = LizzyWrite()
        writer.project_name = self.project_name
        writer.db_path = start.db_path
        writer.conn = self.conn
        # Ensure writer connection also has row_factory
        if not hasattr(writer.conn, 'row_factory') or writer.conn.row_factory != sqlite3.Row:
            writer.conn.row_factory = sqlite3.Row
        
        # Configure writing
        writer.writing_style = "cinematic"
        writer.tone = "witty and heartfelt"
        writer.easter_egg = brainstorm.easter_egg if 'brainstorm' in locals() else ""
        
        # Get data
        metadata = writer.get_project_metadata()
        characters_list = writer.get_characters()
        scenes_list = writer.get_story_outline()
        brainstorm_table = writer.get_latest_brainstorm_table()
        
        # Write each scene
        for scene in scenes_list:
            act, scene_num = scene['act'], scene['scene']
            print(f"   Writing Act {act}, Scene {scene_num}: {scene.get('scene_title', 'Untitled')}...")
            
            # Get contexts
            brainstorm_context = None
            if brainstorm_table:
                brainstorm_context = writer.get_brainstorm_for_scene(brainstorm_table, act, scene_num)
            
            prev_text = writer.summarize_prev_if_long(writer.get_prev_scene_text(act, scene_num))
            outline_snap = writer.make_outline_snapshot(scenes_list, act, scene_num)
            next_desc = writer.get_next_scene_outline_desc(act, scene_num)
            
            # Build and execute
            prompt = writer.build_scene_prompt(
                metadata, characters_list, scene, brainstorm_context,
                outline_snapshot=outline_snap,
                prev_scene_text=prev_text,
                next_scene_desc=next_desc,
                min_words=700, max_words=900
            )
            
            try:
                scene_text = writer.generate_scene_text(prompt)
                writer.save_scene_draft(scene, prompt, scene_text)
                writer.save_finalized_scene(scene, scene_text)
            except Exception as e:
                print(f"      ⚠️  Error: {e}")
        
        print(f"   ✅ Writing complete\n")
        
        # Step 6: Export to Desktop
        print("💾 Step 6: Exporting to Desktop...")
        writer.export_full_script(scenes_list, metadata)
        
        # Close connections
        if self.conn:
            self.conn.close()
        
        print("\n" + "=" * 50)
        print("🎉 COMPLETE! Your unique 30-scene romantic comedy is on your Desktop!")
        print(f"   Title: {self.project_title}")
        print(f"   Project: {self.project_name}")
        print(f"   Length: ~21,000-27,000 words (30 scenes × 700-900 words)")
        print("=" * 50)


def main():
    """Entry point for the orchestrator."""
    orchestrator = LizzyOrchestrator()
    
    try:
        orchestrator.run_complete_pipeline()
    except KeyboardInterrupt:
        print("\n\n⏸️  Generation cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
