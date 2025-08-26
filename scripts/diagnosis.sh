#!/bin/bash
# 🔍 Complete TTS Voice Installation Diagnostic Script

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}🔍 TTS Voice Installation Diagnostic${NC}"
echo "======================================"

# Check project structure
echo -e "\n${PURPLE}📁 Project Structure:${NC}"
echo "Current directory: $(pwd)"
echo "Project root check:"
[ -f "README.md" ] && echo "  ✅ README.md found" || echo "  ❌ README.md missing"
[ -d "backend" ] && echo "  ✅ backend/ directory found" || echo "  ❌ backend/ directory missing"
[ -d "frontend" ] && echo "  ✅ frontend/ directory found" || echo "  ❌ frontend/ directory missing"

# Check Piper TTS installation
echo -e "\n${PURPLE}🎤 Piper TTS Installation:${NC}"
if command -v piper &> /dev/null; then
    echo "  ✅ Piper TTS found in PATH"
    echo "  📍 Location: $(which piper)"
    
    # Try to get version
    if piper_version=$(piper --version 2>/dev/null); then
        echo "  📋 Version: $piper_version"
    elif piper --help &>/dev/null; then
        echo "  📋 Version: unknown (responds to --help)"
    else
        echo "  ⚠️  Version detection failed"
    fi
else
    echo -e "  ${RED}❌ Piper TTS not found in PATH${NC}"
    echo -e "  ${YELLOW}💡 Install with: ./scripts/install-piper.sh${NC}"
fi

# Check voices directory structure
echo -e "\n${PURPLE}📂 Voices Directory Structure:${NC}"
VOICES_DIR="backend/voices"

if [ -d "$VOICES_DIR" ]; then
    echo "  ✅ Voices directory exists: $VOICES_DIR"
    
    # Count files
    onnx_count=$(find "$VOICES_DIR" -name "*.onnx" 2>/dev/null | wc -l)
    json_count=$(find "$VOICES_DIR" -name "*.onnx.json" 2>/dev/null | wc -l)
    
    echo "  📊 ONNX models: $onnx_count"
    echo "  📊 JSON metadata: $json_count"
    
    if [ "$onnx_count" -gt 0 ]; then
        echo -e "\n  ${GREEN}🎵 Installed Voice Models:${NC}"
        find "$VOICES_DIR" -name "*.onnx" | while read -r voice_file; do
            # Get file info
            size=$(du -h "$voice_file" 2>/dev/null | cut -f1 || echo "?MB")
            name=$(basename "$voice_file" .onnx)
            path=$(dirname "$voice_file")
            
            # Check for metadata
            json_file="${voice_file}.json"
            if [ -f "$json_file" ]; then
                metadata="✅ with metadata"
            else
                metadata="⚠️  no metadata"
            fi
            
            echo "    • $name ($size, $metadata)"
            echo "      Path: $voice_file"
        done
        
        # Calculate total size
        if command -v du &> /dev/null; then
            total_size=$(du -sh "$VOICES_DIR" 2>/dev/null | cut -f1 || echo "unknown")
            echo -e "\n  💾 Total voices size: $total_size"
        fi
    else
        echo -e "  ${YELLOW}⚠️  No voice models found${NC}"
    fi
    
    # Show directory tree (first few levels)
    echo -e "\n  🌳 Directory tree:"
    if command -v tree &> /dev/null; then
        tree -L 4 "$VOICES_DIR" 2>/dev/null || ls -la "$VOICES_DIR"
    else
        find "$VOICES_DIR" -type d | head -10 | sed 's/^/    /'
    fi
    
else
    echo -e "  ${RED}❌ Voices directory not found: $VOICES_DIR${NC}"
fi

# Test Piper with available voices
echo -e "\n${PURPLE}🧪 Piper TTS Voice Testing:${NC}"

if command -v piper &> /dev/null && [ "$onnx_count" -gt 0 ]; then
    echo "  Testing voice synthesis..."
    
    test_count=0
    working_count=0
    
    find "$VOICES_DIR" -name "*.onnx" | head -3 | while read -r voice_file; do
        test_count=$((test_count + 1))
        voice_name=$(basename "$voice_file" .onnx)
        test_output="/tmp/voice_test_${voice_name}_$(date +%s).wav"
        
        echo -n "    Testing $voice_name... "
        
        # Test with timeout
        if timeout 20 echo "Bonjour, ceci est un test." | piper --model "$voice_file" --output_file "$test_output" &>/dev/null; then
            if [ -f "$test_output" ] && [ -s "$test_output" ]; then
                output_size=$(du -h "$test_output" 2>/dev/null | cut -f1)
                echo -e "${GREEN}✅ OK${NC} (output: $output_size)"
                working_count=$((working_count + 1))
                rm -f "$test_output"
            else
                echo -e "${RED}❌ No output file${NC}"
            fi
        else
            echo -e "${RED}❌ Synthesis failed${NC}"
        fi
    done
    
    echo "  📊 Working voices: $working_count/$test_count"
    
