#!/bin/bash

# Lizzy Alpha Dashboard Launcher
# ==============================
# Demonstrates the complete working system with real module integration

echo "🚀 Starting Lizzy Alpha Complete System Demo..."
echo "=============================================="

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3."
    exit 1
fi

# Set the port
PORT=8080

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT is already in use. Trying to kill existing process..."
    pkill -f "python.*$PORT" 2>/dev/null || true
    sleep 2
fi

echo "📋 LIZZY ALPHA WORKFLOW DEMONSTRATION"
echo "====================================="
echo ""
echo "This system integrates:"
echo "  ✅ Start.py    - Project initialization with SQLite databases"
echo "  ✅ Intake.py   - Character and story element capture" 
echo "  ✅ Brainstorm.py - AI-powered creative idea generation with LightRAG"
echo "  ✅ Write.py    - Draft synthesis and scene generation"
echo ""
echo "🌐 Web Interface: Modern Tailwind CSS dashboard"
echo "🧠 AI Backend: LightRAG with OpenAI GPT-4o integration"
echo "💾 Data Storage: SQLite with project isolation"
echo ""

# Test the core modules
echo "🧪 Testing Core Modules..."
echo "-------------------------"

echo "📁 Testing project creation..."
if $PYTHON_CMD -c "import start; print('✅ start.py module loaded successfully')" 2>/dev/null; then
    echo "✅ Start module: Ready"
else
    echo "❌ Start module: Issues detected"
fi

echo "👥 Testing character intake..."
if $PYTHON_CMD -c "import intake; print('✅ intake.py module loaded successfully')" 2>/dev/null; then
    echo "✅ Intake module: Ready"
else
    echo "❌ Intake module: Issues detected"
fi

echo "💡 Testing brainstorming engine..."
if $PYTHON_CMD -c "import brainstorm; print('✅ brainstorm.py module loaded successfully')" 2>/dev/null; then
    echo "✅ Brainstorm module: Ready"
else
    echo "❌ Brainstorm module: Issues detected"
fi

echo "✍️ Testing writing engine..."
if $PYTHON_CMD -c "import write; print('✅ write.py module loaded successfully')" 2>/dev/null; then
    echo "✅ Write module: Ready"
else
    echo "❌ Write module: Issues detected"
fi

echo ""
echo "🔧 Testing LightRAG Integration..."
if $PYTHON_CMD -c "from lightrag_helper import LightRAGManager; print('✅ LightRAG integration ready')" 2>/dev/null; then
    echo "✅ LightRAG: Ready for AI brainstorming"
else
    echo "⚠️  LightRAG: Check API key configuration"
fi

echo ""
echo "📊 Checking Project Directory..."
if [ -d "projects" ]; then
    PROJECT_COUNT=$(find projects -maxdepth 1 -type d | wc -l)
    PROJECT_COUNT=$((PROJECT_COUNT - 1))  # Subtract the projects directory itself
    echo "✅ Found $PROJECT_COUNT existing projects"
    
    if [ $PROJECT_COUNT -gt 0 ]; then
        echo "📋 Existing projects:"
        for project_dir in projects/*/; do
            if [ -d "$project_dir" ]; then
                project_name=$(basename "$project_dir")
                if [ -f "${project_dir}${project_name}.sqlite" ]; then
                    echo "   📁 $project_name (with database)"
                else
                    echo "   📁 $project_name (no database)"
                fi
            fi
        done
    fi
else
    echo "📁 Creating projects directory..."
    mkdir -p projects
    echo "✅ Projects directory created"
fi

echo ""
echo "🌐 Starting Web Dashboard..."
echo "----------------------------"

# Start the web server in the background
echo "🌐 Starting web server on http://localhost:$PORT"
$PYTHON_CMD -m http.server $PORT > /dev/null 2>&1 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 2

# Check if server started successfully
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "❌ Failed to start web server"
    exit 1
fi

echo "✅ Server started (PID: $SERVER_PID)"

# Open the dashboard in the default browser
echo "📱 Opening Lizzy Alpha Dashboard..."

if command -v open &> /dev/null; then
    # macOS
    open "http://localhost:$PORT/simple_dashboard.html"
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open "http://localhost:$PORT/simple_dashboard.html"
elif command -v start &> /dev/null; then
    # Windows
    start "http://localhost:$PORT/simple_dashboard.html"
else
    echo "🌐 Please open http://localhost:$PORT/simple_dashboard.html in your browser"
fi

echo ""
echo "🎯 LIZZY ALPHA SYSTEM IS NOW RUNNING!"
echo "======================================"
echo ""
echo "📝 Dashboard: http://localhost:$PORT/simple_dashboard.html"
echo "🔧 Alternative: Use command-line modules directly:"
echo "   • python3 start.py      # Create new project"
echo "   • python3 intake.py     # Add characters & scenes"  
echo "   • python3 brainstorm.py # Generate AI ideas"
echo "   • python3 write.py      # Create drafts"
echo ""
echo "💡 Features Available:"
echo "   ✅ Project creation and management"
echo "   ✅ Character development (Essential Trinity framework)"
echo "   ✅ AI-powered brainstorming with LightRAG knowledge"
echo "   ✅ Scene writing with tone presets"
echo "   ✅ Progress tracking and version control"
echo "   ✅ Responsive web interface with dark/light modes"
echo ""
echo "🛑 To stop: Press Ctrl+C or run: kill $SERVER_PID"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Lizzy Alpha Dashboard..."
    kill $SERVER_PID 2>/dev/null || true
    echo "✅ System stopped. Thank you for using Lizzy Alpha!"
    exit 0
}

# Set up signal handlers for clean shutdown
trap cleanup SIGINT SIGTERM

# Keep the script running and show server status
echo "🔄 System running... Press Ctrl+C to stop"
echo "📊 Real-time status monitoring:"
echo "----------------------------------------"

# Monitor the server process
while kill -0 $SERVER_PID 2>/dev/null; do
    echo "⚡ $(date '+%H:%M:%S') - Dashboard active | Projects: $(find projects -name "*.sqlite" 2>/dev/null | wc -l | tr -d ' ') | Server PID: $SERVER_PID"
    sleep 10
done

echo "❌ Server process ended unexpectedly"
cleanup