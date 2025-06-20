# OODA.wiki - Map of Captured Territory Dashboard
**Version:** 0.1.0 (Initial GitHub Draft)
**Last Updated:** {{Meta_File_Last_Updated_Timestamp}} <!-- This should be the commit date -->
**Primary Focus:** Production Server (`oodawiki-test-ubuntu-s-1vcpu-1gb-intel-nyc1-01`)

This document serves as the primary, high-level dashboard for the Map of Captured Territory (MCT) for the OODA.wiki production environment. Its purpose is to provide an at-a-glance overview of the system's state, with links to detailed, timestamped source files containing raw outputs and configurations stored within this repository. This MCT is designed to be a resilient Single Point of Truth.

---

## System Identity & Access (`oodawiki-test-ubuntu-s-1vcpu-1gb-intel-nyc1-01`)

### Overall Status
*   **Site URL:** `https://www.ooda.wiki`
*   **General Status:** `Online and Stable`
*   **Data As Of:** `2025-06-15 00:32 UTC` (from MCT 1.3.11.C)
*   **Source:** *Placeholder: Future link to `Sources/System_OverallStatus_Prod_YYYYMMDD-HHMMSS.txt`*

### Core Identifiers
*   **Provider:** DigitalOcean
*   **Hostname:** `oodawiki-test-ubuntu-s-1vcpu-1gb-intel-nyc1-01`
*   **Data As Of:** `2025-06-15 00:32 UTC` (from MCT 1.3.11.C, Sec 3)
*   **Source:** *Placeholder: Future link to `Sources/System_Identifiers_Prod_YYYYMMDD-HHMMSS.txt`*

### Network
*   **External IP:** `178.128.155.201`
*   **Internal IPs:** `[REDACTED_OPSEC]`
*   **Data As Of:** `2025-06-15 00:32 UTC` (from MCT 1.3.11.C, Sec 6)
*   **Source:** *Placeholder: Future link to `Sources/Network_Details_Prod_YYYYMMDD-HHMMSS.txt`*

---

## Operating System & Hardware (`oodawiki-test-ubuntu-s-1vcpu-1gb-intel-nyc1-01`)

### OS Details
*   **OS:** Ubuntu 22.04.5 LTS (jammy)
*   **Kernel:** Linux 5.15.0-141-generic
*   **Data As Of:** `2025-06-15 00:32 UTC` (from MCT 1.3.11.C, Sec 3)
*   **Source:** *Placeholder: Future link to `Sources/System_OS_Prod_YYYYMMDD-HHMMSS.txt` (e.g., from `uname -a`, `lsb_release -a`)*

### Hardware Resources
*   **vCPUs:** 2x DO-Premium-Intel (x86_64)
*   **Memory (RAM):** 3911 MB Total
*   **Swap:** 1023 MB Total
*   **Disk Space (/):** 49G Size, 26G Used, 23G Avail
*   **Uptime & Load (Snapshot):** 6h 17m, load average: 0.72, 0.56, 0.83
*   **Data As Of:** `2025-06-15 00:32 UTC` (from MCT 1.3.11.C, Sec 4, for Uptime/Load)
*   **Source:** *Placeholder: Future link to `Sources/System_Hardware_Prod_YYYYMMDD-HHMMSS.txt` (e.g., from `lscpu`, `free -m`, `df -h`, `uptime`)*

---

## Core Services (`oodawiki-test-ubuntu-s-1vcpu-1gb-intel-nyc1-01`)

### Nginx (Web Server)
*   **Status:** `Active (running)`
*   **Version:** `nginx/1.18.0 (Ubuntu)`
*   **Key Configuration Points:** Redirects http to https, Serves from `/var/www/mediawiki`, Rate limiting enabled (zone=bots, rate=5r/s), Passes `.php` files to `unix:/run/php/php8.1-fpm.sock`, `fastcgi_read_timeout` is 90s.
*   **Data As Of:** `2025-06-15 00:32 UTC` (from MCT 1.3.11.C, Sec 5 & 7)
*   **Source:** *Placeholder: Future link to `Sources/Service_Nginx_Status_Prod_YYYYMMDD-HHMMSS.txt` & `Sources/Config_Nginx_Site_Prod_YYYYMMDD-HHMMSS.txt`*

