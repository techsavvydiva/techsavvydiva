# Snobos V2 Plan: Show Logistics And Output

## Scope

V2 builds on the Stage 1 rundown and later Stage 2 slate / Stage 3 show-notes outputs described in [snobos-v1.md](snobos-v1.md). It adds show logistics and integrations. Every external publishing or notifying action requires the user's explicit approval immediately before it goes live. Scheduling a future public livestream or creating a supporter notification is a publish/notify action and must not happen automatically without that approval. No integration may auto-post to a public channel.

Every generated artifact includes the episode number and show date at the top and follows the episode naming convention. V2 show notes use `<episode> Show Notes` (for example, `383 Show Notes`) and the existing show-notes template. A copy of that template must be added to the repository before Stage 3 implementation begins.

## Episode And Schedule Rules

- The episode-number anchor is episode `383` on Wednesday, October 14, 2026, stored in the Snobos YAML configuration.
- Main-show episodes normally occur every Wednesday and increment by one regardless of producer. The user's every-other-Wednesday production rotation is anchored at episode `383` on October 14, 2026; the next user-produced episode is `385` on October 28, 2026.
- Skipped show dates configured in YAML do not consume episode numbers. The CLI may override the calculated episode number.
- Generate the rundown automatically ahead of the user's show weeks. The lead time, scheduler host, and behavior when a show is skipped or a prior run fails remain open decisions. Scheduled execution must not publish or notify.
- The livestream schedule target is Wednesdays at 6:00 PM `America/New_York`, streamed to YouTube. Daylight-saving transitions must retain the wall-clock local time.

## Integration Approval Rule

For every integration below, the system may prepare content or a preview, but the user must explicitly approve each publishing, scheduling, or notifying action before submission. Approval is per action/run, not an evergreen permission. Show the destination, episode/date, content or event details, and any visibility/audience setting before asking. If approval is absent, expired, or ambiguous, do not send the write request.

Credentials and OAuth tokens belong under `secrets/`, which must be gitignored before credentials are created. Never print, log, expose, or commit credentials or tokens. The repository currently has no `secrets/` ignore rule; adding and verifying it is a prerequisite to implementing credential storage. Tokens should be stored with restrictive local filesystem permissions and excluded from backups or sync locations unless those are protected.

## Google Docs: Show Notes

**Purpose:** Create the approved show-notes document from the repository's Stage 3 template, named `<episode> Show Notes` (for example, `383 Show Notes`), and include episode number and show date at the top.

- **What's needed:** Enable Google Docs API and Drive API in a Google Cloud project; register an OAuth Desktop app; download the OAuth client configuration into `secrets/`; first run opens browser consent and stores the refresh token locally. Select or share the existing template with the application (Google Picker is the narrow-access route). A later unattended deployment can move to a service account, but it must be granted access to the destination folder/template and tested in the relevant Workspace account.
- **Auth and permissions:** Start with the user's OAuth Desktop app as the user, with browser consent on first run. Prefer the `drive.file` scope: it permits creating files and accessing files the user explicitly opens/shares with the app, and is the least-privilege Drive option appropriate when the template is explicitly selected/shared. Use Google Picker or an equivalent explicit file-selection flow for the template. The broader Drive scope grants access across Drive and is restricted; it is not needed for this workflow unless the implementation must search or edit arbitrary existing Drive files without explicit selection. Google Docs API also documents a `documents` scope; confirm the minimal effective scope combination for the chosen create/copy/edit sequence during implementation. Do not request broad Drive access merely for convenience.
- **API support:** Google Docs API supports creating and editing documents. Drive API supports file operations. OAuth Desktop flow is supported. A direct Docs API workflow is viable; exact template-copy and scope combination should be verified in a working test.
- **Approval:** Creating or updating the final show-notes document is a publishing action. Require the user to review the exact title, target folder, template, and document content and approve before the write.
- **Open questions:** What is the canonical Google Drive folder? Where is the current template, and should each episode copy it or create a fresh document? Should approved content overwrite/update an existing episode doc or refuse duplicates? Which Google account/Workspace owns the folder? When should migration to a service account happen, and is Workspace domain delegation allowed?

