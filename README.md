# Projects Directory

This directory contains your individual writing projects. Each project gets its own isolated folder with a SQLite database.

## How Projects Are Organized

```
projects/
├── YourProjectName/
│   ├── YourProjectName.sqlite    # Complete project database
│   └── import_metadata.json      # Import information (if applicable)
└── README.md                     # This file
```

## Getting Started

1. Run `python3 start.py` to create your first project
2. The system will create a new folder here with your project name
3. Each project is completely isolated - you can work on multiple stories simultaneously

## Example Projects (Included for Reference)

The system comes with three example projects imported from legacy systems:

- **Elle**: Basic character template examples
- **EsteandTheo**: 27-scene romantic comedy structure with rich character development
- **TNK_A4**: 34-scene complex relationship drama with love triangle dynamics

These examples demonstrate:
- Complete character development using the "Essential Trinity" (Romantic Challenge, Lovable Trait, Comedic Flaw)
- Proven story structures with scene-by-scene breakdowns
- Professional-quality character profiles and story outlines

## Project Database Contents

Each project database contains:
- **Characters**: With romantic challenges, traits, and flaws
- **Story Outline**: Scene-by-scene structure with beats and events
- **Brainstorming Sessions**: AI-generated creative ideas with ratings
- **Drafts**: Versioned scene drafts with word counts and metadata

## Privacy Note

Project databases contain your creative work and are automatically excluded from version control via `.gitignore`. Your stories remain private and local to your machine.

## Templates Available

See the template files in the main directory:
- `CHARACTER_DEVELOPMENT_TEMPLATES.md` - Character creation framework
- `STORY_OUTLINE_TEMPLATES.md` - Story structure templates  
- `AVAILABLE_TEMPLATES.md` - Overview of all available templates

Happy writing! 🎭✍️