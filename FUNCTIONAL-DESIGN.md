# Echo AI — Functional Product Design

**Status:** Product baseline  
**Prepared:** 2026-11-11  
**Design basis:** Current product documentation and the user's Echo feature history.  
**Audience:** Product owner, designers, implementers, and testers.

## 1. Product intent

Echo is a desktop-first AI assistant that brings conversation, voice, personal
productivity, and carefully gated computer automation into one interface. It
should help a person get work done without hiding when it is using AI, touching
local data, operating a device, or communicating with an external service.

The primary product experience is a local web interface on the computer running
Echo. The user can speak or type naturally, then use focused workspaces for
camera controls, system care, web automation, research, and personal planning.
Capabilities that can affect privacy, the operating system, a microphone, a
purchase, or another person's data require a clear user action and an observable
status.

### Product principles

1. **User-directed:** background monitoring and consequential actions are off
   until the user explicitly enables them.
2. **Understandable:** Echo reports what it recognized, what it did, and when it
   could not determine an outcome.
3. **Fail safe:** uncertain recognition, missing permissions, lock state,
   incomplete data, or network errors must not be reported as success.
4. **Local by default for device features:** camera, system, and device
   monitoring do not send their raw data to an AI service.
5. **Explicit authority:** a user grants the permission needed for each
   consequential workflow; permission for one feature does not imply permission
   for another.
6. **Reversible where possible:** users can stop, pause, disarm, undo a
   configuration, or restore a saved system setting. Irreversible actions are
   separately confirmed and their outcome is made clear.

## 2. Scope baseline

- **Discovery method:** reviewed the current README feature descriptions and
  recent product conversation; no project constitution, clarification
  document, architecture summary, or knowledge graph was present.
- **Functional domains identified:** 9.
- **Domains in scope:** all 9, as the current Echo product baseline:
  assistant and device commands; voice and wake; dashboard and settings;
  workspace and planning; presence and camera assistance; system care; web
  automation and website scanning; personal exposure checks; business
  knowledge and tenant administration.
- **Assumption:** this document describes the existing product direction and
  documented behavior. It is not a request to enable every feature by default
  or to expand the system's permissions.

## 3. Users and access modes

### User types

- **Personal user:** uses Echo on their own computer and manages their own
  settings, notes, devices, and automation.
- **Demo visitor:** uses a deliberately restricted demonstration of Echo.
- **Enterprise platform administrator:** creates and manages enterprise
  tenants and their initial administrators.
- **Enterprise administrator:** manages users and approved documents within
  their own tenant.
- **Enterprise member:** asks questions of their tenant's approved knowledge
  base and provides feedback.

### Operating modes

| Mode | Intended use | Functional boundary |
|---|---|---|
| Personal | User's own trusted computer | Local features are available when the user explicitly enables them. It is not an authenticated multi-user service. |
| Demo | Guided demonstration | Requires configured access; computer-control and monitoring features are disabled. Demo knowledge is not confidential or tenant-isolated. |
| Enterprise | Local multi-tenant trial | Account and tenant boundaries apply. Tenant members access only approved tenant documents and their own permitted functions. Device-control features remain unavailable. |

The interface must show the current mode and must not imply that demo or
enterprise users have personal-device authority.

## 4. Information architecture

1. **Dashboard:** entry point, feature cards, status, and action filtering.
2. **Assistant:** text and voice conversation, command results, and explicit
   confirmations.
3. **Workspace:** speech notes, reading list, translation, and summarization.
4. **Planning and memory:** tasks, timers, reminders, agenda, and user-directed
   memory management.
5. **Presence & Security:** opt-in away detection and Windows screen locking.
6. **Posture & Gestures:** camera consent, calibration, hand scan, practice,
   action arming, live recognition, and stop controls.
7. **System Care:** local network observations, event/log analysis, and
   confirmed hardware-profile actions.
8. **Web Automation:** stock watchers, browser workflows, selector health, and
   activity history.
9. **Data Leak Check:** authorized personal identifiers, results, and
   rescan settings.
10. **Website Scanner:** website inspection and scan results.
11. **Settings:** language, voice, AI provider, profile, and feature preferences.
12. **Enterprise knowledge and administration:** source-grounded questions,
   document management, user management, and tenant-scoped activity.

