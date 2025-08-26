#!/bin/bash
# 🔧 Fix voice structure and test Piper TTS functionality

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Fixing Voice Structure and Testing TTS${NC}"

VOICES_DIR="backend/voices"

# Step 1: Fix voice directory structure
echo -e "\n${YELLOW}📁 Step 1: Fixing voice directory structure...${NC}"

if [ ! -d "$VOICES_DIR" ]; then
    echo -e "${RED}❌ Voices directory not found: $VOICES_DIR${NC}"
    exit 1
fi

# Create proper directory structure
mkdir -p "$VOICES_DIR/fr/fr_FR/siwis/low"
mkdir -p "$VOICES_DIR/fr/fr_FR/siwis/medium"
mkdir -p "$VOICES_DIR/fr/fr_FR/upmc/medium"

# Move misplaced UPMC files if they exist in siwis directory
if [ -f "$VOICES_DIR/fr/fr_FR/siwis/medium/fr_FR-upmc-medium.onnx" ]; then
    echo -e "${YELLOW}🔄 Moving misplaced UPMC files...${NC}"
    mv "$VOICES_DIR/fr/fr_FR/siwis/medium/fr_FR-upmc-medium.onnx" "$VOICES_DIR/fr/fr_FR/upmc/medium/"
    mv "$VOICES_DIR/fr/fr_FR/siwis/medium/fr_FR-upmc-medium.onnx.json" "$VOICES_DIR/fr/fr_FR/upmc/medium/" 2>/dev/null || true
fi

echo -e "${GREEN}✅ Directory structure fixed${NC}"

# Step 2: Verify file structure
echo -e "\n${YELLOW}📊 Step 2: Verifying voice files...${NC}"

find "$VOICES_DIR" -name "*.onnx" -type f | while read -r voice_file; do
    size=$(du -h "$voice_file" | cut -f1)
    name=$(basename "$voice_file" .onnx)
    echo "  • $name: $size"
    
    # Check if JSON metadata exists
    json_file="${voice_file}.json"
    if [ -f "$json_file" ]; then
        echo "    ✅ Metadata file present"
    else
        echo "    ⚠️  Metadata file missing"
    fi
done

# Step 3: Test individual voice models with Piper
echo -e "\n${YELLOW}🧪 Step 3: Testing individual voice models...${NC}"

if ! command -v piper &> /dev/null; then
    echo -e "${RED}❌ Piper TTS not found in PATH${NC}"
    echo -e "${YELLOW}💡 Install with: ./scripts/install-piper.sh${NC}"
    exit 1
fi

test_text="Bonjour, ceci est un test de synthèse vocale."
test_count=0
working_count=0

find "$VOICES_DIR" -name "*.onnx" -type f | while read -r voice_file; do
    test_count=$((test_count + 1))
    voice_name=$(basename "$voice_file" .onnx)
    test_output="/tmp/test_${voice_name}_$(date +%s).wav"
    
    echo -n "  Testing $voice_name... "
    
    # Test with detailed error capture
    if timeout 20 echo "$test_text" | piper --model "$voice_file" --output_file "$test_output" 2>/tmp/piper_error.log; then
        if [ -f "$test_output" ] && [ -s "$test_output" ]; then
            output_size=$(du -h "$test_output" | cut -f1)
            echo -e "${GREEN}✅ OK${NC} (output: $output_size)"
            working_count=$((working_count + 1))
            rm -f "$test_output"
        else
            echo -e "${RED}❌ No output file generated${NC}"
            if [ -f "/tmp/piper_error.log" ] && [ -s "/tmp/piper_error.log" ]; then
                echo "    Error: $(head -1 /tmp/piper_error.log)"
            fi
        fi
    else
        echo -e "${RED}❌ Synthesis failed${NC}"
        if [ -f "/tmp/piper_error.log" ] && [ -s "/tmp/piper_error.log" ]; then
            echo "    Error: $(head -1 /tmp/piper_error.log)"
        fi
    fi
    
    # Clean up
    rm -f "/tmp/piper_error.log"
