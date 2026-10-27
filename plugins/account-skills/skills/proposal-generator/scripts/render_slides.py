#!/usr/bin/env python3
"""Render the proposal as a self-contained slide deck.

Consumes proposal_data.json and produces proposal-slides.html: a scroll-snap
deck (the visual-explainer SlideEngine pattern) in the Operator Console theme.
Self-contained — no reveal.js / CDN dependency — so it presents offline. Covers
title, goals, scope, estimations, timeline, and the cost summary, all from the
same data object as the webpage and PDF.
"""
from __future__ import annotations

import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fmt_money  # noqa: E402
from render_webpage import FONTS, _read, esc  # noqa: E402


def _slide_title(data: dict) -> str:
    m, c, p = data["meta"], data["client"], data["provider"]
    head, rec = data["costs"]["headline"], data["costs"]["recommended"]
    return f"""<section class="slide">
  <div class="s-lockup reveal"><span class="wamark">W</span><span>{esc(p['wordmark'][:4])}</span><b>{esc(p['wordmark'][4:])}</b></div>
  <div class="s-eyebrow reveal">{esc(p['positioning'])}</div>
  <h1 class="reveal">{esc(m['title'])}<br>for <em>{esc(c['name'])}</em></h1>
  <div class="s-counter-row reveal">
    <div class="s-stat"><div class="v">{esc(fmt_money(head['amount']))}</div><div class="l">{esc(head['label'])}</div></div>
    <div class="s-stat"><div class="v accent">{esc(fmt_money(rec['amount']))}</div><div class="l">Recommended · {esc(rec['core_weeks'])}-wk core</div></div>
    <div class="s-stat"><div class="v">{esc(data['estimations']['total_hours'])}h</div><div class="l">Estimated build</div></div>
  </div>
  <p class="reveal" style="margin-top:34px;font-family:var(--font-mono);font-size:12px;letter-spacing:1px;color:var(--text-3)">{esc(m['proposal_id'])} · STARTS {esc(data['timeline']['start_label']).upper()}</p>
</section>"""


def _slide_goals(data: dict) -> str:
    cards = "".join(
        f"""<div class="s-card reveal"><div class="l">Goal {i+1}</div><h3>{esc(g['title'])}</h3><p>{esc(g.get('detail',''))}</p></div>"""
        for i, g in enumerate(data["overview"]["goals"][:4])
    )
    return f"""<section class="slide">
  <div class="s-eyebrow reveal">Overview</div>
  <h2 class="reveal">What we're building toward</h2>
  <div class="s-grid2 reveal">{cards}</div>
</section>"""


def _slide_scope(data: dict) -> str:
    rows = data["estimations"]["by_deliverable"]
    cards = "".join(
        f"""<div class="s-card reveal"><span class="hrs">{esc(r['hours'])}h</span><div class="l">{esc(r['id'])}</div><h3>{esc(r['name'])}</h3></div>"""
        for r in rows
    )
    return f"""<section class="slide">
  <div class="s-eyebrow reveal">Scope</div>
  <h2 class="reveal">{esc(len(rows))} deliverables · {esc(data['estimations']['total_hours'])} hours</h2>
  <div class="s-grid2 reveal">{cards}</div>
</section>"""


def _slide_estimations(data: dict) -> str:
    e = data["estimations"]
    mx = max((r["hours"] for r in e["by_phase"]), default=1) or 1
    bars = "".join(
        f"""<div class="s-bar reveal"><span class="bl">{esc(r['phase'])}</span>
        <span class="bt"><span class="bf" style="width:{r['hours']/mx*100:.0f}%"></span></span>
        <span class="bv">{esc(r['hours'])}h · {esc(r['pct'])}%</span></div>"""
        for r in e["by_phase"]
    )
    return f"""<section class="slide">
  <div class="s-eyebrow reveal">Estimations</div>
  <h2 class="reveal">Effort by phase</h2>
  <div class="s-bars">{bars}</div>
</section>"""


def _slide_timeline(data: dict) -> str:
    weeks = data["timeline"]["weeks"]
    steps = []
    for i, w in enumerate(weeks):
        steps.append(
            f"""<div class="s-step reveal"><div class="wk">{esc(w['label'])}</div><div class="fc">{esc(w['focus'])}</div><div class="hh">{esc(w['dates_label'])} · {esc(w['hours'])}h</div></div>"""
        )
        if i < len(weeks) - 1:
            steps.append('<div class="s-arrow reveal">→</div>')
    t = data["timeline"]
    return f"""<section class="slide">
  <div class="s-eyebrow reveal">Timeline</div>
  <h2 class="reveal">{esc(t['recommended_weeks'])}-week core · {esc(t['range_label'])} range</h2>
  <div class="s-pipe">{''.join(steps)}</div>
  <p class="reveal" style="margin-top:24px;font-family:var(--font-mono);font-size:13px;color:var(--text-3)">Starts {esc(t['start_label'])}</p>
</section>"""


