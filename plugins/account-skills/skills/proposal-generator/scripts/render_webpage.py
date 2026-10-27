#!/usr/bin/env python3
"""Render the interactive proposal webpage (primary deliverable).

Consumes proposal_data.json and produces a single self-contained
proposal.html in the WithAgents Operator Console look. Interactivity is pure
vanilla JS + native <details> (per the visual-explainer reference): an
estimations view toggle, a headline/recommended cost toggle, expandable
deliverables, and an expandable week-by-week timeline. tokens.css + webpage.css
are inlined so the file opens anywhere with no external assets except fonts.
"""
from __future__ import annotations

import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fmt_money  # noqa: E402

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Inter:wght@400;500;600;700;800&'
    'family=Fraunces:ital,opsz,wght@1,9..144,400;1,9..144,500&'
    'family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">'
)


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def _read(path: str) -> str:
    with open(path) as fh:
        return fh.read()


def _tasks_in_phase(data: dict, phase: str):
    out = []
    for d in data["scope"]["deliverables"]:
        for t in d["tasks"]:
            if t["phase"] == phase:
                out.append((d["id"], t))
    return out


def _topbar(data: dict) -> str:
    p = data["provider"]
    return f"""<nav class="topbar"><div class="wrap">
  <div class="lockup"><span class="wamark">W</span><span>{esc(p['wordmark'][:4])}</span><b>{esc(p['wordmark'][4:])}</b></div>
  <div class="topnav">
    <a href="#overview">Overview</a><a href="#scope">Scope</a><a href="#estimations">Estimates</a>
    <a href="#timeline">Timeline</a><a href="#costs">Costs</a><a href="#terms">Terms</a>
  </div>
</div></nav>"""


def _hero(data: dict) -> str:
    m, c, p = data["meta"], data["client"], data["provider"]
    cost = data["costs"]
    head, rec = cost["headline"], cost["recommended"]
    return f"""<header class="hero"><div class="wrap">
  <span class="eyebrow">{esc(p['positioning'])}</span>
  <h1>{esc(m['title'])} for <em>{esc(c['name'])}</em></h1>
  <p class="lede">{esc(data['overview']['summary'])}</p>
  <div class="hero__parties">
    <div class="party"><div class="avatar avatar--wa">W</div><div class="who"><small>Prepared by</small><b>{esc(p['name'])}</b></div></div>
    <span class="arrow">→</span>
    <div class="party"><div class="avatar avatar--client">{esc(c['initial'])}</div><div class="who"><small>Prepared for</small><b>{esc(c['name'])}</b></div></div>
  </div>
  <div class="hero__meta">
    <span class="kv">PROPOSAL <b>{esc(m['proposal_id'])}</b></span>
    <span class="kv">ISSUED <b>{esc(m['generated_label'])}</b></span>
    <span class="kv">VALID UNTIL <b>{esc(m['valid_until_label'])}</b></span>
  </div>
  <div class="price-cards">
    <div class="card price reveal-up">
      <span class="mono-label">{esc(head['label'])}</span>
      <span class="amount">{esc(fmt_money(head['amount']))}</span>
      <span class="note">{esc(head['note'])}</span>
    </div>
    <div class="card price price--rec reveal-up">
      <span class="mono-label">{esc(rec['label'])} · recommended</span>
      <span class="amount">{esc(fmt_money(rec['amount']))}</span>
      <span class="note">{esc(rec['note'])}</span>
    </div>
  </div>
  <div class="cta">
    <a class="btn btn--primary" href="#costs">See the plan</a>
    <a class="btn btn--ghost" href="#scope">Scope &amp; deliverables</a>
  </div>
</div></header>"""


