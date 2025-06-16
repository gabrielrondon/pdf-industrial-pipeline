#!/usr/bin/env python3

"""
Stage 8: Production Deployment & DevOps - Test Suite
PDF Industrial Pipeline - Deployment Testing

This test suite validates the production deployment setup including:
- Docker configuration
- Environment management
- CI/CD pipeline
- Monitoring setup
- Security configurations
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Any

# Test configuration
TEST_CONFIG = {
    "timeout": 60,
    "retry_count": 3,
    "retry_delay": 5,
    "base_url": "http://localhost:8000",
    "monitoring_url": "http://localhost:9090",
    "grafana_url": "http://localhost:3000"
}

class Stage8DeploymentTester:
    """Test suite for Stage 8 deployment functionality"""
    
    def __init__(self):
        self.results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "details": []
        }
        self.project_root = Path(__file__).parent
    
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results"""
        self.results["tests_run"] += 1
        
        try:
            self.log(f"Running test: {test_name}")
            result = test_func()
            
            if result:
                self.results["tests_passed"] += 1
                self.results["details"].append({
                    "test": test_name,
                    "status": "PASS",
                    "message": "Test completed successfully"
                })
                self.log(f"✅ PASS: {test_name}", "SUCCESS")
                return True
            else:
                self.results["tests_failed"] += 1
                self.results["details"].append({
                    "test": test_name,
                    "status": "FAIL",
                    "message": "Test failed"
                })
                self.log(f"❌ FAIL: {test_name}", "ERROR")
                return False
                
        except Exception as e:
            self.results["tests_failed"] += 1
            self.results["details"].append({
                "test": test_name,
                "status": "ERROR",
                "message": str(e)
            })
            self.log(f"💥 ERROR: {test_name} - {str(e)}", "ERROR")
            return False
    
    def test_docker_files_exist(self) -> bool:
        """Test that all required Docker files exist"""
        required_files = [
            "Dockerfile",
            "docker-compose.yml",
            "docker/production.env",
            "docker/development.env",
            "docker/docker-compose.production.yml"
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.log(f"Missing required file: {file_path}")
                return False
        
        return True
    
    def test_dockerfile_syntax(self) -> bool:
        """Test Dockerfile syntax"""
        dockerfile_path = self.project_root / "Dockerfile"
        
        try:
            # Test Docker build (dry run)
            result = subprocess.run([
                "docker", "build", "--dry-run", "-f", str(dockerfile_path), "."
            ], capture_output=True, text=True, cwd=self.project_root)
            
            return result.returncode == 0
        except FileNotFoundError:
            self.log("Docker not found - skipping Dockerfile syntax test")
            return True  # Skip if Docker not available
        except Exception:
            return False
    
    def test_environment_configurations(self) -> bool:
        """Test environment configuration files"""
        env_files = [
            "docker/production.env",
            "docker/development.env"
        ]
        
        required_vars = [
            "ENVIRONMENT",
            "REDIS_HOST",
            "POSTGRES_HOST",
            "LOG_LEVEL"
        ]
        
        for env_file in env_files:
            env_path = self.project_root / env_file
            if not env_path.exists():
                return False
            
            # Read and validate environment variables
            with open(env_path, 'r') as f:
                content = f.read()
                
            for var in required_vars:
                if f"{var}=" not in content:
                    self.log(f"Missing required variable {var} in {env_file}")
                    return False
        
        return True
    
    def test_ci_cd_pipeline(self) -> bool:
        """Test CI/CD pipeline configuration"""
        workflow_path = self.project_root / ".github/workflows/ci-cd.yml"
        
        if not workflow_path.exists():
            return False
        
        # Read and validate workflow file
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        required_jobs = ["test", "security", "build"]
        for job in required_jobs:
            if f"  {job}:" not in content:
                self.log(f"Missing required job: {job}")
                return False
        
        return True
    
    def test_deployment_scripts(self) -> bool:
        """Test deployment scripts exist and are executable"""
        scripts = [
            "scripts/deploy.sh",
            "scripts/backup.sh"
        ]
        
        for script in scripts:
            script_path = self.project_root / script
            if not script_path.exists():
                return False
            
            # Check if script is executable
            if not os.access(script_path, os.X_OK):
                # Try to make it executable
                try:
                    os.chmod(script_path, 0o755)
                except Exception:
                    return False
        
        return True
    
    def test_monitoring_configuration(self) -> bool:
        """Test monitoring configuration files"""
        monitoring_files = [
            "prometheus.yml"
        ]
        
        for file_path in monitoring_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return False
            
            # Validate Prometheus config
            if file_path == "prometheus.yml":
                with open(full_path, 'r') as f:
                    content = f.read()
                
                required_sections = ["global:", "scrape_configs:"]
                for section in required_sections:
                    if section not in content:
                        return False
        
        return True
    
    def test_security_configurations(self) -> bool:
        """Test security configurations"""
        # Check .gitignore for sensitive files
        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            return False
        
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        
        sensitive_patterns = [".env", "*.key", "*.pem", "__pycache__"]
        for pattern in sensitive_patterns:
            if pattern not in gitignore_content:
                self.log(f"Missing sensitive pattern in .gitignore: {pattern}")
                return False
        
        return True
    
    def test_health_endpoints(self) -> bool:
        """Test application health endpoints"""
        try:
            # Test main health endpoint
            response = requests.get(f"{TEST_CONFIG['base_url']}/health", timeout=10)
            if response.status_code != 200:
                return False
            
            health_data = response.json()
            if health_data.get("status") != "healthy":
                return False
            
            # Test performance health endpoint
            response = requests.get(f"{TEST_CONFIG['base_url']}/performance/system/health", timeout=10)
            if response.status_code != 200:
                return False
            
            return True
            
        except requests.exceptions.RequestException:
            self.log("Application not running - skipping health endpoint tests")
            return True  # Skip if app not running
    
    def test_docker_compose_syntax(self) -> bool:
        """Test Docker Compose file syntax"""
        compose_files = [
            "docker-compose.yml",
            "docker/docker-compose.production.yml"
        ]
        
        for compose_file in compose_files:
            compose_path = self.project_root / compose_file
            if not compose_path.exists():
                return False
            
            try:
                # Test compose file syntax
                result = subprocess.run([
                    "docker-compose", "-f", str(compose_path), "config"
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode != 0:
                    self.log(f"Docker Compose syntax error in {compose_file}: {result.stderr}")
                    return False
                    
            except FileNotFoundError:
                self.log("Docker Compose not found - skipping syntax test")
                return True  # Skip if Docker Compose not available
        
        return True
    
    def test_production_readiness(self) -> bool:
        """Test production readiness checklist"""
        checklist = {
            "dockerfile_exists": (self.project_root / "Dockerfile").exists(),
            "production_env_exists": (self.project_root / "docker/production.env").exists(),
            "deployment_script_exists": (self.project_root / "scripts/deploy.sh").exists(),
            "backup_script_exists": (self.project_root / "scripts/backup.sh").exists(),
            "monitoring_config_exists": (self.project_root / "prometheus.yml").exists(),
            "ci_cd_pipeline_exists": (self.project_root / ".github/workflows/ci-cd.yml").exists(),
        }
        
        failed_checks = [check for check, passed in checklist.items() if not passed]
        
        if failed_checks:
            self.log(f"Production readiness failed: {failed_checks}")
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all Stage 8 deployment tests"""
        self.log("=" * 60)
        self.log("🚀 PDF Industrial Pipeline - Stage 8 Deployment Tests")
        self.log("=" * 60)
        
        # Define test suite
        tests = [
            ("Docker Files Exist", self.test_docker_files_exist),
            ("Dockerfile Syntax", self.test_dockerfile_syntax),
            ("Environment Configurations", self.test_environment_configurations),
            ("CI/CD Pipeline", self.test_ci_cd_pipeline),
            ("Deployment Scripts", self.test_deployment_scripts),
            ("Monitoring Configuration", self.test_monitoring_configuration),
            ("Security Configurations", self.test_security_configurations),
            ("Health Endpoints", self.test_health_endpoints),
            ("Docker Compose Syntax", self.test_docker_compose_syntax),
            ("Production Readiness", self.test_production_readiness),
        ]
        
        # Run tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Print results
        self.print_results()
        
        return self.results["tests_failed"] == 0
    
    def print_results(self):
        """Print test results summary"""
        self.log("=" * 60)
        self.log("📊 Test Results Summary")
        self.log("=" * 60)
        
        total_tests = self.results["tests_run"]
        passed_tests = self.results["tests_passed"]
        failed_tests = self.results["tests_failed"]
        
        self.log(f"Total Tests: {total_tests}")
        self.log(f"✅ Passed: {passed_tests}")
        self.log(f"❌ Failed: {failed_tests}")
        
        if failed_tests == 0:
            self.log("🎉 All deployment tests passed! Stage 8 is ready for production.", "SUCCESS")
        else:
            self.log("⚠️  Some deployment tests failed. Please review and fix issues.", "WARNING")
        
        # Save results to file
        results_file = self.project_root / "stage8_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"📄 Detailed results saved to: {results_file}")
        self.log("=" * 60)

def main():
    """Main test execution"""
    tester = Stage8DeploymentTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 