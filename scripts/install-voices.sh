#!/bin/bash
# 🎤 Automatic French Voice Installation Script for Piper TTS
# Installs male and female voices with medium/high quality

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}🎤 Piper TTS French Voice Installer${NC}"
echo "============================================="

# Configuration
VOICES_DIR="backend/voices"
TMP_DIR="/tmp/piper_voices_$$"
PIPER_RELEASE_URL="https://github.com/rhasspy/piper/releases/latest/download"

# Voice configurations: URL, size, gender, quality, description
declare -A VOICE_CONFIGS=(
    # Female voices
    ["siwis-medium"]="voice-fr-fr-siwis-medium.tar.gz|45MB|female|medium|Voix féminine expressive, qualité optimale"
    ["siwis-high"]="voice-fr-fr-siwis-high.tar.gz|85MB|female|high|Voix féminine très haute qualité (plus lent)"
    
    # Male voices  
    ["tom-medium"]="voice-fr-fr-tom-medium.tar.gz|52MB|male|medium|Voix masculine chaleureuse et professionnelle"
    ["bernard-high"]="voice-fr-fr-bernard-high.tar.gz|125MB|male|high|Voix masculine mature, très haute qualité"
    ["gilles-medium"]="voice-fr-fr-gilles-medium.tar.gz|48MB|male|medium|Voix masculine claire et naturelle"
    
    # Multi-speaker
    ["upmc-medium"]="voice-fr-fr-upmc-medium.tar.gz|85MB|multi|medium|Voix multiple (Jessica♀ + Pierre♂)"
)

# Default installation set (balanced)
DEFAULT_VOICES=("siwis-medium" "tom-medium" "upmc-medium")

# Premium installation set (high quality)  
PREMIUM_VOICES=("siwis-high" "tom-medium" "bernard-high" "upmc-medium")

# Check prerequisites
check_prerequisites() {
    echo -e "\n${PURPLE}📋 Checking prerequisites...${NC}"
    
    # Check project structure
    if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
        echo -e "${RED}❌ Please run from project root directory${NC}"
        exit 1
    fi
    
    # Check tools
    local missing_tools=()
    for tool in curl tar; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing tools: ${missing_tools[*]}${NC}"
        echo -e "${YELLOW}Install with: sudo apt-get install curl tar${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Show available voices
show_voice_menu() {
    echo -e "\n${PURPLE}🎵 Available French Voices:${NC}"
    echo ""
    
    local i=1
    for voice_key in "${!VOICE_CONFIGS[@]}"; do
        IFS='|' read -r filename size gender quality description <<< "${VOICE_CONFIGS[$voice_key]}"
        
        # Gender icon
        local icon="🎭"
        case "$gender" in
            "female") icon="👩‍💼" ;;
            "male") icon="👨‍💼" ;;  
            "multi") icon="👫" ;;
        esac
        
        # Quality badge
        local quality_badge
        case "$quality" in
            "low") quality_badge="${YELLOW}LOW${NC}" ;;
            "medium") quality_badge="${BLUE}MED${NC}" ;;
            "high") quality_badge="${GREEN}HIGH${NC}" ;;
        esac
        
        printf "%2d. %s %-20s [%s] %s - %s\n" "$i" "$icon" "$voice_key" "$quality_badge" "$size" "$description"
        ((i++))
    done
    
    echo ""
    echo -e "${BLUE}📦 Installation Presets:${NC}"
    echo -e "  ${GREEN}default${NC}  - Balanced set (3 voices, ~180MB): siwis-medium + tom-medium + upmc-medium"
    echo -e "  ${PURPLE}premium${NC}  - High quality (4 voices, ~340MB): siwis-high + tom-medium + bernard-high + upmc-medium"
    echo -e "  ${YELLOW}minimal${NC}  - Fastest setup (1 voice, ~45MB): siwis-medium only"
    echo -e "  ${RED}all${NC}      - Complete collection (6 voices, ~440MB): all available voices"
}

