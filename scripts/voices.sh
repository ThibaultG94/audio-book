#!/bin/bash
# 🎤 Automatic voice models installation script for Piper TTS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎤 Piper TTS Voice Models Installation${NC}"

# Check if we're in project root
if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
    echo -e "${RED}❌ Please run from project root directory${NC}"
    exit 1
fi

# Create voices directory
VOICES_DIR="backend/voices"
mkdir -p "$VOICES_DIR"

# Voice models configuration
declare -A VOICE_MODELS=(
    # French voices (recommended)
    ["fr-siwis-low"]="voice-fr-siwis-low.tar.gz|Français Siwis Qualité Rapide|10MB"
    ["fr-siwis-medium"]="voice-fr-siwis-medium.tar.gz|Français Siwis Qualité Équilibrée|25MB" 
    ["fr-upmc-medium"]="voice-fr-upmc-medium.tar.gz|Français UPMC Qualité Élevée|30MB"
    ["fr-tom-medium"]="voice-fr-tom-medium.tar.gz|Français Tom Voix Masculine|28MB"
    
    # English voices (popular)
    ["en-us-amy-low"]="voice-en_US-amy-low.tar.gz|English US Amy Fast|12MB"
    ["en-us-amy-medium"]="voice-en_US-amy-medium.tar.gz|English US Amy Natural|35MB"
    ["en-us-danny-low"]="voice-en_US-danny-low.tar.gz|English US Danny Male|15MB"
    ["en-gb-alba-medium"]="voice-en_GB-alba-medium.tar.gz|English UK Alba Female|32MB"
    
    # Other languages
    ["es-es-davefx-medium"]="voice-es_ES-davefx-medium.tar.gz|Español David Masculine|25MB"
    ["de-de-thorsten-medium"]="voice-de_DE-thorsten-medium.tar.gz|Deutsch Thorsten Natural|40MB"
    ["it-it-riccardo-medium"]="voice-it_IT-riccardo-medium.tar.gz|Italiano Riccardo|30MB"
)

# Piper TTS release URL
PIPER_RELEASE_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0"

show_usage() {
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [options] [voice-codes...]"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  -h, --help          Show this help"
    echo "  -l, --list          List all available voices"
    echo "  -r, --recommended   Install recommended French voices only"
    echo "  -a, --all          Install all available voices (large download!)"
    echo "  -f, --french       Install all French voices"
    echo "  -e, --english      Install all English voices"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 --recommended                    # Install best French voices"
    echo "  $0 --french                        # Install all French voices"
    echo "  $0 fr-siwis-medium en-us-amy-low   # Install specific voices"
    echo "  $0 --list                          # Show all available voices"
}

list_voices() {
    echo -e "${BLUE}📋 Available Voice Models:${NC}"
    echo ""
    echo -e "${PURPLE}French Voices (Français):${NC}"
    for voice_code in "${!VOICE_MODELS[@]}"; do
        if [[ $voice_code == fr-* ]]; then
            IFS='|' read -r filename description size <<< "${VOICE_MODELS[$voice_code]}"
            printf "  %-20s %s (%s)\n" "$voice_code" "$description" "$size"
        fi
    done
    
    echo ""
    echo -e "${PURPLE}English Voices:${NC}"
    for voice_code in "${!VOICE_MODELS[@]}"; do
        if [[ $voice_code == en-* ]]; then
            IFS='|' read -r filename description size <<< "${VOICE_MODELS[$voice_code]}"
            printf "  %-20s %s (%s)\n" "$voice_code" "$description" "$size"
        fi
    done
    
    echo ""
    echo -e "${PURPLE}Other Languages:${NC}"
    for voice_code in "${!VOICE_MODELS[@]}"; do
        if [[ $voice_code != fr-* && $voice_code != en-* ]]; then
            IFS='|' read -r filename description size <<< "${VOICE_MODELS[$voice_code]}"
            printf "  %-20s %s (%s)\n" "$voice_code" "$description" "$size"
        fi
    done
    
    echo ""
    echo -e "${YELLOW}💡 Recommandations:${NC}"
    echo "  • fr-siwis-medium    : Meilleur équilibre qualité/vitesse pour le français"
    echo "  • fr-upmc-medium     : Très haute qualité française (plus lent)"
    echo "  • en-us-amy-medium   : Anglais américain naturel"
    echo "  • fr-tom-medium      : Voix masculine française"
}

