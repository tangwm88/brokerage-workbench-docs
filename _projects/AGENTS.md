# AGENTS.md - Project Workspace

This is an isolated project workspace.

## Structure

```
_projects/{project-name}/
├── AGENTS.md          # Project agents config
├── MEMORY.md          # Project memory
├── SOUL.md            # Project personality
├── USER.md            # Project user info
├── TOOLS.md           # Project tools
├── BOOTSTRAP.md       # Project bootstrap (delete after setup)
├── src/               # Source code
├── docs/              # Documentation
└── memory/            # Daily notes
```

## Usage

1. Create new project: `mkdir _projects/新项目`
2. Copy template files
3. Start working in isolation

## Rules

- Each project has independent memory
- Cross-project references use explicit paths
- System files in root workspace are shared