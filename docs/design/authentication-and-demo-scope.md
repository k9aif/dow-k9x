# Authentication and demo scope

DAS at das.k9x.ai is a **public demonstration and proof of concept**. Anyone can sign in with the demo
login and run the flow. Some access controls are therefore left open **on purpose**, so visitors can test
freely. This page records how authentication works today, what is open by design, and what a
production deployment would change.

## How it works today

| Step | What is checked | Where |
|---|---|---|
| Sign-in | Two roles. **Viewer** (demo login, shown on the sign-in page) runs jobs and views results. **Admin** (password only in the deployment's environment, never published) also starts later stages and can withdraw any job. Passwords are compared in constant time. | `api/auth.py` |
| Session token | User, role and expiry, signed with HMAC-SHA256 (`DAS_SESSION_SECRET`); expires after 12 hours. | `api/auth.py` |
| Protected actions | `require_user` (401 without a valid token): grade a package, withdraw your own job. `require_admin` (403 otherwise): advance a stage, withdraw any job, delete a withdrawn job's data, the Governance tab. | `api/app.py` |
| Submitting a job | Model reachable; shared queue of 5; at most 2 queued or running jobs per visitor. Over a limit, the submission is refused, not queued. | `api/app.py` (`_submit_job`) |
| Routing | `DasRouter` reads only the event type and gate id and chooses the topic. It does not authenticate; it trusts what reaches its Kafka topic. | `routers/das_router.py` |
| Human decisions | Each gate is decided in K9X HIL, which handles its own sign-in. The decider recorded by K9X HIL is stored with the decision. | `runtime/dow_router_process.py`, `gates/hil_gateway.py` |
| Content safety | k9x Shield (input size, prompt injection, personal data, outbound links) and Granite Guardian screen documents and agent input/output. These protect content, not identity. | `config/config.yaml` (`security`) |

## Open by design (demo)

| Decision | Why | Effect |
|---|---|---|
| Job submission (`POST /jobs/upload`, `POST /jobs/demo/{file}`) needs no server-side sign-in; the sign-in page gates it in the browser only | Free testing, including scripted tests, without account management | The queue limits are the protection: 5 in total, so the shared demo cannot be flooded |
| The per-visitor limit uses a session id sent by the browser | No user accounts to tie it to | A script can present a new session id each time; the total queue limit still holds |
| The demo login is published | Anyone can try it | The admin login is never published; stage advancement and data deletion stay admin-only |
| Zero Trust identity is off: the K9-AIF `BaseRouter.admit()` signed-identity stamp is not used, and `enable_zero_trust` is false | One shared demo identity would add nothing; the demo keeps the event path simple | Events on the Kafka topics carry no verified submitter. The topics are not exposed outside the deployment |
| HIL approver list (`DAS_HIL_APPROVERS`) unset on the public demo | Reviewers can act on gates in K9X HIL | Any decision K9X HIL records is accepted. When set, only the listed deciders are accepted |

## For a production deployment

1. **Require sign-in to submit:** add `Depends(require_user)` to both submission endpoints, and tie the
   per-visitor limit to the signed-in user, not a browser session id.
2. **Use the framework's Zero Trust edge:** call `BaseRouter.admit()` in the API with the signed-in user
   (removing any identity fields a caller could set and adding an HMAC-signed identity with
   `K9_IDENTITY_SECRET`), and set `enable_zero_trust: true`, so every router and orchestrator verifies who
   submitted the job.
3. **Use the organisation's identity provider** (OIDC; K9-AIF supports it) instead of local logins.
4. **Set `DAS_HIL_APPROVERS`** to the named decision authorities for each deployment.
5. **Set `DAS_SESSION_SECRET` and `K9_IDENTITY_SECRET`** explicitly and rotate them; keep all credentials
   in the deployment environment, never in the repository.
6. **Authenticate the message bus and storage** (Kafka, object storage, databases) with per-service
   credentials and network policy.
