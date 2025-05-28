#!/bin/bash

# healthchecks.sh
# Script to check the health status of SmileAdventure microservices

echo "Starting SmileAdventure Health Checks..."
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check HTTP services
check_http_service() {
  local service_name=$1
  local url=$2
  local expected_code=${3:-200}
  
  printf "%-20s %-35s " "$service_name" "$url"
  
  if command -v curl &> /dev/null; then
    response_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$url" 2>/dev/null)
    
    if [ "$response_code" == "$expected_code" ]; then
      echo -e "${GREEN}✓ OK${NC} ($response_code)"
      return 0
    else
      echo -e "${RED}✗ FAIL${NC} ($response_code)"
      return 1
    fi
  else
    echo -e "${YELLOW}⚠ SKIP${NC} (curl not available)"
    return 2
  fi
}

# Function to check Docker container health
check_docker_health() {
  local service_name=$1
  local container_name=$2
  
  printf "%-20s %-35s " "$service_name" "Container: $container_name"
  
  if command -v docker &> /dev/null; then
    if docker ps --format "table {{.Names}}" | grep -q "$container_name"; then
      status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null)
      
      case "$status" in
        "healthy")
          echo -e "${GREEN}✓ HEALTHY${NC}"
          return 0
          ;;
        "unhealthy")
          echo -e "${RED}✗ UNHEALTHY${NC}"
          return 1
          ;;
        "starting")
          echo -e "${YELLOW}⟳ STARTING${NC}"
          return 2
          ;;
        *)
          # No health check defined, check if running
          running_status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null)
          if [ "$running_status" == "running" ]; then
            echo -e "${GREEN}✓ RUNNING${NC} (no healthcheck)"
            return 0
          else
            echo -e "${RED}✗ NOT RUNNING${NC}"
            return 1
          fi
          ;;
      esac
    else
      echo -e "${RED}✗ NOT FOUND${NC}"
      return 1
    fi
  else
    echo -e "${YELLOW}⚠ SKIP${NC} (docker not available)"
    return 2
  fi
}

# Initialize counters
total_checks=0
passed_checks=0
failed_checks=0
skipped_checks=0

# Function to update counters
update_counters() {
  total_checks=$((total_checks + 1))
  case $1 in
    0) passed_checks=$((passed_checks + 1)) ;;
    1) failed_checks=$((failed_checks + 1)) ;;
    2) skipped_checks=$((skipped_checks + 1)) ;;
  esac
}

echo
echo "HTTP Service Health Checks:"
echo "--------------------------"

# API Gateway
check_http_service "API Gateway" "http://localhost:8000/status"
update_counters $?

# Auth Service
check_http_service "Auth Service" "http://localhost:8001/status"
update_counters $?

# Users Service  
check_http_service "Users Service" "http://localhost:8006/status"
update_counters $?

# Reports Service
check_http_service "Reports Service" "http://localhost:8007/status"
update_counters $?

# Web Frontend (if applicable)
check_http_service "Web Frontend" "http://localhost:3000" 200
update_counters $?

echo
echo "Docker Container Health Checks:"
echo "-------------------------------"

# PostgreSQL Database
check_docker_health "PostgreSQL DB" "smileadventure-postgres-db"
update_counters $?

# API Gateway Container
check_docker_health "API Gateway" "smileadventure-api-gateway"
update_counters $?

# Auth Service Container
check_docker_health "Auth Service" "smileadventure-auth-service"
update_counters $?

# Users Service Container
check_docker_health "Users Service" "smileadventure-users-service"
update_counters $?

# Reports Service Container
check_docker_health "Reports Service" "smileadventure-reports-service"
update_counters $?

echo
echo "========================================="
echo "Health Check Summary:"
echo "  Total checks: $total_checks"
echo -e "  ${GREEN}Passed: $passed_checks${NC}"
echo -e "  ${RED}Failed: $failed_checks${NC}"
echo -e "  ${YELLOW}Skipped: $skipped_checks${NC}"

if [ $failed_checks -eq 0 ]; then
  echo -e "\n${GREEN}🎉 All services are healthy!${NC}"
  exit 0
else
  echo -e "\n${RED}⚠️  Some services have issues. Check the logs above.${NC}"
  exit 1
fi