def _overview(data: dict) -> str:
    goals = data["overview"]["goals"]
    cards = "".join(
        f"""<div class="card card--hover goal reveal-up"><div class="n">G{i+1}</div>
        <h3>{esc(g['title'])}</h3><p>{esc(g.get('detail',''))}</p></div>"""
        for i, g in enumerate(goals)
    )
    return f"""<section id="overview" class="block"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Overview</span><h2>Goals for this engagement</h2>
  <p>{esc(data['overview'].get('product_summary',''))}</p></div>
  <div class="goals">{cards}</div>
</div></section>"""


def _scope(data: dict) -> str:
    s = data["scope"]
    est_by_id = {r["id"]: r["hours"] for r in data["estimations"]["by_deliverable"]}
    blocks = []
    for d in s["deliverables"]:
        rows = "".join(
            f"""<div class="task-row"><span class="tname">{esc(t['name'])}</span>
            <span class="phase-badge">{esc(t['phase'])}</span><span class="thrs">{esc(t['hours'])}h</span></div>"""
            for t in d["tasks"]
        )
        blocks.append(f"""<details class="card deliv reveal-up">
  <summary><span class="did">{esc(d['id'])}</span><span class="dname">{esc(d['name'])}</span>
  <span class="dhrs">{esc(est_by_id.get(d['id'],0))}h</span></summary>
  <div class="deliv__body"><p>{esc(d.get('description',''))}</p>{rows}</div>
</details>""")

    def _list(title, items, cls=""):
        lis = "".join(f"<li>{esc(x)}</li>" for x in items)
        return f"""<div><h4>{esc(title)}</h4><ul class="{cls}">{lis}</ul></div>"""

    lists = f"""<div class="lists">
      {_list('Assumptions', s.get('assumptions', []))}
      {_list('Constraints', s.get('constraints', []))}
      {_list('Out of scope', s.get('out_of_scope', []), 'lists--oos')}
    </div>"""
    return f"""<section id="scope" class="block"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Scope</span><h2>Deliverables &amp; tasks</h2>
  <p>Every deliverable expands to its tasks, each tagged with its delivery phase and hour estimate.</p></div>
  <div class="deliverables">{''.join(blocks)}</div>
  {lists}
</div></section>"""


def _estimations(data: dict) -> str:
    e = data["estimations"]
    t = data["timeline"]
    rec = data["costs"]["recommended"]
    kpis = [
        (str(e["total_hours"]), "Total hours", False),
        (str(len(e["by_deliverable"])), "Deliverables", False),
        (str(t["recommended_weeks"]), "Core weeks", False),
        (fmt_money(rec["amount"]), "Recommended", True),
    ]
    kpi_html = "".join(
        f"""<div class="card kpi reveal-up"><div class="v {'accent' if acc else ''}">{esc(v)}</div><div class="l">{esc(l)}</div></div>"""
        for v, l, acc in kpis
    )

    def bars(rows, key):
        mx = max((r["hours"] for r in rows), default=1) or 1
        out = []
        for r in rows:
            label = r.get("name") or r.get("phase")
            w = r["hours"] / mx * 100
            out.append(f"""<div class="bar-row"><span class="bl">{esc(label)}</span>
            <span class="bar-track"><span class="bar-fill" style="width:{w:.1f}%"></span></span>
            <span class="bv">{esc(r['hours'])}h · {esc(r['pct'])}%</span></div>""")
        return "".join(out)

    return f"""<section id="estimations" class="block"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Estimations</span><h2>Where the hours go</h2></div>
  <div class="kpis">{kpi_html}</div>
  <div class="breakdown" data-view="deliverable">
    <div class="toggle">
      <button class="active" onclick="setView(this,'deliverable')">By deliverable</button>
      <button onclick="setView(this,'phase')">By phase</button>
    </div>
    <div class="by-deliv">{bars(e['by_deliverable'],'name')}</div>
    <div class="by-phase">{bars(e['by_phase'],'phase')}</div>
  </div>
</div></section>"""


