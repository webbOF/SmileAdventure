#!/usr/bin/env python3
"""
🎮 GAME SERVICE - COMPREHENSIVE ASSESSMENT
Evaluates current implementation status and identifies gaps
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

# Add the Game service path
game_path = Path(__file__).parent / "src"
sys.path.insert(0, str(game_path))

BASE_URL = "http://localhost:8005"
SERVICE_DIR = Path(__file__).parent

def analyze_file_implementation(file_path):
    """Analyze implementation status of a file"""
    if not file_path.exists():
        return {"status": "MISSING", "content": "", "lines": 0, "implementation": 0}
    
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Count non-empty, non-comment lines
        code_lines = 0
        comment_lines = 0
        empty_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                empty_lines += 1
            elif stripped.startswith('#'):
                comment_lines += 1
            else:
                code_lines += 1
        
        if total_lines == 0:
            implementation = 0
        elif code_lines == 0:
            implementation = 0  # Only comments or empty
        else:
            implementation = min(100, (code_lines / max(1, total_lines - empty_lines)) * 100)
        
        status = "EMPTY" if code_lines == 0 else "PARTIAL" if implementation < 80 else "COMPLETE"
        
        return {
            "status": status,
            "content": content,
            "lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "empty_lines": empty_lines,
            "implementation": round(implementation, 1)
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "implementation": 0}

def test_service_connectivity():
    """Test if service is running and accessible"""
    print("🔍 Testing Service Connectivity...")
    
    tests = [
        {"name": "Status Endpoint", "url": f"{BASE_URL}/status", "method": "GET"},
        {"name": "Root Endpoint", "url": f"{BASE_URL}/", "method": "GET"},
        {"name": "API v1 Root", "url": f"{BASE_URL}/api/v1/", "method": "GET"},
        {"name": "Health Check", "url": f"{BASE_URL}/health", "method": "GET"}
    ]
    
    results = []
    for test in tests:
        try:
            response = requests.request(test["method"], test["url"], timeout=5)
            results.append({
                "test": test["name"],
                "status": "✅ PASS",
                "http_code": response.status_code,
                "response": response.text[:200] if response.text else "No content"
            })
        except requests.exceptions.ConnectionError:
            results.append({
                "test": test["name"],
                "status": "❌ CONNECTION_ERROR",
                "http_code": "N/A",
                "response": "Service not running"
            })
        except Exception as e:
            results.append({
                "test": test["name"],
                "status": "💥 ERROR",
                "http_code": "N/A",
                "response": str(e)
            })
    
    return results

def analyze_models():
    """Analyze the game models implementation"""
    print("📊 Analyzing Models Implementation...")
    
    model_file = SERVICE_DIR / "src" / "models" / "game_model.py"
    analysis = analyze_file_implementation(model_file)
    
    if analysis["status"] != "MISSING":
        content = analysis["content"]
        
        # Check for key model definitions
        models_defined = {
            "SensoryProfile": "class SensoryProfile(Base):" in content,
            "LearningModule": "class LearningModule(Base):" in content,
            "GameSession": "class GameSession(Base):" in content,
            "ProgressMetric": "class ProgressMetric(Base):" in content,
            "ContentItem": "class ContentItem(Base):" in content
        }
        
        # Check for enums
        enums_defined = {
            "EmotionalState": "class EmotionalState(str, Enum):" in content,
            "DifficultyLevel": "class DifficultyLevel(str, Enum):" in content,
            "ModuleType": "class ModuleType(str, Enum):" in content,
            "ASDSupportLevel": "class ASDSupportLevel(int, Enum):" in content
        }
        
        # Check for Pydantic schemas
        schemas_defined = {
            "SensoryProfileCreate": "class SensoryProfileCreate" in content,
            "GameSessionCreate": "class GameSessionCreate" in content,
            "LearningModuleCreate": "class LearningModuleCreate" in content
        }
        
        analysis["models"] = models_defined
        analysis["enums"] = enums_defined
        analysis["schemas"] = schemas_defined
        analysis["models_count"] = sum(models_defined.values())
        analysis["enums_count"] = sum(enums_defined.values())
        analysis["schemas_count"] = sum(schemas_defined.values())
    
    return analysis

def analyze_core_files():
    """Analyze core implementation files"""
    print("🔧 Analyzing Core Implementation Files...")
    
    files_to_check = {
        "main.py": SERVICE_DIR / "src" / "main.py",
        "game_service.py": SERVICE_DIR / "src" / "services" / "game_service.py",
        "game_controller.py": SERVICE_DIR / "src" / "controllers" / "game_controller.py",
        "game_routes.py": SERVICE_DIR / "src" / "routes" / "game_routes.py",
        "session.py": SERVICE_DIR / "src" / "db" / "session.py"
    }
    
    results = {}
    for name, path in files_to_check.items():
        results[name] = analyze_file_implementation(path)
    
    return results

def test_database_setup():
    """Test database configuration and setup"""
    print("🗄️ Testing Database Setup...")
    
    try:
        # Test PostgreSQL database connection
        import os
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/smileadventure_game")
        
        # Try to import database session
        sys.path.insert(0, str(SERVICE_DIR / "src"))
        from db.session import Base, engine
        from models.game_model import SensoryProfile

        # Test database connection and try to create tables
        Base.metadata.create_all(bind=engine)
        
        return {
            "status": "✅ SUCCESS",
            "database_url": database_url,
            "connection_type": "PostgreSQL",
            "tables_created": True,
            "models_imported": True
        }
    except Exception as e:
        return {
            "status": "❌ ERROR",
            "error": str(e),
            "connection_type": "PostgreSQL",
            "tables_created": False,
            "models_imported": False
        }

def estimate_asd_features():
    """Estimate ASD-specific feature implementation"""
    print("🧩 Analyzing ASD-Specific Features...")
    
    model_analysis = analyze_models()
    
    asd_features = {
        "sensory_profile_management": {
            "implemented": model_analysis.get("models", {}).get("SensoryProfile", False),
            "priority": "CRITICAL",
            "description": "Sensory sensitivity and preference tracking"
        },
        "adaptive_learning": {
            "implemented": False,  # Need to check service layer
            "priority": "HIGH",
            "description": "Dynamic difficulty adjustment based on ASD needs"
        },
        "emotional_state_tracking": {
            "implemented": "EmotionalState" in str(model_analysis.get("content", "")),
            "priority": "HIGH",
            "description": "Real-time emotional state monitoring"
        },
        "social_interaction_metrics": {
            "implemented": "robot_interaction_quality" in str(model_analysis.get("content", "")),
            "priority": "MEDIUM",
            "description": "Tracking interaction with Pepper robot"
        },
        "sensory_overload_prevention": {
            "implemented": "sensory_overload_incidents" in str(model_analysis.get("content", "")),
            "priority": "CRITICAL",
            "description": "Preventing sensory overwhelm"
        }
    }
    
    return asd_features

def generate_comprehensive_report():
    """Generate the comprehensive assessment report"""
    print("📋 GAME SERVICE - COMPREHENSIVE ASSESSMENT")
    print("=" * 80)
    print(f"📅 Assessment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Service: SmileAdventure Game Microservice")
    print(f"📍 Location: {SERVICE_DIR}")
    print("=" * 80)
    
    # 1. Service Connectivity
    print("\n1. 🔗 SERVICE CONNECTIVITY TESTS")
    connectivity = test_service_connectivity()
    for result in connectivity:
        print(f"   {result['test']:<20} {result['status']:<15} HTTP: {result['http_code']}")
    
    # 2. Core Files Analysis
    print("\n2. 🔧 CORE FILES IMPLEMENTATION")
    core_files = analyze_core_files()
    total_implementation = 0
    for filename, analysis in core_files.items():
        status_icon = "✅" if analysis['implementation'] > 80 else "⚠️" if analysis['implementation'] > 0 else "❌"
        print(f"   {filename:<20} {status_icon} {analysis['status']:<10} {analysis['implementation']:>5.1f}% ({analysis.get('code_lines', 0)} lines)")
        total_implementation += analysis['implementation']
    
    avg_implementation = total_implementation / len(core_files) if core_files else 0
    
    # 3. Models Analysis
    print("\n3. 📊 DATA MODELS ANALYSIS")
    models = analyze_models()
    if models['status'] != 'MISSING':
        print(f"   Models Status:     {models['status']} ({models['implementation']:.1f}%)")
        print(f"   SQLAlchemy Models: {models.get('models_count', 0)}/5 defined")
        print(f"   Enums Defined:     {models.get('enums_count', 0)}/4 defined")
        print(f"   Pydantic Schemas:  {models.get('schemas_count', 0)}/3+ defined")
    else:
        print("   ❌ Models file missing!")
      # 4. Database Setup
    print("\n4. 🗄️ DATABASE CONFIGURATION")
    db_status = test_database_setup()
    print(f"   Status: {db_status['status']}")
    if 'error' not in db_status:
        print(f"   Database URL:      {db_status.get('database_url', 'Not set')}")
        print(f"   Connection Type:   {db_status.get('connection_type', 'Unknown')}")
        print(f"   Tables Created:    {db_status['tables_created']}")
        print(f"   Models Imported:   {db_status['models_imported']}")
    else:
        print(f"   Error: {db_status['error']}")
    
    # 5. ASD Features
    print("\n5. 🧩 ASD-SPECIFIC FEATURES")
    asd_features = estimate_asd_features()
    implemented_features = sum(1 for f in asd_features.values() if f['implemented'])
    total_features = len(asd_features)
    
    for name, feature in asd_features.items():
        status = "✅" if feature['implemented'] else "❌"
        print(f"   {name:<30} {status} {feature['priority']:<8} - {feature['description']}")
    
    print(f"\n   ASD Features: {implemented_features}/{total_features} implemented ({implemented_features/total_features*100:.1f}%)")
    
    # 6. Overall Assessment
    print("\n6. 📈 OVERALL ASSESSMENT")
    overall_score = (avg_implementation * 0.4 + 
                    models.get('implementation', 0) * 0.3 + 
                    (implemented_features/total_features) * 100 * 0.3)
    
    print(f"   Core Implementation: {avg_implementation:.1f}%")
    print(f"   Models Implementation: {models.get('implementation', 0):.1f}%")
    print(f"   ASD Features: {implemented_features/total_features*100:.1f}%")
    print(f"   📊 OVERALL SCORE: {overall_score:.1f}%")
    
    # 7. Priority Action Plan
    print("\n7. 🎯 PRIORITY ACTION PLAN")
    if overall_score < 10:
        print("   Status: 🚨 CRITICAL - Service is essentially empty")
        print("   Priority Actions:")
        print("     1. Implement basic FastAPI application structure")
        print("     2. Create database tables and basic endpoints")
        print("     3. Implement sensory profile management")
        print("     4. Add basic game session functionality")
        print("     5. Integrate with Reports service")
    elif overall_score < 30:
        print("   Status: ⚠️ EARLY DEVELOPMENT - Basic structure exists")
        print("   Priority Actions:")
        print("     1. Complete endpoint implementations")
        print("     2. Add business logic to services")
        print("     3. Implement ASD-specific features")
        print("     4. Add comprehensive testing")
    elif overall_score < 70:
        print("   Status: 🔄 IN PROGRESS - Core functionality partial")
        print("   Priority Actions:")
        print("     1. Complete missing endpoint implementations")
        print("     2. Enhance ASD-specific features")
        print("     3. Add integration testing")
        print("     4. Performance optimization")
    else:
        print("   Status: ✅ WELL DEVELOPED - Ready for testing")
    
    # 8. MVP Requirements
    print("\n8. 🏗️ MVP REQUIREMENTS (Demo-Ready)")
    mvp_requirements = [
        "✅ Basic FastAPI app with health endpoint" if avg_implementation > 20 else "❌ Basic FastAPI app with health endpoint",
        "✅ Sensory profile CRUD operations" if asd_features['sensory_profile_management']['implemented'] else "❌ Sensory profile CRUD operations",
        "❌ Game session start/end endpoints",
        "❌ Basic emotion detection integration",
        "❌ Reports service integration",
        "❌ Database with sample data"
    ]
    
    for req in mvp_requirements:
        print(f"     {req}")
    
    print(f"\n📊 FINAL ASSESSMENT: {overall_score:.1f}% Complete")
    if overall_score < 5:
        print("🎯 Estimated effort for MVP: 3-4 days")
    elif overall_score < 15:
        print("🎯 Estimated effort for MVP: 2-3 days")
    elif overall_score < 30:
        print("🎯 Estimated effort for MVP: 1-2 days")
    else:
        print("🎯 Estimated effort for MVP: < 1 day")
    
    return {
        "overall_score": overall_score,
        "core_files": core_files,
        "models": models,
        "asd_features": asd_features,
        "connectivity": connectivity,
        "db_status": db_status
    }

if __name__ == "__main__":
    try:
        report = generate_comprehensive_report()
        
        # Save detailed report
        with open(SERVICE_DIR / "assessment_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to: {SERVICE_DIR / 'assessment_report.json'}")
        
    except Exception as e:
        print(f"❌ Assessment failed: {e}")
        import traceback
        traceback.print_exc()
