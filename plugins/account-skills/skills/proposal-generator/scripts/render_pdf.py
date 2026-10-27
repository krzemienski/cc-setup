#!/usr/bin/env python3
"""Render the proposal as a branded PDF.

Builds a linear, print-styled HTML from proposal_data.json (everything expanded,
since paper has no interactivity) and converts it to PDF with weasyprint — a
pure-Python engine that needs no headless browser. The PDF mirrors the webpage's
numbers exactly because it reads the same data object. print.css inverts the
Operator Console palette to ink-on-paper while keeping crimson as the one accent.

Requires: weasyprint  (pip install weasyprint --break-system-packages)
"""
from __future__ import annotations

import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fmt_money  # noqa: E402
from render_webpage import _read, esc  # noqa: E402

PDF_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Inter:wght@400;500;600;700;800&'
    'family=Fraunces:ital,opsz,wght@1,9..144,400&'
    'family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">'
)


def _cover(data: dict) -> str:
    m, c, p = data["meta"], data["client"], data["provider"]
    head, rec = data["costs"]["headline"], data["costs"]["recommended"]
    return f"""<section class="keep" style="margin-bottom:18px">
  <div class="eyebrow">{esc(p['positioning'])}</div>
  <h1 style="margin:8px 0 6px">{esc(m['title'])} for <span class="display-italic">{esc(c['name'])}</span></h1>
  <p style="font-size:11.5pt;max-width:60ch">{esc(data['overview']['summary'])}</p>
  <div style="display:flex;gap:24px;margin:14px 0 16px;font-family:'JetBrains Mono',monospace;font-size:8pt;color:#6f6f78">
    <span>PREPARED BY <strong>{esc(p['name'])}</strong></span>
    <span>FOR <strong>{esc(c['name'])}</strong></span>
    <span>{esc(m['proposal_id'])}</span>
    <span>ISSUED {esc(m['generated_label']).upper()}</span>
    <span>VALID {esc(m['valid_until_label']).upper()}</span>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
    <div class="card"><div class="mono-label">{esc(head['label'])}</div>
      <div class="num" style="font-size:26pt">{esc(fmt_money(head['amount']))}</div>
      <p style="font-size:9pt">{esc(head['note'])}</p></div>
    <div class="card" style="border-color:#f3b9c1;background:#fdf3f4"><div class="mono-label" style="color:#E0273C">{esc(rec['label'])} · recommended</div>
      <div class="num num-accent" style="font-size:26pt">{esc(fmt_money(rec['amount']))}</div>
      <p style="font-size:9pt">{esc(rec['note'])}</p></div>
  </div>
</section>"""


def _goals(data: dict) -> str:
    items = "".join(
        f"""<div class="card keep" style="margin-bottom:8px"><strong>G{i+1} · {esc(g['title'])}</strong>
        <p style="font-size:9.5pt;margin-top:3px">{esc(g.get('detail',''))}</p></div>"""
        for i, g in enumerate(data["overview"]["goals"])
    )
    return f"""<section><div class="eyebrow">Overview</div><h2>Goals</h2>
  <p style="font-size:10pt;margin-bottom:10px">{esc(data['overview'].get('product_summary',''))}</p>{items}</section>"""


