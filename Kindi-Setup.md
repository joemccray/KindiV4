Context:
I'm building a OSINT B2B SaaS platform that directly competes with https://www.maltego.com/, and https://www.osint.industries/


Task 1: Data Collection
=======================

Task 1a: Proxy Rotation and Management
--------------------------------------
Context: My OSINT platform, Kindi, must perform a high volume of web requests to various third-party data sources to gather intelligence. 
To avoid being rate-limited, blocked, or throttled, a robust, integrated IP rotation system is a foundational requirement. 
This will be the backbone for all data collection modules, ensuring reliable and uninterrupted service.

Goal: To analyze the requests-ip-rotator library, extract its core proxy rotation and management logic, and natively integrate these features into a new Django app called ip_rotator within the Kindi-BE3 project. 
The goal is to build a scalable, self-contained service that provides reliable, rotating IP addresses for all outgoing API requests made by other applications within the project.

Reference Code:
https://github.com/Ge0rg3/requests-ip-rotator

Tasks:
Analyze the reference code listed above and identify the core, non-redundant, and essential features and functionality that deliver distinct value, ensuring there is no overlapping or duplicated capability between the features. 
Provide a detailed, hierarchical list of these unique, deduplicated features, along with a brief description and their primary benefit. 
Create a detailed, step-by-step technical plan for extracting each identified unique, deduplicated feature and porting it into the new Python Django app called Kindi-BE3. Call the plan Kindi-BE3-ip-rotator.md
This plan must include: database schema adjustments, API endpoints, necessary third-party libraries, and a modular architecture design that ensures future scalability and maintainability. 
Emphasize how this new app will natively integrate these features, not just wrap existing functionalities.
Create the new Django app Kindi-BE3 by adding the unique deduplicated functionality from the plan Kindi-BE3-ip-rotator.md
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, reference code, representative sample code, or TODOs in the application. 
Make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it

Task 1b: PeopleSearch
---------------------
Context: To be competitive, the Kindi platform must provide rich data on individuals and professionals for B2B intelligence, lead generation, and investigative purposes. 
Integrating a specialized People Search API is a critical step in building out this capability and offering a key feature set to corporate and security clients.

Goal: To develop a people_search app within Kindi-BE3 that seamlessly integrates with the ReachStream API. 
This module must leverage the ip_rotator service for all outgoing requests. The goal is to create secure API endpoints that allow Kindi users to perform people searches, with the results being processed and stored in the platform's database for analysis and enrichment.

Reference Code:
https://www.reachstream.com/reachapi-documentation.html

Tasks:
Create a detailed, step-by-step technical plan for allowing the new Python Django app called Kindi-BE3 to interact with the API listed above via the IP Rotating functionality from task 1a. Call the plan Kindi-BE3-people-search.md
This plan must include: database schema adjustments, API endpoints, necessary third-party libraries, and a modular architecture design that ensures future scalability and maintainability. 
Emphasize how this new app will natively integrate these features, not just wrap existing functionalities.
Ensure the new Django app Kindi-BE3 allows its users to query the People Search API by adding the functionality from the plan Kindi-BE3-people-search.md
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, reference code, representative sample code, or TODOs in the application. 
Make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it


Task 1c: Threat Intel
---------------------
Context: Kindi needs to offer robust cybersecurity and threat intelligence capabilities to its users. 
Integrating a comprehensive threat intelligence feed like ThreatMiner will allow users to investigate domains, IPs, hashes, and other indicators of compromise (IOCs), adding significant value for cybersecurity analysts and corporate security teams.

Goal: To build a dedicated threat_intel app in Kindi-BE3 that queries the ThreatMiner API, using the core ip_rotator service to ensure reliable data retrieval. 
The objective is to expose endpoints in Kindi that allow users to query ThreatMiner's data and to design a database schema to store and correlate this threat intelligence information with other data points on the platform.

Reference Code:
https://www.threatminer.org/api.php