download_voice_model() {
    local voice_code="$1"
    
    if [[ ! "${VOICE_MODELS[$voice_code]+isset}" ]]; then
        echo -e "${RED}❌ Unknown voice model: $voice_code${NC}"
        echo "Run '$0 --list' to see available voices"
        return 1
    fi
    
    IFS='|' read -r filename description size <<< "${VOICE_MODELS[$voice_code]}"
    
    echo -e "${YELLOW}📥 Downloading: $description ($size)${NC}"
    
    # Download with progress
    download_url="$PIPER_RELEASE_URL/$filename"
    temp_file="/tmp/$filename"
    
    if command -v curl &> /dev/null; then
        curl -L --progress-bar "$download_url" -o "$temp_file"
    elif command -v wget &> /dev/null; then
        wget --progress=bar "$download_url" -O "$temp_file"
    else
        echo -e "${RED}❌ Neither curl nor wget found. Please install one.${NC}"
        return 1
    fi
    
    # Verify download
    if [ ! -f "$temp_file" ] || [ ! -s "$temp_file" ]; then
        echo -e "${RED}❌ Download failed or file empty${NC}"
        return 1
    fi
    
    # Extract to voices directory
    echo -e "${YELLOW}📦 Extracting voice model...${NC}"
    cd "$VOICES_DIR"
    
    if ! tar -xzf "$temp_file"; then
        echo -e "${RED}❌ Extraction failed${NC}"
        rm -f "$temp_file"
        return 1
    fi
    
    # Cleanup
    rm -f "$temp_file"
    
    # Verify extraction
    extracted_files=$(find . -name "*.onnx" -newer /tmp -o -name "*.onnx.json" -newer /tmp 2>/dev/null | wc -l)
    if [ "$extracted_files" -gt 0 ]; then
        echo -e "${GREEN}✅ Successfully installed: $description${NC}"
        
        # Show extracted files
        echo -e "${BLUE}📁 Extracted files:${NC}"
        find . -name "*.onnx" -newer /tmp -o -name "*.onnx.json" -newer /tmp 2>/dev/null | head -5 | sed 's/^/  /'
    else
        echo -e "${YELLOW}⚠️  Voice model downloaded but files not found${NC}"
        echo "   Check manually in: $VOICES_DIR"
    fi
    
    cd - > /dev/null
}

install_recommended() {
    echo -e "${GREEN}🌟 Installing recommended French voices...${NC}"
    download_voice_model "fr-siwis-medium"
    download_voice_model "fr-upmc-medium"
    echo -e "${GREEN}✅ Recommended voices installed${NC}"
}

install_french() {
    echo -e "${GREEN}🇫🇷 Installing all French voices...${NC}"
    for voice_code in "${!VOICE_MODELS[@]}"; do
        if [[ $voice_code == fr-* ]]; then
            download_voice_model "$voice_code"
        fi
    done
    echo -e "${GREEN}✅ All French voices installed${NC}"
}

install_english() {
    echo -e "${GREEN}🇺🇸 Installing English voices...${NC}"
    for voice_code in "${!VOICE_MODELS[@]}"; do
        if [[ $voice_code == en-* ]]; then
            download_voice_model "$voice_code"
        fi
    done
    echo -e "${GREEN}✅ All English voices installed${NC}"
}

install_all() {
    echo -e "${YELLOW}⚠️  This will download ALL voices (~400MB total)${NC}"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled"
        return 0
    fi
    
    echo -e "${GREEN}🌍 Installing all available voices...${NC}"
    for voice_code in "${!VOICE_MODELS[@]}"; do
        download_voice_model "$voice_code"
    done
    echo -e "${GREEN}✅ All voices installed${NC}"
}

