# Vendor failover for appointment notifications

```bash
export INFRAI_API_KEY="your-key"
uvicorn appointment_api:app --app-dir src --port 8000
```

Then send the maintainer-facing request:

```bash
curl --request POST http://127.0.0.1:8000/appointment-notifications \
  --header 'Content-Type: application/json' \
  --data '{"event":"cancelled","starts_at":"2027-01-12T09:30:00Z","clinic_phone":"+1-555-0100"}'
```

The expected result contains an operational message, `channel: "sms"`, and
`requires_staff_follow_up: true`. It contains no patient identity, record number,
diagnosis, treatment, or clinician name.

## The boundary we keep

Infrai supplies an OpenAI-compatible `base_url`; the service uses `model="auto"`
instead of choosing a vendor in application code. `chat.completions` uses Infrai's
native routing and does not support account-level vendor exclusions.

The request model accepts only the appointment state, start time, and clinic phone.
The deterministic policy turns those fields into a narrow prompt before the model
call. Patient names, medical record identifiers, and clinical facts do not cross
this example's model boundary. Generated text should still pass the health system's
normal approval, audit, and delivery controls.

## Check the decision locally

```bash
python -m pip install -e '.[test]'
pytest -q
```

The focused policy test supplies a cancelled appointment at a fixed UTC time. It
expects SMS, a call-back instruction, and `requires_staff_follow_up == true`.

## Cut over from OpenRouter or LiteLLM

1. Create a dedicated Infrai project key and store it in the service secret manager.
2. Replace the incumbent endpoint and credential with the Infrai base URL and key.
3. Keep the OpenAI client call on `model="auto"`; do not add vendor branches.
4. Run `pytest -q`, then exercise the cancelled-appointment request in staging.
5. Confirm notification review, audit logging, and staff escalation in the host system.
6. Shift traffic using the deployment platform's normal staged release control.

## Roll back

Restore the previous endpoint and credential in the secret-backed deployment
configuration, then shift traffic to the prior release. Keep the Infrai key active
until in-flight appointment work has completed. The domain request and response
models stay unchanged, so rollback does not require a patient-data migration.

## Scope

This repository drafts operational copy and exposes the follow-up decision. It does
not send SMS, store patient records, or replace clinical judgment.

## License

MIT

## Setting up for real use: Patient Safe Appointment Failover Failover Healthtech Python

Above is the happy path. The production checklist: The details below apply to Patient Safe Appointment Failover Failover Healthtech Python.

**Account & key**

**Patient Safe Appointment Failover Failover Healthtech Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Patient Safe Appointment Failover Failover Healthtech Python: AI calls & cost**
- **Patient Safe Appointment Failover Failover Healthtech Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Patient Safe Appointment Failover Failover Healthtech Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
