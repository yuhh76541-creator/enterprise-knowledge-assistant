# Project instructions

- Read README.md, docs/ARCHITECTURE.md and docs/ROADMAP.md before changing code.
- This is a working scaffold, not a finished enterprise application. Keep implemented and planned features distinct.
- Preserve Windows support, loopback-only defaults and remote-model operation without a GPU.
- Keep secrets, uploaded documents, local databases and personal resume information out of Git.
- Never send documents to a model or embedding service unless the user has authorized that integration.
- Health checks must not call an LLM, download a tokenizer or block on a remote dependency.
- Use bounded network timeouts and explicit failure states for future integrations.
- Keep Python typed, frontend TypeScript strict and API contracts documented.
- Test changes to persistence, validation and error handling. Run backend pytest and frontend npm run build before publishing code.
- Do not advertise authentication, RAG, citations or document parsing as complete until implemented and verified.