Each feature page should include a concise explanation, prerequisites,
permission/consent controls, current status, primary action, stop or recovery
action, and a user-readable outcome.

## 5. Primary user journeys

### Journey A — Ask Echo for help (Priority: P1)

The user opens the dashboard, types or speaks a request, reviews Echo's answer
or proposed action, and sees the result. For consequential local actions, the
user reviews a clear confirmation before execution.

**Independent test:** complete one information question and one permitted local
command from the assistant interface.

**Acceptance scenarios:**

1. **Given** a configured AI provider, **when** the user asks a question,
   **then** Echo displays a response and identifies unavailable or failed
   services instead of inventing a successful result.
2. **Given** a command that changes or deletes local data, **when** the user
   submits it, **then** Echo presents the target and asks for confirmation
   before performing the change.
3. **Given** no configured AI provider, **when** the user requests an
   AI-dependent task, **then** Echo explains the missing setup and does not
   present a fabricated answer.

### Journey B — Capture, organize, and revisit work (Priority: P1)

The user creates a transcript-based note, saves an article for later, translates
or summarizes permitted content, and uses tasks, timers, or reminders to
organize follow-up work.

**Independent test:** create a note, add and find a reading-list entry, and set
a reminder.

**Acceptance scenarios:**

1. **Given** supported text or a supported document, **when** the user requests
   translation or a summary, **then** Echo presents editable output and
   identifies material it could not read.
2. **Given** a public article URL, **when** the user saves it, **then** Echo
   stores its URL and readable metadata and allows the user to find, mark, or
   remove it.
3. **Given** a timer or reminder request, **when** the user saves it,
   **then** Echo shows its scheduled state and later surfaces the notification.

### Journey C — Enable safe camera assistance (Priority: P1)

The user grants camera consent, starts the assistant, calibrates posture if
wanted, and performs a one-hand gesture scan. Recognition is practice-only
until the user explicitly arms actions. The user can disarm or stop at any time.

**Independent test:** with synthetic camera landmarks, scan, arm, recognize,
disarm, and stop without operating a physical device.

**Acceptance scenarios:**

1. **Given** the user has not consented or has not completed a scan, **when**
   the camera page opens, **then** computer actions remain off.
2. **Given** an armed session and a clear pinch, **when** the user holds the
   pinch briefly and changes fingertip spacing, **then** Echo adjusts system
   volume in small steps and reports the action.
3. **Given** ambiguous or lost hand tracking, **when** an action might
   otherwise be triggered, **then** Echo does nothing and does not catch up
   missed volume changes later.
4. **Given** the user disarms, stops, or the desktop is locked, **when** a
   gesture is seen, **then** it causes no computer action.

### Journey D — Protect a workstation when away (Priority: P2)

The user selects a camera and delay, grants permission, and explicitly starts
presence detection. Echo locks Windows after no face is detected for the
configured interval and may provide a return notification. The user unlocks
through Windows, not through Echo.

**Independent test:** simulate absent/present observations and verify locking,
return notification, stop, and camera-error behavior.

**Acceptance scenarios:**

1. **Given** active detection and no face for the configured interval,
   **when** the interval expires, **then** Echo requests Windows screen lock.
2. **Given** the user returns and remains visible, **when** return detection
   completes, **then** Echo may notify them but does not unlock Windows.
3. **Given** camera or lock failure, **when** the failure occurs, **then**
   Echo reports it and stops detection rather than claiming protection is
   active.

### Journey E — Review local system signals (Priority: P2)

The user selects local LAN and/or supported system-log checks, configures
intervals, grants permission, and starts monitoring. The user reviews unknown
devices or event summaries and decides what to trust or investigate. Echo
does not block devices or raise its own privileges.

**Independent test:** feed known and unknown synthetic devices/events and
verify that only the configured checks run and notifications avoid exposing
private detail in unrelated dashboard surfaces.

### Journey F — Monitor a product or perform an authorized transaction (Priority: P2)

The user configures a product watcher, chooses notification, cart, manual
checkout, or an explicitly authorized order/reservation workflow, and reviews
the activity. Any binding transaction requires a separate, one-time
confirmation with product, quantity, total budget, and currency. Uncertain
submission outcomes are treated as unknown, not as success or as permission to
retry.

