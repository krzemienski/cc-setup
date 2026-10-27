# CLI Validation Strategy

## When This Applies
Project has `Cargo.toml`, `go.mod`, `pyproject.toml` with CLI entry points,
Makefile producing binaries, or any executable command-line tool.

## Build Verification

```bash
# Rust
cargo build 2>&1 | tail -10

# Go
go build ./... 2>&1 | tail -10

# Python (check entry point exists)
python -m <module> --help

# Swift
swift build 2>&1 | tail -10
```

## Finding the Binary

| Language | Typical Location |
|----------|-----------------|
| Rust | `target/debug/<name>` or `target/release/<name>` |
| Go | `./<name>` or `./bin/<name>` |
| Python | `python -m <module>` or script in `pyproject.toml [project.scripts]` |
| Swift | `.build/debug/<name>` |
| Node | `node dist/index.js` or `npx <name>` |

## Evidence Collection

### Standard Output and Exit Codes
```bash
# Capture stdout, stderr, and exit code
./binary args > stdout.txt 2> stderr.txt
echo "Exit code: $?" >> exit_code.txt

# Or combined
./binary args 2>&1 | tee output.txt
echo "Exit code: ${PIPESTATUS[0]}"
```

### Structured Verification Pattern
```bash
EVIDENCE_DIR="./evidence"
mkdir -p "$EVIDENCE_DIR"

# Test 1: Help output
./binary --help > "$EVIDENCE_DIR/01-help.txt" 2>&1
echo "Exit: $?" >> "$EVIDENCE_DIR/01-help.txt"

# Test 2: Valid input
./binary process input.txt > "$EVIDENCE_DIR/02-valid-input.txt" 2>&1
echo "Exit: $?" >> "$EVIDENCE_DIR/02-valid-input.txt"

# Test 3: Invalid input (should fail gracefully)
./binary process nonexistent.txt > "$EVIDENCE_DIR/03-invalid-input.txt" 2>&1
echo "Exit: $?" >> "$EVIDENCE_DIR/03-invalid-input.txt"

# Test 4: Edge case
echo "" | ./binary process - > "$EVIDENCE_DIR/04-empty-input.txt" 2>&1
echo "Exit: $?" >> "$EVIDENCE_DIR/04-empty-input.txt"
```

## Validation Criteria

### What to Check for Every Command

| Aspect | Check | How |
|--------|-------|-----|
| Help text | `--help` produces useful output | Read output, verify it documents all flags |
| Valid input | Expected output produced | Compare against spec's acceptance criteria |
| Invalid input | Graceful error message, non-zero exit | Run with bad input, check stderr |
| Exit codes | 0 for success, non-zero for failure | `echo $?` after each invocation |
| Piping | Works with stdin/stdout | `echo "input" \| ./binary` |
| Performance | Completes in reasonable time | `time ./binary args` |
| Verbose/debug mode | Extra output when requested | `./binary --verbose args` |

### For Subcommands
Exercise every subcommand separately:
```bash
./binary list > evidence/cmd-list.txt 2>&1
./binary create --name "test" > evidence/cmd-create.txt 2>&1
./binary delete --id 1 > evidence/cmd-delete.txt 2>&1
```

## Data Validation

If the CLI produces output files:
```bash
# Check output file exists and is non-empty
ls -la output.csv
wc -l output.csv

# Check format is correct
head -5 output.csv  # Verify headers
tail -5 output.csv  # Verify data rows

# For JSON output
cat output.json | jq . > /dev/null 2>&1 && echo "Valid JSON" || echo "Invalid JSON"
```

## Backend Integration

If the CLI calls an API:
```bash
# Verify backend is reachable
curl -sf http://localhost:<PORT>/health

# Then test CLI commands that call the API
./binary sync --server http://localhost:<PORT> > evidence/api-sync.txt 2>&1
```

## CLI-Specific Gotchas

| Gotcha | Impact | Solution |
|--------|--------|----------|
| Binary not in PATH | Command not found | Use full path `./target/debug/binary` |
| Missing permissions | Permission denied | `chmod +x ./binary` |
| Missing config file | Cryptic error on launch | Check if `.config` or env vars needed |
| Relative paths in binary | Works from project root only | Test from different directories |
| Interactive prompts | Blocks automation | Use `--yes` or `--no-interactive` flags, or pipe input |
| Color codes in captured output | Garbled text files | Use `--no-color` or `NO_COLOR=1` |