def _slide_costs(data: dict) -> str:
    c = data["costs"]
    head, rec = c["headline"], c["recommended"]
    sched = "".join(
        f"""<tr><td class="mono">{esc(s['week'])}</td><td>{esc(s['milestone'])}</td>
        <td class="amt">{esc(fmt_money(s['amount']))}</td><td class="run">{esc(fmt_money(s['running_total']))}</td></tr>"""
        for s in c["schedule"]
    )
    return f"""<section class="slide">
  <div class="s-eyebrow reveal">Costs</div>
  <h2 class="reveal">Investment &amp; pay-as-you-go plan</h2>
  <div class="s-counter-row reveal" style="margin-top:0;margin-bottom:18px">
    <div class="s-stat"><div class="v">{esc(fmt_money(head['amount']))}</div><div class="l">{esc(head['label'])}</div></div>
    <div class="s-stat"><div class="v accent">{esc(fmt_money(rec['amount']))}</div><div class="l">Recommended</div></div>
    <div class="s-stat"><div class="v">{esc(fmt_money(c['down_payment']['amount']))}</div><div class="l">Down payment</div></div>
    <div class="s-stat"><div class="v">{esc(fmt_money(c['remediation_rate']['amount']))}/hr</div><div class="l">Remediation</div></div>
    <div class="s-stat"><div class="v">{esc(fmt_money(c['change_budget']['amount']))}</div><div class="l">Change budget</div></div>
  </div>
  <table class="s-table reveal"><thead><tr><th>When</th><th>Milestone</th><th style="text-align:right">Invoice</th><th style="text-align:right">Cumulative</th></tr></thead>
  <tbody>{sched}</tbody></table>
</section>"""


def _slide_close(data: dict) -> str:
    p = data["provider"]
    terms = "".join(
        f"""<div class="s-card reveal"><div class="l">{esc(t['title'])}</div><p>{esc(t['body'])}</p></div>"""
        for t in data["terms"]
    )
    return f"""<section class="slide">
  <div class="s-eyebrow reveal">Terms · let's build</div>
  <h2 class="reveal">How we work together</h2>
  <div class="s-grid2 reveal">{terms}</div>
  <p class="reveal" style="margin-top:30px;font-size:20px;color:var(--text)"><em class="display-italic" style="font-size:24px">{esc(p['positioning'])}</em> — {esc(p['tagline'])}</p>
</section>"""


SCRIPT = """<script>
function SlideEngine(){this.deck=document.querySelector('.deck');
  this.slides=[].slice.call(document.querySelectorAll('.slide'));
  this.current=0;this.total=this.slides.length;this.buildChrome();this.bindEvents();this.observe();this.update();}
SlideEngine.prototype.buildChrome=function(){
  this.bar=document.createElement('div');this.bar.className='deck-progress';document.body.appendChild(this.bar);
  var dots=document.createElement('div');dots.className='deck-dots';var self=this;this.dots=[];
  this.slides.forEach(function(s,i){var b=document.createElement('button');b.onclick=function(){self.goTo(i);};dots.appendChild(b);self.dots.push(b);});
  document.body.appendChild(dots);
  this.counter=document.createElement('div');this.counter.className='deck-counter';document.body.appendChild(this.counter);
  this.hints=document.createElement('div');this.hints.className='deck-hints';this.hints.textContent='\\u2191 \\u2193 arrows / scroll';document.body.appendChild(this.hints);};
SlideEngine.prototype.bindEvents=function(){var self=this;
  document.addEventListener('keydown',function(e){
    if(e.target.closest('input,textarea,[contenteditable]'))return;
    if(['ArrowDown','ArrowRight',' ','PageDown'].indexOf(e.key)>-1){e.preventDefault();self.next();}
    else if(['ArrowUp','ArrowLeft','PageUp'].indexOf(e.key)>-1){e.preventDefault();self.prev();}
    else if(e.key==='Home'){e.preventDefault();self.goTo(0);}
    else if(e.key==='End'){e.preventDefault();self.goTo(self.total-1);}
    if(self.hints)self.hints.classList.add('faded');});
  var tY=null;this.deck.addEventListener('touchstart',function(e){tY=e.touches[0].clientY;},{passive:true});
  this.deck.addEventListener('touchend',function(e){if(tY===null)return;var dy=tY-e.changedTouches[0].clientY;
    if(Math.abs(dy)>50){dy>0?self.next():self.prev();}tY=null;});
  setTimeout(function(){if(self.hints)self.hints.classList.add('faded');},4000);};
SlideEngine.prototype.observe=function(){var self=this;
  var obs=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){
    en.target.classList.add('visible');self.current=self.slides.indexOf(en.target);self.update();}});},{threshold:.5});
  this.slides.forEach(function(s){obs.observe(s);});};
SlideEngine.prototype.goTo=function(i){this.slides[Math.max(0,Math.min(i,this.total-1))].scrollIntoView({behavior:'smooth'});};
SlideEngine.prototype.next=function(){if(this.current<this.total-1)this.goTo(this.current+1);};
SlideEngine.prototype.prev=function(){if(this.current>0)this.goTo(this.current-1);};
SlideEngine.prototype.update=function(){this.bar.style.width=((this.current+1)/this.total*100)+'%';
  var c=this.current;this.dots.forEach(function(d,i){d.classList.toggle('active',i===c);});
  this.counter.textContent=(this.current+1)+' / '+this.total;};
document.addEventListener('DOMContentLoaded',function(){document.querySelector('.slide').classList.add('visible');new SlideEngine();});
</script>"""


def render(data: dict, out_dir: str, assets_dir: str) -> str:
    css = _read(os.path.join(assets_dir, "tokens.css")) + "\n" + _read(os.path.join(assets_dir, "slides.css"))
    slides = "".join([
        _slide_title(data), _slide_goals(data), _slide_scope(data),
        _slide_estimations(data), _slide_timeline(data), _slide_costs(data), _slide_close(data),
    ])
    title = f"{data['meta']['title']} — {data['client']['name']} · slides"
    doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>{FONTS}
<style>{css}</style>
<script>document.documentElement.classList.add('js')</script></head><body>
<div class="deck">{slides}</div>{SCRIPT}</body></html>"""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "proposal-slides.html")
    with open(path, "w") as fh:
        fh.write(doc)
    return path


if __name__ == "__main__":
    import json
    with open(sys.argv[1]) as fh:
        _data = json.load(fh)
    _assets = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    print(render(_data, sys.argv[2] if len(sys.argv) > 2 else ".", _assets))