elif ! command -v piper &> /dev/null; then
    echo -e "  ${YELLOW}⚠️  Cannot test: Piper TTS not installed${NC}"
elif [ "$onnx_count" -eq 0 ]; then
    echo -e "  ${YELLOW}⚠️  Cannot test: No voice models found${NC}"
fi

# Check backend configuration
echo -e "\n${PURPLE}⚙️  Backend Configuration:${NC}"

if [ -f "backend/app/core/config.py" ]; then
    echo "  ✅ Backend config file found"
    
    # Try to extract voice_model setting
    if grep -q "voice_model" backend/app/core/config.py; then
        voice_model_line=$(grep "voice_model.*=" backend/app/core/config.py | head -1)
        echo "  🎤 Config voice model: $voice_model_line"
        
        # Extract the path and check if it exists
        voice_path=$(echo "$voice_model_line" | sed -n 's/.*"\([^"]*\)".*/\1/p')
        if [ -n "$voice_path" ] && [ -f "$voice_path" ]; then
            echo "  ✅ Configured voice model exists"
        elif [ -n "$voice_path" ]; then
            echo -e "  ${YELLOW}⚠️  Configured voice model not found: $voice_path${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠️  voice_model setting not found in config${NC}"
    fi
else
    echo -e "  ${RED}❌ Backend config file not found${NC}"
fi

# Check if backend is running
echo -e "\n${PURPLE}🔄 Backend Service Status:${NC}"

if curl -s http://localhost:8000/health &>/dev/null; then
    echo -e "  ✅ Backend is running on port 8000"
    
    # Test voice preview API
    if curl -s http://localhost:8000/api/preview/voices &>/dev/null; then
        voice_count=$(curl -s http://localhost:8000/api/preview/voices | jq -r '.count // 0' 2>/dev/null || echo "unknown")
        echo "  🎤 API reports $voice_count voices available"
    else
        echo -e "  ${YELLOW}⚠️  Preview voices API not responding${NC}"
    fi
    
else
    echo -e "  ${YELLOW}⚠️  Backend not running on port 8000${NC}"
    echo -e "  ${BLUE}💡 Start with: make backend${NC}"
fi

# Check frontend
echo -e "\n${PURPLE}🌐 Frontend Status:${NC}"

if curl -s http://localhost:3000 &>/dev/null; then
    echo "  ✅ Frontend is running on port 3000"
else
    echo -e "  ${YELLOW}⚠️  Frontend not running on port 3000${NC}"
    echo -e "  ${BLUE}💡 Start with: make frontend${NC}"
fi

# Environment variables
echo -e "\n${PURPLE}🔧 Environment Variables:${NC}"

if [ -f ".env" ]; then
    echo "  ✅ .env file found"
    if grep -q "VOICE_MODEL" .env; then
        env_voice=$(grep "VOICE_MODEL" .env)
        echo "  🎤 $env_voice"
    fi
else
    echo -e "  ${YELLOW}⚠️  .env file not found${NC}"
fi

# Installation recommendations
echo -e "\n${PURPLE}💡 Recommendations:${NC}"

if [ "$onnx_count" -eq 0 ]; then
    echo -e "  ${YELLOW}1. Install voice models: ./scripts/voices.sh --recommended${NC}"
fi

if ! command -v piper &> /dev/null; then
    echo -e "  ${YELLOW}2. Install Piper TTS: ./scripts/install-piper.sh${NC}"
fi

if ! curl -s http://localhost:8000/health &>/dev/null; then
    echo -e "  ${YELLOW}3. Start backend: make backend${NC}"
fi

if ! curl -s http://localhost:3000 &>/dev/null; then
    echo -e "  ${YELLOW}4. Start frontend: make frontend${NC}"
fi

if [ "$onnx_count" -gt 0 ] && command -v piper &> /dev/null; then
    echo -e "  ${GREEN}✨ System looks ready! Try: http://localhost:3000${NC}"
fi

echo -e "\n${BLUE}🎉 Diagnostic completed!${NC}"
echo "======================================"