def _timeline(data: dict) -> str:
    t = data["timeline"]
    weeks = t["weeks"]
    mx = max((w["hours"] for w in weeks), default=1) or 1
    nodes = "".join(
        f"""<div class="tl-node"><div class="wk">{esc(w['label'])}</div><div class="fc">{esc(w['focus'])}</div>
        <div class="hr" style="width:{w['hours']/mx*100:.0f}%"></div><div class="dt">{esc(w['dates_label'])} · {esc(w['hours'])}h</div></div>"""
        for w in weeks
    )
    details = []
    for w in weeks:
        tasks = _tasks_in_phase(data, w["focus"])
        rows = "".join(
            f"""<div class="task-row"><span class="tname"><span class="phase-badge">{esc(did)}</span> {esc(tk['name'])}</span>
            <span class="thrs">{esc(tk['hours'])}h</span></div>"""
            for did, tk in tasks
        )
        details.append(f"""<details class="card twk reveal-up">
  <summary><span class="wkn">{esc(w['label'])}</span><span class="wkf">{esc(w['focus'])}</span>
  <span class="wkmeta">{esc(w['dates_label'])} · {esc(w['hours'])}h · {esc(', '.join(w['deliverable_ids']))}</span></summary>
  <div class="twk__body">{rows}</div>
</details>""")
    return f"""<section id="timeline" class="block"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Timeline</span><h2>{esc(t['recommended_weeks'])}-week core · starts {esc(t['start_label'])}</h2>
  <p>A lean core delivered across a flexible {esc(t['range_label'])} range. Click any week to see the tasks in play.</p></div>
  <div class="tl-track">{nodes}</div>
  <div class="deliverables">{''.join(details)}</div>
</div></section>"""


def _costs(data: dict) -> str:
    c = data["costs"]
    head, rec = c["headline"], c["recommended"]
    li_rows = "".join(
        f"""<tr><td>{esc(li['label'])}<small style="display:block;color:var(--text-3);font-size:11px">{esc(li['detail'])}</small></td>
        <td class="li-amt">{('<span class="li-incl">included</span>' if li['kind']=='included' else esc(fmt_money(li['amount'])))}</td></tr>"""
        for li in c["line_items"]
    )
    sched_rows = "".join(
        f"""<tr><td class="mono">{esc(s['week'])}</td><td>{esc(s['milestone'])}</td>
        <td class="li-amt sched-amt">{esc(fmt_money(s['amount']))}</td><td class="li-amt">{esc(fmt_money(s['running_total']))}</td></tr>"""
        for s in c["schedule"]
    )
    dp, rem, cb = c["down_payment"], c["remediation_rate"], c["change_budget"]
    return f"""<section id="costs" class="block"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Costs</span><h2>Investment &amp; payment plan</h2></div>
  <div class="cost" data-mode="recommended">
    <div class="cost-toggle">
      <button onclick="setMode(this,'headline')">Headline</button>
      <button class="active" onclick="setMode(this,'recommended')">Recommended</button>
    </div>
    <div class="card card--xl reveal-up" style="margin-bottom:24px">
      <div class="show-head">
        <span class="mono-label">{esc(head['label'])}</span>
        <div class="amount num" style="font-size:40px;margin:8px 0">{esc(fmt_money(head['amount']))}</div>
        <p>{esc(head['note'])}</p>
      </div>
      <div class="show-rec">
        <span class="mono-label" style="color:var(--accent)">{esc(rec['label'])}</span>
        <div class="amount num num-accent" style="font-size:40px;margin:8px 0">{esc(fmt_money(rec['amount']))}</div>
        <p>{esc(rec['note'])}</p>
      </div>
    </div>
    <div class="cost-grid">
      <div>
        <div class="card" style="margin-bottom:16px"><table>
          <thead><tr><th>Build line item</th><th style="text-align:right">Amount</th></tr></thead>
          <tbody>{li_rows}</tbody>
          <tfoot><tr><td>Recommended initial build</td><td class="li-amt">{esc(fmt_money(rec['amount']))}</td></tr></tfoot>
        </table></div>
        <div class="card"><div class="mono-label" style="margin-bottom:12px">Weekly payment schedule · pay-as-you-go</div><table>
          <thead><tr><th>When</th><th>Milestone</th><th style="text-align:right">Invoice</th><th style="text-align:right">Cumulative</th></tr></thead>
          <tbody>{sched_rows}</tbody>
        </table></div>
      </div>
      <div class="terms-cb">
        <div class="card cb cb--accent reveal-up"><div class="l">Down payment</div><div class="v">{esc(fmt_money(dp['amount']))}</div><p>{esc(dp['covers'])} — kicks off the build.</p></div>
        <div class="card cb reveal-up"><div class="l">Remediation</div><div class="v">{esc(fmt_money(rem['amount']))}<span style="font-size:14px;color:var(--text-3)">/hr</span></div><p>{esc(rem['note'])}</p></div>
        <div class="card cb cb--warn reveal-up"><div class="l">Change budget</div><div class="v">{esc(fmt_money(cb['amount']))}</div><p>{esc(cb['note'])}</p></div>
      </div>
    </div>
  </div>
</div></section>"""