### PHP-FPM (`php8.1-fpm`)
*   **Status:** `Active (running); Status: "Processes active: 0, idle: 3"`
*   **Version (CLI):** `PHP 8.1.2-1ubuntu2.21 (cli)`
*   **Key Configuration Points (Pool):** `pm.max_children = 8`, `request_terminate_timeout = 90`, `php_admin_value[max_execution_time] = 90`.
*   **Data As Of:** `2025-06-15 00:32 UTC` (from MCT 1.3.11.C, Sec 5 & 8)
*   **Source:** *Placeholder: Future link to `Sources/Service_PHP-FPM_Status_Prod_YYYYMMDD-HHMMSS.txt` & `Sources/Config_PHP-FPM_Pool_Prod_YYYYMMDD-HHMMSS.txt`*

### MySQL (Database)
*   **Status:** `Active (running); Status: "Server is operational"`
*   **Version:** `8.0.42-0ubuntu0.22.04.1`
*   **Key Configuration Points (MediaWiki User Grants):** The `wikiuser` is granted all privileges on the `mediawiki` database from localhost only.
*   **Data As Of:** `2025-06-15 00:32 UTC` (from MCT 1.3.11.C, Sec 5 & 10)
*   **Source:** *Placeholder: Future link to `Sources/Service_MySQL_Status_Prod_YYYYMMDD-HHMMSS.txt` & `Sources/Config_MySQL_Grants_Prod_YYYYMMDD-HHMMSS.txt`*

### Memcached
*   **Status:** `Active (running)`
*   **Data As Of:** `2025-06-15 00:32 UTC` (from MCT 1.3.11.C, Sec 5)
*   **Source:** *Placeholder: Future link to `Sources/Service_Memcached_Status_Prod_YYYYMMDD-HHMMSS.txt`*

### Fail2Ban
*   **Status:** `Active (running)`
*   **Data As Of:** `2025-06-15 00:32 UTC` (from MCT 1.3.11.C, Sec 5)
*   **Source:** *Placeholder: Future link to `Sources/Service_Fail2Ban_Status_Prod_YYYYMMDD-HHMMSS.txt`*

### Firewall (UFW)
*   **Status:** `Active`
*   **Allowed Traffic (Key Ports):** `22 (OpenSSH)`, `80/443 (Nginx Full)`, `4000`.
*   **Data As Of:** `2025-06-15 00:32 UTC` (from MCT 1.3.11.C, Sec 6)
*   **Source:** *Placeholder: Future link to `Sources/Network_Firewall_UFW_Status_Prod_YYYYMMDD-HHMMSS.txt`*

---

## Application: MediaWiki (`oodawiki-test-ubuntu-s-1vcpu-1gb-intel-nyc1-01`)

### Core Application
*   **MediaWiki Version:** `1.39.2`
*   **Data As Of:** `2025-06-15 00:32 UTC` (from MCT 1.3.11.C, Sec 9)
*   **Source:** *Placeholder: Version info usually in Special:Version or bottom of pages.*

### `LocalSettings.php` (Sanitized)
*   **Key Highlights (from MCT 1.3.11.C for brevity):** `$wgServer: https://www.ooda.wiki`, `$wgMainCacheType: CACHE_ACCEL`, `$wgEnableUploads: true`, `$wgHTTPTimeout: 20`, Scribunto extension is enabled.
*   **Full Sanitized Configuration & Data As Of:** `2025-06-20 17:51:19 UTC`
*   **Source Link:** [./Sources/Config_LocalSettings_Prod_20250620-175119.txt](./Sources/Config_LocalSettings_Prod_20250620-175119.txt)

---

## Log File Summaries (Sanitized)
*These sections will link to files containing sanitized excerpts from key logs.*

*   **Nginx Access Log:** *Placeholder: Future link to `Sources/Log_Nginx_Access_Sanitized_Prod_YYYYMMDD-HHMMSS.txt`*
*   **PHP-FPM Error Log:** *Placeholder: Future link to `Sources/Log_PHP-FPM_Error_Sanitized_Prod_YYYYMMDD-HHMMSS.txt`*
*   **System Journal (SSH Failures):** *Placeholder: Future link to `Sources/Log_SysJournal_SSH_Sanitized_Prod_YYYYMMDD-HHMMSS.txt`*

