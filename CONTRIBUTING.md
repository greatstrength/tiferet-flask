# Contributing to Tiferet Flask

Tiferet Flask follows the Tiferet two-strand process. Read [tiferet/docs/collab/process.md](https://github.com/greatstrength/tiferet/blob/main/docs/collab/process.md) before inventing a branch name.

Facts that belong only to this repo — proto branch, RFP prefix, GitHub owner — live in [docs/collab/binding.md](docs/collab/binding.md).

| You want to… | You submit | It lands on | The guide |
|---|---|---|---|
| Test a domain theory | an **RFP** | `v1.x-proto` | [rfp.md](https://github.com/greatstrength/tiferet/blob/main/docs/collab/rfp.md) |
| Rebuild a frozen catalog, or hotfix | a **TRD** | `main` | [main.md](https://github.com/greatstrength/tiferet/blob/main/docs/collab/main.md) |
| Change docs or agent skills | a **Doc PR** | `main` | [doc.md](https://github.com/greatstrength/tiferet/blob/main/docs/collab/doc.md) |

RFP ids use prefix `TFL1`. The GitHub issue title is `RFP-00N — <Plain Title>`. Working copies live in `.rfp/` (gitignored); the issue body is the public copy.

Never commit or merge unless someone asked you to.