References: [Google Drive API scopes](https://developers.google.com/drive/api/guides/api-specific-auth), [Google Docs API overview](https://developers.google.com/docs/api/how-tos/overview), [Google Docs create and manage documents](https://developers.google.com/docs/api/how-tos/documents).

## Streamlabs And YouTube Live: Weekly Livestream

**Purpose:** Schedule the weekly livestream for Wednesdays at 6:00 PM `America/New_York`, streamed to YouTube.

- **What's needed:** A Streamlabs account and configured streaming software/scene, a YouTube channel eligible for live streaming, YouTube OAuth credentials with live-broadcast permissions, and a configured stream/encoder. Credentials and stream keys stay in `secrets/` and must never appear in logs or previews.
- **Auth and permissions:** YouTube Live Streaming API uses OAuth 2.0 on behalf of the channel owner; the authorized account must be permitted to manage the channel and live events. Streamlabs API requires a registered application and user OAuth authorization for the required account operations. Exact Streamlabs permission scopes depend on whether it only configures account features or manages a stream.
- **API support:** YouTube's Live Streaming API exposes broadcast and stream resources that support creating scheduled broadcasts. Streamlabs' public API documentation describes account access and custom alerts; it does not establish a supported API for scheduling/starting a Streamlabs Desktop livestream. Treat scheduling via Streamlabs API as **needs verification**. A possible split route is to schedule the YouTube broadcast through YouTube API and use Streamlabs Desktop to stream to it, but end-to-end compatibility and Streamlabs setup may require the UI/manual operation. Do not assume an API can control the local encoder.
- **Approval:** Require explicit approval before creating/updating any scheduled public YouTube broadcast, changing audience/visibility, or starting a stream. Never auto-start a stream.
- **Open questions:** Is Streamlabs Desktop the intended encoder, or is Streamlabs Talk Studio/another product involved? Should the software create the YouTube event, or will the user create it manually? What title, description, visibility, latency, thumbnail, and stream duration should be used? Does the schedule occur every Wednesday even when the user is not producing? Who handles the live-start action?

References: [Streamlabs API docs](https://dev.streamlabs.com/docs), [YouTube Live Streaming API](https://developers.google.com/youtube/v3/live/docs).

## Patreon: Supporter Notification

**Purpose:** Notify supporters about the show, including the Patreon-exclusive `snobist Show` only after that separate future consideration is resolved.

- **What's needed:** Patreon creator account/campaign access, a registered Patreon API v2 OAuth client, creator OAuth consent, campaign identity, and only the minimum campaign scopes required for the chosen notification route. Patreon v1 is retired; use v2. Store client secret and tokens in `secrets/`.
- **Auth and permissions:** OAuth as the creator. Patreon v2 scopes are endpoint-specific. The Live API documents `w:campaigns.lives` for creating/updating livestreams and campaign access rules; this is early access. Do not request member email or broad member scopes for a simple notification.
- **API support:** Patreon API v2 documentation exposes an early-access Live resource, including scheduled lives and access rules. The public docs inspected here document reading campaign posts, but do not establish a generally available endpoint for creating an ordinary supporter-notification post. Direct post creation/notification API support is **needs verification**. Until verified, prepare a draft and use Patreon Creator UI manually after approval. Patreon may notify eligible supporters when an approved post/live is published, but exact notification behavior and recipient controls need verification.
- **Approval:** Explicit approval is required before creating/publishing a Patreon post or live event and before triggering any supporter notification. Never send a notification automatically.
- **Open questions:** Is the desired notification a Patreon post, scheduled Patreon Live, or an existing campaign update workflow? Which tiers should see it? Should free followers receive it? What copy/link should be included? Is a manual UI handoff acceptable if the API cannot publish the desired item?

References: [Patreon API v2 docs](https://docs.patreon.com/), [Patreon clients and API keys](https://www.patreon.com/portal/registration/register-clients).

## Scheduled Runs: Rundown Ahead Of User Show Weeks

**Purpose:** Run the research/rundown workflow ahead of each user's every-other-Wednesday show week, anchored to episode 383 on October 14, 2026. This scheduler is for draft generation only and has no publishing permissions.

- **What's needed:** A scheduler (local `launchd` for a single Mac, or a managed scheduler if the workflow moves to a server), a reliable runtime, network access to feeds and Anthropic, secure access to `configs/snobos.env`, and persistent logs that exclude secrets. Scheduling credentials must be scoped to running the research job, not writing to social or publishing destinations.
- **Auth and permissions:** Use the local Snobos Anthropic key for a local scheduler. A managed scheduler needs a secrets manager or explicitly protected injected secret. Google/Patreon/social credentials are not required for rundown generation.
- **API support:** A local scheduler such as `launchd` can invoke the CLI without a service API; this is an operating-system scheduling route, not an integration API. Managed scheduler choice is open. No scheduler is authorized to publish, schedule the livestream, or notify supporters.
- **Approval:** No approval is needed to create a local draft rundown under the already approved research workflow. Approval remains mandatory for all external writes and notifications.
- **Open questions:** How many hours/days before the user's show should the run happen? Should a missed/failed run retry, and how many times? Should it alert the user locally? Does this run on the user's Mac or an always-on host? How do skipped Wednesdays and producer-rotation changes affect the trigger?

## Future Consideration: snobist Show

The snobist Show is a 15-minute Patreon-exclusive show for paying supporters. This is documentation only; do not design or build it in V2. Open questions:

- Does it need its own sourcing or show notes?
- Does it share the main show's reporting window?
- How does its content differ from the main show?
