# VS Code Prompt Files

This directory contains VS Code prompt files (`.prompt.md`) that can be executed directly in GitHub Copilot Chat.

## What are VS Code Prompt Files?

VS Code prompt files are reusable prompts that can be invoked by typing `/` in GitHub Copilot Chat. They provide a native, integrated way to run systematic review workflows without leaving VS Code.

## Available Prompts

### `/generate-multidb-prompt`

**Purpose:** Generates a new VS Code prompt file for multi-database query generation.

**Usage (Two Options):**

**Option 1: One-Line Command (Recommended)**
```
/generate-multidb-prompt run_godos_2024_multidb studies/Godos_2024/prospero_godos_2024.md pubmed,scopus,wos,embase extended 1990/01/01 2023/12/31
```

**Option 2: Interactive Prompts**
1. Open GitHub Copilot Chat in VS Code (Ctrl+Shift+I or Cmd+Shift+I)
2. Type `/generate-multidb-prompt`
3. Provide the requested parameters when prompted:
   - **command_name**: Name for the new command (e.g., `run_godos_2024_multidb`)
   - **protocol_path**: Path to PROSPERO protocol (e.g., `studies/Godos_2024/prospero_godos_2024.md`)
   - **databases**: Comma-separated list (e.g., `pubmed,scopus,embase`)
   - **level**: Query complexity (`basic`, `extended`, `keywords`, `exhaustive`)
   - **min_date**: Start date (YYYY/MM/DD format)
   - **max_date**: End date (YYYY/MM/DD format)

**Output:** Creates a new prompt file at `.github/prompts/<command_name>.prompt.md`

**Complete Example:**

```bash
# One-line format (fastest - equivalent to Gemini CLI)
/generate-multidb-prompt run_godos_2024_multidb_extended studies/Godos_2024/prospero_godos_2024.md pubmed,scopus,wos,embase extended 1990/01/01 2023/12/31

# Result: New command /run-godos-2024-multidb-extended is created
```

**Argument Order:**
1. `command_name` - Name for the generated command
2. `protocol_path` - Path to protocol file  
3. `databases` - Comma-separated (NO SPACES!)
4. `level` - basic/extended/keywords/exhaustive
5. `min_date` - YYYY/MM/DD format
6. `max_date` - YYYY/MM/DD format

## How It Works

1. **Generation Step**: `/generate-multidb-prompt` reads your protocol file and creates a customized prompt
2. **Execution Step**: The generated command (e.g., `/run-godos-2024-multidb`) generates actual query files

This mirrors the Gemini CLI workflow but runs natively in VS Code.

## File Structure

```
.github/prompts/
├── README.md                           # This file
├── generate_multidb_prompt.prompt.md   # Generator prompt (permanent)
└── run_<study>_multidb.prompt.md      # Generated prompts (created by generator)
```

## Comparison with Gemini CLI

| Feature | Gemini CLI | VS Code Prompt Files |
|---------|------------|---------------------|
| **Invocation** | `/generate_multidb_prompt --flag value` | `/generate-multidb-prompt` (prompts for values) |
| **Location** | `.gemini/commands/` | `.github/prompts/` |
| **Requires** | Gemini CLI installed | GitHub Copilot subscription |
| **Interface** | Terminal | VS Code Chat |
| **Logic** | ✅ Identical | ✅ Identical |
| **Output** | ✅ Same files | ✅ Same files |

**Both approaches produce identical query files** - choose based on your preferred workflow.

## Testing

To verify the prompt file is working correctly:

```bash
bash scripts/test_vscode_prompt.sh
```

This validates:
- File structure and YAML syntax
- Input variable formatting
- File references
- Generation logic steps
- Output location

## Requirements

- VS Code with GitHub Copilot extension
- GitHub Copilot subscription (individual or business)
- Workspace must be opened in VS Code

## Troubleshooting

**Prompt doesn't appear in chat suggestions**
- Ensure you're in the correct workspace
- Try typing the full name: `/generate-multidb-prompt`
- Check that the file has `.prompt.md` extension

**"Tool not available" error**
- Ensure `agent: agent` is set in YAML frontmatter
- Verify `tools: [filesystem]` is present

**Generated file not created**
- Check VS Code output panel for errors
- Ensure workspace root is correct
- Verify the `.github/prompts/` directory exists

## Documentation

For complete workflow documentation, see:
- `Documentations/AUTOMATION_GUIDE.md` - Complete automation workflow
- `Documentations/complete_pipeline_guide.md` - Detailed pipeline guide
- `README.md` - Project overview

## Related Files

- **Gemini version**: `.gemini/commands/generate_multidb_prompt.toml`
- **Templates**: `prompts/prompt_template_multidb.md`
- **Guidelines**: `prompts/database_guidelines.md`