Tasks:
Create a detailed, step-by-step technical plan for allowing the new Python Django app called Kindi-BE3 to interact with the API listed above via the IP Rotating functionality from task 1a. Call the plan Kindi-BE3-threat-intel.md
This plan must include: database schema adjustments, API endpoints, necessary third-party libraries, and a modular architecture design that ensures future scalability and maintainability. 
Emphasize how this new app will natively integrate these features, not just wrap existing functionalities.
Ensure the new Django app Kindi-BE3 allows its users to query the Threat Intel API by adding the functionality from the plan Kindi-BE3-threat-intel.md
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, reference code, representative sample code, or TODOs in the application. 
Make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it




Task 1d: Phishing:
------------------
Context: Phishing is a primary vector for cyberattacks. Providing users with up-to-date intelligence on known phishing campaigns and malicious URLs is a crucial feature for a modern OSINT platform. 
This allows corporate security teams and analysts to proactively identify and mitigate threats.

Goal: To integrate the PhishTank API into Kindi-BE3 by creating a phishing_intel app. This module will utilize the ip_rotator service for all API calls. 
The goal is to implement functionality that allows users to verify URLs against the PhishTank database, retrieve details on known phishing sites, and store relevant findings to build a historical intelligence database.

Reference Code:
https://phishtank.org/developer_info.php
https://phishtank.org/api_info.php

Tasks:
Create a detailed, step-by-step technical plan for allowing the new Python Django app called Kindi-BE3 to interact with the API listed above via the IP Rotating functionality from task 1a. Call the plan Kindi-BE3-phishing.md
This plan must include: database schema adjustments, API endpoints, necessary third-party libraries, and a modular architecture design that ensures future scalability and maintainability. 
Emphasize how this new app will natively integrate these features, not just wrap existing functionalities.
Ensure the new Django app Kindi-BE3 allows its users to query the Phishing API by adding the functionality from the plan Kindi-BE3-phishing.md
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, reference code, representative sample code, or TODOs in the application. 
Make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it




Task 1e: Malware:
-----------------
Context: To further enhance the platform's cybersecurity offerings, Kindi must provide intelligence on malware-hosting URLs and associated infrastructure. 
This helps users identify, track, and block malicious activity, protecting their networks and assets from malware infections.

Goal: To create a malware_intel app in Kindi-BE3 by integrating the URLhaus API. 
Leveraging the central ip_rotator service, the objective is to provide Kindi users with API endpoints to query for malware-associated URLs, hostnames, and IPs, and to structure the application to store and link this data with other entities within the platform.

Reference Code:
https://urlhaus.abuse.ch/api/

Tasks:
Create a detailed, step-by-step technical plan for allowing the new Python Django app called Kindi-BE3 to interact with the API listed above via the IP Rotating functionality from task 1a. Call the plan Kindi-BE3-malware.md
This plan must include: database schema adjustments, API endpoints, necessary third-party libraries, and a modular architecture design that ensures future scalability and maintainability. 
Emphasize how this new app will natively integrate these features, not just wrap existing functionalities.
Ensure the new Django app Kindi-BE3 allows its users to query the Malware API by adding the functionality from the plan Kindi-BE3-malware.md
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, reference code, representative sample code, or TODOs in the application. 
Make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it





Task 1e: Vulnerabilities
------------------------
Context: A complete security intelligence platform must provide data on software and hardware vulnerabilities. 
Integrating data from authoritative sources like the National Vulnerability Database (NVD) and Vulners gives users the ability to assess the security posture of technical assets, which is critical for risk management, penetration testing, and defensive operations.

Goal: To build a vulnerability_intel app in Kindi-BE3 by integrating with both the NVD and Vulners APIs, using the ip_rotator service for requests. 
The goal is to create a robust system that allows users to search for vulnerabilities (e.g., by CVE, product name), retrieve detailed information, and store this data in a structured way that allows for correlation with other assets tracked within the Kindi platform.

Reference Code:
https://nvd.nist.gov/developers/vulnerabilities
https://vulners.com/docs/api_reference/api_methods/

Tasks:
Create a detailed, step-by-step technical plan for allowing the new Python Django app called Kindi-BE3 to interact with the APIs listed above via the IP Rotating functionality from task 1a. Call the plan Kindi-BE3-vulnerabilities.md
This plan must include: database schema adjustments, API endpoints, necessary third-party libraries, and a modular architecture design that ensures future scalability and maintainability. 
Emphasize how this new app will natively integrate these features, not just wrap existing functionalities.
Ensure the new Django app Kindi-BE3 allows its users to query the Vulnerabilties APIs by adding the functionality from the plan Kindi-BE3-vulnerabilities.md
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, reference code, representative sample code, or TODOs in the application. 
Make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it


