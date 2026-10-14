# Snobos V3 Plan: Distribution

## Scope And Non-Negotiable Approval Rule

V3 covers distribution of approved episode media and approved promotional teasers. It depends on the V2 logistics and show-notes work and the Stage 3 show-notes template prerequisite in [snobos-v1.md](snobos-v1.md). Every publishing or notifying action requires the user's explicit approval immediately before it goes live. No auto-posting to public channels. Approval must identify the destination, episode, exact content/media, audience/visibility, and timing. Missing or ambiguous approval means no write request.

Credentials, OAuth client files, access/refresh tokens, webhook secrets, and platform keys must live under `secrets/`, which must be gitignored before any credentials are created. Never print, log, expose, or commit them. The current repository does not yet ignore `secrets/`; adding and verifying that ignore rule is an implementation prerequisite.

For API eligibility and product requirements, re-check the linked official documentation before implementation: platform policies, scopes, versions, and access levels change. Anything not established by the docs inspected for this plan is explicitly marked **needs verification**.

## Podcast Episode Distribution

### snoboscast.com

- **What's needed:** Access to the site's hosting/CMS and domain, the media asset or podcast-host URL, episode metadata, approved show notes, and a publication destination. Credentials belong in `secrets/`.
- **Auth and permissions:** Depends on the website stack (CMS API token, OAuth, or deployment credentials) and a role allowed to create/publish episodes. The site platform is not identified in the repository.
- **API support:** **Needs verification.** The domain alone does not identify its CMS, hosting provider, upload API, or supported publishing route. A CMS API may be possible; otherwise use the site's authenticated admin interface. Do not assume a public API or RSS host.
- **Approval:** Explicit approval before upload, publication, or updating the episode page.
- **Open questions:** What CMS/host powers snoboscast.com? Is it the canonical audio/video host or only a website? Where is the master episode asset? Does publication update an RSS feed? What URL, metadata, and schedule are required?

### YouTube

- **What's needed:** YouTube channel, Google Cloud project with YouTube Data API enabled, OAuth client and channel-owner consent, final approved video, metadata, thumbnail, visibility and scheduling settings. Keep client credentials/tokens in `secrets/`.
- **Auth and permissions:** OAuth 2.0 as a channel owner/manager with upload permission; use the narrow YouTube upload scope needed by the upload workflow. Channel must be eligible for the requested features, and API quota applies.
- **API support:** **Supported by API.** YouTube Data API supports video uploads and metadata updates. YouTube Live Streaming API separately manages live broadcast resources; it is not a substitute for uploading a recorded episode. Validate current quota, verification/audit requirements, and any project restrictions during implementation.
- **Approval:** Explicit approval before upload and again before making a private/unlisted/scheduled item public if the workflow separates those actions. Never auto-publish.
- **Open questions:** Is YouTube the video or audio destination, or both? Which channel? What default visibility and publish timing? Who supplies thumbnail and final title/description? Should upload be a draft/private item until separately approved?

