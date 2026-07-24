#!/bin/bash
# MultiClip V3 Unified Launcher
# Usage: ./multiclip-launcher.sh [start|stop|restart|status|launch|now]
#
#   start   - Start the sysVinit service (runs at boot)
#   stop    - Stop the service
#   restart - Restart the service
#   status  - Check if service is running
#   launch  - Launch MultiClip interactively in current terminal (for debugging)
#   now     - Launch MultiClip right now, visible on all XFCE workspaces
#   (no arg)- Same as 'start'

set -e

NAME="multiclip"
INIT_SCRIPT="/etc/init.d/multiclip"
PIDFILE="/var/run/multiclip.pid"
LOG="/var/log/multiclip.log"
PROJECT_DIR="/home/flintx/multiclip"
RUNUSER="flintx"

# X11 environment for root to access user's display
export DISPLAY=:0
export XAUTHORITY=/tmp/.Xauthority_multiclip
export XDG_RUNTIME_DIR=/run/user/1000
export HOME=/home/flintx

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Ensure X authority cookie is available
_ensure_xauth() {
    if [ -f "/home/$RUNUSER/.Xauthority" ]; then
        cp -f "/home/$RUNUSER/.Xauthority" "$XAUTHORITY" 2>/dev/null || true
        chmod 644 "$XAUTHORITY" 2>/dev/null || true
    fi
}

# Wait for X11 to be ready (up to 30s)
_wait_for_x() {
    for i in $(seq 1 30); do
        if xset q >/dev/null 2>&1; then
            return 0
        fi
        sleep 1
    done
    return 1
}

# Find the right Python binary
_find_python() {
    cd "$PROJECT_DIR"
    if [ -x "./.venv/bin/python3" ]; then
        echo "./.venv/bin/python3"
    elif [ -x "./.venv/bin/python" ]; then
        echo "./.venv/bin/python"
    elif [ -x "./venv/bin/python3" ]; then
        echo "./venv/bin/python3"
    else
        echo "python3"
    fi
}

# Make window sticky (visible on all workspaces) via xdotool
_make_sticky() {
    sleep 2
    # Find the MultiClip window and make it sticky
    for i in $(seq 1 10); do
        WID=$(xdotool search --name "MultiClip" 2>/dev/null | head -1)
        if [ -n "$WID" ]; then
            # _NET_WM_STATE_STICKY = 0x1 (bit 0 of _NET_WM_STATE)
            xdotool set_window --overrideredirect 0 "$WID" 2>/dev/null || true
            # Use wmctrl to set sticky state
            wmctrl -i -r "$WID" -b add,sticky 2>/dev/null || true
            # Also set it to appear on all desktops
            wmctrl -i -r "$WID" -b add,skip_taskbar 2>/dev/null || true
            log_ok "Window made sticky (all workspaces)"
            return 0
        fi
        sleep 0.5
    done
    log_warn "Could not find MultiClip window to make sticky"
}

cmd="${1:-start}"

case "$cmd" in
    start)
        log_info "Starting MultiClip service..."
        _ensure_xauth
        if [ -f "$INIT_SCRIPT" ]; then
            "$INIT_SCRIPT" start
            log_ok "Service started. Check status with: $0 status"
        else
            log_error "Init script not found at $INIT_SCRIPT"
            exit 1
        fi
        ;;

    stop)
        log_info "Stopping MultiClip service..."
        if [ -f "$INIT_SCRIPT" ]; then
            "$INIT_SCRIPT" stop
            log_ok "Service stopped"
        else
            log_error "Init script not found"
            exit 1
        fi
        ;;

    restart)
        log_info "Restarting MultiClip service..."
        if [ -f "$INIT_SCRIPT" ]; then
            "$INIT_SCRIPT" restart
            log_ok "Service restarted"
        else
            log_error "Init script not found"
            exit 1
        fi
        ;;

    status)
        if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE" 2>/dev/null) 2>/dev/null; then
            PID=$(cat "$PIDFILE")
            log_ok "MultiClip is RUNNING (pid $PID)"
            echo ""
            echo "  PID:      $PID"
            echo "  Log:      $LOG"
            echo "  PID file: $PIDFILE"
            echo ""
            # Show last 5 log lines
            if [ -f "$LOG" ]; then
                echo "  Last 5 log lines:"
                tail -n 5 "$LOG" | sed 's/^/    /'
            fi
        else
            log_warn "MultiClip is NOT running"
            if [ -f "$LOG" ]; then
                echo ""
                echo "  Last 10 log lines:"
                tail -n 10 "$LOG" | sed 's/^/    /'
            fi
        fi
        ;;

    launch)
        log_info "Launching MultiClip interactively (for debugging)..."
        _ensure_xauth
        if ! _wait_for_x; then
            log_error "X11 not available. Is the desktop running?"
            exit 1
        fi
        cd "$PROJECT_DIR"
        PYTHON_BIN=$(_find_python)
        log_info "Using Python: $PYTHON_BIN"
        exec "$PYTHON_BIN" multiclip.py
        ;;

    now)
        log_info "Launching MultiClip RIGHT NOW..."
        _ensure_xauth
        if ! _wait_for_x; then
            log_error "X11 not available. Is the desktop running?"
            exit 1
        fi
        cd "$PROJECT_DIR"
        PYTHON_BIN=$(_find_python)
        log_info "Using Python: $PYTHON_BIN"
        # Launch in background and make sticky
        nohup "$PYTHON_BIN" multiclip.py >> "$LOG" 2>&1 &
        MPID=$!
        log_ok "MultiClip launched (pid $MPID)"
        # Make window sticky on all workspaces
        _make_sticky &
        log_info "Window will appear on ALL workspaces"
        ;;

    help|--help|-h)
        echo "MultiClip V3 Unified Launcher"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start   Start the boot service (default)"
        echo "  stop    Stop the service"
        echo "  restart Restart the service"
        echo "  status  Check if running + show recent logs"
        echo "  launch  Launch interactively in terminal (debug mode)"
        echo "  now     Launch right now, visible on all workspaces"
        echo "  help    Show this help"
        echo ""
        echo "Examples:"
        echo "  $0              # Start service"
        echo "  $0 restart      # Restart after code changes"
        echo "  $0 status       # Check if alive"
        echo "  $0 now          # Launch immediately for testing"
        ;;

    *)
        log_error "Unknown command: $cmd"
        echo "Run '$0 help' for usage"
        exit 1
        ;;
esac