**Independent test:** simulate in-stock/out-of-stock transitions, price
changes, selector failures, and final confirmation outcomes without submitting
a real transaction.

### Journey G — Check the user's own public exposure (Priority: P2)

The user identifies an email, username, or domain as theirs, selects a check,
and reviews results and limitations. Scheduled checks are opt-in. Echo does not
claim that a username match proves identity or compromise.

**Independent test:** verify ownership confirmation, result-source labels,
scheduled opt-in, and secret clearing behavior using a mock provider.

### Journey H — Answer from approved business knowledge (Priority: P3)

An enterprise member asks a question, Echo retrieves approved tenant
documents, and the answer includes source references. An administrator manages
only that tenant's users and documents; a platform administrator manages tenant
setup.

**Independent test:** verify an answer cites its source and that a user from one
tenant cannot view another tenant's documents or administrative activity.

### Journey I — Record and transcribe an online meeting (Priority: P2)

The user confirms that all participants know about the recording, starts a
recording (speaker output plus optional microphone), sees a live indicator and
timer, stops it after the meeting, and transcribes it locally into a
timestamped text and subtitle file, optionally labeled "You" / "Others".

**Independent test:** verify recording cannot start without confirmation, both
tracks share one timeline after silences, transcription works without network
access, and deleting a meeting removes its audio and transcript.

### Journey J — Get meeting minutes and record calls automatically (Priority: P2)

After transcription, the user picks a locally installed language model and gets
a short summary, the decisions and a "who does what" list. Optionally the user
enables automatic recording after confirming they will announce it at the start
of every call; Echo then starts when a supported meeting app uses the
microphone and stops, transcribes and summarizes after the call ends.

**Independent test:** verify no transcript content is sent to a non-local or
cloud model, invented timestamps are dropped, automatic mode cannot be enabled
without the announcement confirmation, a short microphone drop-out does not end
the recording, and a manually started recording is never stopped automatically.

## 6. Functional requirements

### Assistant and interaction

- **REQ-001:** Echo MUST accept text input and, when configured and permitted,
  voice input; it MUST clearly distinguish a completed action from a proposed
  or failed action.
- **REQ-002:** Echo MUST route supported local commands through a bounded,
  user-visible command flow and MUST request confirmation before destructive
  file changes, submission, or other consequential actions.
- **REQ-003:** Echo MUST expose dashboard navigation, current feature status,
  and search/filtering without starting a camera, monitor, or transaction when
  the user merely opens a page.
- **REQ-004:** Echo MUST support configurable speech input/output and report
  when a requested speech or AI service is unavailable. Wake listening MUST be
  separately startable and MUST NOT silently authorize computer-control
  actions.

### Workspace and planning

- **REQ-005:** Echo MUST allow the user to create and manage notes, reading-list
  entries, tasks, timers, and reminders, and to search or retrieve those items
  through the relevant interface.
- **REQ-006:** Echo MUST allow supported text, documents, and public URLs to be
  summarized or translated, communicate format/size/reading limitations, and
  leave generated content reviewable by the user.
- **REQ-007:** Echo MUST allow the user to inspect, add, recall, and clear
  persistent personal memory; memory MUST NOT be implied when a fact has not
  been saved.

### Presence and camera assistance

- **REQ-008:** Echo MUST obtain explicit permission and show a distinct running
  status before capturing camera frames for presence, posture, or gestures.
- **REQ-009:** Presence detection MUST lock the operating-system session only
  after its configured absence condition; return detection MUST only notify
  and MUST NOT authenticate or unlock the user.
- **REQ-010:** Posture assistance MUST let the user calibrate a comfortable
  baseline, configure a reminder delay, and stop reminders; its messages MUST
  not present webcam posture estimates as medical advice.
- **REQ-011:** Gesture actions MUST remain disarmed until the user completes a
  fresh, explicit hand scan for the current detection session and chooses to
  enable actions.
- **REQ-012:** With extra gestures enabled, a held pinch with three other
  fingers extended MUST provide bounded incremental system-volume control;
  greater normalized fingertip spacing raises volume and smaller spacing lowers
  it. A stable pinch MUST NOT repeat volume changes solely because it is held.