# Install specific voice
install_voice() {
    local voice_key="$1"
    local config="${VOICE_CONFIGS[$voice_key]}"
    
    if [ -z "$config" ]; then
        echo -e "${RED}❌ Unknown voice: $voice_key${NC}"
        return 1
    fi
    
    IFS='|' read -r filename size gender quality description <<< "$config"
    
    echo -e "\n${BLUE}📥 Installing $voice_key ($gender, $quality, $size)...${NC}"
    
    # Create temporary directory
    mkdir -p "$TMP_DIR"
    cd "$TMP_DIR"
    
    # Download voice package
    local download_url="$PIPER_RELEASE_URL/$filename"
    echo -e "  📡 Downloading: $download_url"
    
    if ! curl -L -f --progress-bar -o "$filename" "$download_url"; then
        echo -e "${YELLOW}⚠️  Official download failed, trying alternative sources...${NC}"
        
        # Alternative: try older release or manual mirror
        local alt_url="https://github.com/rhasspy/piper/releases/download/v1.2.0/$filename"
        if ! curl -L -f --progress-bar -o "$filename" "$alt_url"; then
            echo -e "${RED}❌ Download failed for $voice_key${NC}"
            cd - > /dev/null
            return 1
        fi
    fi
    
    # Verify download
    if [ ! -f "$filename" ] || [ ! -s "$filename" ]; then
        echo -e "${RED}❌ Downloaded file is empty or missing${NC}"
        cd - > /dev/null
        return 1
    fi
    
    # Extract voice files
    echo -e "  📦 Extracting voice files..."
    if ! tar -xzf "$filename"; then
        echo -e "${RED}❌ Extraction failed${NC}"
        cd - > /dev/null
        return 1
    fi
    
    # Find extracted files
    local onnx_file=$(find . -name "*.onnx" | head -1)
    local json_file=$(find . -name "*.onnx.json" | head -1)
    
    if [ -z "$onnx_file" ]; then
        echo -e "${RED}❌ No .onnx file found in archive${NC}"
        cd - > /dev/null
        return 1
    fi
    
    # Determine target directory based on voice characteristics
    local dataset=$(basename "$onnx_file" .onnx | cut -d'-' -f3)
    local target_dir="../$VOICES_DIR/fr/fr_FR/$dataset/$quality"
    
    echo -e "  📁 Installing to: $target_dir"
    mkdir -p "$target_dir"
    
    # Copy files
    cp "$onnx_file" "$target_dir/"
    if [ -n "$json_file" ]; then
        cp "$json_file" "$target_dir/"
    fi
    
    cd - > /dev/null
    
    # Verify installation
    local installed_onnx="$target_dir/$(basename "$onnx_file")"
    if [ -f "$installed_onnx" ]; then
        local file_size=$(du -h "$installed_onnx" | cut -f1)
        echo -e "${GREEN}✅ Installed: $(basename "$onnx_file") ($file_size)${NC}"
        return 0
    else
        echo -e "${RED}❌ Installation verification failed${NC}"
        return 1
    fi
}

# Install preset
install_preset() {
    local preset="$1"
    local voices_to_install=()
    
    case "$preset" in
        "default")
            voices_to_install=("${DEFAULT_VOICES[@]}")
            echo -e "\n${GREEN}📦 Installing DEFAULT preset (balanced quality)${NC}"
            ;;
        "premium")
            voices_to_install=("${PREMIUM_VOICES[@]}")
            echo -e "\n${PURPLE}📦 Installing PREMIUM preset (high quality)${NC}"
            ;;
        "minimal")
            voices_to_install=("siwis-medium")
            echo -e "\n${YELLOW}📦 Installing MINIMAL preset (fastest)${NC}"
            ;;
        "all")
            voices_to_install=($(printf "%s\n" "${!VOICE_CONFIGS[@]}" | sort))
            echo -e "\n${RED}📦 Installing ALL voices (complete collection)${NC}"
            ;;
        *)
            echo -e "${RED}❌ Unknown preset: $preset${NC}"
            echo -e "Available presets: default, premium, minimal, all"
            return 1
            ;;
    esac
    
    local total=${#voices_to_install[@]}
    local success_count=0
    
    echo -e "Installing $total voices..."
    
    for voice in "${voices_to_install[@]}"; do
        if install_voice "$voice"; then
            ((success_count++))
        fi
    done
    
    echo -e "\n${BLUE}📊 Installation Summary:${NC}"
    echo -e "  Successfully installed: $success_count/$total voices"
    
    if [ $success_count -eq $total ]; then
        echo -e "${GREEN}🎉 All voices installed successfully!${NC}"
        return 0
    elif [ $success_count -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Partial installation completed${NC}"
        return 1
    else
        echo -e "${RED}❌ No voices were installed${NC}"
        return 1
    fi
}

# Test installed voices
test_voices() {
    echo -e "\n${PURPLE}🧪 Testing installed voices...${NC}"
    
    if ! command -v piper &> /dev/null; then
        echo -e "${YELLOW}⚠️  Piper TTS not found - cannot test voices${NC}"
        echo -e "${BLUE}💡 Install Piper with: ./scripts/install-piper.sh${NC}"
        return 1
    fi
    
    local test_text="Bonjour, ceci est un test de synthèse vocale française."
    local voices_found=0
    local voices_working=0
    
    for onnx_file in $(find "$VOICES_DIR" -name "*.onnx" 2>/dev/null); do
        ((voices_found++))
        local voice_name=$(basename "$onnx_file" .onnx)
        local test_output="/tmp/test_${voice_name}_$(date +%s).wav"
        
        echo -n "  Testing $voice_name... "
        
        if timeout 15 echo "$test_text" | piper --model "$onnx_file" --output_file "$test_output" &>/dev/null; then
            if [ -f "$test_output" ] && [ -s "$test_output" ]; then
                echo -e "${GREEN}✅ OK${NC}"
                ((voices_working++))
                rm -f "$test_output"
            else
                echo -e "${RED}❌ No output${NC}"
            fi
        else
            echo -e "${RED}❌ Failed${NC}"
        fi
    done
    
    echo -e "\n${BLUE}📊 Voice Test Results:${NC}"
    echo -e "  Found: $voices_found voices"
    echo -e "  Working: $voices_working voices"
    
    if [ $voices_working -eq 0 ]; then
        echo -e "${RED}❌ No working voices found${NC}"
        return 1
    elif [ $voices_working -lt $voices_found ]; then
        echo -e "${YELLOW}⚠️  Some voices have issues${NC}"
        return 1
    else
        echo -e "${GREEN}✅ All voices are working correctly${NC}"
        return 0
    fi
}

# Generate voice metadata
generate_metadata() {
    echo -e "\n${PURPLE}📝 Generating voice metadata...${NC}"
    
    # Check if backend is available
    if [ ! -f "backend/app/services/voice_manager.py" ]; then
        echo -e "${YELLOW}⚠️  Voice manager service not found${NC}"
        echo -e "Metadata will be generated automatically when backend starts"
        return 0
    fi
    
    cd backend
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Generate metadata using Python service
    python -c "
from app.services.voice_manager import voice_manager
voice_manager.generate_metadata_from_models()
stats = voice_manager.get_voice_statistics()
print(f'✅ Generated metadata for {stats[\"total\"]} voices')
print(f'   - Female: {stats[\"by_gender\"][\"female\"]}')
print(f'   - Male: {stats[\"by_gender\"][\"male\"]}')
print(f'   - Multi: {stats[\"by_gender\"][\"multi\"]}')
print(f'   - Total size: {stats[\"total_size_mb\"]}MB')
"
    
    cd - > /dev/null
    echo -e "${GREEN}✅ Voice metadata generated${NC}"
}

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up temporary files...${NC}"
    rm -rf "$TMP_DIR"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTIONS] [PRESET|VOICE...]"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help        Show this help"
    echo "  -l, --list        List available voices"
    echo "  -t, --test        Test installed voices"
    echo "  -m, --metadata    Generate voice metadata"
    echo "  --no-test         Skip voice testing after installation"
    echo ""
    echo "PRESETS:"
    echo "  default          Install balanced voice set (recommended)"
    echo "  premium          Install high-quality voices" 
    echo "  minimal          Install single voice (fastest)"
    echo "  all              Install all available voices"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                    # Interactive menu"
    echo "  $0 default            # Install default preset"
    echo "  $0 siwis-medium tom-medium    # Install specific voices"
    echo "  $0 --list             # Show available voices"
    echo "  $0 --test             # Test installed voices"
    echo ""
}

