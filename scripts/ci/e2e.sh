#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:5000}"

log() {
  echo "[e2e] $*"
}

json_get() {
  local payload="$1"
  local expr="$2"
  JSON_PAYLOAD="$payload" python3 -c "import json, os; data=json.loads(os.environ['JSON_PAYLOAD']); print($expr)"
}

assert_json() {
  local payload="$1"
  local code="$2"
  JSON_PAYLOAD="$payload" python3 - <<PY
import json
import os

obj = json.loads(os.environ["JSON_PAYLOAD"])
$code
PY
}

http_get() {
  local url="$1"
  curl -sS "$url"
}

http_post_json() {
  local url="$1"
  local body="$2"
  curl -sS -X POST "$url" -H 'Content-Type: application/json' -d "$body"
}

wait_for_health() {
  for _ in $(seq 1 40); do
    if body=$(http_get "$BASE_URL/health" 2>/dev/null); then
      healthy=$(json_get "$body" "data.get('can_serve_traffic')")
      if [[ "$healthy" == "True" ]]; then
        echo "$body"
        return 0
      fi
    fi
    sleep 2
  done
  log "health endpoint did not become ready in time"
  return 1
}

log "Waiting for service readiness"
health_body=$(wait_for_health)
log "Health: $health_body"

assert_json "$health_body" '
assert obj.get("can_serve_traffic") is True, obj
assert obj.get("checks", {}).get("database", {}).get("reachable") is True, obj
'

llm_configured=$(json_get "$health_body" "data.get('checks', {}).get('llm', {}).get('configured')")
if [[ "$llm_configured" == "False" ]]; then
  assert_json "$health_body" '
assert obj.get("status") == "degraded", obj
assert obj.get("checks", {}).get("llm", {}).get("configured") is False, obj
'
fi

before_analytics=$(http_get "$BASE_URL/api/analytics")
before_total=$(json_get "$before_analytics" "data.get('total_traces')")
log "total_traces before: $before_total"

chat_payload='{"message":"I was charged twice and want a refund"}'
chat_response=$(http_post_json "$BASE_URL/api/chat" "$chat_payload")
log "chat response: $chat_response"

chat_user_message=$(json_get "$chat_response" "json.dumps(data.get('user_message'))")
chat_bot_response=$(json_get "$chat_response" "json.dumps(data.get('bot_response'))")

trace_payload=$(python3 - <<PY
import json
user_msg = $chat_user_message
bot_msg = $chat_bot_response
print(json.dumps({"user_message": user_msg, "bot_response": bot_msg}))
PY
)

create_trace_response=$(http_post_json "$BASE_URL/api/traces" "$trace_payload")
log "create trace response: $create_trace_response"

trace_id=$(json_get "$create_trace_response" "data.get('id')")
trace_category=$(json_get "$create_trace_response" "data.get('category')")

after_analytics=$(http_get "$BASE_URL/api/analytics")
after_total=$(json_get "$after_analytics" "data.get('total_traces')")
log "total_traces after: $after_total"

python3 - <<PY
before_total = int("$before_total")
after_total = int("$after_total")
assert after_total == before_total + 1, {
  "before_total": before_total,
  "after_total": after_total,
}
PY

encoded_category=$(python3 - <<PY
import urllib.parse
print(urllib.parse.quote("$trace_category", safe=""))
PY
)

filtered_traces=$(http_get "$BASE_URL/api/traces?category=$encoded_category")
log "filtered traces count: $(json_get "$filtered_traces" "len(data)")"

TRACE_ID="$trace_id" TRACE_CATEGORY="$trace_category" FILTERED_TRACES="$filtered_traces" python3 - <<'PY'
import json
import os

trace_id = os.environ["TRACE_ID"]
trace_category = os.environ["TRACE_CATEGORY"]
rows = json.loads(os.environ["FILTERED_TRACES"])

assert len(rows) > 0, "Expected at least one filtered trace"
assert all(row.get("category") == trace_category for row in rows), rows
assert any(row.get("id") == trace_id for row in rows), {
    "trace_id": trace_id,
    "returned_ids": [row.get("id") for row in rows],
}
PY

log "E2E checks passed"
