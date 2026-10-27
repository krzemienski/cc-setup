# promptkit

Eight skills for writing model-correct prompts and requests, verified against Anthropic's and OpenAI's documentation on
2026-09-28.

## Use

Invoke a model skill with anything: a spoken ramble, a rough idea, a transcript, or an existing prompt. It returns a
ready-to-use prompt for that model, a settings table, and a request file that `kit.py send` can send.

```
/promptkit:prompting-opus-5-5 ok so I want something that turns my car voice memos into todos with owners…
/promptkit:prompting-gpt-6-luna You are a helpful assistant. Think step by step. Summarize this: {{input}}
/promptkit:optimizing-prompts turn standup transcripts into three bullets per person, cheap and fast
```

The skills also trigger on their own when you ask for a prompt, a request, or a fix for one of these models.

| Skill | For |
|---|---|
| `/promptkit:building-speakwright` | building speakwright |
| `/promptkit:optimizing-prompts` | optimizing prompts |
| `/promptkit:prompting-fable-5-1` | fable 5 1 |
| `/promptkit:prompting-gpt-6-astra` | gpt 6 astra |
| `/promptkit:prompting-gpt-6-luna` | gpt 6 luna |
| `/promptkit:prompting-gpt-6-sol` | gpt 6 sol |
| `/promptkit:prompting-opus-5-5` | opus 5 5 |
| `/promptkit:writing-prds` | writing prds |

## Requirements

Python 3.9+ (standard library only). Sending a request needs `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`; building,
auditing, linting, rendering, and agent dry runs need no key. The agent loops run shell commands in the directory you
give them and refuse destructive commands unless `--allow-destructive` is passed.

## Evals

`claude plugin eval . --allow-tools Bash Write --trust-plugin` runs 11 cases: a ramble and a prompt rewrite per
model, plus the router. Graders check that the kit's audit and render ran, the rendered prompt's structure and settings,
that legacy lines are gone, and a rubric on the content.