- **REQ-013:** Gesture controls MUST preserve the distinction between an open
  hand swipe, a stationary pointing gesture for play/pause, pinch volume,
  single-hand gestures, and two-hand gestures. Unclear, overlapping, or lost
  tracking MUST cause no action.
- **REQ-014:** Gesture actions MUST be disabled in practice mode, after
  disarming, on lock/unavailable desktop, and after an action error until the
  user explicitly reactivates them. A microphone mute MUST NOT silently unmute.

### System care

- **REQ-015:** LAN and system-log monitoring MUST be individually configurable,
  explicitly started and stopped, and report coverage gaps, permission errors,
  and uncertain observations.
- **REQ-016:** Unknown LAN devices MUST be presented as observations for user
  review; Echo MUST NOT automatically block them or represent a device
  observation as proof of intrusion.
- **REQ-017:** Any process or hardware-profile action MUST show the affected
  targets and require confirmation. Protected processes and other users'
  sessions MUST remain out of scope, and Echo MUST provide an available
  recovery path for reversible system-setting changes.

### Meeting recording and transcription

- **REQ-025:** Meeting recording MUST require explicit confirmation that all
  participants are informed, show a distinct recording indicator, stop on user
  request or after a maximum duration, and store audio only on this PC outside
  the project folder.
- **REQ-026:** Meeting transcription MUST run locally, produce timestamped text
  and subtitle output, report progress and errors, and continue on the CPU when
  GPU libraries are unavailable.
- **REQ-027:** Meeting summaries MUST use only a verified local model, treat the
  transcript as untrusted data, list decisions and action items with owner,
  deadline and transcript time without inventing them, and cover the whole
  transcript without silently omitting parts.
- **REQ-028:** Automatic call recording MUST be off by default, require the
  user's confirmation that participants will be informed, announce each
  automatic start to the user, only stop recordings it started itself, and be
  switchable off at any time.

### Web automation, scanning, and exposure checks

- **REQ-018:** Product watchers MUST allow the user to test without action,
  pause, resume, edit, or remove a watcher; ordinary cart and manual-checkout
  modes MUST NOT submit a final order or reservation.
- **REQ-019:** An order or reservation MUST require distinct workflow and
  one-time transaction authorization, a configured total budget, exact
  transaction checks, and a visible confirmation outcome. Missing or changed
  product, quantity, price, destination, or success evidence MUST block or
  leave the outcome explicitly unknown. Echo MUST NOT automatically retry an
  uncertain submission.
- **REQ-020:** Automatic selector repair MUST be limited to non-transactional
  elements with a sufficiently clear match. Final payment, order, and
  reservation controls MUST require explicit user-configured selectors and
  renewed authorization when they change.
- **REQ-021:** Website scans and personal-exposure checks MUST show their
  scope, data sources, limitations, and failures. Exposure checks MUST require
  the user to confirm they own or may check the supplied identifiers.

### Business access and privacy

- **REQ-022:** Business-knowledge answers MUST cite the approved source
  documents used; lack of a relevant source MUST be reported rather than
  replaced with an unsupported answer.
- **REQ-023:** Enterprise users, documents, and activity MUST be isolated by
  tenant and role. Demo mode MUST be clearly labeled and MUST disable
  personal-device control.
- **REQ-024:** Echo MUST explain which data stays local and which content is
  sent to an external AI or service before use where that distinction affects
  user privacy. It MUST provide stop controls for continuous monitoring and
  avoid success-shaped fallbacks when status is unknown.

## 7. Edge cases and recovery

- Camera permission is denied, the camera is occupied, or another feature is
  using the same camera: show the conflict and do not claim detection is active.
- The computer is locked, asleep, or unavailable: suppress gesture actions and
  require explicit reactivation when the policy requires it.
- Gesture recognition is interrupted or hands overlap: reset the gesture's
  movement baseline; do not perform a delayed action.
- A selected microphone disappears: require the user to select another device;
  do not silently substitute one.
- A log source is unreadable or a network device cannot be probed: disclose
  the missing coverage and do not infer "clean" or "safe."
- A process has changed identity between preview and execution: refuse to
  terminate it and require a new preview.
- A product page changes, price exceeds budget, a CAPTCHA appears, or the
  checkout result cannot be confirmed: stop, report the reason/unknown state,
  and never retry a transaction automatically.