# Main execution
main() {
    local run_tests=true
    local interactive=true
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -l|--list)
                show_voice_menu
                exit 0
                ;;
            -t|--test)
                check_prerequisites
                test_voices
                exit $?
                ;;
            -m|--metadata)
                generate_metadata
                exit $?
                ;;
            --no-test)
                run_tests=false
                shift
                ;;
            default|premium|minimal|all)
                interactive=false
                install_preset "$1"
                local result=$?
                [ "$run_tests" = true ] && test_voices
                generate_metadata
                cleanup
                exit $result
                ;;
            *)
                # Check if it's a valid voice name
                if [[ -n "${VOICE_CONFIGS[$1]}" ]]; then
                    interactive=false
                    install_voice "$1"
                    local result=$?
                    shift
                    # Install additional voices if specified
                    while [[ $# -gt 0 && -n "${VOICE_CONFIGS[$1]}" ]]; do
                        install_voice "$1"
                        shift
                    done
                    [ "$run_tests" = true ] && test_voices
                    generate_metadata
                    cleanup
                    exit $result
                else
                    echo -e "${RED}❌ Unknown option or voice: $1${NC}"
                    show_usage
                    exit 1
                fi
                ;;
        esac
    done
    
    # Interactive mode
    if [ "$interactive" = true ]; then
        check_prerequisites
        show_voice_menu
        
        echo -e "\n${BLUE}🤔 What would you like to install?${NC}"
        echo "Enter preset name (default/premium/minimal/all) or specific voice names:"
        read -r -p "Your choice: " user_choice
        
        if [ -z "$user_choice" ]; then
            user_choice="default"
        fi
        
        # Handle user input
        case "$user_choice" in
            default|premium|minimal|all)
                install_preset "$user_choice"
                ;;
            *)
                # Try to install as individual voices
                IFS=' ' read -ra VOICES <<< "$user_choice"
                local success=true
                for voice in "${VOICES[@]}"; do
                    if ! install_voice "$voice"; then
                        success=false
                    fi
                done
                [ "$success" = false ] && exit 1
                ;;
        esac
        
        [ "$run_tests" = true ] && test_voices
        generate_metadata
    fi
    
    cleanup
}

# Set trap for cleanup
trap cleanup EXIT

# Run main function
main "$@"