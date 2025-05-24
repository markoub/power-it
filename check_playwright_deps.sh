#!/bin/bash

# Script to check and install Playwright system dependencies
# This script helps resolve the common Playwright dependency issues on Linux

echo "🔍 Checking Playwright system dependencies..."

# Check if we're on a Linux system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✅ Linux system detected"
    
    # Check if apt-get is available
    if command -v apt-get >/dev/null 2>&1; then
        echo "✅ apt package manager found"
        
        # Check if we have testing directory and package.json
        if [ -f "testing/package.json" ]; then
            echo "✅ Testing directory with package.json found"
            
            echo ""
            echo "🚀 Installing Playwright system dependencies..."
            echo "This may require sudo privileges..."
            
            cd testing
            
            # Install system dependencies
            if npx playwright install-deps; then
                echo "✅ Playwright system dependencies installed successfully!"
                
                # Also reinstall browsers to ensure compatibility
                echo ""
                echo "🔄 Reinstalling Playwright browsers..."
                if npx playwright install; then
                    echo "✅ Playwright browsers reinstalled successfully!"
                    echo ""
                    echo "🎉 Setup complete! You can now run 'make setup' or 'make test-e2e'"
                else
                    echo "❌ Failed to install Playwright browsers"
                    exit 1
                fi
            else
                echo "❌ Failed to install system dependencies"
                echo ""
                echo "💡 Try running with sudo if you got permission errors:"
                echo "   sudo npx playwright install-deps"
                exit 1
            fi
        else
            echo "❌ testing/package.json not found"
            echo "💡 Please run this script from the project root directory"
            exit 1
        fi
    else
        echo "❌ apt package manager not found"
        echo "💡 This script currently supports only Debian/Ubuntu-based systems"
        echo "💡 For other Linux distributions, please install the missing libraries manually:"
        echo "   - libgtk-4.so.1, libwoff2dec.so.1.0.2, libvpx.so.9, libevent-2.1.so.7"
        echo "   - gstreamer plugins, flite libraries, webp libraries, etc."
        exit 1
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ macOS system detected - system dependencies should be handled automatically"
    echo "💡 If you're having issues, try: brew install playwright"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "✅ Windows system detected - system dependencies should be handled automatically"
else
    echo "⚠️  Unknown operating system: $OSTYPE"
    echo "💡 Please check Playwright documentation for your system"
fi 