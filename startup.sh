#!/bin/bash

# ==================================================================================
# SonarQube Migration Script
# ==================================================================================
# This script automates the process of migrating data from SonarQube Server to 
# SonarQube Cloud using the sonar-reports tool.
#
# Prerequisites:
# - Docker installed and running
# - Access to both source SonarQube Server and target SonarQube Cloud
# - Admin tokens for both instances
#
# ⚠️  SECURITY WARNING: 
# - NEVER commit real tokens or URLs to version control
# - Keep this file in .gitignore or use environment variables in production
# - Review your commits before pushing to ensure no secrets are exposed
# ==================================================================================

# User-configurable variables
# ------------------------------------------------------------------------------------------
# Source SonarQube Server information

SOURCE_URL=""                                  # URL of the source SonarQube server (REQUIRED)
SOURCE_TOKEN=""                               # Admin user token for the source SonarQube server (REQUIRED)

# Certificate information (if needed)
PEM_FILE_PATH=""                                # Path to client certificate pem file
KEY_FILE_PATH=""                                # Path to client certificate key file
CERT_PASSWORD=""                                # Password for client certificate

# Extract options
EXPORT_DIRECTORY="./sonarqube-export"           # Directory to store exported data
EXTRACT_TYPE=""                                 # Type of Extract to run (leave empty for default)
CONCURRENCY=4                                   # Maximum number of concurrent requests
TIMEOUT=60                                      # Request timeout in seconds
EXTRACT_ID=""                                   # ID of an extract to resume in case of failures

# Target SonarQube Cloud information
CLOUD_TOKEN=""                                    # Admin token for SonarQube Cloud (REQUIRED for migration)
ENTERPRISE_KEY=""                                 # Enterprise key in SonarQube Cloud (REQUIRED for migration)
CLOUD_URL="https://sonarcloud.io"                # SonarQube Cloud URL
EDITION="enterprise"                            # SonarQube Cloud Edition

# Migration options
RUN_ID=""                                       # ID of a run to resume in case of failures
TARGET_TASK=""                                  # Name of a specific migration task (leave empty for all tasks)

# Docker image
DOCKER_IMAGE="sonar-reports-fixed"

# ------------------------------------------------------------------------------------------
# Script execution starts here
# ------------------------------------------------------------------------------------------

# Function to show progress bar
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    
    printf "\rProgress: ["
    printf "%*s" $completed | tr ' ' '='
    printf "%*s" $((width - completed)) | tr ' ' '-'
    printf "] %d%% (%d/%d)" $percentage $current $total
}

# Set up export directory
EXPORT_DIRECTORY=$(realpath "${EXPORT_DIRECTORY}" 2>/dev/null || echo "${EXPORT_DIRECTORY}")

# Create export directory if it doesn't exist
mkdir -p "${EXPORT_DIRECTORY}"

# Validate required variables
if [ -z "${SOURCE_URL}" ] || [ -z "${SOURCE_TOKEN}" ]; then
  echo "❌ Error: SOURCE_URL and SOURCE_TOKEN must be set in the script."
  echo "Please edit the startup.sh file and provide:"
  echo "  - SOURCE_URL: URL of your source SonarQube server"
  echo "  - SOURCE_TOKEN: Admin user token for the source SonarQube server"
  exit 1
fi

echo "==================================================================="
echo "Starting SonarQube migration process"
echo "==================================================================="
echo "Source SonarQube Server: ${SOURCE_URL}"
echo "Export Directory: ${EXPORT_DIRECTORY}"
echo "==================================================================="

# STEP 1: Extract data from source SonarQube server
echo "STEP 1: Extracting data from source SonarQube server..."
EXTRACT_CMD="docker run -v ${EXPORT_DIRECTORY}:/app/files ${DOCKER_IMAGE} extract ${SOURCE_URL} ${SOURCE_TOKEN}"

# Add optional parameters if they're set
if [ -n "${PEM_FILE_PATH}" ]; then
    EXTRACT_CMD="${EXTRACT_CMD} --pem_file_path ${PEM_FILE_PATH}"
fi
if [ -n "${KEY_FILE_PATH}" ]; then
    EXTRACT_CMD="${EXTRACT_CMD} --key_file_path ${KEY_FILE_PATH}"
fi
if [ -n "${CERT_PASSWORD}" ]; then
    EXTRACT_CMD="${EXTRACT_CMD} --cert_password ${CERT_PASSWORD}"
fi
if [ -n "${EXTRACT_TYPE}" ]; then
    EXTRACT_CMD="${EXTRACT_CMD} --extract_type ${EXTRACT_TYPE}"
fi
if [ -n "${CONCURRENCY}" ]; then
    EXTRACT_CMD="${EXTRACT_CMD} --concurrency ${CONCURRENCY}"
fi
if [ -n "${TIMEOUT}" ]; then
    EXTRACT_CMD="${EXTRACT_CMD} --timeout ${TIMEOUT}"
fi
if [ -n "${EXTRACT_ID}" ]; then
    EXTRACT_CMD="${EXTRACT_CMD} --extract_id ${EXTRACT_ID}"
fi
if [ -n "${TARGET_TASK}" ]; then
    EXTRACT_CMD="${EXTRACT_CMD} --target_task ${TARGET_TASK}"
fi

