# Task 1: Data Collection Traceability Matrix

This matrix tracks the relationship between the database, models, serializers, and API endpoints for the data collection applications.

| DB Table | Model | Serializer(s) | ViewSet | URL Example | Tasks |
|---|---|---|---|---|---|
| `ip_rotator_apigatewayproxy` | `ApiGatewayProxy` | `ApiGatewayProxySerializer` | `ApiGatewayProxyViewSet` | `GET /api/v1/ip-rotator/proxies/<uuid>/` | `provision_proxies`, `decommission_proxies` (management commands) |
| `people_search_searchquery` | `SearchQuery` | `SearchQuerySerializer`, `SearchQueryCreateSerializer` | `PeopleSearchViewSet` | `POST /api/v1/people-search/search/` | `poll_searches` (management command) |
| `people_search_personprofile` | `PersonProfile` | `PersonProfileSerializer` | `PeopleSearchViewSet` (nested) | `GET /api/v1/people-search/search/<uuid>/results/` | N/A |
| `threat_intel_indicator` | `Indicator` | `IndicatorSerializer` | `ThreatIntelViewSet` | `GET /api/v1/threat-intel/query/domain/example.com/` | N/A |
| `threat_intel_threatreport` | `ThreatReport` | `ThreatReportSerializer` (nested) | `ThreatIntelViewSet` (nested) | (nested in Indicator response) | N/A |
| `phishing_intel_urlcheck` | `URLCheck` | `URLCheckRequestSerializer`, `URLCheckResponseSerializer` | `PhishingIntelViewSet` | `POST /api/v1/phishing-intel/check/` | N/A |
| `malware_intel_malwareindicator` | `MalwareIndicator` | `MalwareQuerySerializer`, `MalwareIndicatorSerializer` | `MalwareIntelViewSet` | `POST /api/v1/malware-intel/url/` | N/A |
| `vulnerability_intel_vulnerability` | `Vulnerability` | `VulnerabilitySerializer` | `VulnerabilityViewSet` | `GET /api/v1/vulnerabilities/CVE-2023-12345/` | N/A |
| `vulnerability_intel_vulnerabilityreference` | `VulnerabilityReference` | `VulnerabilityReferenceSerializer` (nested) | `VulnerabilityViewSet` (nested) | (nested in Vulnerability response) | N/A |
| `vulnerability_intel_vulnerabilitysourcedata` | `VulnerabilitySourceData` | `VulnerabilitySourceDataSerializer` (nested) | `VulnerabilityViewSet` (nested) | (nested in Vulnerability response) | N/A |
| `serpapi_integration_serpapisearch` | `SerpApiSearch` | `SerpApiQuerySerializer` | `SerpApiViewSet` | `POST /api/v1/serpapi/news/` | N/A |
