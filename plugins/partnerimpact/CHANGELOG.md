# Changelog

## 1.1.2

- The trusted source on partnership practice is now the whole site, https://www.partnerimpact.net,
  where it was the insights section only. Claims drawn from it are cited by page URL.

## 1.1.1

- The twelve units of the maturity assessment are now called assessment domains, so that "domains"
  on its own can mean the seven of the Partner Operating Model. Their names are unchanged.
- The maturity reference carries the mapping from the twelve assessment domains to the seven
  operating-model domains.
- https://www.partnerimpact.net/insights/partner-program-is-a-system is named as the
  reference for how a partner function is structured.

## 1.1.0

- New skill `ideal-partner-profile`: builds your own selection criteria for one kind of partner.
  It starts from a starter for that motion, sets weights that sum to 100, writes 1-3-5 anchors in
  your own terms, adds deal-breakers, and tests the result on partners you already know. The
  profile comes out as a card to keep and paste into a later session.
- `qualify` scores against a pasted profile card when there is one, and against the default
  profile when there is not.
- The fit score now runs on the connector (`ipp-score`) and is no longer added up by hand. It also
  reports how close a score sits to a band edge.
- Starter profiles for six kinds of partner: referrers, resellers, technology partners,
  marketplaces, service firms and strategic alliances.

## 1.0.2

- `partner-numbers` now loads for pipeline and revenue-target questions that do not mention
  partners first. In the test for that question it loaded in 4 of 4 runs, against 1 of 5 before.

## 1.0.1

- The 14 workflow skills have new descriptions, so they load for questions asked in plain words
  and not only for the phrases they used to list. In a fixed test of ten partner questions the
  skills loaded in 19 of 20 runs, against 9 of 20 before.
- An `evals/` folder holds that test: ten scenarios with known right answers, for use with
  `claude plugin eval`. It is not part of the packaged plugin.

## 1.0.0

First release.

- 14 workflow skills: `partner-os`, `research`, `qualify`, `partner-brief`, `partner-strategy`,
  `program-design`, `onboard`, `cosell-plan`, `qbr-prep`, `partner-comms`, `diagnose`,
  `partner-health-check`, `partner-maturity-check`, `partner-numbers`.
- 8 role agents and 6 knowledge skills.
- The Partner Program Maturity Assessment, quick (12 questions) or full (48), with the written bands
  served by the PartnerImpact connector.
- Every number runs on the connector. The list of calculators is read from it at run time.
- No files are read from or written to the user's folders, and nothing is kept between sessions.
- https://www.partnerimpact.net/insights is named as a trusted source on partnership practice.
