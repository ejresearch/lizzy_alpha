#!/bin/bash

# Lizzy Alpha Dashboard Launcher
# ==============================
# Starts a local web server and opens the dashboard

echo "🚀 Starting Lizzy Alpha Dashboard..."
echo "=================================="

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
echo "📱 Opening dashboard at http://localhost:$PORT/lizzy_alpha_dashboard.html"

# Open the dashboard in the default browser
if command -v open &> /dev/null; then
    # macOS
    open "http://localhost:$PORT/lizzy_alpha_dashboard.html"
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open "http://localhost:$PORT/lizzy_alpha_dashboard.html"
elif command -v start &> /dev/null; then
    # Windows
    start "http://localhost:$PORT/lizzy_alpha_dashboard.html"
else
    echo "🌐 Please open http://localhost:$PORT/lizzy_alpha_dashboard.html in your browser"
fi

echo ""
echo "🎯 Dashboard is now running!"
echo "📝 Access your Lizzy Alpha writing framework at:"
echo "   http://localhost:$PORT/lizzy_alpha_dashboard.html"
echo ""
echo "💡 To stop the server:"
echo "   Press Ctrl+C or run: kill $SERVER_PID"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Lizzy Alpha Dashboard..."
    kill $SERVER_PID 2>/dev/null || true
    echo "✅ Server stopped. Goodbye!"
    exit 0
}

# Set up signal handlers for clean shutdown
trap cleanup SIGINT SIGTERM

# Keep the script running and show server status
echo "🔄 Server running... Press Ctrl+C to stop"
echo "----------------------------------------"

# Monitor the server process
while kill -0 $SERVER_PID 2>/dev/null; do
    sleep 5
done

echo "❌ Server process ended unexpectedly"
cleanup