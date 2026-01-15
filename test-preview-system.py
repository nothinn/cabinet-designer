#!/usr/bin/env python3
"""
Test script to verify the preview system is working correctly.
"""

import json
import os
import sys

def test_preview_files_exist():
    """Test that all required preview files exist."""
    required_files = [
        "preview-index.html",
        "generate-previews-json.py", 
        "previews.json",
        ".github/workflows/deploy.yml",
        ".github/workflows/preview-deploy.yml",
        ".github/workflows/update-preview-index.yml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing preview system files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All preview system files exist")
        return True

def test_previews_json_valid():
    """Test that previews.json is valid JSON."""
    try:
        with open("previews.json", "r") as f:
            data = json.load(f)
        
        # Check required fields
        if "previews" not in data:
            print("❌ previews.json missing 'previews' field")
            return False
            
        if not isinstance(data["previews"], list):
            print("❌ previews.json 'previews' field is not a list")
            return False
            
        if len(data["previews"]) == 0:
            print("❌ previews.json 'previews' list is empty")
            return False
            
        # Check preview structure
        for preview in data["previews"]:
            required_fields = ["name", "url", "type", "updated_at"]
            for field in required_fields:
                if field not in preview:
                    print(f"❌ Preview missing required field: {field}")
                    return False
        
        print(f"✅ previews.json is valid with {len(data['previews'])} previews")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ previews.json is not valid JSON: {e}")
        return False
    except FileNotFoundError:
        print("❌ previews.json file not found")
        return False

def test_workflow_files_valid():
    """Test that workflow files are valid YAML."""
    try:
        import yaml
    except ImportError:
        print("⚠️  yaml module not installed, skipping workflow validation")
        return True
    
    workflow_files = [
        ".github/workflows/deploy.yml",
        ".github/workflows/preview-deploy.yml", 
        ".github/workflows/update-preview-index.yml"
    ]
    
    for workflow_file in workflow_files:
        try:
            with open(workflow_file, "r") as f:
                yaml.safe_load(f)
            print(f"✅ {workflow_file} is valid YAML")
        except yaml.YAMLError as e:
            print(f"❌ {workflow_file} is not valid YAML: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ {workflow_file} not found")
            return False
    
    return True

def test_index_html_has_preview_links():
    """Test that index.html has preview navigation links."""
    try:
        with open("index.html", "r") as f:
            content = f.read()
        
        # Check for base tag
        if "<base href=\"/\">" not in content:
            print("❌ index.html missing base tag for subdirectory support")
            return False
        
        # Check for preview links
        if "preview-index.html" not in content:
            print("❌ index.html missing preview index link")
            return False
            
        print("✅ index.html has proper preview navigation")
        return True
        
    except FileNotFoundError:
        print("❌ index.html not found")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Cabinet Designer Preview System")
    print("=" * 50)
    
    tests = [
        ("Preview files exist", test_preview_files_exist),
        ("previews.json is valid", test_previews_json_valid),
        ("index.html has preview links", test_index_html_has_preview_links),
        ("Workflow files are valid", test_workflow_files_valid),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}...")
        if test_func():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Preview system is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())