def _terms(data: dict) -> str:
    cards = "".join(
        f"""<div class="card term reveal-up"><h3><span class="dot"></span>{esc(t['title'])}</h3><p>{esc(t['body'])}</p></div>"""
        for t in data["terms"]
    )
    return f"""<section id="terms" class="block"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Terms</span><h2>How we work together</h2></div>
  <div class="terms">{cards}</div>
</div></section>"""


def _footer(data: dict) -> str:
    p, m = data["provider"], data["meta"]
    return f"""<footer class="foot"><div class="wrap">
  <div class="lockup"><span class="wamark">W</span><span>{esc(p['wordmark'][:4])}</span><b>{esc(p['wordmark'][4:])}</b></div>
  <span class="mono" style="color:var(--text-3);font-size:11px">{esc(p['tagline'])} · valid until {esc(m['valid_until_label'])}</span>
  <div class="links">
    <a href="https://github.com/krzemienski" target="_blank" rel="noopener">GitHub</a>
    <a href="https://withagents.dev" target="_blank" rel="noopener">withagents.dev</a>
  </div>
</div></footer>"""


SCRIPT = """<script>
function setView(b,v){var r=b.closest('.breakdown');r.setAttribute('data-view',v);
  r.querySelectorAll('.toggle button').forEach(function(x){x.classList.remove('active');});b.classList.add('active');}
function setMode(b,m){var r=b.closest('.cost');r.setAttribute('data-mode',m);
  r.querySelectorAll('.cost-toggle button').forEach(function(x){x.classList.remove('active');});b.classList.add('active');}
document.addEventListener('DOMContentLoaded',function(){
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.12});
  document.querySelectorAll('.reveal-up').forEach(function(el){io.observe(el);});
});
</script>"""


def render(data: dict, out_dir: str, assets_dir: str) -> str:
    css = _read(os.path.join(assets_dir, "tokens.css")) + "\n" + _read(os.path.join(assets_dir, "webpage.css"))
    body = "".join([
        _topbar(data), _hero(data), _overview(data), _scope(data),
        _estimations(data), _timeline(data), _costs(data), _terms(data), _footer(data),
    ])
    title = f"{data['meta']['title']} — {data['client']['name']} · {data['provider']['name']}"
    doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>{FONTS}
<style>{css}</style>
<script>document.documentElement.classList.add('js')</script></head><body>
<h2 class="sr-only" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">{esc(title)} — interactive project proposal.</h2>
{body}{SCRIPT}</body></html>"""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "proposal.html")
    with open(path, "w") as fh:
        fh.write(doc)
    return path


if __name__ == "__main__":
    import json
    with open(sys.argv[1]) as fh:
        _data = json.load(fh)
    _assets = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    print(render(_data, sys.argv[2] if len(sys.argv) > 2 else ".", _assets))
