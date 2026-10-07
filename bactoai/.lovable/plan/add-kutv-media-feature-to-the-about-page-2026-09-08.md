Add KUTV media feature to the About page

Goal
Turn the KUTV Kenya appearance into an "In the media" card/section on /about that builds credibility, highlights the AMR awareness call-to-action, and positions Samwel Elegwa as a public voice for BactoAI.

What we will build
1. Upload both uploaded KUTV images to the Lovable CDN and create `.asset.json` pointers.
   - `1003663672.jpg` → KUTV branded poster (hero visual)
   - `1003663688.jpg` → behind-the-scenes photo with Hassan Lewa
2. Add a new `Media` section component (`src/components/site/Media.tsx`) rendered on `/about` between `Team` and `Partners`.
   - Eyebrow: "In the media"
   - Heading: "Bringing the AMR conversation to national television."
   - Lede: one line about Samwel representing BactoAI on KUTV Kenya to call for AMR awareness.
   - Hero card with the KUTV poster, show details, and a link to the YouTube interview.
   - Secondary card/figure with the behind-the-scenes photo and a short caption.
   - Copy blends all three angles: media credibility, AMR awareness, and founder thought leadership.
3. Update `src/routes/about.tsx` to import and render the new `Media` section.
4. Keep existing styles and design tokens untouched; reuse existing card, button, and typography patterns from the site.
5. Ensure the section has a stable anchor id (e.g. `#media`) for future deep links.
6. Run `bun run build` to verify no TypeScript or import errors, then confirm the About page renders the new section.

Out of scope
- No new routes or nav changes (the feature lives on the existing About page).
- No changes to other pages or components unless required by the build.
- No email/inbox wiring; that remains a separate task.