Task 1f. SerpAPI
Context: The application needs to be able to Scrape Google and other search engines

Goal: Ensure that SerpAPI (https://serpapi.com/integrations/python) is tightly integrated

Tasks: 

Integrate the following APIs
- https://serpapi.com/google-ai-overview-api
- https://serpapi.com/google-news-api
- https://serpapi.com/google-scholar-api
- https://serpapi.com/google-trends-api
- https://serpapi.com/google-maps-api
- https://serpapi.com/google-events-api
- https://serpapi.com/google-finance-api
- https://serpapi.com/youtube-search-api

Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, reference code, representative sample code, or TODOs in the application. 
Make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it







Task 1g: Tracability
--------------------
Context: I need to verify that all core functionality in this Django + DRF project is fully traceable
Goal: produce a production-ready, fully functional codebase with no missing links between DB schema, models, serializers, viewsets, routers, URLs, and tasks.

Tasks:
 A. Build a traceability matrix for the application (see column headers below) and pinpoint gaps.  
 B. Run manage.py check, pytest, flake8; list any failures verbatim (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).  
 C. Fix every gap/failure with PEP 8–clean, production-ready code and matching tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).  
 D. Deliver the application containing updated code, docs/traceability.md, tests/, and a CI workflow that passes locally.

Acceptance criteria:
 • Zero errors from Django checks, pytest, flake8, bandit (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).  
 • All models appear in the matrix and are reachable via REST  
 • No TODOs, placeholders, commented-out secrets, or nested legacy folders  
 • README updated with quick-start

Traceability table headers: DB Table | Model | Serializer | ViewSet | URL Example | Tasks

Make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it





Task 2: Data Model and Core API Implementation
==============================================
Overall Context: The Kindi-Lite platform requires a robust and scalable backend foundation to support the features outlined in KINDI_API_SPECIFICATION.md. 
This task involves translating the API specification into a concrete implementation using Django and the Django REST Framework (DRF). 
The data models created here will store and organize the intelligence gathered in Task 1 (PeopleSearch, Threat Intel, etc.) and serve as the backbone for all analytical tools within the platform, such as relationship mapping, timeline analysis, and geographic visualization.

Overall Goal: To design and implement the complete database schema and corresponding RESTful API endpoints for the core resources of the Kindi-Lite platform: Entities, Events, Locations, and Investigation Workspaces. 
The implementation must be production-ready, fully tested, and directly align with the provided KINDI_API_SPECIFICATION.md.

Task 2a: Entities API Implementation
------------------------------------
Context: Entities are the fundamental nodes in any investigation—representing people, organizations, locations, or digital assets. 
A flexible and well-structured Entity model is critical for correlating disparate data points gathered from OSINT sources (Task 1) and enabling powerful analytical features like network graphing and relationship analysis.

Goal: To build the complete backend functionality for the /entities API endpoints. This includes creating the Django model to store entity data, the DRF serializer for data validation and representation, and the ViewSet to handle all CRUD (Create, Read, Update, Delete) operations and custom actions as defined in KINDI_API_SPECIFICATION.md.

Reference Documentation:
KINDI_API_SPECIFICATION.md - Entities API section.

Tasks:
Create a entities Django app.
Define the Entity model in entities/models.py. It must include:
name: CharField
type: CharField with choices (person, organization, asset).
attributes: JSONField to allow for flexible, unstructured data.
coordinates: JSONField to store x/y positions for graph visualizations.
Implement the EntitySerializer in entities/serializers.py for validating and serializing Entity model instances.
Implement the EntityViewSet in entities/views.py to handle the following API actions:
List (GET /entities) with filtering by type and query.
Retrieve (GET /entities/{id}).
Create (POST /entities).
Update (PUT /entities/{id}).
Delete (DELETE /entities/{id}).
A custom action for GET /entities/{id}/related.
Configure URL routing in entities/urls.py and the project's main urls.py to map the endpoints to the EntityViewSet.
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, reference code, representative sample code, or TODOs in the application. 
Make sure that all of the code is 100% functional.
Reflect on your work, and prove that the implemented Entities API fully meets the requirements of the specification document.

