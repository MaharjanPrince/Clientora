# Me_CRM Project Documentation

## Overview

**Me_CRM** is a high-performance, multi-tenant CRM built with **FastAPI** and **PostgreSQL**. It features strict data isolation, secure JWT authentication, and a dynamic sales pipeline engine.

---

## 1. Authentication & Security

The "Gatekeeper" of the system.

- **Stateful Security**: Uses **JWT (JSON Web Tokens)** for session management.
- **Password Safety**: Implements **Bcrypt** hashing via `passlib`.
- **Standardization**: Follows the **OAuth2** password flow.

> 💡 **Note:** When logging in via Postman, the email must be sent in the `username` field of the `form-data` section.
> 

## 2. Data Architecture & Relationships

The system uses a hierarchical relational model. Data ownership is the #1 priority.

| **Entity** | **Description** | **Relationship** |
| --- | --- | --- |
| **Users** | Account holders / CRM owners | One-to-Many with Contacts & Deals |
| **Contacts** | The people you sell to | Belongs to a User; One-to-Many with Deals |
| **Notes** | Timeline interactions | Belongs to a Contact |
| **Deals** | Sales opportunities | Belongs to a User & Contact |

## 3. Core Logic Features

### Data Isolation (The "Owner" Filter)

Every request is filtered by `user_id`.

```python
db.query(Deal).filter(id=deal_id, user_id=current_user.id)
```

*This ensures User A can never "guess" a URL to see User B's financial data.*

### Cascading Intelligence

We use database-level cascades to maintain a clean environment.

- **If you delete a Contact:** All associated **Notes** and **Deals** are instantly purged to prevent "Ghost Data" (Orphaned records).

## 4. API Endpoint Map

### Authentication

| **Method** | **Endpoint** | **Use Case** |
| --- | --- | --- |
| `POST` | `/auth/register` | Sign up a new user |
| `POST` | `/auth/login` | Get your Bearer Token |

### Contacts & Notes

| **Method** | **Endpoint** | **Use Case** |
| --- | --- | --- |
| `POST` | `/contacts/` | Add a new person to the CRM |
| `GET` | `/contacts/` | View your personal address book |
| `POST` | `/contacts/{id}/notes` | Add a meeting summary or call log |

### Deals & Pipeline

| **Method** | **Endpoint** | **Use Case** |
| --- | --- | --- |
| `POST` | `/deals/` | Log a new sales opportunity |
| `GET` | `/deals/pipeline` | **Dashboard View**: Returns sums, counts, and grouped deals |

## 5. Pipeline Logic (Current Progress)

The `/deals/pipeline` endpoint is our first "Intelligence" feature.

- **Aggregation**: Automatically groups deals by stage (`lead`, `proposal`, `negotiation`, `won`, `lost`).
- **Financial Logic**: Calculates a `total_value` that sums up potential revenue but **excludes** "lost" deals.
- **Consistency**: Even if a stage is empty, the API returns `count: 0` to keep the frontend charts from breaking.

## 6. AI Insight Engine

Logical workflow

- **Context Retrieval**: The system fetches all notes for a specific `contact_id`, ordered by date.
- **Security Layer**: The system verifies the `current_user` owns the contact before any data is sent to the AI.
- **Prompt Engineering**: Notes are formatted into a timeline and sent to the LLM with a strict JSON system prompt.
- **Metadata Calculation**: The backend calculates `days_since_contact` using timezone-aware UTC logic to avoid calculation errors.
- **Schema Validation**: The AI response is parsed and validated against a Pydantic `ContactContext` schema.

Implements Safeguards

- **Timezone-Awareness**: Uses `datetime.now(timezone.utc)` to ensure compatibility with PostgreSQL timestamps.
- **JSON Enforcement**: Uses `response_format={"type": "json_object"}` to prevent the AI from returning non-parsable conversational text.
- **Plurality Validation**: Strict Pydantic schemas ensure that singular fields like `next_action` match the AI output exactly.

## 7. DashBoard

| **Pillar** | **Data Source** | **Logic** |
| --- | --- | --- |
| **Pipeline Stats** | `Deals` | Real-time sum of value per stage; excludes "lost" revenue. |
| **Urgency Engine** | `Contacts` + `Notes` | Flags "stale" leads with no interaction for >30 days. |
| **Activity Feed** | `Notes` + `Deals` | A unified stream of the latest 15 CRM updates. |

Key logic

- **Follow-Up Math**: Uses `now_utc - last_note.created_at` to sort contacts by neglect.
- **Feed Merging**: Combines `Note` and `Deal` objects, calculates `days_ago`, and formats human-readable timestamps.
- **Timezone Safety**: Enforces `timezone.utc` to prevent naive-vs-aware datetime crashes.

**Response Structure:**

- `total_pipeline_value`: Total active revenue.
- `deals_by_stage`: Grouped counts/values.
- `contacts_needing_followup`: List of stale leads.
- `recent_activity`: Unified event feed.