References: [YouTube Data API videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert), [YouTube API upload guide](https://developers.google.com/youtube/v3/guides/uploading_a_video).

### Apple Podcasts

- **What's needed:** An Apple Podcasts Connect account with authority over the show, a valid publicly reachable podcast RSS feed with enclosure/media metadata, artwork, and feed-host account access. If the feed host is external, manage episode uploads and RSS metadata there.
- **Auth and permissions:** Apple Podcasts Connect account access for show submission/ownership and any required provider credentials. A direct public episode-upload API credential is not established here.
- **API support:** Apple Podcasts distribution generally uses a show RSS feed submitted/validated in Apple Podcasts Connect; episodes are then ingested from that feed. Direct upload/API support for this workflow is **needs verification**. Likely route is publish the episode through the podcast host's RSS feed, with initial show submission and feed management via Apple Podcasts Connect UI.
- **Approval:** Explicit approval before the host publishes the episode to the feed, which distributes it to Apple Podcasts. Approval is also required before changing show/episode metadata.
- **Open questions:** Who hosts the canonical RSS feed? Is Snobos already listed in Apple Podcasts, and which Apple account owns it? Are there Apple-specific metadata/artwork requirements? Does the hosting provider have a supported publishing API?

References: [Apple Podcasts for Creators](https://podcasters.apple.com/). Apple support pages were not retrievable during preparation; confirm current RSS submission and episode ingestion requirements before implementation.

### Spotify

- **What's needed:** A Spotify for Creators account claiming/controlling the show, the canonical podcast RSS feed and feed-host access, episode media/metadata, and access to the hosting provider. If Spotify hosts the show, use the Spotify for Creators account and available publishing tools.
- **Auth and permissions:** Spotify account owner/editor permissions for Spotify for Creators and separate host credentials if publishing through an external host. A general Spotify Web API token is not assumed to grant podcast episode upload privileges.
- **API support:** Spotify's official guidance says shows hosted with Spotify for Creators publish there directly, while podcasts hosted with partner providers are submitted through the hosting provider's distribution instructions. External-host distribution is generally RSS-based; a public general-purpose direct episode-upload API for this workflow is **needs verification**. Prefer the canonical host/RSS route unless Spotify's current creator tools or chosen host document a supported API.
- **Approval:** Explicit approval before publishing through the host or Spotify creator interface; publishing a feed item may distribute it to Spotify automatically.
- **Open questions:** Is Spotify the RSS host or only a destination? Which provider hosts the feed? Is Snobos claimed in Spotify for Creators? Does the host offer an API, and what metadata does Spotify ingest from RSS?

References: [Spotify: Getting your show on Spotify](https://support.spotify.com/us/creators/article/getting-your-podcast-on-spotify/), [Spotify for Creators](https://creators.spotify.com/).

## Video Teaser Distribution

Teaser captions must add context or promotion without restating any line or question already spoken in the clip. Before approval, compare the draft caption with the selected clip transcript/captions, flag semantic and near-verbatim overlap, and require human review. Do not publish a caption that repeats clip dialogue. Captions do not replace the user's explicit approval.

### Facebook

- **What's needed:** A Facebook Page (or other supported destination), Meta developer app, final video, caption, and a role on the Page with publishing authority.
- **Auth and permissions:** Meta OAuth/Page access token and the current video publishing permissions (for example, Page video publishing permissions as applicable); app review/advanced access may be required for non-app-role users. Verify the current exact permission and account type before implementation.
- **API support:** **Supported by Meta APIs for eligible Pages/video publishing**, subject to current Graph API endpoints, app review, Page roles, and upload constraints. The specific Facebook Reels/video endpoint and capability required for this teaser are **needs verification**.
- **Approval:** Explicit approval of video, non-repeating caption, destination, and visibility before publishing.
- **Open questions:** Facebook Page or personal profile? Is this a Reel or standard video? Which Page role/account and Meta app can be used? Should the teaser link to the full episode?

Reference: [Meta Graph API documentation](https://developers.facebook.com/docs/graph-api/).

### Threads

- **What's needed:** Threads profile, Meta developer app, final supported video asset hosted at a publicly accessible URL, caption, and a publishing flow that creates then publishes a media container.
- **Auth and permissions:** Threads OAuth authorization for the profile and the applicable publishing permission/product access. Exact app mode/access level and review requirements must be confirmed against the current Threads API onboarding docs.
- **API support:** **Supported by API.** Official Threads Posts documentation describes video media containers and a separate publish call. Observe current media specs, wait/status behavior, and rate limits.
- **Approval:** Explicit approval before container publication; creating an unpublished container must also be surfaced as an external upload and approved unless the user specifically approves draft upload.
- **Open questions:** Which Threads profile? Can the video be hosted temporarily at a secure, publicly fetchable URL? What caption/hashtags/link are preferred? Should upload drafts be allowed before final approval?

Reference: [Threads Posts API](https://developers.facebook.com/docs/threads/posts).

### TikTok

- **What's needed:** TikTok account, developer app, approved Content Posting API product access, final video, caption, and creator-specific posting preferences/visibility.
- **Auth and permissions:** TikTok Login Kit/OAuth creator authorization and the relevant Content Posting API permission. Direct Post use may require app review/audit and has creator/posting restrictions; verify eligibility and whether unaudited clients are limited to private visibility.
- **API support:** **Supported by API, with eligibility/audit constraints.** TikTok documents both Direct Post and Upload-to-TikTok draft flows. If public Direct Post is unavailable, use the official upload-to-draft flow or manual TikTok app; do not attempt unofficial automation.
- **Approval:** Explicit approval for any upload; a draft upload must be labeled as an external upload, and a separate approval is required before posting publicly.
- **Open questions:** Is the TikTok account personal, creator, or business? Which API access level is available? Is a draft handoff acceptable? What content disclosure, music, and audience settings apply?

Reference: [TikTok Content Posting API](https://developers.tiktok.com/products/content-posting-api/).

### Instagram

- **What's needed:** Instagram professional account (Business or Creator), Meta developer app, final teaser video, caption, and a publicly fetchable media URL or supported resumable upload.
- **Auth and permissions:** Instagram Login or Facebook Login OAuth, professional account access, content-publishing permission (`instagram_business_content_publish` or the current equivalent for the chosen login flow), app access level/review, and any required Page connection/authorization. Complete Page Publishing Authorization if applicable.
- **API support:** **Supported by API for professional accounts.** Instagram Content Publishing API supports Reels/video containers followed by a publish operation; personal-account eligibility is not assumed. Publicly accessible media hosting and current format/size limits apply.
- **Approval:** Explicit approval before publishing; for separated container/upload and publish actions, seek approval before the publish action and surface any external upload first.
- **Open questions:** Is the account Business or Creator? Which login flow and connected Page should be used? Who hosts teaser media temporarily? Is the intended placement Reels, Feed, or both?

Reference: [Instagram API content publishing](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/content-publishing).

## Sources Checked

Platform statements above are based on official documentation linked in each integration section, consulted on 2026-10-14. Apple Podcasts and Streamlabs scheduling details were not fully verifiable from retrieved documentation and remain explicitly open/marked for verification.
