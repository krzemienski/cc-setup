# Consent, disclosure, and the legal landscape

A voice identifies a person, and a convincing clone can be used to defraud their family, their bank, or their audience. Treat consent as a precondition, not a formality. This file is practical guidance, not legal advice; point users with commercial or cross-border plans to a lawyer.

## 1. The consent gate

Before helping with any cloning, fine-tuning, or voice-conversion workflow for a specific voice, establish whose voice it is and what rights the user holds. Ask plainly and keep it short:

1. Whose voice is in the recordings?
2. If it is not yours: has that person agreed to having their voice cloned, for this purpose? Is the agreement in writing or on a recording?
3. If the person has died: are you acting with the estate or next of kin's agreement?
4. What will the cloned voice be used for, and who will hear it?

Then proceed according to the answer:

| Situation | Action |
|---|---|
| The user's own voice | Proceed. |
| Another living person who has consented, and the user can say how (signed release, recorded statement, contract) | Proceed. Suggest recording a spoken consent statement (section 2) if they do not already have one. |
| A deceased person, with the estate or family's agreement, for a private or memorial purpose | Proceed with care; note that several jurisdictions give estates control over a voice (section 5). |
| Invented or designed voices, generic stock voices, or voices from datasets licensed for synthesis | Proceed; confirm the dataset license. |
| A public figure, celebrity, politician, or any real person without consent | Do not help clone that voice. Offer alternatives: a designed voice, a licensed stock voice, or the user's own voice. Parody and commentary do not change this for a skill that produces the clone itself. |
| Signs of deception: impersonating someone to their contacts, getting past voice authentication, fake calls, fabricated statements | Decline the cloning work entirely, even if the user claims consent. |

Do not demand documents or interrogate. Ask once, take the user's answer at face value unless the conversation contradicts it, and carry on.

## 2. Recording consent

A good practice, adopted by commercial providers, is to capture consent in the same voice that is being cloned:

- Have the speaker read a consent sentence that names the purpose and the date, for example: "I, [name], agree to my voice being used to train a synthetic voice for [purpose], on [date]."
- Record it in the same session as the training audio, with the same mic. Hugging Face's "voice consent gate" reference pattern (Oct 2025) uses this consent recording as part of the training data, which ties the two together. https://huggingface.co/blog/voice-consent-gate
- ElevenLabs' professional cloning requires the user to read verification lines that are matched against the training audio, and only allows cloning one's own voice. https://elevenlabs.io/docs/product-guides/voices/voice-cloning/professional-voice-cloning
- Store the consent recording with the dataset. If consent is withdrawn, delete the dataset, checkpoints, and any hosted copies.

## 3. Disclosure and watermarking

- **Disclose** synthetic speech to listeners whenever it could be mistaken for the real person: a spoken or written note in podcasts, videos, and voice apps.
- **Keep built-in watermarks.** Chatterbox embeds Resemble's PerTh watermark in all output (https://www.resemble.ai/products/watermarker); VibeVoice and some others watermark too. Do not strip them.
- **Add one when the model does not:** Meta's AudioSeal (MIT, sample-level detection, streaming since v0.2) — https://github.com/facebookresearch/audioseal.
- **Provenance metadata:** C2PA Content Credentials can be embedded in WAV, MP3, and FLAC (C2PA spec v2.2).
- Google's SynthID audio covers Google's own models; its detector is limited to an early-access waitlist.

## 4. Handling voice data

- Voice recordings are personal data; under the GDPR, voice processed to identify someone is biometric data requiring explicit consent (EDPB Guidelines 02/2021). https://cuatrecasas.com/en/spain/article/new-eu-guidelines-on-voice-assistants-and-data-protection
- Keep datasets and checkpoints in **private** repositories or local storage. Never upload another person's voice to a public Space or shared drive without their consent.
- Delete data and models on request.

## 5. Legal landscape (status as of 2026-10-07)

Statuses were checked against the linked sources on 2026-10-07. Items marked NOT VERIFIED could not be confirmed that day.

### United States — federal

- **NO FAKES Act** (S.4591 / H.R.8915): would create a federal right in voice and likeness with DMCA-style notice and takedown, preempting state law. Advanced unanimously by Senate Judiciary on 2026-06-18; no floor vote yet; not law. https://www.blackburn.senate.gov/2026/6/blackburn-coons-bipartisan-bill-to-protect-individuals-and-creators-from-deepfakes-passes-senate-judiciary-committee
- **FCC Declaratory Ruling 24-17** (Feb 2024): AI-generated voices are "artificial" voices under the TCPA, so robocalls using them need the called party's prior express consent. In force. https://wsgr.com/en/insights/fcc-rules-ai-generated-voices-are-artificial-under-the-tcpa.html
- **FTC impersonation rule:** impersonating governments and businesses is covered (Feb 2024). Extending it to impersonating individuals has **not** been finalized; an ANPRM on 2026-10-01 said the FTC is still evaluating options. https://public-inspection.federalregister.gov/2026-20143.pdf
- **TAKE IT DOWN Act** (platform compliance from 2026-05-19) covers intimate *visual* depictions only, not audio. https://wilmerhale.com/en/insights/client-alerts/20260615-the-take-it-down-act-goes-live