Task 2b: Events API Implementation
----------------------------------
Context: Events provide the crucial temporal and contextual links between entities in an investigation. They are the backbone of the timeline analysis feature, allowing users to understand the sequence of activities, identify patterns, and build a narrative.

Goal: To implement the backend for the /events API. This involves creating the Event model with relationships to entities and locations, along with the corresponding serializer and ViewSet to manage event data and serve the investigation timeline.

Reference Documentation:
KINDI_API_SPECIFICATION.md - Events API section.

Tasks:
Create an events Django app.
Define the Event model in events/models.py with relationships to other core models:
title, description, severity, type: Appropriate CharField or TextField.
timestamp: DateTimeField.
entities: A ManyToManyField to the Entity model.
location: A ForeignKey to the Location model (to be created in Task 2c).
Implement the EventSerializer in events/serializers.py.
Implement the EventViewSet in events/views.py with full CRUD functionality and a custom action for the GET /events/timeline endpoint.
Configure URL routing for all /events endpoints.
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, reference code, representative sample code, or TODOs in the application. 
Make sure that all of the code is 100% functional.
Reflect on your work, and demonstrate that the Events API correctly provides data for both list-based and timeline-based views.


Task 2c: Locations API Implementation
-------------------------------------
Context: Geographic visualization is a core feature of the Kindi-Lite platform. 
The Location model represents physical points of interest, providing the spatial dimension for analysis and allowing users to see where events occurred and where entities are located.

Goal: To build the backend for the /locations API. This requires a Location model to store geographic coordinates and its relationships with entities and events, along with the necessary serializer and ViewSet for API interaction.

Reference Documentation:
KINDI_API_SPECIFICATION.md - Locations API section.

Tasks:
Create a locations Django app.
Define the Location model in locations/models.py. It must include:
name: CharField.
latitude, longitude: FloatField or DecimalField.
markerType: CharField with choices (primary, secondary, threat, asset).
associatedEntities: A ManyToManyField to the Entity model.
associatedEvents: A ManyToManyField to the Event model.
Implement the LocationSerializer in locations/serializers.py.
Implement the LocationViewSet in locations/views.py with full CRUD functionality and filtering by markerType and geographic bounds.
Configure URL routing for all /locations endpoints.
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, reference code, representative sample code, or TODOs in the application. 
Make sure that all of the code is 100% functional.
Reflect on your work, and prove the Locations API can effectively serve data for a map-based visualization front-end.

Task 2d: Investigation Workspaces API Implementation
---------------------------------------------------
Context: Investigation Workspaces are the central containers where analysts conduct their work. They group relevant entities, events, and locations, and save the state of the analysis (filters, selections, notes). 
This functionality is fundamental to the user experience, enabling session persistence and collaboration.

Goal: To implement the complex /workspaces API. This involves creating a Workspace model to act as a container, an Activity model to log user actions, and a comprehensive ViewSet to manage the workspace state, its contents, and its associated activities.

Reference Documentation:
KINDI_API_SPECIFICATION.md - Investigation Workspaces API section.

Tasks:
Create a workspaces Django app.
Define the Workspace and Activity models in workspaces/models.py.
Workspace Model: Must include fields for name, description, notes, priority, status, tags, and an analysisState JSONField. It needs ManyToManyField relationships to Entity, Event, and Location.
Activity Model: Must include timestamp, type, description, metadata (JSONField), and a ForeignKey to the Workspace.
Implement nested serializers as needed in workspaces/serializers.py to handle the complex structure of the workspace GET response.
Implement the WorkspaceViewSet in workspaces/views.py. This is a large task and must include:
Standard CRUD operations for workspaces (GET, POST, PUT, DELETE).
Custom actions for managing nested resources and state:
PATCH /workspaces/{id}/analysis-state
POST /workspaces/{id}/activities
POST /workspaces/{id}/entities
DELETE /workspaces/{id}/entities/{entityId}
Configure URL routing for all primary and nested workspace endpoints.
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, reference code, representative sample code, or TODOs in the application. 
Make sure that all of the code is 100% functional.
Reflect on your work, and prove that the Workspaces API provides a complete and reliable system for managing an entire investigation session.


