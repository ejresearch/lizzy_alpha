# Lizzy Alpha - AI-Assisted Long-Form Writing Framework

A modular framework for AI-powered creative writing that combines structured memory, dynamic document retrieval, and iterative refinement to help writers create compelling long-form content.

## Overview

Lizzy is an innovative system designed to empower writers across all genres by leveraging AI-assisted, modular workflows. Originally tested with romantic comedy screenwriting, the system's architecture can be adapted for any writing project including novels, technical documents, research articles, and more.

## Key Features

- **Structured Memory**: Each project maintains its own SQLite database with character profiles, scene outlines, and version history
- **Dynamic Brainstorming**: Queries multiple knowledge buckets (books, scripts, plays) using LightRAG for context-aware creative suggestions
- **Iterative Refinement**: Tracks multiple versions of drafts and brainstorming sessions for continuous improvement
- **Golden Era Romcom Tone**: Built-in presets for creating content inspired by classics like When Harry Met Sally and You've Got Mail
- **Automatic Export**: Generates formatted scripts in both text and markdown formats

## Prerequisites

- Python 3.x
- OpenAI API key
- Required Python packages:
  - `lightrag`
  - `openai`
  - `python-dotenv`
  - `sqlite3` (built-in)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd lizzy_alpha
```

2. Install required packages:
```bash
pip install lightrag openai python-dotenv
```

3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or create a `.env` file in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

## Quick Start

The framework consists of 4 sequential scripts that guide you through the entire writing process:

### 1. Start a New Project
```bash
python start.py
```
- Creates a new project database
- Sets up the 30-scene professional screenplay structure
- Initializes all required tables for the workflow

### 2. Input Story Elements
```bash
python intake.py
```
- Add character profiles with romantic comedy specific traits:
  - Romantic challenges
  - Lovable traits
  - Comedic flaws
- Define scene outlines with locations, purposes, and emotional beats
- Set project metadata (genre, POV, tense)

### 3. Generate Creative Ideas
```bash
python brainstorm.py
```
- Queries knowledge buckets for creative inspiration:
  - **Books**: Screenwriting theory and structure
  - **Scripts**: Top romantic comedy screenplays
  - **Plays**: Shakespearean comedy and drama
- Optional: Add an "easter egg" theme to weave throughout
- Creates versioned brainstorming logs for each scene

### 4. Write Your Scenes
```bash
python write.py
```
- Choose your writing style:
  - **Prose**: Cinematic, Literary, Commercial, or Minimalist
  - **Screenplay**: Proper script format with scene headings and dialogue
- Automatically processes all scenes with:
  - Previous scene continuity
  - Full outline context
  - Blended brainstorming insights
- Exports completed script to Desktop

## Project Structure

```
lizzy_alpha/
├── start.py          # Project initialization
├── intake.py         # Character & story setup
├── brainstorm.py     # AI-powered idea generation
├── write.py          # Scene writing & export
├── projects/         # Project databases
│   └── [project_name]/
│       └── [project_name].sqlite
└── lightrag_working_dir/
    ├── books/        # Screenwriting knowledge
    ├── scripts/      # Romcom screenplay examples
    └── plays/        # Shakespeare references
```

## Database Schema

Each project database contains:

- **project_metadata**: Genre, tone, POV settings
- **characters**: Full character profiles with romcom traits
- **story_outline**: 30-scene structure with detailed scene information
- **brainstorming_sessions**: Session metadata
- **brainstorming_log_vX**: Versioned creative ideas
- **scene_drafts**: Multiple draft versions
- **finalized_scenes**: Production-ready scenes
- **write_runs_vX**: Writing session history

## Output Formats

### Prose Format
- `.txt` file with full manuscript
- `.md` file with structured scene index

### Screenplay Format
- `.fountain` file for screenplay software
- `.txt` file for easy reading

Both formats are automatically saved to your Desktop after writing completes.

## Advanced Usage

### Custom Tone Presets

The framework includes a golden-era romantic comedy tone by default, optimized for creating content with:
- Genuine emotional stakes
- Witty, quotable dialogue
- Earned romantic moments
- Universal yet specific conflicts

### Easter Eggs

Add optional creative constraints or recurring themes that appear throughout your project:
- Running gags
- Symbolic objects
- Thematic motifs

### Knowledge Buckets

The system queries three specialized knowledge sources:
1. **Books**: Structure, pacing, character arcs
2. **Scripts**: Genre conventions, successful tropes
3. **Plays**: Dramatic irony, elevated language

## Troubleshooting

### LightRAG Not Found
```bash
pip install lightrag
```

### API Key Issues
Ensure your OpenAI API key is properly set:
```bash
echo $OPENAI_API_KEY
```

### Database Errors
If you encounter database issues, you can start fresh:
```bash
rm -rf projects/[project_name]
python start.py
```

## Tech Stack

- **Language Model**: GPT-4o Mini for efficient, iterative text generation
- **Database**: SQLite for structured project memory
- **Retrieval**: LightRAG for graph-based document querying
- **Prompt Engineering**: Advanced templates for context-rich generation

## Future Enhancements

Planned improvements include:
- Support for additional genres beyond romantic comedy
- Real-time collaborative editing
- Custom knowledge bucket creation
- Quality assurance and consistency checks
- Export to additional formats (Final Draft, Celtx)

## Contributing

This is an alpha release. Feedback and contributions are welcome! Please report issues at the project repository.

## License

[License information to be added]

## Documentation

- [White Paper](WHITEPAPER.md) - Detailed technical overview and research findings
- [API Documentation](docs/api.md) - Coming soon
- [Examples](examples/) - Coming soon

## Contact

For questions or support, contact: ellejansickresearch@gmail.com

---

**Note**: This framework was designed based on the Lizzy White Paper (4/4/2025) and represents a unique approach to AI-assisted long-form writing that addresses traditional challenges like limited context, fragmented workflows, and static outputs.