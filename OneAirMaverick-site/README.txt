ONE AIR MAVERICK WEBSITE: SETUP INSTRUCTIONS
=============================================

WHAT'S IN THIS FOLDER
  public/             The website. This is the only folder that gets uploaded to Cloudflare Pages.
  form-worker/        A small Cloudflare Worker that emails each flight request to the inbox.
  tools/              Scripts that rebuild the airport list and map. Not needed to run the site.
  IMAGE-CREDITS.md    Where each photo came from (all public domain or CC0).

The site has no outside dependencies: fonts, map, airport search and images are all local files.
Everything below uses Cloudflare's free plan.


STEP 1. PREVIEW IT (2 minutes)
  Double-click public/index.html. It opens in your browser and works offline.
  The request form is in demo mode until Step 6: it shows a confirmation but sends nothing.


STEP 2. PUT THE DOMAIN ON CLOUDFLARE (10 minutes, plus DNS wait)
  1. Create a free account at dash.cloudflare.com (or log in).
  2. Add the domain: Add a domain > enter it > Free plan. If it's registered elsewhere,
     change its nameservers at the registrar to the two Cloudflare gives you. It can take
     up to a day to switch over; the dashboard shows "Active" when it's done.
     (No domain yet? Skip to Step 3 and use the free .pages.dev address for now. The form
     email in Step 4 needs the domain, so it waits until then.)


STEP 3. PUBLISH THE WEBSITE (5 minutes)
  1. Workers & Pages > Create > Pages > Upload assets.
  2. Project name: e.g. oneairmaverick. Drag in the "public" folder. Deploy.
  3. The site is live at https://<project-name>.pages.dev
  4. In the project: Custom domains > Set up a custom domain > enter the domain
     (add both example.com and www.example.com).
  To update the site later: open the project > Create deployment > upload "public" again.


STEP 4. TURN ON EMAIL FOR THE FORM (10 minutes)
  1. In the domain: Email > Email Routing > Get started / Enable. Accept the DNS records
     it adds (this is what lets Cloudflare send mail from the domain).
  2. Email Routing > Destination addresses > add the inbox that should receive requests.
     Open the verification email Cloudflare sends and click Verify.
     (Sending to your own verified address is free on every plan.)


STEP 5. TURN ON SPAM PROTECTION (5 minutes)
  1. Turnstile > Add widget. Name: One Air Maverick form.
     Hostnames: the domain, www.<domain>, and <project-name>.pages.dev. Mode: Managed.
  2. Copy the Site Key and the Secret Key. You need both in Step 6.


STEP 6. DEPLOY THE FORM WORKER (15 minutes)
  Needs Node.js (free, from nodejs.org, the LTS version). Then in Terminal:
  1. cd into the form-worker folder.
  2. Open wrangler.toml in any text editor and replace every REPLACE_ value:
       destination_address and TO_EMAIL  -> the inbox you verified in Step 4 (both the same)
       FROM_EMAIL                        -> e.g. requests@<domain>  (must be on the domain)
       ALLOWED_ORIGINS                   -> https://<project-name>.pages.dev,https://<domain>,https://www.<domain>
  3. Run:
       npx wrangler login                       (opens the browser to approve)
       npx wrangler secret put TURNSTILE_SECRET (paste the Turnstile Secret Key)
       npx wrangler deploy
  4. It prints the Worker address, like https://oam-flight-requests.<name>.workers.dev
  5. Open public/index.html in a text editor, find the CONFIG block near the top of the
     main script, and fill in:
       endpoint: "https://oam-flight-requests.<name>.workers.dev",
       turnstileSiteKey: "<the Turnstile Site Key>",
  6. Re-upload the "public" folder to Pages (Step 3, "To update").


STEP 7. TEST IT (5 minutes)
  On the live site (not the local file; the Worker only accepts the addresses in
  ALLOWED_ORIGINS), fill out Plan your flight with your own details and send it.
  Within a minute the inbox should get "Flight request: ..." with every detail.
  Hitting Reply should address the email to the person who filled out the form.
  If it fails: in Cloudflare, Workers & Pages > oam-flight-requests > Logs shows why
  (most often FROM_EMAIL isn't on the domain, or the inbox isn't verified yet).


STEP 8. FILL IN THE BUSINESS DETAILS (Gracie will send these)
  All placeholders are highlighted in yellow on the pages so they're easy to spot.
  public/index.html, CONFIG block near the top of the main script:
    disclosure        -> replace [LEGAL ENTITY NAME] (twice) and [CERTIFICATE NO.]
                         in BOTH the prelaunch and live lines
    contact           -> contact: { email: "...", phone: "...", base: "..." },
                         (this adds the email, phone and home airport across the site)
    petsConfirmed / walkaroundConfirmed -> set to true only if Gracie confirms
  public/index.html, top of the file (only once the real domain is live):
    change <meta property="og:image" content="og-image.png"> to the full address,
    e.g. https://<domain>/og-image.png, and add under it:
    <link rel="canonical" href="https://<domain>/">
  public/privacy.html (search for "[" to find each one):
    [EFFECTIVE DATE], [LEGAL ENTITY NAME], [MAILING ADDRESS], [PRIVACY EMAIL], [PHONE],
    [HOSTING PROVIDER...], the service-provider list, the retention period,
    and delete the analytics bullet (analytics are off) and the spam-protection
    bullet only if Turnstile was NOT turned on.
  Re-upload "public" after editing.


STEP 9. GO LIVE (only when Gracie says so)
  After the attorney signs off, change  launchMode: "prelaunch"  to  launchMode: "live"
  in the CONFIG block and re-upload. That switches "Join the priority list" to
  "Request a flight" across the site.


NOT FOR YOU (Gracie handles these)
  - Attorney review of everything marked COUNSEL in the code.
  - Confirming "One Air Maverick" is a business name in the Part 135 operations specifications.
  - Confirming the VERIFY items: cruise speeds, Turbo Commander model, seat counts,
    maintenance-records line.