Task 2e: Tracability
--------------------
Context: I need to verify that all core functionality in this Django + DRF project is fully traceable
Goal: produce a production-ready, fully functional codebase with no missing links between DB schema, models, serializers, viewsets, routers, URLs, and tasks.

Tasks:
 A. Build a traceability matrix for the application (see column headers below) and pinpoint gaps.  
 B. Run manage.py check, pytest, flake8; list any failures verbatim (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).  
 C. Fix every gap/failure with PEP 8–clean, production-ready code and matching tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).  
 D. Deliver the application containing updated code, docs/traceability.md, tests/, and a CI workflow that passes locally.

Acceptance criteria:
 • Zero errors from Django checks, pytest, flake8, bandit (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).  
 • All models appear in the matrix and are reachable via REST  
 • No TODOs, placeholders, commented-out secrets, or nested legacy folders  
 • README updated with quick-start

Traceability table headers: DB Table | Model | Serializer | ViewSet | URL Example | Tasks

Make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it




Task 3: Analyze the application logic
=====================================
Context: Evaluate and optimize the core business logic of the application to ensure it efficiently and effectively serves the target users.

Task 3a. Analyze the Kindi-BE3 application logic both for effectiveness and efficiency on a scale of 1 to 10 with 1 being the worst and 10 being the best specifically for my ICPs. 


References:
http://146.190.150.94/app-reference-docs/Django-Business-Logic.md
http://146.190.150.94/app-reference-docs/Django-clerk.md

Task 3b. Do all of the enhancements required to ensure that all items from task 3a score no less than a 9.5 against the entire fully functioning django application and is 100% aligned with my ICPs' needs.
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, no reference code, no representative sample code, no TODOs - make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it



Task 4: Analyze the data flow
=============================
Context: Examine and improve how data moves through the application to ensure optimal performance and integrity for your target users.

Task 4a. Analyze the Kindi-BE3 application data flow, both for effectiveness and efficiency, on a scale of 1 to 10, with one being the worst and 10 being the best, specifically for my ICPs.


References:
http://146.190.150.94/app-reference-docs/Django-Data-Flow.md
https://damianztone.medium.com/understanding-the-data-flow-for-full-stack-development-with-django-rest-and-react-3d27cf362fc4


Task 4b. Do all of the enhancements required to ensure that all items from task 4a score no less than a 9.5 against the entire fully functioning django application and is 100% aligned with my ICPs' needs.
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, no reference code, no representative sample code, no TODOs - make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it


Task 5: DRF
===========
Context: Evaluate and optimize the application's API implementation to ensure it effectively and efficiently serves your target users.

Task 5a. Analyze the Kindi-BE3 application DRF implementation on its readiness to serve my specific ICPs, both for effectiveness and efficiency on a scale of 1 to 10 with 1 being the worst and 10 being the best, specifically for my ICPs.


References:
http://146.190.150.94/app-reference-docs/Django-REST-Framework-Cheat-Sheet.md

Task 5b. Do all of the enhancements required to ensure that all items from task 5a score no less than a 9.5 against the entire fully functioning Django application that it is aligned with my ICPs' needs.
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, reference code, representative sample code, or TODOs. Make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it


Task 6: AI Agent implementation
===============================
Context:
You are enhancing a production Django application with a CrewAI-based agent system that must deliver measurable value to our ICPs (Ideal Customer Profiles). 
The system must be production-grade (no example/reference/sample code, no TODOs), fully automated, and operable via Django REST Framework (DRF) APIs.

Task 6a.  CrewAI Agent Implementation
Create no less than 10 CrewAI agents with corresponding qa agents that each validate thier corresponding primary agent.
Each agent should be configured as a specialist with a clear Role, an outcome-focused Goal, and a detailed Backstory to create a cohesive, expert persona.
Each QA agent should be configured as a specialist validator, with its Role, Goal, and Backstory focused on enforcing acceptance criteria and ensuring the quality of a primary agent's output