check_installation() {
    echo -e "${BLUE}🔍 Checking current voice installation...${NC}"
    
    if [ ! -d "$VOICES_DIR" ]; then
        echo -e "${YELLOW}📁 Voices directory doesn't exist yet${NC}"
        return
    fi
    
    cd "$VOICES_DIR"
    
    # Count installed models
    onnx_count=$(find . -name "*.onnx" 2>/dev/null | wc -l)
    json_count=$(find . -name "*.onnx.json" 2>/dev/null | wc -l)
    
    echo -e "${GREEN}📊 Installation Status:${NC}"
    echo "  Voice models (.onnx): $onnx_count"
    echo "  Metadata files (.json): $json_count"
    
    if [ "$onnx_count" -gt 0 ]; then
        echo ""
        echo -e "${BLUE}🎤 Installed voices:${NC}"
        find . -name "*.onnx" | head -10 | while read -r voice_file; do
            voice_name=$(basename "$voice_file" .onnx)
            file_size=$(du -h "$voice_file" 2>/dev/null | cut -f1)
            echo "  • $voice_name ($file_size)"
        done
        
        if [ "$onnx_count" -gt 10 ]; then
            echo "  ... and $((onnx_count - 10)) more voices"
        fi
    else
        echo -e "${YELLOW}⚠️  No voice models installed yet${NC}"
        echo "   Run: $0 --recommended"
    fi
    
    # Check disk usage
    if command -v du &> /dev/null; then
        total_size=$(du -sh . 2>/dev/null | cut -f1)
        echo ""
        echo -e "${BLUE}💾 Total voices size: $total_size${NC}"
    fi
    
    cd - > /dev/null
}

verify_installation() {
    echo -e "${BLUE}🧪 Testing voice models with Piper TTS...${NC}"
    
    if ! command -v piper &> /dev/null; then
        echo -e "${RED}❌ Piper TTS not found in PATH${NC}"
        echo "   Install with: ./scripts/install-piper.sh"
        return 1
    fi
    
    cd "$VOICES_DIR"
    
    tested_count=0
    working_count=0
    
    # Test up to 5 voice models
    find . -name "*.onnx" | head -5 | while read -r voice_file; do
        tested_count=$((tested_count + 1))
        voice_name=$(basename "$voice_file" .onnx)
        
        echo -n "  Testing $voice_name... "
        
        # Quick test with minimal text
        if timeout 10 piper --model "$voice_file" --output_file "/tmp/test_${voice_name}.wav" <<< "Test." &>/dev/null; then
            echo -e "${GREEN}✅ OK${NC}"
            working_count=$((working_count + 1))
            rm -f "/tmp/test_${voice_name}.wav"
        else
            echo -e "${RED}❌ Failed${NC}"
        fi
    done
    
    echo ""
    echo -e "${GREEN}📊 Test results: $working_count/$tested_count voices working${NC}"
    
    cd - > /dev/null
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_usage
        exit 0
        ;;
    -l|--list)
        list_voices
        check_installation
        exit 0
        ;;
    -r|--recommended)
        check_installation
        install_recommended
        verify_installation
        exit 0
        ;;
    -f|--french)
        check_installation
        install_french
        verify_installation
        exit 0
        ;;
    -e|--english)
        check_installation
        install_english
        verify_installation
        exit 0
        ;;
    -a|--all)
        check_installation
        install_all
        verify_installation
        exit 0
        ;;
    "")
        echo -e "${YELLOW}No arguments provided${NC}"
        show_usage
        echo ""
        check_installation
        echo ""
        echo -e "${BLUE}💡 Quick start:${NC}"
        echo "  $0 --recommended    # Install best French voices"
        echo "  $0 --list          # See all available voices"
        exit 0
        ;;
    *)
        # Install specific voice models
        check_installation
        echo ""
        echo -e "${GREEN}🎯 Installing specific voices...${NC}"
        
        for voice_code in "$@"; do
            if [[ "${VOICE_MODELS[$voice_code]+isset}" ]]; then
                download_voice_model "$voice_code"
            else
                echo -e "${RED}❌ Unknown voice: $voice_code${NC}"
                echo "   Run '$0 --list' to see available voices"
            fi
        done
        
        verify_installation
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Voice installation completed!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Restart backend: make backend"
echo "  2. Test voices: http://localhost:3000"
echo "  3. Check API: http://localhost:8000/api/preview/voices"