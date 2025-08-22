#!/bin/bash

# Modern Lizzy Alpha Dashboard Launcher
# ====================================
# Launches the professional web dashboard with API backend integration

echo "🚀 Starting Lizzy Alpha Modern Dashboard..."
echo "============================================"

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
PORT=5003

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT is already in use. Trying to kill existing process..."
    pkill -f "python.*$PORT" 2>/dev/null || true
    sleep 2
fi

echo "🎯 MODERN LIZZY ALPHA DASHBOARD"
echo "==============================="
echo ""
echo "✨ Features:"
echo "  🎨 Modern, responsive web interface"
echo "  🌙 Dark/light mode toggle"
echo "  📱 Mobile-friendly design"
echo "  🔗 Full API integration with existing modules"
echo "  📊 Real-time project management"
echo "  🔄 Live data synchronization"
echo ""

# Test the core modules
echo "🧪 Testing Core Modules..."
echo "-------------------------"

echo "📁 Testing project creation..."
if $PYTHON_CMD -c "import start; print('✅ start.py module loaded successfully')" 2>/dev/null; then
    echo "✅ Start module: Ready"
else
    echo "⚠️  Start module: Issues detected (will use simulation mode)"
fi

echo "👥 Testing character intake..."
if $PYTHON_CMD -c "import intake; print('✅ intake.py module loaded successfully')" 2>/dev/null; then
    echo "✅ Intake module: Ready"
else
    echo "⚠️  Intake module: Issues detected (will use simulation mode)"
fi

echo "💡 Testing brainstorming engine..."
if $PYTHON_CMD -c "import brainstorm; print('✅ brainstorm.py module loaded successfully')" 2>/dev/null; then
    echo "✅ Brainstorm module: Ready"
else
    echo "⚠️  Brainstorm module: Issues detected (will use simulation mode)"
fi

echo "✍️  Testing writing engine..."
if $PYTHON_CMD -c "import write; print('✅ write.py module loaded successfully')" 2>/dev/null; then
    echo "✅ Write module: Ready"
else
    echo "⚠️  Write module: Issues detected (will use simulation mode)"
fi

echo ""
echo "🔧 Testing Flask and Dependencies..."
if $PYTHON_CMD -c "import flask, flask_cors; print('✅ Flask dependencies ready')" 2>/dev/null; then
    echo "✅ Flask: Ready"
else
    echo "❌ Flask dependencies missing. Installing..."
    $PYTHON_CMD -m pip install flask flask-cors
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
echo "🌐 Starting Modern Dashboard API..."
echo "-----------------------------------"

# Start the Flask API server in the background
echo "🔗 Starting Flask API server on http://localhost:$PORT"
$PYTHON_CMD modern_api.py > /dev/null 2>&1 &
API_PID=$!

# Wait a moment for server to start
sleep 3

# Check if server started successfully
if ! kill -0 $API_PID 2>/dev/null; then
    echo "❌ Failed to start API server"
    exit 1
fi

echo "✅ API Server started (PID: $API_PID)"

# Open the dashboard in the default browser
echo "📱 Opening Modern Dashboard..."

if command -v open &> /dev/null; then
    # macOS
    open "http://localhost:$PORT/"
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open "http://localhost:$PORT/"
elif command -v start &> /dev/null; then
    # Windows
    start "http://localhost:$PORT/"
else
    echo "🌐 Please open http://localhost:$PORT/ in your browser"
fi

echo ""
echo "🎯 MODERN LIZZY ALPHA DASHBOARD IS NOW RUNNING!"
echo "==============================================="
echo ""
echo "📝 Dashboard: http://localhost:$PORT/"
echo "🔗 API Base: http://localhost:$PORT/api/"
echo "📊 API Status: http://localhost:$PORT/api/status"
echo ""
echo "💡 Features Available:"
echo "   ✅ Modern responsive web interface"
echo "   ✅ Project creation and management"
echo "   ✅ Character development with Essential Trinity framework"
echo "   ✅ AI-powered brainstorming with LightRAG integration" 
echo "   ✅ Scene writing and generation"
echo "   ✅ Dark/light mode toggle"
echo "   ✅ Mobile-friendly design"
echo "   ✅ Real-time data synchronization"
echo ""
echo "🛑 To stop: Press Ctrl+C or run: kill $API_PID"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Modern Dashboard..."
    kill $API_PID 2>/dev/null || true
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
while kill -0 $API_PID 2>/dev/null; do
    echo "⚡ $(date '+%H:%M:%S') - Dashboard active | Projects: $(find projects -name "*.sqlite" 2>/dev/null | wc -l | tr -d ' ') | API PID: $API_PID"
    sleep 10
done

echo "❌ API server process ended unexpectedly"
cleanup