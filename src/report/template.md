# SonarQube Utilization Assessment
## {server_url}

# Table of Contents

* Instance Overview
* Devops Integrations
* CI Environment Overview
* Permissions
* Governance
    * Installed Plugins
    * Custom Quality Profiles
    * Portfolios
    * Applications
* Installed Plugins
* Project Metrics
* Other Information

# Instance Overview

* {server_version}
* {project_count} Projects
* {lines_of_code} lines of code
* {user_count} users
* {orphan_issues} issues that cannot be migrated

# DevOps Integrations

| DevOps Platform Binding | Type | \# Projects | Multi-branch Projects? | PR Projects? |
|:------------------------|:-----|:------------|:-----------------------|:-------------|
{devops_bindings}

# CI Environment Overview

| CI Tool | \# Projects | First Run | Most Recent Run | Total Scans |
|:--------|:------------|:----------|:----------------|:------------|
{pipelines}

# Permissions

## Permission Templates

| Template Name | Description | Project key pattern | Default For |
|:--------------|:------------|:--------------------|:------------|
{permission_templates}

# Governance

## Custom Quality Profiles

| Language | Quality Profile Name | Parent Profile | Default Profile | Template Rules   | Rules from 3rd party plugins | \# of Projects using |
|:---------|:---------------------|:---------------|:----------------|:-----------------|:-----------------------------|:---------------------|
{quality_profiles}

## Custom Quality Gates

| Quality Gate Name | \# of Projects using |
|:------------------|:---------------------|
{quality_gates}

## Portfolios

| Portfolio Name | Project selection type | Contains Nested Portfolios | \# of Projects | 
|:---------------|:-----------------------|:---------------------------|:------------|
{portfolios}

## Applications

| Application Name | \# of Projects |
|:-----------------|:---------------|
{applications}

# Installed Plugins

| Plugin Name | Description | Version | Home Page URL |
|:------------|:------------|:--------|:--------------|
{plugins}

# Project Metrics

| Project Name | Template Issues | Plugin Issues | Devops Binding |
|:-------------|:----------------|:--------------|:---------------|
{project_metrics}

# Other Information

* SAST Configured: {sast_configued}
* {safe_hotspots} Hotspots Marked Safe
* {fixed_hotspots} Hotspots Fixed
* {accepted_issues} Issues Accepted
* {false_positives} False Positives   