def _scope(data: dict) -> str:
    est = {r["id"]: r["hours"] for r in data["estimations"]["by_deliverable"]}
    blocks = []
    for d in data["scope"]["deliverables"]:
        rows = "".join(
            f"""<tr><td>{esc(t['name'])}</td><td class="mono" style="color:#6f6f78">{esc(t['phase'])}</td>
            <td style="text-align:right;font-family:'JetBrains Mono',monospace;font-weight:700">{esc(t['hours'])}h</td></tr>"""
            for t in d["tasks"]
        )
        blocks.append(f"""<div class="card keep" style="margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;align-items:baseline">
    <strong style="font-size:11pt">{esc(d['id'])} · {esc(d['name'])}</strong>
    <span class="num">{esc(est.get(d['id'],0))}h</span></div>
  <p style="font-size:9pt;margin:4px 0 6px">{esc(d.get('description',''))}</p>
  <table><tbody>{rows}</tbody></table></div>""")

    def lst(title, items, dot="#6f6f78"):
        lis = "".join(
            f"""<li style="font-size:9pt;padding:3px 0 3px 14px;position:relative;list-style:none">
            <span style="position:absolute;left:0;top:8px;width:5px;height:5px;border-radius:50%;background:{dot}"></span>{esc(x)}</li>"""
            for x in items
        )
        return f"""<div><div class="mono-label" style="margin-bottom:4px">{esc(title)}</div><ul style="margin:0;padding:0">{lis}</ul></div>"""

    lists = f"""<div class="keep" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:8px">
      {lst('Assumptions', data['scope'].get('assumptions',[]))}
      {lst('Constraints', data['scope'].get('constraints',[]))}
      {lst('Out of scope', data['scope'].get('out_of_scope',[]), '#E0273C')}</div>"""
    return f"""<section class="page-break"><div class="eyebrow">Scope</div><h2>Deliverables &amp; tasks</h2>{''.join(blocks)}{lists}</section>"""


def _estimations(data: dict) -> str:
    e = data["estimations"]
    mx = max((r["hours"] for r in e["by_phase"]), default=1) or 1
    bars = "".join(
        f"""<div style="display:grid;grid-template-columns:150px 1fr 80px;align-items:center;gap:12px;padding:4px 0">
        <span style="font-size:9.5pt">{esc(r['phase'])}</span>
        <span class="bar-track"><span class="bar-fill" style="width:{r['hours']/mx*100:.0f}%"></span></span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:9pt;text-align:right;font-weight:700">{esc(r['hours'])}h · {esc(r['pct'])}%</span></div>"""
        for r in e["by_phase"]
    )
    return f"""<section class="keep"><div class="eyebrow">Estimations</div><h2>Effort by phase</h2>
  <div class="card">{bars}<div style="border-top:1.5px solid #d6d4ce;margin-top:8px;padding-top:8px;text-align:right;font-family:'JetBrains Mono',monospace;font-weight:700">Total {esc(e['total_hours'])}h</div></div></section>"""


def _timeline(data: dict) -> str:
    t = data["timeline"]
    rows = "".join(
        f"""<tr><td class="mono" style="color:#E0273C;font-weight:700">{esc(w['label'])}</td>
        <td><strong>{esc(w['focus'])}</strong></td><td>{esc(w['dates_label'])}</td>
        <td>{esc(', '.join(w['deliverable_ids']))}</td>
        <td style="text-align:right;font-family:'JetBrains Mono',monospace;font-weight:700">{esc(w['hours'])}h</td></tr>"""
        for w in t["weeks"]
    )
    return f"""<section class="keep"><div class="eyebrow">Timeline</div>
  <h2>{esc(t['recommended_weeks'])}-week core · starts {esc(t['start_label'])}</h2>
  <p style="font-size:9.5pt;margin-bottom:8px">Flexible across a {esc(t['range_label'])} range.</p>
  <div class="card"><table><thead><tr><th>Week</th><th>Focus</th><th>Dates</th><th>Deliverables</th><th style="text-align:right">Hours</th></tr></thead>
  <tbody>{rows}</tbody></table></div></section>"""


