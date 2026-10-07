# Add BIK Ventures hackathon feature (media + roadmap)

## Goal
Showcase BactoAI's representation at the BIK Ventures Hub pitch event at Kenyatta University (16 May 2026), using the newspaper clipping, Samwel's feedback video, and the BIK YouTube coverage — with accurate framing.

## Accuracy rule (important)
The 2nd-place prize at that event was won by a different innovation (GEES), not BactoAI. All copy must say BactoAI was **represented / featured**, never that BactoAI won the prize.

## What we will build

1. **Upload assets via Lovable CDN**
   - Newspaper clipping image (`WhatsApp_Image_2026-09-09_at_10.41.51.jpeg`) → `src/assets/bik-magazine.jpg.asset.json`
   - Feedback video (`WhatsApp_Video_2026-09-09_at_10.43.43.mp4`) → `src/assets/bik-feedback.mp4.asset.json` (check size/duration first with ffprobe; if very large, note it to you)

2. **Extend `src/components/site/Media.tsx`** with a second press item below the KUTV block:
   - Sub-heading: "On the ecosystem stage" or similar
   - Copy: Samwel Elegwa and William Otieno represented BactoAI at the BIK Ventures Hub startup pitch event at Kenyatta University (16 May 2026); the event was covered in print and on BIK's YouTube channel.
   - Newspaper clipping shown as an image card (rotated upright if needed)
   - Embedded playable feedback video (HTML5 `<video>` with poster)
   - Link button to the BIK YouTube video (https://youtu.be/SOSCWDj7mYk), labelled as BIK's event coverage featuring multiple innovations
   - No claim of prize placement

3. **Add a milestone to `src/components/site/Roadmap.tsx`** at the top of the list:
   - Title: "BIK Ventures pitch event" — "Represented BactoAI at Kenyatta University's startup pitch showcase; featured in press and event coverage." (May 2026)
   - Framed as ecosystem visibility, not a win

4. **Verify**: `bun run build` passes; Playwright check on `/about` confirms the clipping, video, and YouTube link render.

## Out of scope
- No design-token or restyle changes
- No blog post (not selected)
- No new routes or nav changes
