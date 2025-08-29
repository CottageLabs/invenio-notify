#!/bin/bash
#
# render_mermaid_diagrams.sh - Render Mermaid diagrams to PNG format
#
# This script finds all .mmd files in docs/diagram directory and converts them
# to PNG format using mermaid-cli (mmdc).
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DIAGRAM_DIR="${PROJECT_ROOT}/docs/diagram"
OUTPUT_DIR="${PROJECT_ROOT}/docs_sphinx/_static/mmd"

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if mmdc is installed
check_mmdc() {
    if ! command -v mmdc &> /dev/null; then
        log_error "mermaid-cli (mmdc) is not installed or not in PATH"
        log_error "Install with: npm install -g @mermaid-js/mermaid-cli"
        exit 1
    fi
    log_info "Found mmdc: $(which mmdc)"
}

# Check if diagram directory exists
check_diagram_dir() {
    if [ ! -d "$DIAGRAM_DIR" ]; then
        log_error "Diagram directory not found: $DIAGRAM_DIR"
        exit 1
    fi
    log_info "Diagram directory: $DIAGRAM_DIR"
}

# Process mermaid files
process_mermaid_files() {
    local file_count=0
    local success_count=0
    local error_count=0

    # Find all .mmd files in the diagram directory
    while IFS= read -r -d '' file; do
        file_count=$((file_count + 1))

        local _file_path=`realpath --relative-to="$DIAGRAM_DIR" "$file"`
        local output_file="${OUTPUT_DIR}/${_file_path%.mmd}.png"
        mkdir -p "$(dirname "$output_file")"
        
        log_info "Processing: $(basename "$file")"
        
        # Determine diagram type and use appropriate settings
        local diagram_type=$(head -n 10 "$file" | grep -E "^(sequenceDiagram|erDiagram|graph|flowchart)" | head -n 1)
        local mmdc_options="-t default --quiet"
        
        # Enhanced options for sequence diagrams
        if [[ "$diagram_type" =~ sequenceDiagram ]]; then
            mmdc_options="-t default -w 1200 -H 800 --backgroundColor white --scale 2 --quiet"
        # Enhanced options for ER diagrams  
        elif [[ "$diagram_type" =~ erDiagram ]]; then
            mmdc_options="-t default -w 1400 -H 1000 --backgroundColor white --scale 2 --quiet"
        fi
        
        if mmdc -i "$file" -o "$output_file" $mmdc_options; then
            success_count=$((success_count + 1))
            log_info "Generated: $(basename "$output_file")"
        else
            error_count=$((error_count + 1))
            log_error "Failed to process: $(basename "$file")"
        fi
    done < <(find "$DIAGRAM_DIR" -name '*.mmd' -print0)

    # Summary
    if [ $file_count -eq 0 ]; then
        log_warn "No .mmd files found in $DIAGRAM_DIR"
        return 0
    fi

    log_info "Summary: $success_count successful, $error_count failed out of $file_count files"
    
    if [ $error_count -gt 0 ]; then
        return 1
    fi
    return 0
}

# Main execution
main() {
    log_info "Starting Mermaid diagram rendering..."
    log_info "Project root: $PROJECT_ROOT"
    
    check_mmdc
    check_diagram_dir

    mkdir -p "$OUTPUT_DIR"

    if process_mermaid_files; then
        log_info "All diagrams rendered successfully!"
    else
        log_error "Some diagrams failed to render"
        exit 1
    fi
}

# Run main function
main "$@"