def _costs(data: dict) -> str:
    c = data["costs"]
    rec = c["recommended"]
    li = "".join(
        f"""<tr><td>{esc(x['label'])} <span style="color:#6f6f78;font-size:8pt">{esc(x['detail'])}</span></td>
        <td style="text-align:right;font-family:'JetBrains Mono',monospace;font-weight:700">{('included' if x['kind']=='included' else esc(fmt_money(x['amount'])))}</td></tr>"""
        for x in c["line_items"]
    )
    sched = "".join(
        f"""<tr><td class="mono">{esc(s['week'])}</td><td>{esc(s['milestone'])}</td>
        <td style="text-align:right;font-family:'JetBrains Mono',monospace;color:#E0273C;font-weight:700">{esc(fmt_money(s['amount']))}</td>
        <td style="text-align:right;font-family:'JetBrains Mono',monospace">{esc(fmt_money(s['running_total']))}</td></tr>"""
        for s in c["schedule"]
    )
    dp, rem, cb = c["down_payment"], c["remediation_rate"], c["change_budget"]
    return f"""<section class="page-break"><div class="eyebrow">Costs</div><h2>Investment &amp; payment plan</h2>
  <div class="card keep" style="margin-bottom:10px"><table>
    <thead><tr><th>Build line item</th><th style="text-align:right">Amount</th></tr></thead>
    <tbody>{li}</tbody>
    <tfoot><tr><td>Recommended initial build</td><td style="text-align:right;font-family:'JetBrains Mono',monospace">{esc(fmt_money(rec['amount']))}</td></tr></tfoot></table></div>
  <div class="card keep" style="margin-bottom:10px"><div class="mono-label" style="margin-bottom:6px">Weekly payment schedule · pay-as-you-go</div><table>
    <thead><tr><th>When</th><th>Milestone</th><th style="text-align:right">Invoice</th><th style="text-align:right">Cumulative</th></tr></thead>
    <tbody>{sched}</tbody></table></div>
  <div class="keep" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
    <div class="card"><div class="mono-label" style="color:#E0273C">Down payment</div><div class="num num-accent" style="font-size:16pt">{esc(fmt_money(dp['amount']))}</div><p style="font-size:8.5pt">{esc(dp['covers'])}.</p></div>
    <div class="card"><div class="mono-label">Remediation</div><div class="num" style="font-size:16pt">{esc(fmt_money(rem['amount']))}/hr</div><p style="font-size:8.5pt">{esc(rem['note'])}</p></div>
    <div class="card"><div class="mono-label" style="color:#c2790a">Change budget</div><div class="num" style="font-size:16pt;color:#c2790a">{esc(fmt_money(cb['amount']))}</div><p style="font-size:8.5pt">{esc(cb['note'])}</p></div>
  </div></section>"""


def _terms(data: dict) -> str:
    cards = "".join(
        f"""<div class="card keep" style="margin-bottom:8px"><strong>{esc(t['title'])}</strong>
        <p style="font-size:9.5pt;margin-top:3px">{esc(t['body'])}</p></div>"""
        for t in data["terms"]
    )
    p = data["provider"]
    return f"""<section><div class="eyebrow">Terms</div><h2>How we work together</h2>{cards}
  <p style="margin-top:12px;font-size:11pt"><span class="display-italic">{esc(p['positioning'])}</span> — {esc(p['tagline'])}</p></section>"""


def build_print_html(data: dict, assets_dir: str) -> str:
    css = _read(os.path.join(assets_dir, "print.css"))
    body = "".join([
        _cover(data), _goals(data), _scope(data), _estimations(data),
        _timeline(data), _costs(data), _terms(data),
    ])
    title = f"{data['meta']['title']} — {data['client']['name']}"
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>{esc(title)}</title>{PDF_FONTS}<style>{css}</style></head><body>{body}</body></html>"""


def render(data: dict, out_dir: str, assets_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    html_doc = build_print_html(data, assets_dir)
    html_path = os.path.join(out_dir, "proposal-print.html")
    with open(html_path, "w") as fh:
        fh.write(html_doc)
    pdf_path = os.path.join(out_dir, "proposal.pdf")
    from weasyprint import HTML  # lazy import so the rest of the skill works without it
    HTML(string=html_doc, base_url=assets_dir).write_pdf(pdf_path)
    return pdf_path


if __name__ == "__main__":
    import json
    with open(sys.argv[1]) as fh:
        _data = json.load(fh)
    _assets = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    print(render(_data, sys.argv[2] if len(sys.argv) > 2 else ".", _assets))
