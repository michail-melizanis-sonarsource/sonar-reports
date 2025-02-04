# SonarQube Maturity Assessment

## Table of Contents

* Summary
* Adoption
    * Instances
    * Usage
    * Languages
    * User Management
* Governance
    * Project Groupings
    * Languages
    * Profiles
    * Gates
    * Active Gates
    * Permissions
* Workflow Integration
    * Scans
    * Issues
    * Testing
    * IDE
* Automation
    * API Usage
    * Webhooks
* Reporting
    * Portfolios
    * Subscriptions

## Overview

| Category             | Positives                                                                            | Opportunities                                                        | Score |
|:---------------------|:-------------------------------------------------------------------------------------|:---------------------------------------------------------------------|:------| 
| Adoption             | High Scans per Day, High Unique Projects Scanned, High Active Users, High SSO Users, | Add new projects, add daily main branch scans to discover new issues | 3     |         
| Governance           | Lorem ipsum                                                                          | Lorem ipsum                                                          | 4     |         
| Workflow Integration | Lorem ipsum                                                                          | Lorem ipsum                                                          | 3     |         
| Automation           | Lorem ipsum                                                                          | Lorem ipsum                                                          | 2     |        
| Reporting            | Lorem ipsum                                                                          | Lorem ipsum                                                          | 4     |
| Overall              |                                                                                      |                                                                      |       |

## Adoption

### Instances

| Server ID | URL       | Edition    | Version | Lines of Code | LoC Limit | Plugins Installed |
|:----------|:----------|:-----------|:--------|:--------------|:----------|:------------------|
| Server 1  | localhost | Enterprise | 2025.1  | 20103254      | 25000000  | 2                 |

### DevOps Integrations

| Server ID | DevOps Platform Binding | Type   | # Projects | Multi-branch Projects? | PR Projects? |
|:----------|:------------------------|:-------|:-----------|:-----------------------|:-------------|
| Server 1  | Azure Devops            | ADO    | 100        | Yes                    | Yes          |
| Server 1  | GitHub                  | Github | 100        | Yes                    | Yes          |

## CI Environment Overview

| Server ID | CI Tool | # Projects | First Run  | Most Recent Run | Total Scans |
|:----------|:--------|:-----------|------------|:----------------|:------------|
| Server 1  | Jenkins | 100        | 2025-01-01 | 2025-01-30      | 300         |

### Usage

| Projects | Scans Per Day | Unique Projects Scanned <br/> (Past 30 Days) | Lines of Code | Scanned Lines of Code <br/> (Past 30 Days) |
|:---------|:--------------|:---------------------------------------------|:--------------|:-------------------------------------------|
| 1250     | 300           | 72                                           | 20103254      | 1039200                                    |

### User Management

| Total Users | Unique Users | Active Users | SSO Users | Groups | 
|:------------|:-------------|:-------------|:----------|:-------|
| 100         | 100          | 70           | 65        | 2      |

## Governance

### Detected Project Groupings

| Server ID | Permission Template | Regex Pattern | Projects | Admin Groups | Editor Groups | Viewer Groups |
|:----------|:--------------------|:--------------|:---------|:-------------|:--------------|:--------------|
| Server 1  | Template 1          | ^[A-Z]{3}$    | 10       | 2            | 3             | 5             |

### Languages

| Language | Lines of Code | % of Total LoC | # of Projects | Custom Profiles | Default Rule Count | Min Rule Count | Max Rule Count | Average Active Rule Count |
|:---------|:--------------|:---------------|:--------------|:----------------|:-------------------|:---------------|:---------------|:--------------------------|
| Java     | 10000000      | 50             | 500           | 2               | 1000               | 500            | 1500           | 1000                      |

### Profiles

| Total Profiles | Active Profiles | Custom Default Profile? | Template Rule Count |
|:---------------|:----------------|:------------------------|:--------------------|
| 10             | 5               | Yes                     | 1000                |

### Gates

| Total Gates | Active Gates | CaYC Compliant Gates | AI Code Assurance Compliant Gates |
|:------------|:-------------|:---------------------|:----------------------------------|
| 10          | 5            | 2                    | 0                                 |

### Active Quality Gates

| Server ID | Quality Gate Name | # of Projects using | Quality | Hotspots | Coverage | Duplication |
|:----------|:------------------|:--------------------|:--------|:---------|:---------|:------------|
| Server 1  | Security          | 50                  | 50      | 50       | 50       | 50          |

### Permissions

| Users with Profile Edit Permissions | Users with Gate Edit Permissions | Groups with Profile Edit Permissions | Groups with Gate Edit Permissions |
|:------------------------------------|:---------------------------------|:-------------------------------------|:----------------------------------|
| 2                                   | 0                                | 5                                    | 20                                |

## Workflow Integration

### Scans

| Projects Scanned<br/>(Past 30 Days) | Projects with PR scans<br/>(Past 30 Days) | # of Failed Scans<br/>(past 30 days) | Projects with Failed Scans in past 30 days |
|:------------------------------------|:------------------------------------------|:-------------------------------------|:-------------------------------------------|
| 72                                  | 10                                        | 5                                    | 5                                          |

### Issues

| Total Issues | Reliability Issues Added (Past 30 Days) | Vulnerabilities Added Past 30 Days | Maintainability Issues Added (Past 30 Days) | Issues Resolved (Past 30 Days) | Projects with new Issues (past 30 days) |  
|:-------------|:----------------------------------------|:-----------------------------------|:--------------------------------------------|:-------------------------------|:----------------------------------------|
| 1000         | 100                                     | 200                                | 300                                         | 500                            | 50                                      |

### Resolutions

| Fixed Vulnerabilities (90 Days) | Fixed Reliability Issues (90 Days) | Fixed Maintainability Issues (90 Days) |
|:--------------------------------|:-----------------------------------|:---------------------------------------|
| 100                             | 200                                | 300                                    |

| Fixed Vulnerabilities (All Time) | Fixed Reliability Issues (All Time) | Fixed Maintainability Issues (All Time) |
|:---------------------------------|:------------------------------------|:----------------------------------------|
| 100                              | 200                                 | 300                                     |

### Testing

| Code to Cover | Overall Coverage Percentage | New Code to Cover | New Code Coverage |
|:--------------|:----------------------------|:------------------|:------------------|
| 1000000       | 48%                         | 100000            | 70%               |

### IDE

| Connected Mode Users | Active Connected Mode Users |
|:---------------------|:----------------------------|
| 10                   | 5                           |

## Automation

### API Usage

| Created User Tokens | Active User Tokens | Users with Active Tokens | Active Admin Tokens |
|:--------------------|:-------------------|:-------------------------|:--------------------|
| 10                  | 5                  | 5                        | 2                   |

### Webhooks

| Global Webhooks | Project Webhooks | Webhook Deliveries (Past 30 Days) | Webhook Failures (Past 30 Days) |
|:----------------|:-----------------|:----------------------------------|:--------------------------------|
| 10              | 5                | 1000                              | 5                               |

## Reporting

### Portfolios

| Portfolios Created | Total Portfolio Projects |
|:-------------------|:-------------------------|
| 10                 | 100                      |

### Subscriptions

| Project Subscriptions | Portfolio Subscriptions | Users with Project Subscriptions | Users with Portfolio Subscriptions |
|:----------------------|:------------------------|:---------------------------------|:-----------------------------------|
| 100                   | 10                      | 50                               | 5                                  |

