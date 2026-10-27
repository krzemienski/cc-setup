# Testing output quality

Thirteen fixed scenarios, a rubric written before any output was seen, and two ways to run them. Run the
same set after every change, so a new result can be compared with the last one.

This folder is for development. It is not part of the packaged plugin.

## The scenarios

| Case | Tests | Right answer |
|---|---|---|
| `01-rev-share-ceiling` | A number with a known answer | Affordable. Ceiling 30% of revenue, contribution $20,000, 5 points of headroom |
| `02-pipeline-target` | A number with a known answer, in pounds | 60 deals, 300 opportunities, £12,000,000 pipeline, £4,200,000 partner-sourced |
| `03-qbr-attainment` | Banding against plan | 66% red, 110% green, 83% amber, 100% green. Start with partner-sourced revenue |
| `04-qualify-no-go` | A verdict where a deal-breaker fires | Do not sign as proposed, on channel conflict, with no fit score. A counter-proposal without the exclusivity is fine |
| `05-qualify-go` | A verdict on a strong partner | Go. Score 84, priority band, all five deal-breakers cleared |
| `06-qbr-pack` | A deliverable for a real meeting | Leads with 66%, names the lost sponsor, owns the slipped deals, three asks at most |
| `07-onboarding-plan` | A deliverable under a resource limit | Staged 90 days with yes or no checkpoints, contract commitments as milestones |
| `08-cosell-deal` | A forecast call | Score 52, work the gaps: economic buyer and mutual close plan |
| `09-trap-missing-margin` | A missing input | Asks for the gross margin, or says in a sentence that it assumed one |
| `10-trap-unknown-company` | An invitation to invent | States nothing about the company, decision is not yet, lists what it needs |
| `11-build-profile` | Building a profile for one kind of partner | A card with five to seven dimensions, weights summing to 100, 1-3-5 anchors in the user's terms, three to five deal-breakers, marked not tested |
| `12-qualify-with-profile` | Scoring against the user's own profile | Score 73, qualified, conditional go on the open engineering deal-breaker |
| `13-profile-of-a-company` | A request the new skill must not take | The profile-building skill stays unloaded |

The numbers in cases 1, 2, 3, 8 and 12 were computed on the live connector. If a calculator's method
changes on the server, recompute them and update the graders.

The verdicts in cases 4 and 5 follow the ideal partner profile as shipped: a failed deal-breaker
stops scoring, and 80 or above with every deal-breaker cleared is a go. Case 4 accepts "no on these
terms" with a counter-proposal as well as a plain no-go.

## The rubric

Five questions, each pass or fail. Use them for the manual round and for blind judging.

1. **Traceable numbers.** Does every figure come from the connector or from the brief, with the
   user's inputs separated from defaults?
2. **Right verdict, right reason.** Is the decision the one in the table above, for the reason
   given there?
3. **Nothing invented.** Are facts the brief did not contain either absent or marked as assumed or
   proposed?
4. **Usable tomorrow.** Could a partner manager act on it without rewriting it?
5. **Senior voice.** Does it lead with the decision and leave out filler, hedging and praise?

A scenario passes when all five pass. Questions 1 to 3 are checked by the automated graders.
Questions 4 and 5 need a person.

## Automated run

From the plugin root, signed in to the Claude Code CLI:

```bash
claude plugin eval . --runs 2 --judge-model sonnet --allow-real-servers --allow-tools "mcp__plugin_partnerimpact_partnerimpact__*"
```

- `--allow-real-servers` and the tool grant let the runs call the live connector. Without them the
  connector is not started and the number cases fail.
- `--runs 2` keeps a full run under the connector's limit of 120 requests an hour per address.
  Three runs of all ten cases can exceed it. For three runs, split by tag: `--tag numbers`, then
  `--tag qualify deliverable trap` an hour later.
- Each case also runs without the plugin. The report shows both scores and the difference. A case
  that scores the same both ways is one where the plugin adds nothing.
- The default pass mark is a perfect score on every case. Add `--threshold 0.8` to allow for one
  judge disagreement.

Useful variations:

```bash
claude plugin eval . --tag trap --runs 3 --judge-model sonnet --allow-real-servers --allow-tools "mcp__plugin_partnerimpact_partnerimpact__*"
```

```bash
claude plugin eval . --case "04-*" --runs 1 --ablation none --judge-model sonnet
```

What the automated run cannot test: the interview. Runs have no user to answer questions, so every
brief carries its facts and says follow-ups cannot be answered. Web research is off as well.

## Manual round

This is the round that tests the app your users are in, with the interview.

1. Open a new Cowork or Claude session with the plugin enabled.
2. Paste the body of one `prompt.md`, without the lines between the `---` markers. For a truer
   test, leave out the last sentence about the meeting and answer the questions it asks from the
   facts in the brief.
3. Save the output.
4. Repeat in a session with the plugin disabled.
5. Score both against the rubric, or use the blind prompt below.

Cases 4, 5, 6 and 7 are the ones worth your own read, because you know what a good one looks like.

## Blind judging prompt

Paste this into a fresh session with no plugin, followed by the two outputs.

```text
Two assistants answered the same request from a partner manager. Judge them without knowing which
is which.

THE REQUEST:
<paste the prompt>

THE RIGHT ANSWER, FOR YOUR REFERENCE:
<paste the row from the scenario table>

OUTPUT A:
<paste>

OUTPUT B:
<paste>

For each output, answer pass or fail on each question, with one sentence of evidence quoted from
the output:
1. Does every figure come from the request or from a named calculation, with the user's inputs
   separated from assumed values?
2. Is the decision the right one, for the right reason?
3. Are facts the request did not contain either absent or marked as assumed?
4. Could a partner manager act on it tomorrow without rewriting it?
5. Does it lead with the decision and leave out filler, hedging and praise?

Then say which output you would send to a VP of Partnerships, and the single most important
difference between them. Do not reward length.
```

Swap which output is A and which is B between scenarios.