Reference: http://146.190.150.94/app-reference-docs/Django-CrewAI.v2.md

Make sure there is no example code, reference code, representative sample code, or TODOs. Make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it

Task 6b.  CrewAI Workflow Implementation
Each agentic workflow should be configured as a crew where collaborative agents (allow_delegation=True) work together to execute a series of Tasks, orchestrated by a defined Process (e.g., sequential or hierarchical).
Ensure that these CrewAI agents are integrated into no less than 10 workflows that are no less than 3 steps  (a step being the execution of an agent/qa agent pair) each and directly contribute to reducing my ICPs average time on task by no less than 50%

Reference: http://146.190.150.94/app-reference-docs/Django-CrewAI.v2.md

Make sure there is no example code, reference code, representative sample code, or TODOs. Make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it



Task 7: SaaS Ready
==================
Context: Prepare the application for commercial launch as a multi-tenant SaaS solution, including robust billing, trouble ticketing, and authentication.

Task 7a. Analyze the Kindi-BE3 application on its readiness to serve my specific ICPs as a SaaS solution, both for effectiveness and efficiency on a scale of 1 to 10, with one being the worst and 10 being the best, specifically for my ICPs.

References:
http://146.190.150.94/app-reference-docs/Django-SaaS.md
http://146.190.150.94/app-reference-docs/Django-clerk.md

Reflect on your work, and prove to me that you've done this task as I've described it

Task 7b. Billing
Ensure the the RobFi application fully integrates Stripe subscription billing with Clerk. 
The pricing will be a free tier, a $99 per month tier, a $199 per month tier, and a $399 per month tier.


References:
http://146.190.150.94/app-reference-docs/Django-SaaS.md

Reflect on your work, and prove to me that you've done this task as I've described it


Task 7c. Ensure that the backend and the frontend are both configured to use clerk for authentication (see reference: http://146.190.150.94/app-reference-docs/Clerk+Token+Refresh+Issue+v2.pdf)
Reflect on your work, and prove to me that you've done this task as I've described it


Task 7d. Ensure that the system natively allows for users to create freshdesk trouble tickets if they encounter issues with the application

References:
http://146.190.150.94/app-reference-docs/Django-Freshdesk.md


Task 7f. Do all of the enhancements required to ensure that all items from task 7a - 5e score no less than a 9.5.
Ensure all generated code is production-ready, fully tested with unit and integration tests (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md), self-documenting through clear variable/function names. 
Ensure adherence to PEP 8 standards. The code should pass all linting checks with zero warnings/errors (all environment variables, configurations, and installed dependancies MUST NOT conflict with the prompts/instructions/commands from Jules-Setup-v2.md).
Make sure there is no example code, no reference code, no representative sample code, no TODOs - make sure that all of the code is 100% functional.
Reflect on your work, and prove to me that you've done this task as I've described it





Task 8: Railway Deployment
==========================
Context: Configure the Django project for seamless native deployment on Railway and provide a comprehensive API specification.

Ensure the codebase Kindi-BE3 is configured to deploy to railway natively, and create a YAML OpenAPI specification file called Kindi-BE3-api-spec.yaml

References:
http://146.190.150.94/app-reference-docs/Railway-Native-Django-Deployment-Tips.md

Reflect on your work, and prove to me that you've done this task as I've described it



Task 9: Source Code Review
==========================
Context: Conduct a detailed quality assurance review of the codebase and implement necessary improvements to meet coding standards.

Task 8a. Analyze the codebase Kindi-BE3 in accordance with the reference file "Code+Review+Template.pdf" (http://146.190.150.94/app-reference-docs/Code+Review+Template.pdf). 
Perform each check from Code+Review+Template.pdf categories (Module Header, Module definitions and declarations, Function header block, Lint results, and Code Checks) against the application bundle. 

Task 8. Enhance the attached codebase Kindi-BE3 to satisfy each check from Code+Review+Template.pdf categories (Module Header, Module definitions and declarations, Function header block, Lint results, and Code Checks).

References:
http://146.190.150.94/app-reference-docs/Code-Review-Template.md

Reflect on your work, and prove to me that you've done this task as I've described it