- An external provider is unavailable or rate-limits a request: show the
  provider error and preserve the user's ability to retry manually where safe.
- A user crosses demo/enterprise/personal boundaries: retain each mode's
  access restrictions and do not expose another mode's data or controls.

## 8. Key entities

- **User and access mode:** person, role, tenant, and current operating mode.
- **Conversation and command:** user request, assistant response, proposed
  action, confirmation, and outcome.
- **Preference and permission:** user-selected settings, consent, and feature
  enablement state.
- **Workspace item:** note, reading-list entry, task, timer, reminder, or
  saved memory.
- **Monitoring session:** feature, target device/source, start/stop state,
  intervals, consent, and latest status.
- **Gesture scan and action:** current-session scan, practice/armed state,
  recognized gesture, action, and result.
- **System observation and policy:** device/log event, trust decision,
  confirmed resource policy, preview, and restoration information.
- **Web watcher and transaction attempt:** target, monitoring policy, action
  class, budget, authorization, attempt state, and confirmation evidence.
- **Exposure check:** user-authorized identifier, provider, result, and
  previous check state.
- **Knowledge source and answer:** tenant-scoped approved document, retrieved
  evidence, answer, and feedback.

## 9. Non-functional expectations

- The interface MUST work on a desktop browser at common desktop and mobile
  viewport widths without hiding primary stop, consent, or status controls.
- Every persistent monitor MUST have an explicit running/stopped state and a
  reachable stop action. Restarting Echo MUST NOT silently restart sensitive
  monitoring or transaction authorization.
- Status, error, and action feedback MUST be understandable in the selected
  language and MUST distinguish "off," "running," "paused," "unknown," and
  "failed."
- Camera and local system data MUST remain local unless the user initiates a
  specifically explained external service request. Secrets MUST NOT be exposed
  in the browser or written into unprotected project files.
- The design MUST support keyboard and screen-reader access to primary
  actions, labels, consent, progress, status, and error messages.

## 10. Success criteria

- **SC-001:** A first-time user can find the assistant, submit a basic request,
  and understand its result without assistance in under 3 minutes.
- **SC-002:** In usability testing, at least 90% of participants can tell
  whether camera monitoring is off, running, or uncertain before leaving the
  camera page.
- **SC-003:** In a controlled set of ambiguous, interrupted, overlapping, and
  disarmed gesture cases, zero computer actions are executed.
- **SC-004:** At least 90% of test users can explain how to disarm/stop camera
  actions and how to resume them after a lock or interruption.
- **SC-005:** Every transaction test with a mismatched product, quantity,
  budget, currency, final control, or missing confirmation is blocked or
  reported as unknown; none is reported as confirmed.
- **SC-006:** Every enterprise access-control test prevents cross-tenant
  document and activity access.
- **SC-007:** For each monitoring page, at least 90% of test users can locate
  its stop control and identify whether it continues after the page is closed.

## 11. Assumptions and boundaries

- This design treats Echo as a Windows-first desktop product with a local web
  interface; selected workspace and document functions may also run on other
  supported operating systems.
- Echo does not unlock Windows with face recognition. Windows Hello or a
  normal Windows credential handles authentication.
- A detected LAN device or log pattern is a signal for the user to review, not
  proof of an attack or an automatic enforcement decision.
- Camera gestures control the operating-system media/volume interfaces; they
  do not establish an authenticated Spotify account or guarantee that Spotify
  is the active media session.
- Safe product monitoring, cart actions, and final transactions are separate
  user-selected levels of authority. A watcher is not permission to purchase.
- This document is a functional baseline, not a claim of security
  certification, medical accuracy, guaranteed detection, or guaranteed
  compatibility with every external site or device.

## 12. Out of scope

- Unlocking the computer by ordinary webcam face recognition.
- Automatically blocking unknown LAN devices or declaring an intrusion based
  only on a device/log observation.
- Bypassing CAPTCHAs, bot protections, authentication, payment authorization,
  or website access controls.
- Unbounded autonomous purchases, retries after uncertain submission, or
  purchases without a separate, explicit transaction authorization.
- Clinical posture assessment or biometric identity profiling.
- Direct fan-speed control on hardware that does not expose a supported
  control; system cooling policy is not a guaranteed RPM setting.
- Treating AI output as authoritative without user review or source evidence.