done

echo -e "\n${BLUE}📊 Test summary: $working_count working voices${NC}"

# Step 4: Test with different Piper parameters
echo -e "\n${YELLOW}🔧 Step 4: Testing with different TTS parameters...${NC}"

# Find first working voice for parameter testing
first_voice=$(find "$VOICES_DIR" -name "*.onnx" -type f | head -1)

if [ -n "$first_voice" ]; then
    voice_name=$(basename "$first_voice" .onnx)
    echo "Testing parameters with: $voice_name"
    
    # Test with different parameters
    test_params=(
        "--length_scale 0.9 --noise_scale 0.5"
        "--length_scale 1.1 --noise_scale 0.8"
        "--sentence_silence 0.5"
    )
    
    for params in "${test_params[@]}"; do
        test_output="/tmp/param_test_$(date +%s).wav"
        echo -n "  Testing with params ($params)... "
        
        if timeout 15 echo "Test paramètres $params" | piper --model "$first_voice" $params --output_file "$test_output" 2>/dev/null; then
            if [ -f "$test_output" ] && [ -s "$test_output" ]; then
                echo -e "${GREEN}✅ OK${NC}"
                rm -f "$test_output"
            else
                echo -e "${RED}❌ No output${NC}"
            fi
        else
            echo -e "${RED}❌ Failed${NC}"
        fi
    done
fi

# Step 5: Update backend configuration
echo -e "\n${YELLOW}⚙️ Step 5: Checking backend configuration...${NC}"

config_file="backend/app/core/config.py"
if [ -f "$config_file" ]; then
    # Find best available voice for default
    best_voice=""
    
    # Priority: medium quality first
    if [ -f "$VOICES_DIR/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx" ]; then
        best_voice="voices/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx"
    elif [ -f "$VOICES_DIR/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx" ]; then
        best_voice="voices/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx"
    elif [ -f "$VOICES_DIR/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx" ]; then
        best_voice="voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx"
    fi
    
    if [ -n "$best_voice" ]; then
        echo -e "${GREEN}✅ Best available voice: $best_voice${NC}"
        echo "  Backend will auto-detect this voice on startup"
    else
        echo -e "${YELLOW}⚠️  No voice models found for backend configuration${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Backend config file not found${NC}"
fi

# Step 6: Test API endpoints
echo -e "\n${YELLOW}🌐 Step 6: Testing API endpoints...${NC}"

# Check if backend is running
if curl -s http://localhost:8000/health &>/dev/null; then
    echo -e "${GREEN}✅ Backend is running${NC}"
    
    # Test voices API
    if curl -s http://localhost:8000/api/preview/voices &>/dev/null; then
        voice_count=$(curl -s http://localhost:8000/api/preview/voices | jq -r '.count // "unknown"' 2>/dev/null)
        echo "  🎤 API reports: $voice_count voices"
    else
        echo -e "${YELLOW}⚠️  Voices API not responding${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Backend not running${NC}"
    echo "  Start with: make backend"
fi

# Step 7: Recommendations
echo -e "\n${BLUE}💡 Recommendations:${NC}"

if [ "$working_count" -eq 0 ]; then
    echo -e "${RED}❌ No working voices found${NC}"
    echo "  1. Check Piper TTS installation: piper --version"
    echo "  2. Verify voice file integrity"
    echo "  3. Try manual test: echo 'test' | piper --model [voice_file] --output_file test.wav"
elif [ "$working_count" -lt 3 ]; then
    echo -e "${YELLOW}⚠️  Limited working voices ($working_count)${NC}"
    echo "  1. Consider re-downloading problematic voice models"
    echo "  2. Check file permissions in voices directory"
else
    echo -e "${GREEN}✅ Good voice setup ($working_count working voices)${NC}"
    echo "  1. Restart backend: make backend"
    echo "  2. Test interface: http://localhost:3000"
    echo "  3. Try voice preview functionality"
fi

echo -e "\n${GREEN}🎉 Voice structure fix completed!${NC}"