### United States — states

- **Tennessee ELVIS Act** (in force 2024-07-01): adds voice, real or simulated, to the publicity right, and makes it unlawful to distribute a tool whose primary purpose is reproducing a specific person's voice without authorization. https://manatt.com/insights/newsletters/client-alert/tennessees-elvis-act-expands-publicity-rights-for
- **California AB 2602 and AB 1836** (signed 2024-09-17): AB 2602 limits contract terms for performers' digital replicas (effective 2025-01-01); AB 1836 bars digital replicas of a deceased person's voice in audiovisual works and sound recordings without the estate's consent. https://perkinscoie.com/insights/update/single-day-california-enacts-five-bills-tackling-digital-replicas-and-deepfakes
- **New York S.8420 and S.8882** (signed 2025-12-11): disclosure required for synthetic performers in ads (effective 2026-06-09); digital replicas of deceased performers' voices regulated (effective on signing). https://www.skadden.com/insights/publications/2026/01/two-newly-enacted-new-york-laws-will-regulate
- **Washington SB 5886** (in force 2026-06-10): adds "forged digital likeness", including audio, to the publicity right for living and deceased people. https://www.dwt.com/insights/2026/06/washington-state-right-of-publicity-ai-replicas

### European Union

- **AI Act Article 50** (applies from 2026-08-02): providers must make synthetic audio machine-detectable, and anyone publishing a deepfake must label it; systems already on the market have until 2026-12-02 for machine-readable marking (single law-firm source for the grace period). https://www.kingsleynapley.co.uk/our-insights/articles/the-eu-ai-acts-transparency-rules-are-now-live-what-organisations-need-to-do/
- **GDPR:** see section 4.

### Elsewhere

- **Denmark:** a Copyright Act amendment protecting voice and likeness against realistic imitation (50 years after death, with satire exceptions). **NOT VERIFIED as adopted** — still pending as of a 2026-10-02 tracker. https://eprs.europarl.europa.eu/contents/publications/EPRS/2026/01/EPRS_ATA(2026)782611.html
- **United Kingdom:** no standalone voice or personality right; claims rely on passing off, data protection, and defamation. A government consultation on digital replicas was promised in March 2026; **NOT VERIFIED** whether it has launched. https://www.scl.org/uk-government-issues-report-on-ai-and-copyright/
- **China:** the Deep Synthesis Provisions (in force 2023-01-10) require separate consent from anyone whose voice is edited and conspicuous labels on synthetic content; AI content labeling measures (in force 2025-09-01) add explicit and metadata labels, including audio cues. https://www.aoshearman.com/en/insights/ao-shearman-on-data/china-brings-into-force-regulations-on-the-administration-of-deep-synthesis-of-internet-technology · https://www.loeb.com/en/insights/publications/2025/03/chinas-ai-labeling-measures-and-mandatory-national-standards-take-effect-september-1

### Posthumous rights

- **California Civ. Code §3344.1:** a deceased person's voice is protected for 70 years; successors must register to recover damages. https://rightofpublicity.com/statutes/california
- **Tennessee:** 10 years after death, continuing as long as the right stays in commercial use. https://rightofpublicityroadmap.com/state_page/tennessee/
- **New York S.8882** and **Washington SB 5886** also cover deceased people (above).

## 6. Publishing platforms have their own rules

A permissive model license and full consent still do not guarantee a platform will accept synthetic speech. Before the user invests in a cloned voice for a specific outlet, check that outlet's current policy on AI or synthetic narration and labeling, and tell the user what you found.

- **Audible / ACX:** "Your submitted audiobook must be narrated by a human unless otherwise authorized. Unauthorized use of text-to-speech, AI, or automated recordings in ACX titles is prohibited." (ACX Audio Submission Requirements, last updated 2026-04-15; verified 2026-10-07 — https://help.acx.com/s/article/acx-audio-submission-requirements). Amazon's own authorized AI programs are separate from a self-built clone; verify their current eligibility before suggesting them.
- **Other audiobook stores, podcast hosts, video platforms, and ad networks** each set their own disclosure and acceptance rules, and these change often. Look up the specific platform's current help-center page rather than relying on memory or third-party summaries; cite the page and its date.
- If the target platform rejects AI narration, offer the alternatives: the user narrates that edition themselves, publishes the synthetic edition only where it is allowed (with the required label), or uses the clone for drafts, previews, and corrections rather than the final product.

## 7. Model licenses that encode consent rules

Some model licenses restrict use regardless of local law: the Sesame CSM card forbids imitating people without consent, pocket-tts's README prohibits cloning anyone without consent, and Higgs TTS 3 bans using its outputs to train other speech models. Check `references/model-landscape.md` before recommending a model for a given purpose.
