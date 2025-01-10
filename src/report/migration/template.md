# SonarQube Utilization Assessment

## Table of Contents

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
* Appendix

{instance_overview}
{devops_integrations}
{pipeline_overview}
## Overview
* Number of Instances: {instance_count}
* Total Projects: {project_count}
* Total Lines of Code: {lines_of_code}

## Instances
| Url | Server ID | Version | Projects | Lines of Code | Users | SAST Configured |
|:----|:----------|:--------|:---------|:--------------|:------|:----------------|
{instances}

## DevOps Integrations
| Server ID | DevOps Platform Binding  | Type | \# Projects | Multi-branch Projects? | PR Projects? |
|:----------|:-------------------------|:-----|:------------|:-----------------------|:-------------|
{devops_bindings}

## CI Environment Overview
| Server ID  | CI Tool | \# Projects | First Run | Most Recent Run | Total Scans |
|:-----------|:--------|:------------|-----------|:----------------|:------------|
{pipelines}

## Permissions
### Permission Templates
| Server ID  | Template Name | Description | Project key pattern | Default For |
|:-----------|:--------------|:------------|:--------------------|:------------|
{permission_templates}

## Governance
### Active Quality Profiles
| Server ID  | Language | Quality Profile Name | Parent Profile | Default Profile | Template Rules   | Rules from 3rd party plugins | \# of Projects using |
|:-----------|:---------|:---------------------|:---------------|:----------------|:-----------------|:-----------------------------|:---------------------|
{quality_profiles}

### Active Quality Gates
| Server ID  | Quality Gate Name | # of Projects using |
|:-----------|:------------------|:--------------------|
{quality_gates}

### Portfolios
| Server ID | Portfolio Name | Project selection type | Contains Nested Portfolios | \# of Projects | 
|:----------|:---------------|:-----------------------|:---------------------------|:---------------|
{portfolios}

### Applications
| Server ID | Application Name | \# of Projects |
|:----------|:-----------------|:---------------|
{applications}

## Installed Plugins
| Server ID | Plugin Name | Description | Version | Home Page URL |
|:----------|:------------|:------------|:--------|:--------------|
{plugins}

## Project Metrics
| Server ID | Project Name | Total Rules | Template Rules  | Plugin Rules |
|:----------|:-------------|:------------|:----------------|:-------------|
{project_metrics}

## Appendix
### Scan Frequency
| Server ID | Project Name | CI Tool | # of Scans  | First Scan | Most Recent Scan |
|:----------|:-------------|:--------|:------------|:-----------|:-----------------|
{scan_frequency}

### Unused Quality Gates
| Server ID | Quality Gate Name |
|:----------|:------------------|
{unused_quality_gates}

### Unused Quality Profiles
| Server ID | Quality Profile Name |
|:----------|:---------------------|
{unused_quality_profiles}