echo "Executing: ${EXTRACT_CMD}"
echo "Note: This may take several minutes depending on the size of your SonarQube instance..."

# Start extraction with progress monitoring
${EXTRACT_CMD} &
EXTRACT_PID=$!

# Simple progress indicator
echo "Extraction in progress..."
while kill -0 $EXTRACT_PID 2>/dev/null; do
    printf "."
    sleep 2
done
wait $EXTRACT_PID
EXTRACT_EXIT_CODE=$?

echo ""
if [ $EXTRACT_EXIT_CODE -eq 0 ]; then
    echo "✅ Extraction completed successfully!"
else
    echo "❌ Extraction failed with exit code: $EXTRACT_EXIT_CODE"
    exit $EXTRACT_EXIT_CODE
fi

# STEP 2: Generate organization <> project structure
echo "STEP 2: Generating organization <> project structure..."
STRUCTURE_CMD="docker run -v ${EXPORT_DIRECTORY}:/app/files ${DOCKER_IMAGE} structure --export_directory /app/files"
echo "Executing: ${STRUCTURE_CMD}"
${STRUCTURE_CMD}

if [ $? -eq 0 ]; then
    echo "✅ Structure generation completed successfully!"
else
    echo "❌ Structure generation failed"
    exit 1
fi

# STEP 3: Generate migration report  
echo "STEP 3: Generating migration report..."
REPORT_CMD="docker run -v ${EXPORT_DIRECTORY}:/app/files ${DOCKER_IMAGE} report --export_directory /app/files"
echo "Executing: ${REPORT_CMD}"
${REPORT_CMD}

if [ $? -eq 0 ]; then
    echo "✅ Migration report generated successfully!"
    echo "📄 Report available at: ${EXPORT_DIRECTORY}/migration.md"
    echo ""
    echo "==================================================================="
    echo "REPORT GENERATION COMPLETE"
    echo "==================================================================="
    echo "You can now:"
    echo "1. Review the migration report at: ${EXPORT_DIRECTORY}/migration.md"
    echo "2. Continue with the migration process (answer 'y' below)"
    echo "3. Or stop here if you only wanted the report (answer 'n' below)"
    echo "==================================================================="
else
    echo "❌ Report generation failed"
    exit 1
fi

# Ask user if they want to continue with migration
read -p "Do you want to continue with the actual migration process? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Migration process stopped by user. Report is available at: ${EXPORT_DIRECTORY}/migration.md"
    exit 0
fi

# STEP 4: Manual step for organization configuration
echo "==================================================================="
echo "STEP 4: Manual step required"
echo "==================================================================="
echo "Please edit the organizations.csv file in ${EXPORT_DIRECTORY} to add SonarQube Cloud organization keys in the sonarcloud_org_key column."
echo "Open the file in a spreadsheet application or text editor and add the appropriate organization keys."
echo "Press Enter when done to continue..."
read -r

# STEP 5: Run migration
echo "STEP 5: Running migration to SonarQube Cloud..."

# Validate cloud migration variables
if [ -z "${CLOUD_TOKEN}" ] || [ -z "${ENTERPRISE_KEY}" ]; then
  echo "❌ Error: CLOUD_TOKEN and ENTERPRISE_KEY must be set for migration."
  echo "Please edit the startup.sh file and provide:"
  echo "  - CLOUD_TOKEN: Admin token for SonarQube Cloud"
  echo "  - ENTERPRISE_KEY: Enterprise key in SonarQube Cloud"
  exit 1
fi

MIGRATE_CMD="docker run -v ${EXPORT_DIRECTORY}:/app/files ${DOCKER_IMAGE} migrate ${CLOUD_URL} ${CLOUD_TOKEN}"

# Add optional parameters
if [ -n "${ENTERPRISE_KEY}" ]; then
    MIGRATE_CMD="${MIGRATE_CMD} --enterprise_key ${ENTERPRISE_KEY}"
fi
if [ -n "${EDITION}" ]; then
    MIGRATE_CMD="${MIGRATE_CMD} --edition ${EDITION}"
fi
if [ -n "${RUN_ID}" ]; then
    MIGRATE_CMD="${MIGRATE_CMD} --run_id ${RUN_ID}"
fi
if [ -n "${TARGET_TASK}" ]; then
    MIGRATE_CMD="${MIGRATE_CMD} --target_task ${TARGET_TASK}"
fi

echo "Executing: ${MIGRATE_CMD}"
echo "Note: This may take several minutes depending on the amount of data to migrate..."

# Start migration with progress monitoring
${MIGRATE_CMD} &
MIGRATE_PID=$!

# Simple progress indicator
echo "Migration in progress..."
while kill -0 $MIGRATE_PID 2>/dev/null; do
    printf "."
    sleep 2
done
wait $MIGRATE_PID
MIGRATE_EXIT_CODE=$?

echo ""
if [ $MIGRATE_EXIT_CODE -eq 0 ]; then
    echo "✅ Migration completed successfully!"
    echo "==================================================================="
    echo "MIGRATION COMPLETE!"
    echo "==================================================================="
    echo "Your data has been successfully migrated to SonarQube Cloud."
    echo "Please verify the migration in your SonarQube Cloud instance."
else
    echo "❌ Migration failed with exit code: $MIGRATE_EXIT_CODE"
    exit $MIGRATE_EXIT_CODE
fi
