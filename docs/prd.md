# Can I Click It?

**AI-Powered Personal Safety Assistant**

*A Seatbelt for the Internet*

| | |
|---|---|
| **Version** | 3.0 |
| **Date** | February 20, 2026 |
| **Status** | Build-Ready |
| **Classification** | Confidential |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision and Positioning](#3-product-vision-and-positioning)
4. [Target Users and Personas](#4-target-users-and-personas)
5. [User Stories and Use Cases](#5-user-stories-and-use-cases)
6. [Feature Requirements](#6-feature-requirements)
7. [Emergency Recovery System](#7-emergency-recovery-system)
8. [Psychological Design Framework](#8-psychological-design-framework)
9. [AI and ML Intelligence Layer](#9-ai-and-ml-intelligence-layer)
10. [Platform Constraints and Mitigations](#10-platform-constraints-and-mitigations)
11. [Technical Architecture](#11-technical-architecture)
12. [Unit Economics and Cost Model](#12-unit-economics-and-cost-model)
13. [Data Moat and Network Effects Strategy](#13-data-moat-and-network-effects-strategy)
14. [Competitive Defense Narrative](#14-competitive-defense-narrative)
15. [Privacy and Security](#15-privacy-and-security)
16. [Liability and Legal Architecture](#16-liability-and-legal-architecture)
17. [Monetization Strategy](#17-monetization-strategy)
18. [Go-to-Market Strategy](#18-go-to-market-strategy)
19. [Success Metrics and KPIs](#19-success-metrics-and-kpis)
20. [MVP Development Roadmap](#20-mvp-development-roadmap)
21. [Risks and Mitigations](#21-risks-and-mitigations)
22. [Open Questions for Stakeholder Resolution](#22-open-questions-for-stakeholder-resolution)
23. [Appendices](#23-appendices)

---

## 1. Executive Summary

"Can I Click It?" is a consumer-focused AI safety assistant that provides instant threat analysis for suspicious messages, links, QR codes, screenshots, and attachments across every digital channel. It defines a new product category — the **Personal AI Security Assistant (PASA)** — and positions itself as a seatbelt for the internet.

The product addresses the full lifecycle of a threat encounter. Before interaction, it analyzes intent, artifacts, and context to deliver a color-coded verdict with a transparent confidence level. After interaction, it provides guided, step-by-step emergency recovery tailored to what happened. It answers not just "Can I click this?" but also "What do I do now that I already clicked it?"

> *Before you click — ask us. After you click — we've got you.*

The MVP ships as a mobile app (iOS and Android) with a browser extension (Chrome, Safari, Edge, Firefox), buildable in 8–12 weeks. It is designed for seniors, non-technical users, busy professionals, and families, with a Grandma Mode interface for the least technical users and voice input for accessibility. The product expands into call screening, deepfake detection, identity protection, and financial fraud prevention.

This v3.0 PRD incorporates six critical additions based on strategic review: platform constraint analysis, liability and legal architecture, unit economics and cost modeling, expanded false negative mitigation, data moat and network effects strategy, and a competitive defense narrative against big-tech entry.

---

## 2. Problem Statement

### 2.1 The Evolving Threat Landscape

AI has fundamentally altered the economics of scam operations. Large language models produce flawless phishing messages at scale, eliminating grammatical errors that once served as reliable warning signs. Attackers impersonate banks, employers, family members, and government agencies with messages indistinguishable from legitimate communications.

1. AI-generated phishing messages are grammatically perfect and contextually personalized.
2. Scammers impersonate known contacts, banks, and government agencies with high fidelity.
3. Deepfake voice and video support increasingly sophisticated social engineering.
4. Traditional spam filters miss targeted, low-volume spear-phishing attacks.
5. Seniors lose an estimated $3.4 billion annually to fraud (FBI IC3, 2024).
6. Even cybersecurity professionals report being momentarily fooled.

### 2.2 Why Current Solutions Fail

| Current Tool | Coverage | Gap | Timing |
|---|---|---|---|
| Email Spam Filters | Email only | No SMS, messaging, social, QR | Pre-delivery |
| Antivirus Software | Device-level | No messaging context; reactive | Post-infection |
| Browser Warnings | Known-bad URLs | Activates after the click | Post-click |
| Security Training | Awareness | Unrealistic for seniors; decays fast | Preventive but fragile |

No existing tool addresses what happens after a user has already engaged with a threat. The gap between "I think I made a mistake" and "I know what to do next" is where real damage compounds through delayed action and panic-driven decisions.

### 2.3 Core Insight

> *Users do not want to learn security. They want a simple answer before a click — and clear, calming guidance after a mistake.*

The product solves for two critical moments: the decision moment before interaction, and the recovery moment after a mistake. It also removes the embarrassment of asking "Is this a scam?" — a psychological barrier that delays action and increases harm.

---

## 3. Product Vision and Positioning

### 3.1 Vision Statement

Become the world's most trusted personal AI safety assistant — the universal answer to "Is this safe?" — and evolve into the antivirus for human deception: a comprehensive digital guardian that protects individuals and families across every channel, device, and interaction.

### 3.2 Brand Positioning

> *A seatbelt for the internet.*

Most security tools are invisible until after damage occurs. "Can I Click It?" positions itself as a proactive safety layer that is always visible, always available, and always simple. The seatbelt analogy communicates three things: it is universally needed, effortless to use, and expected to be there before something goes wrong.

The tagline **"We analyze threats, not your life"** reinforces privacy trust and should be elevated to primary brand messaging across all channels.

### 3.3 Strategic Goals

| Horizon | Goal | Success Metric |
|---|---|---|
| **6 months** | Launch MVP with core detection, emergency recovery, Grandma Mode, and voice input | 50,000 downloads; 70% of scans < 3 seconds |
| **12 months** | Establish freemium with subscriber base; launch family protection and guardian dashboard | 5% conversion; 10,000 premium subscribers |
| **24 months** | Secure telecom and banking partnerships; expand into call screening and identity protection | 2+ partnerships; 500,000 active users |

### 3.4 Design Principles

1. **Radical Simplicity.** Every interaction completable by a 75-year-old with no technical background.
2. **Speed of Trust.** Results feel instantaneous; credibility degrades with latency.
3. **Explain, Don't Lecture.** Plain-language reasoning without jargon or scare tactics.
4. **Privacy by Design.** Content processed ephemerally; the product analyzes threats, not people.
5. **Full Lifecycle Coverage.** Protection before, during, and after a threat encounter.
6. **Transparent Confidence.** The system communicates its certainty so users calibrate trust.
7. **Safe Action Bias.** When uncertain, always recommend the cautious path.

---

## 4. Target Users and Personas

### 4.1 Primary Personas

#### Persona 1: Margaret, 72 — "The Cautious Grandparent"

Margaret uses an iPhone and receives SMS messages daily. She recently received a text claiming to be from her bank. She felt anxious but did not know who to ask and did not want to bother her adult children.

- **Needs:** One-tap safety check; giant text; voice input; clear recovery guidance after a mistake.
- **Frustrations:** Feels embarrassed asking family; cannot distinguish real messages from scams; does not know what to do after clicking something bad.

#### Persona 2: David, 38 — "The Busy Professional"

David is a marketing director who recently clicked a phishing link disguised as a DocuSign request and had to reset all his credentials. He did not know which accounts were at risk.

- **Needs:** Seamless browser integration; fast link checking; post-click damage assessment and recovery.
- **Frustrations:** Security tools are intrusive; after clicking a bad link, he had no guidance on containment.

#### Persona 3: Priya, 45 — "The Protective Parent"

Priya's 14-year-old daughter uses Instagram and WhatsApp. Priya worries about scam DMs, malicious links in group chats, and social engineering from strangers.

- **Needs:** Family protection with alerts; child-friendly recovery guidance; remote recovery trigger.
- **Frustrations:** Parental controls focus on content filtering, not scam protection; no way to help her child recover remotely.

### 4.2 Secondary Personas

- **Small Business Owners:** Vulnerable to invoice fraud and BEC; need lightweight protection.
- **Caregivers:** Manage digital safety for elderly parents remotely; need alerting and remote recovery.
- **International Users:** Receive scams in multiple languages; need multilingual detection.

---

## 5. User Stories and Use Cases

### 5.1 Core User Stories

| ID | Persona | Story | Acceptance Criteria |
|---|---|---|---|
| **US-01** | Margaret | As a senior, I want to share a suspicious text with the app so I know if it is safe. | Verdict in < 3s with plain-language explanation and confidence level. |
| **US-02** | Margaret | As a senior, I want to speak my question aloud and have the app analyze it. | Voice transcribed and analyzed; result read aloud. |
| **US-03** | David | As a professional, I want to hover over a link and see a safety rating before clicking. | Tooltip in < 1.5s with trust score, domain age, confidence. |
| **US-04** | David | As a professional who clicked a bad link, I want the app to tell me exactly what to do. | Recovery checklist generated in < 5 seconds. |
| **US-05** | Priya | As a parent, I want alerts when my child encounters a high-risk link. | Push notification to parent in < 30 seconds. |
| **US-06** | Priya | As a parent, I want to remotely trigger recovery guidance on my child's device. | Recovery steps appear on child device in < 60 seconds. |
| **US-07** | Any User | As a user who clicked a bad link, I want a recovery process tailored to the threat type. | Personalized checklist based on triage answers. |
| **US-08** | Any User | As a user, I want to see how confident the app is, and what could happen if I proceed. | Confidence level and consequence summary displayed with verdict. |
| **US-09** | Any User | As a user getting a suspicious bank message, I want the app to tell me a safe alternative action. | Safe action suggestion displayed (e.g., "Open your banking app directly"). |
| **US-10** | Any User | As a user, I want to scan a QR code before visiting the destination. | Camera QR scan extracts URL and returns verdict. |
| **US-11** | Any User | As a user who received a threatening email demanding Bitcoin payment, I want the app to tell me if it's a real threat or a bluff so I don't pay unnecessarily. | Sextortion/blackmail pattern detected; verdict explains these are mass-sent bluffs; recovery guidance provided. |
| **US-12** | Any User | As a user who has been chatting with someone online who is now asking me to invest, I want the app to analyze the conversation pattern so I know if it's a scam. | Pig butchering pattern detected from message screenshots or pasted text; consequence warning and recovery steps provided. |

### 5.2 Key Use Case Flows

#### Flow 1: Share-to-Check (Mobile)

User receives suspicious SMS → long-presses → Share → "Can I Click It?" → app analyzes → verdict with confidence level, consequence warning, and safe action suggestion within 3 seconds.

#### Flow 2: Voice Check (Mobile)

User taps microphone → describes message aloud → app transcribes, identifies scam pattern → reads verdict aloud with safe alternative action.

#### Flow 3: "I Already Clicked It" Emergency Recovery

User taps "I Already Clicked Something Bad" → quick triage questions → personalized recovery checklist with one-tap bank calling → optional family alert.

#### Flow 4: Hover-to-Check (Browser Extension)

User hovers over link → extension overlay shows domain age, reputation, confidence → dangerous links trigger warning interstitial with recovery option if user already clicked.

---

## 6. Feature Requirements

### 6.1 MVP Features (v1.0)

#### 6.1.1 Core Detection

| ID | Feature | Priority | Input |
|---|---|---|---|
| **F-01** | Text/Message Analysis with intent detection | P0 — Must Have | Text paste, share sheet |
| **F-02** | Link Scanning: domain reputation, redirects, typosquatting, hosting risk | P0 — Must Have | Paste URL, share sheet |
| **F-03** | Screenshot Intelligence: OCR for text, logos, URLs, UI spoofing | P0 — Must Have | Camera roll, share |
| **F-04** | QR Code Scanning with automatic URL analysis | P0 — Must Have | Device camera |
| **F-05** | Verdict Engine with Confidence Meter (High/Medium/Low) | P0 — Must Have | Output |
| **F-06** | Consequence Warning: "If this is a scam and you proceed, here is what could happen" | P0 — Must Have | Output |
| **F-07** | Safe Action Suggestions: positive alternative actions (e.g., "Open your banking app directly") | P0 — Must Have | Output |
| **F-08** | Emergency Confidence Override: low-confidence verdicts default to Suspicious with safety bias | P0 — Must Have | System logic |
| **F-09** | Scam Coaching: contextual education explaining the detected scam pattern | P1 — Should Have | Output |
| **F-10** | Scan History: local log of past scans with outcomes | P1 — Should Have | Local storage |

#### 6.1.2 Emergency Recovery

| ID | Feature | Priority | Trigger |
|---|---|---|---|
| **F-11** | "I Already Clicked It" Button: prominent emergency entry on home screen | P0 — Must Have | Manual tap |
| **F-12** | Threat Triage Questionnaire: 3–4 questions classifying what happened | P0 — Must Have | Guided flow |
| **F-13** | Personalized Recovery Checklist: step-by-step remediation ordered by urgency | P0 — Must Have | Auto-generated |
| **F-14** | Recovery Action Library: category-specific guides (credential theft, financial fraud, identity theft, malware, gift card scam, remote access, blackmail/sextortion, ransomware, pig butchering/romance-investment) | P0 — Must Have | Content library |
| **F-15** | Quick-Dial Emergency Contacts: one-tap calling for bank, credit card, fraud agency | P1 — Should Have | Contact lookup |
| **F-16** | Family Alert on Recovery: push notification to linked family members | P1 — Should Have | Push notification |

#### 6.1.3 Accessibility and Ease of Use

| ID | Feature | Priority | Input |
|---|---|---|---|
| **F-17** | Voice Input: describe suspicious message verbally; transcription feeds analysis | P1 — Should Have | Microphone |
| **F-18** | Read Aloud Results: TTS for verdicts and recovery steps | P1 — Should Have | TTS output |
| **F-19** | Grandma Mode: one oversized button, giant text, no menus, voice-first | P1 — Should Have | Settings toggle |

#### 6.1.4 Browser Extension

| ID | Feature | Priority | Browsers |
|---|---|---|---|
| **F-20** | Link Hover Analysis with confidence level | P0 — Must Have | Chrome, Safari, Edge, FF |
| **F-21** | Page Trust Score for current webpage | P0 — Must Have | All |
| **F-22** | Fake Login Detection via visual similarity matching | P1 — Should Have | All |
| **F-23** | Warning Interstitial with "What do I do now?" recovery guidance | P1 — Should Have | All |
| **F-24** | Checkout Fraud Detection for fake storefronts | P2 — Nice to Have | All |

### 6.2 Post-MVP Features (v2.0+)

| ID | Feature | Release | Category | Priority |
|---|---|---|---|---|
| **F-25** | Family Guardian Dashboard with remote recovery trigger | v2.0 | Family Safety | P0 |
| **F-26** | Real-Time Background Monitoring with proactive alerts | v2.0 | Premium | P1 |
| **F-27** | Contact Impersonation Detection | v2.0 | AI Detection | P1 |
| **F-28** | Scam Replay Education: anonymized campaign examples | v2.0 | Education | P2 |
| **F-29** | Attachment Sandbox Analysis | v2.5 | Detection | P1 |
| **F-30** | Voice Message Analysis for social engineering | v2.5 | AI Detection | P1 |
| **F-31** | Call Screening AI for scam and robocall detection | v3.0 | Premium | P0 |
| **F-32** | Deepfake Voice Detection during calls | v3.0 | AI Detection | P1 |
| **F-33** | Dark Web Monitoring for breach alerts | v3.0 | Identity | P1 |
| **F-34** | Transaction Verification before payment execution | v3.0 | Financial | P2 |
| **F-35** | On-Device Lightweight Model for offline and privacy-first scanning | v2.5 | Platform | P2 |

---

## 7. Emergency Recovery System

The emergency recovery system addresses the unserved gap between "I made a mistake" and "I know exactly what to do." No competing product provides guided, personalized, post-incident recovery for consumers. This feature is expected to be a major driver of trust, word-of-mouth growth, and premium conversion.

### 7.1 Triage Classification

| What Happened | Threat Category | Risk Level |
|---|---|---|
| I tapped a link in a message | Potential phishing / malware | Medium |
| I entered my password on a site | Credential theft | High |
| I entered credit card or bank info | Financial fraud | Critical |
| I downloaded a file or app | Malware / spyware | High |
| I gave personal info (SSN, DOB) | Identity theft | Critical |
| I sent money, gift cards, or crypto | Financial loss | Critical |
| I gave remote access to my device | Full device compromise | Critical |
| I received a threatening email saying they have my data or footage and demanding payment | Blackmail / sextortion scam | Medium |
| I received an email claiming my files are encrypted and demanding ransom | Ransomware extortion email | High |
| I've been chatting with someone online who is now asking me to invest money | Pig butchering / romance-investment scam | High |
| I'm not sure what happened | Unknown — general guidance | Medium |

### 7.2 Recovery Checklists

Each category triggers a prioritized, step-by-step checklist. Steps are revealed one at a time to reduce cognitive overload. Each step includes a "Help me with this" expansion for additional detail. Full recovery content for all ten categories is specified in Appendix B.

#### Blackmail / Sextortion Email Recovery

When a user reports receiving a threatening email demanding payment in exchange for not releasing personal data, compromising photos, or browsing history:

1. **Do not pay.** These emails are almost always mass-sent bluffs. The sender typically does not have the data or footage they claim. Paying encourages further extortion and does not guarantee the threats will stop.
2. **Do not reply or engage** with the sender in any way. Any response confirms your email is active and may lead to escalated demands.
3. **Check if a password was included in the email.** If so, it likely came from an old data breach. Change that password immediately on any account where you still use it.
4. **Enable two-factor authentication** on your email and any accounts referenced in the message.
5. **Mark the email as spam/phishing** in your email client to help train filters.
6. **Report the email** to the FTC (reportfraud.ftc.gov) and the FBI's IC3 (ic3.gov) if financial demands were made.
7. **If you already paid,** contact your bank or payment provider immediately. If you paid via cryptocurrency, file a report but be aware recovery is unlikely.

#### Ransomware Extortion Email Recovery

When a user reports receiving an email claiming their device or files have been encrypted and demanding ransom payment:

1. **Do not pay the ransom.** Payment does not guarantee file recovery and funds criminal operations.
2. **Verify the claim.** Many ransomware emails are bluffs with no actual encryption. Check whether you can still access your files normally. If your files open fine, the email is a scam — delete it.
3. **If files are actually encrypted:** Disconnect the affected device from Wi-Fi and all networks immediately to prevent spread.
4. **Do not attempt to decrypt files yourself** using unknown tools, as some are themselves malware.
5. **Check No More Ransom** (nomoreransom.org) — a free, legitimate resource with decryption tools for many known ransomware strains.
6. **Report the incident** to the FBI's IC3 (ic3.gov) and your local law enforcement.
7. **Restore files from backup** if available. If you do not have backups, consult a professional data recovery service.
8. **After recovery,** run a full device scan, update all software, and establish a regular backup routine.

#### Pig Butchering / Romance-Investment Scam Recovery

When a user reports an ongoing relationship with someone online — typically met through dating apps, social media, or messaging platforms — who has encouraged them to invest money through a specific platform or method:

1. **Stop all further payments immediately.** No matter what the other person says, do not send any additional money. Claims that "one more payment will unlock your funds" are part of the scam.
2. **Accept that the relationship is likely part of the scam.** This is difficult but important. Pig butchering scams deliberately build emotional trust over weeks or months before introducing the investment component. The person you have been communicating with is almost certainly not who they claim to be.
3. **Document everything:** Save all messages, transaction records, screenshots of the investment platform, and any contact details for the other person.
4. **Contact your bank or financial institution** to report the transactions. Some transfers may be reversible depending on timing and method.
5. **Report the scam** to the FTC (reportfraud.ftc.gov), the FBI's IC3 (ic3.gov), and your state attorney general's office.
6. **Report the fraudulent investment platform** to the SEC (sec.gov/tcr) or CFTC if cryptocurrency was involved.
7. **Report the scammer's profile** on the dating app or social media platform where you met them.
8. **Be wary of "recovery scams."** After being scammed, victims are often targeted by people claiming they can recover lost funds for a fee. These are also scams.
9. **Consider speaking with a counselor or support group.** Pig butchering victims often experience significant emotional distress. AARP's fraud helpline (877-908-3360) provides free support.

### 7.3 Recovery UX Design

- **Tone:** "Don't worry — let's fix this together." Calming, action-oriented, never blaming.
- **Cognitive Load:** One step at a time. User taps "Done" to reveal the next step. Progress bar at top.
- **Quick-Dial:** Persistent "Call for Help" button for one-tap calling to bank or fraud hotline.
- **Family Alert:** Optional push notification to linked family members with summary.
- **Disclaimers:** Each recovery screen includes: "This guidance is informational and not a substitute for professional security or legal advice."

---

## 8. Psychological Design Framework

Security products typically fail at the psychological level: they increase anxiety, use jargon, or shame users for mistakes. This product takes a deliberately different approach, informed by behavioral science research on decision-making under uncertainty.

### 8.1 Panic Reduction

When users realize they may have been scammed, their first reaction is panic. Panic causes delayed action, irrational decisions, and shame-driven avoidance. The product's emergency recovery flow is designed to interrupt the panic cycle with a calm, authoritative, step-by-step process. The opening message — "Don't worry, let's fix this together" — establishes a co-pilot dynamic rather than an alarm.

### 8.2 Decision Simplification

The product reduces complex security judgments to a single, color-coded answer. Users never need to evaluate multiple factors or understand threat categories. The verdict screen presents exactly one recommended action. For ambiguous cases, the safe action bias ensures the product recommends caution, not analysis.

### 8.3 Embarrassment Removal

People hesitate to ask others "Is this a scam?" because they fear looking foolish. The app removes this social barrier entirely. It is a private, non-judgmental advisor available 24/7. This single psychological insight is expected to be one of the strongest adoption drivers, particularly among seniors and less technical users.

### 8.4 Consequence Awareness

When the system detects a threat, it does not stop at a warning label. It tells the user what could happen if they proceed:

- "If this is a phishing site and you enter your password, someone could access your email and any accounts linked to it."
- "If you send money via gift cards, it cannot be recovered. Legitimate companies never request payment this way."
- "This looks like a sextortion scam. These emails are almost always bluffs — the sender likely does not have what they claim. Do not pay or respond."
- "This person may be building trust to eventually ask you to invest money. This pattern matches a common romance-investment scam. Never invest through a platform recommended by someone you have only met online."
- "This email claims your files are encrypted, but many of these are bluff emails. Check whether you can still open your files before taking any action."

This consequence framing activates loss aversion — the most powerful behavioral bias — and significantly increases the likelihood that users heed the warning.

### 8.5 Safe Action Suggestions

Instead of only telling users what not to do, the product tells them what to do instead. This is a critical UX pattern that converts a blocking moment into a constructive one:

- "If this claims to be your bank, open your banking app directly instead of clicking the link."
- "If this claims a package is waiting, go to the carrier's website by typing the URL yourself."
- "If someone claims to be a family member, call them at their known phone number to verify."

Safe action suggestions transform the product from a "no" into a "do this instead" — dramatically improving user satisfaction and compliance.

### 8.6 Cognitive Load Reduction

Every screen in the product follows a single-action principle. No screen presents more than one decision. Recovery checklists reveal one step at a time. The verdict screen shows one color, one icon, one sentence. Grandma Mode eliminates all navigation. This approach respects the cognitive constraints of users in stressful, uncertain moments.

---

## 9. AI and ML Intelligence Layer

### 9.1 Intent Detection (Core Differentiator)

> *Most tools analyze artifacts. We analyze intent.*

Traditional tools check URLs against blocklists or files for malware signatures. These fail against novel attacks. The analysis engine evaluates the communicative intent of the entire message: is it trying to create urgency or fear? Is it impersonating someone trusted? Does it ask for an unusual action? This is where the product wins against Norton, Bitdefender, and Google.

**Example:** "Hey mom, I lost my phone — this is my new number, can you send $200?" contains no malicious link. Traditional tools pass it as safe. Intent detection identifies the impersonation pattern, urgency, and financial request as high-confidence social engineering.

### 9.2 Multi-Signal Framework

#### Content Analysis

- LLM-based phishing intent classification on curated phishing corpora.
- Urgency language detection: deadlines, suspension threats, limited-time offers.
- Emotional manipulation scoring: fear, greed, curiosity, authority exploitation.
- Impersonation pattern matching: bank, IRS, shipping, tech support, family templates.
- Pig butchering / romance-investment detection: identifying patterns of escalating trust-building followed by financial requests, fake investment platform references, and urgency around "limited-time" opportunities.
- Blackmail and sextortion template detection: identifying mass-sent extortion emails referencing old breach passwords, threatening language, and cryptocurrency payment demands.
- Ransomware extortion email classification: distinguishing real ransomware incidents from bluff emails that falsely claim file encryption.
- Multilingual: English, Spanish, French, Mandarin, Hindi, Portuguese at launch.

#### Link Analysis

- Domain reputation via VirusTotal, PhishTank, OpenPhish, URLhaus.
- Typosquatting detection: Levenshtein distance + homoglyph analysis vs top 10K domains.
- Domain age and WHOIS; newly registered domains flagged with elevated risk.
- Redirect chain traversal for cloaking and multi-hop obfuscation.
- SSL certificate analysis for mismatched or self-signed certificates.

#### Sender and Behavioral Context

- Contact spoofing detection against user's address book (with permission).
- Email header forensics: SPF, DKIM, DMARC validation.
- Industry heuristics: "Your bank does not request PINs via SMS."
- Brand pattern matching: "This shipping company does not use this domain."

### 9.3 Tiered AI Pipeline

| Tier | Latency | What Runs | When Used |
|---|---|---|---|
| **Fast Path** | < 500ms | Domain reputation, known campaigns, heuristics, blocklist | All scans (always runs first) |
| **ML Path** | 1–2s | Trained classifiers for phishing, intent, content | Fast path inconclusive or medium confidence |
| **LLM Reasoning** | 2–3s | Chain-of-thought analysis, explanation generation | ML ambiguous (score 40–70) or premium users |

60–70% of scans resolve on the fast path without LLM calls, controlling cost while preserving accuracy for ambiguous cases.

### 9.4 Confidence Scoring and Safety Bias

- **High Confidence:** Multiple independent signals agree. Displayed as solid certainty.
- **Medium Confidence:** Some signals flag risk, others inconclusive. "We're not fully certain — proceed with caution."
- **Low Confidence:** Limited signals available. System defaults to Suspicious (not Safe). "We don't have enough information to confirm this is safe. When in doubt, do not proceed."

The emergency confidence override ensures that insufficient data never produces a false sense of security. Low-confidence verdicts always default toward caution. This safe-action bias is a core product principle.

### 9.5 False Negative Mitigation Strategy

False negatives — marking dangerous content as safe — represent the product's most critical risk. The following layered strategy minimizes this exposure:

1. **Conservative Thresholds:** The decision boundary is calibrated to favor false positives over false negatives. A 5% false positive rate is acceptable; a 1% false negative rate is the hard ceiling.
2. **Safety-Biased Language:** Even Safe verdicts include soft guidance: "This appears safe, but always verify directly with the sender if you are unsure."
3. **Confidence-Gated Verdicts:** The system never issues a "Safe — High Confidence" verdict unless multiple independent signal categories agree. Single-signal Safe verdicts are capped at Medium confidence.
4. **When in Doubt, Suspicious:** Ambiguous cases (score 40–60) default to "Suspicious" with a recommendation to verify through alternative channels.
5. **Escalation Mode:** For scans that remain uncertain after LLM reasoning, the app prompts: "We could not determine this with certainty. We recommend treating it as suspicious and contacting the sender directly."
6. **Continuous Retraining:** A feedback loop where users report incorrect verdicts feeds a retraining pipeline, with misclassified false negatives receiving highest priority.
7. **Red Team Program:** Quarterly adversarial testing with external security researchers simulating novel attack vectors.

---

## 10. Platform Constraints and Mitigations

Mobile operating systems impose significant restrictions on inter-app communication, background processing, and data access. Underestimating these constraints is the most common cause of mobile security product failure. This section maps known restrictions to product mitigations.

### 10.1 iOS Constraints

| Constraint | Impact on Product | Mitigation |
|---|---|---|
| No direct SMS/iMessage access | Cannot proactively scan messages in background | Share sheet integration: user explicitly shares suspicious content to app. Compliant and proven (Norton Genie uses same pattern). |
| Clipboard access requires user consent (iOS 16+) | Cannot silently monitor copied URLs | In-app paste button with clear permission context. No background clipboard monitoring in v1. |
| No call interception API (CallKit is limited) | Call screening restricted to Caller ID-style features | Defer real-time call screening to v3.0; explore CallKit directory extension for known-scam number blocking. |
| App Extension sandbox limitations | Share extensions have limited memory and execution time | Lightweight client-side pre-processing; heavy analysis on server. |
| App Store content scanning policy | Apple may scrutinize content analysis capabilities | Pre-submission review consultation; position as user-initiated safety tool, not surveillance. Minimal permission requests. |
| No background execution for scanning | Cannot monitor incoming messages proactively | Notification-based reminders: "Got a suspicious message? Check it here." Push nudges after inactivity. |

### 10.2 Android Constraints

| Constraint | Impact on Product | Mitigation |
|---|---|---|
| SMS access requires DEFAULT_SMS permission | Proactive SMS scanning requires being default SMS app (users unlikely to switch) | Share sheet and accessibility service approach. Offer optional notification listener with explicit consent for premium. |
| Google Play Protect overlap | Google may flag features as duplicative or restrict functionality | Position as complementary to Play Protect. Focus on intent detection and recovery, which Play Protect does not offer. |
| Background execution limits (Android 12+) | Doze mode and app standby restrict background processing | Use WorkManager for deferred scans; foreground service with notification for real-time monitoring (premium). |
| WhatsApp / Telegram sandboxing | Cannot read messages inside third-party apps | Share sheet integration; screenshot analysis as fallback. |
| Scoped storage (Android 11+) | Limited file system access for attachment scanning | Use Storage Access Framework with explicit user selection; process files via temporary content URI. |

### 10.3 Browser Extension Constraints

| Constraint | Impact on Product | Mitigation |
|---|---|---|
| Manifest V3 (Chrome) limits background scripts | Service workers replace persistent background pages | Use Chrome alarms API and event-driven architecture. |
| Safari Web Extension sandboxing | More restrictive than Chrome; limited APIs | Feature parity may lag Chrome by 1–2 releases; prioritize Chrome at launch. |
| Content Security Policy restrictions | Some sites block injected scripts (e.g., banking sites) | Graceful degradation: extension icon badge shows risk score when overlay injection fails. |
| Cross-origin request limitations | Cannot fetch URL metadata from extension context directly | Route all analysis through backend API; extension sends URL only. |

---

## 11. Technical Architecture

### 11.1 Architecture Layers

| Layer | Components | Technology | Hosting |
|---|---|---|---|
| **Client** | iOS, Android, Browser Extensions | Swift/Kotlin, TypeScript | App/Web Stores |
| **API Gateway** | Auth, rate limiting, routing | AWS API Gateway / Cloudflare | AWS |
| **Analysis Engine** | Tiered pipeline, verdict + recovery | Python / FastAPI, Ray Serve | AWS ECS/EKS |
| **Intelligence** | Link Intel, Threat Feeds, LLM, RAG, Recovery Content | PostgreSQL, Redis, Elasticsearch, Anthropic API | AWS RDS |
| **Data** | Campaign clustering, telemetry, retraining, scam corpus | Kafka, S3, Spark, MLflow | AWS S3/EMR |

### 11.2 Performance Requirements

| Metric | MVP Target | v2.0 Target |
|---|---|---|
| **Scan Latency (p95)** | < 3 seconds | < 2 seconds |
| **Screenshot Scan (p95)** | < 5 seconds | < 3 seconds |
| **Recovery Checklist Gen** | < 5 seconds | < 3 seconds |
| **API Availability** | 99.5% | 99.9% |
| **False Positive Rate** | < 5% | < 2% |
| **False Negative Rate** | < 1% | < 0.5% |
| **Concurrent Users** | 10,000 | 100,000 |

---

## 12. Unit Economics and Cost Model

Understanding cost per scan is critical to pricing decisions, free tier limits, and infrastructure planning. The tiered AI pipeline directly controls unit economics by routing 60–70% of scans through low-cost paths.

### 12.1 Estimated Cost per Scan

| Scan Type | Fast Path Only | Fast + ML | Fast + ML + LLM | Blended Average |
|---|---|---|---|---|
| **Text/Link Scan** | $0.0005 | $0.003 | $0.02–$0.05 | $0.005–$0.01 |
| **Screenshot Scan** | $0.001 | $0.005 | $0.03–$0.07 | $0.008–$0.015 |
| **QR Code Scan** | $0.0005 | $0.003 | $0.02–$0.05 | $0.004–$0.008 |
| **Recovery Checklist** | N/A | N/A | $0.01–$0.03 | $0.01–$0.03 |

Estimates assume Anthropic API pricing for LLM calls (Haiku for fast reasoning, Sonnet for complex cases), cloud-hosted ML inference on GPU instances, and commercial threat intelligence feed licensing. Costs decrease significantly with volume-based pricing and fine-tuned model deployment.

### 12.2 Free Tier Cost Exposure

At 5 free scans per day with a blended cost of $0.008 per scan, a free user costs approximately $0.04/day or $1.20/month. With 50,000 free users, monthly infrastructure cost for the free tier is approximately $60,000. This is sustainable for a venture-backed company and is offset by:

- Premium conversion at 5% generates $34,950/month in subscription revenue (10,000 users at $6.99/month = $69,900; free tier cost is less than the revenue from a 3% conversion rate).
- Free users contribute to the data moat through anonymized scan telemetry.
- Free users drive viral growth through result sharing and word-of-mouth.

### 12.3 Cost Optimization Levers

- **Tiered routing:** Keeping 65% of scans on the fast path avoids LLM costs for clear-cut cases.
- **Result caching:** Hash-based caching for previously seen URLs reduces redundant analysis. Estimated 20–30% cache hit rate.
- **Fine-tuned small models:** Replace general-purpose LLM with fine-tuned smaller model for phishing classification (v2.0), reducing per-call cost by 80–90%.
- **Volume pricing:** Negotiate committed-use discounts with API providers at scale.
- **On-device inference:** Lightweight model for common patterns runs entirely on-device (v2.5), eliminating server costs for those scans.

---

## 13. Data Moat and Network Effects Strategy

Investors will ask: "What prevents Google from building this?" The answer is a compounding data advantage that becomes more defensible with every scan. The product's intelligence improves as usage grows, creating a virtuous cycle that late entrants cannot shortcut.

### 13.1 Learning Network Effects

- **Scam Corpus Growth:** Every user-submitted scan (with consent) contributes to the largest labeled scam dataset outside of law enforcement. This corpus trains better models and catches threats earlier.
- **Campaign Clustering:** The system groups related scam messages into campaigns (e.g., "fake USPS delivery wave targeting Northeast US"). Each new submission that matches a cluster strengthens detection for all users in that cluster.
- **Behavioral Fingerprinting:** Attack patterns (language style, URL structure, timing, targeting) are fingerprinted and tracked across campaigns. This allows detection of new scam variants from known actors before they appear in public threat feeds.
- **User Feedback Loop:** When users report incorrect verdicts ("This was actually safe" / "This was actually a scam"), the feedback enters a prioritized retraining pipeline, continuously calibrating the model.
- **Recovery Intelligence:** Patterns in post-incident recovery (which scams lead to financial loss, which lead to identity theft) inform risk scoring and consequence warnings for future users.

### 13.2 Data Flywheel

More users → more scans → larger corpus → better detection → fewer false negatives → more trust → more users. This flywheel accelerates with each phase of growth and creates a compounding advantage that is extremely difficult for new entrants to replicate, even with superior engineering resources.

### 13.3 Partnership Data Advantages

Telecom and banking partnerships provide access to threat signals unavailable to standalone products: carrier-level SMS metadata, known fraud phone numbers, bank-specific phishing campaign intelligence, and real-time transaction fraud patterns. These exclusive data channels widen the moat further.

---

## 14. Competitive Defense Narrative

The primary competitive threat is not from existing security vendors (Norton, Bitdefender) but from big tech (Google, Apple) building similar features natively. This section addresses why the product wins despite that risk.

### 14.1 Why Big Tech Is Unlikely to Build This

- **Misaligned incentives:** Google's primary revenue is advertising, which depends on users clicking links. A product that tells users not to click competes with Google's core business. Apple's incentives are more aligned, but Apple historically builds platform features, not standalone safety apps.
- **Cross-platform is antithetical:** Neither Google nor Apple will build a tool that works across the other's ecosystem. The product's cross-platform value requires platform neutrality.
- **Recovery is a service, not a feature:** Emergency recovery with guided checklists, quick-dial contacts, and family alerting is a product category, not a feature toggle. Big tech builds features; this is a relationship.
- **Senior UX requires focus:** Building Grandma Mode, voice-first interaction, and age-appropriate design requires dedicated design investment that does not fit big tech's universal design approach.

### 14.2 Why We Win Against Existing Security Vendors

- **Cross-channel unification:** Norton Genie is app-only with no browser extension. Bitdefender Scamio is chat-based with no screenshot intelligence. No vendor covers SMS, email, browser, QR, and screenshots in one product.
- **Intent detection:** Existing vendors rely on artifact analysis (URL blocklists, file signatures). We analyze the intent of the message itself, catching social engineering that has no malicious artifact.
- **Emergency recovery:** No competitor offers post-incident guidance. This is a category-defining feature.
- **Data moat:** Our scam corpus and campaign clustering improve with every scan. Legacy vendors rely on static threat databases.
- **Partnership positioning:** Banks and carriers want to embed a standalone, brand-neutral tool. They will not embed a Norton or Bitdefender product that competes with their own security offerings.

### 14.3 Competitive Moat Summary

| Moat Type | Description | Defensibility Timeline |
|---|---|---|
| **Data Network Effects** | Scam corpus, campaign clustering, and user feedback loops compound with usage | Strengthens monthly; meaningful after 6 months |
| **Partnership Exclusivity** | Carrier/bank integrations with data-sharing agreements | 12–18 months to establish; multi-year contracts |
| **Brand Trust** | First-mover in "personal AI security assistant" category | Builds over 12+ months; hard to replicate |
| **Senior Community** | Word-of-mouth adoption through family networks | Viral within 6 months; high switching cost |
| **Recovery Content** | Expert-reviewed, category-specific recovery library | 6 months to build comprehensively; easy to copy but hard to trust |

---

## 15. Privacy and Security

> *We analyze threats, not your life.*

### 15.1 Privacy Principles

1. **Ephemeral Processing:** User content analyzed in memory, discarded after verdict. No message storage by default.
2. **On-Device Redaction:** PII optionally redacted client-side before transmission.
3. **No Content Logging:** Server logs record metadata only (timestamp, scan type, verdict), never content.
4. **Opt-In Analytics:** Anonymized threat telemetry contributed only with explicit consent.
5. **Transparent Policy:** Plain-language privacy policy at or below 8th-grade reading level.

### 15.2 Data Handling

| Data Type | Stored? | Duration | Encryption |
|---|---|---|---|
| Message Content | No (ephemeral) | In-memory only | TLS in transit; AES-256 if opt-in |
| URLs / Domains | Hashed only | 30 days cache | SHA-256 hash |
| Screenshots | No (ephemeral) | Deleted after analysis | TLS in transit |
| Recovery Interactions | Yes (local + opt-in) | 90 days | AES-256 at rest |
| Scan Metadata | Yes | 12 months | AES-256 at rest |

---

## 16. Liability and Legal Architecture

This product provides security-related guidance that touches financial loss, identity theft, and personal safety. The legal architecture must clearly establish the product as an advisory tool while protecting against liability exposure from false negatives and recovery advice.

### 16.1 Product Classification

The product is classified as a **consumer advisory tool**, not a security product or professional service. This distinction is critical:

- **Advisory, not guaranteeing:** The product provides information to help users make decisions. It does not guarantee safety or claim to prevent all threats.
- **Informational, not professional advice:** Recovery guidance is general consumer education, not professional cybersecurity, legal, or financial advice.
- **Assistive, not automated:** The product assists user judgment; it does not take autonomous action on the user's behalf (no auto-blocking, no auto-reporting without consent).

### 16.2 In-Product Disclaimers

Disclaimers are embedded directly in the product UI at key decision points, not buried in Terms of Service:

- **Verdict screen:** "This analysis is our best assessment based on available signals. Always verify directly with the sender if you are unsure."
- **Safe verdict:** "This appears safe based on our analysis, but no system can guarantee 100% accuracy."
- **Recovery screen:** "This guidance is informational and not a substitute for professional security or legal advice. Contact your bank or a security professional for complex situations."
- **Family alerts:** "Alerts are provided as a courtesy. They do not replace parental supervision or direct communication."

### 16.3 Terms of Service Architecture

- **Limitation of Liability:** Explicit cap on liability for false negatives and false positives. The product is "as-is" advisory software.
- **No Guarantee of Safety:** Clear statement that no security tool can detect all threats and that the user bears responsibility for their actions.
- **Recovery Guidance Disclaimer:** Recovery steps are general guidance; users are advised to consult professionals for financial, legal, or identity theft situations.
- **User Responsibility:** Users are responsible for verifying information and taking appropriate action. The product assists but does not replace judgment.

### 16.4 Insurance Considerations

- **Errors and Omissions (E&O) Insurance:** Required before launch. Covers claims arising from incorrect verdicts or recovery guidance. Estimated $5,000–$15,000/year for a startup-stage policy.
- **Cyber Liability Insurance:** Covers data breaches involving user information. Required given the sensitivity of scan content in transit.
- **General Liability:** Standard business coverage for product liability claims.

### 16.5 Regulatory Compliance

- GDPR, CCPA/CPRA, PIPEDA, LGPD: data protection compliance before expansion to respective markets.
- COPPA: parental consent flow for accounts covering children under 13.
- ADA / WCAG 2.1 AA: accessibility compliance.
- FCC review for telecom partnership integrations.
- Consumer protection: use "designed to help identify" language, never "guaranteed protection."
- Trademark: file for "Can I Click It?" and "Grandma Mode" before public launch.

---

## 17. Monetization Strategy

### 17.1 Consumer Freemium

| Feature | Free Tier | Premium ($6.99/mo) |
|---|---|---|
| **Daily Scans** | 5 per day | Unlimited |
| **Detection Quality** | Fast + ML path | Full LLM reasoning |
| **Emergency Recovery** | Basic checklist (always free) | Personalized + quick-dial + family alert |
| **Voice / Read Aloud / Grandma Mode** | Included | Included |
| **Browser Extension** | Basic link checking | Full hover + login detection |
| **Family Protection** | Not included | Up to 5 accounts |
| **Real-Time Monitoring** | Not included | Background monitoring |
| **Dark Web Monitoring** | Not included | Breach alerts |

Annual: $59.99/year (29% discount). Family plan: $9.99/month for up to 5 members.

Note: basic emergency recovery remains free for all users. Helping someone who has already been scammed should never be paywalled.

### 17.2 Partnership Revenue

- **Mobile Carriers:** White-label integration; $0.50–$2.00/subscriber/month.
- **Banks:** Embedded scam detection for customers; enterprise licensing with SLA.
- **Insurance:** Cyber insurance risk-reduction bundling.
- **Senior Services:** AARP, elder care platforms; group licensing.

---

## 18. Go-to-Market Strategy

### 18.1 Phase 1: Consumer Trust (Months 1–4)

- Launch iOS + Android with free tier and premium.
- Target: seniors (via adult children who install), parents, professionals.
- Viral loop: "Share result" forwards verdicts to contacts.
- ASO: "scam checker," "is this a scam," "phishing detector," "link safety."
- PR: Grandma Mode as a media story.

### 18.2 Phase 2: Media Narrative (Months 3–6)

- Narrative: "AI scams are rising — this protects you."
- Press: TechCrunch, Wired, AARP Magazine, local news.
- Monthly "Scam Trends Report" using anonymized data for earned media.
- Emergency recovery testimonials for human-interest coverage.

### 18.3 Phase 3: Partnerships (Months 6–12)

- Banks: pitch tied to fraud loss reduction metrics.
- Carriers: white-label or pre-install distribution.
- Insurance: customer premium discount for app usage.
- AARP / senior networks for group licensing.

---

## 19. Success Metrics and KPIs

| Metric | Definition | 6-Month Target | 12-Month Target |
|---|---|---|---|
| **Monthly Active Users** | Unique users with 1+ scan/mo | 30,000 | 100,000 |
| **Daily Scans / User** | Avg scans per active user/day | 1.5 | 2.5 |
| **Scan Latency (p95)** | Submission to verdict | < 3s | < 2s |
| **Detection Accuracy** | (TP + TN) / total | > 95% | > 98% |
| **False Negative Rate** | Dangerous marked Safe | < 1% | < 0.5% |
| **Recovery Usage** | % users using recovery | 5% | 10% |
| **Recovery Completion** | % completing all steps | 60% | 75% |
| **NPS** | Net Promoter Score | > 40 | > 55 |
| **Free-to-Paid** | Conversion in 30 days | 3% | 5% |
| **Premium Churn** | Monthly cancellations | < 8% | < 5% |

---

## 20. MVP Development Roadmap

| Phase | Timeline | Deliverables | Team |
|---|---|---|---|
| **1** | Weeks 1–2 | Architecture; AI model selection; UX wireframes; user research with seniors; recovery content authoring; legal review | Eng, Design, ML, Content, Legal |
| **2** | Weeks 3–6 | Backend pipeline; tiered AI routing; link intel; LLM verdict + confidence; recovery engine; safe action suggestions; API | Backend, ML |
| **3** | Weeks 5–8 | Mobile app: text, link, screenshot, QR, voice; share sheet; recovery flow; Grandma Mode; consequence warnings | Mobile, Design |
| **4** | Weeks 6–9 | Browser extension: Chrome first; hover analysis, page trust, warning interstitial with recovery | Frontend |
| **5** | Weeks 9–11 | Integration testing; security audit; usability with seniors; accessibility audit; E&O insurance; legal finalization | QA, Security, Legal |
| **6** | Week 12 | Beta launch (TestFlight + Chrome); feedback; launch prep | All |

---

## 21. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **R-01** | False negatives cause user harm | Medium | Critical | Conservative thresholds; confidence gating; safety-biased language; retraining on misclassified samples; red team program |
| **R-02** | False positives erode trust | Medium | High | Track FP rates; user feedback loop; "Report incorrect" option; threshold tuning by category |
| **R-03** | Adversarial evasion by attackers | High | High | Ensemble models; diverse signals; quarterly red-teaming; threat feed integration |
| **R-04** | Privacy concerns deter adoption | Medium | High | Ephemeral processing; plain-language privacy; on-device-only option |
| **R-05** | LLM cost escalation at scale | High | Medium | Tiered pipeline (65% fast path); fine-tuned models; caching; volume pricing |
| **R-06** | App store rejection | Low | High | Pre-submission consultation; minimal permissions; advisory tool positioning |
| **R-07** | Platform constraints block key features | Medium | High | Share-sheet-first architecture; see Section 10 for full mitigation map |
| **R-08** | Liability from incorrect recovery advice | Low | High | In-UI disclaimers; E&O insurance; recovery content reviewed by professionals |
| **R-09** | Google/Apple build native equivalent | Medium | High | Cross-platform moat; recovery feature; data network effects; partnership exclusivity; see Section 14 |
| **R-10** | Competitor response from Norton/Bitdefender | High | Medium | Speed to market; recovery + senior UX as differentiators; partnership moats |

---

## 22. Open Questions for Stakeholder Resolution

1. Should MVP include a web-only mode (no install) for maximum initial reach?
2. What is the acceptable blended cost per scan? Current estimate is $0.005–$0.01 for text/link. Confirm budget ceiling.
3. Should Grandma Mode be a separate App Store listing (simpler discovery) or a mode within the main app?
4. Should advanced recovery features (quick-dial, family alert) be premium, or should all recovery be free?
5. For family protection, what is the minimum age for independent use vs. parental oversight?
6. Should partnerships be pursued pre-launch (for distribution) or post-launch (with traction data)?
7. Should the product report confirmed scams to national fraud databases (FTC, Action Fraud)?
8. Should the on-device lightweight model be part of MVP or deferred to v2.5?
9. What E&O insurance coverage level is required at launch? Obtain quotes during Phase 1.

---

## 23. Appendices

### Appendix A: Glossary

| Term | Definition |
|---|---|
| **Intent Detection** | Analysis of whether a message is designed to manipulate the recipient, beyond checking for malicious artifacts. |
| **PASA** | Personal AI Security Assistant: the product category this product defines. |
| **Grandma Mode** | Radically simplified interface: one button, giant text, voice-first, no menus. |
| **Confidence Meter** | High/Medium/Low indicator of system certainty in its verdict. |
| **Safe Action Suggestion** | A constructive alternative action (e.g., "Open your banking app directly") presented alongside warnings. |
| **Consequence Warning** | Plain-language description of what could happen if the user proceeds with a suspicious interaction. |
| **Emergency Confidence Override** | System rule that defaults low-confidence verdicts to Suspicious rather than Safe. |
| **Typosquatting** | Registering misspellings of popular domains to deceive users. |
| **RAG** | Retrieval-Augmented Generation: AI technique combining LLM with searchable knowledge base. |
| **Data Flywheel** | Virtuous cycle where more usage improves detection, which drives more usage. |
| **Pig Butchering** | A long-con scam where the attacker builds an emotional relationship (often romantic) over weeks or months, then persuades the victim to "invest" money through a fraudulent platform. Named because the victim is "fattened" with trust before being "slaughtered" financially. |
| **Sextortion / Blackmail Scam** | An email-based scam claiming to have compromising data or footage of the recipient and demanding payment (usually cryptocurrency) to prevent release. Almost always a mass-sent bluff using passwords from old data breaches for credibility. |
| **Ransomware** | Malware that encrypts a victim's files and demands payment for the decryption key. Ransomware extortion emails may be genuine incidents or bluff emails falsely claiming encryption. |

### Appendix B: Recovery Content Categories

| Category | Trigger | Key Actions | Urgency |
|---|---|---|---|
| Credential Theft | Entered password on bad site | Change passwords, enable 2FA, check activity | High |
| Financial Fraud | Shared bank or card details | Call bank, freeze card, monitor, FTC report | Critical |
| Identity Theft | Shared SSN, DOB, gov ID | Credit freeze, FTC, SSA, monitor 90 days | Critical |
| Malware / Download | Downloaded suspicious file | Disconnect, delete, scan device, safe mode | High |
| Gift Card / Wire | Sent money via gift card, wire, crypto | Contact issuer, police report, FTC | Critical |
| Remote Access | Gave device remote access | Disconnect, change all passwords, factory reset | Critical |
| General / Unknown | Unsure what happened | Change key passwords, monitor, enable 2FA | Medium |
| Blackmail / Sextortion | Received threatening email demanding payment | Do not pay or reply, change breached passwords, enable 2FA, report to FTC/IC3 | Medium |
| Ransomware Extortion Email | Email claims files encrypted, demands ransom | Verify claim (check files), do not pay, check nomoreransom.org, report to IC3, restore from backup | High |
| Pig Butchering / Romance-Investment | Online contact encouraging investment | Stop payments, document everything, contact bank, report to FTC/IC3/SEC, beware recovery scams | Critical |

### Appendix C: Brand Names

"Can I Click It?" remains the primary recommendation: memorable, approachable, and immediately communicates purpose. Alternatives for trademark research: SafeClick, TrustTap, ClickSafe, ScamShield, LinkGuardian, SureClick.

---

*End of Document*