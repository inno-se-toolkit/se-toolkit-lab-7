# Task 2: Backend Integration

## Overview

This task implements real backend connectivity for the `/health` and `/scores` commands. The bot will communicate with the LMS API to fetch actual data instead of returning placeholder responses.

## Objectives

1. Create `services/lms_client.py` for LMS API communication
2. Create `services/health_checker.py` for backend status verification
3. Update handlers to fetch real data instead of placeholders
4. Add error handling for API failures and network issues
5. Implement caching to reduce API calls

## Implementation Plan

### Step 1: LMS Client Service

Create `services/lms_client.py` with:
- HTTP client for LMS API requests
- Authentication using `LMS_API_KEY` from config
- Methods:
  - `get_health()` - Check backend health status
  - `get_scores(lab_name)` - Fetch scores for a specific lab
  - `get_labs()` - List all available labs

### Step 2: Health Checker Service

Create `services/health_checker.py` with:
- Health status aggregation
- Response time measurement
- Service availability checks

### Step 3: Update Handlers

Modify handlers in `handlers/` directory:
- `health.py` - Use `LMSClient.get_health()` for real status
- `scores.py` - Use `LMSClient.get_scores(lab_name)` for actual scores
- `labs.py` - Use `LMSClient.get_labs()` for lab list

### Step 4: Error Handling

Implement robust error handling:
- Network timeouts
- API authentication failures
- Invalid responses
- Graceful degradation with user-friendly messages

### Step 5: Caching

Add simple in-memory caching:
- Cache health status for 30 seconds
- Cache scores for 60 seconds
- Invalidate cache on errors

## Configuration

Required environment variables in `.env.bot.secret`:
```
LMS_API_BASE_URL=http://localhost:42002
LMS_API_KEY=my-secret-api-key
```

## Testing

Test commands:
```bash
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
uv run bot.py --test "/scores lab-04"
```

## Acceptance Criteria

- [ ] `/health` returns real backend status from LMS API
- [ ] `/scores <lab>` returns actual scores for the specified lab
- [ ] `/labs` returns list of available labs from backend
- [ ] All handlers handle API errors gracefully
- [ ] Caching reduces API calls for repeated requests
- [ ] All tests pass in both test mode and Telegram mode
