# Contexto Ativo — Atualizado em 2026-05-26 00:21

## Projetos Ativos
| Projeto | Status | Última Sessão | Próxima Ação |
|---------|--------|---------------|--------------|
| MultiClip | ativo | session-001 | Implementar hybrid clipboard monitor + V3 UI |

## Tarefas Pendentes
### Alta Prioridade
- [ ] Replace ClipmanParser textsrc dependency with hybrid monitor writing to ~/.cache/multiclip/history.json (desde session-001)
- [ ] Implement hybrid clipboard monitor integration (polling + Ctrl+C hook) (desde session-001)
- [ ] Fix boot service duplication — exactly one instance on MX Linux boot (desde session-001)
- [ ] Fix MIT-MAGIC-COOKIE-1 X11 display error at startup (desde session-001)

### Média Prioridade
- [ ] Implement lazy-loaded pagination (50 items/page) for clipboard history (desde session-001)
- [ ] Implement Orderly mode: auto-capture Ctrl+C into slots with FIFO/LIFO and wrap-around at 30 (desde session-001)
- [ ] Add double-click preview/transfer dialog with slot selection and view button (desde session-001)
- [ ] Implement visual slot flash feedback (~2 sec gold/green pulse) on transfer (desde session-001)
- [ ] Rename "Transfer as Batch" → "Block Bundle", "Transfer as 1 Slot" → "1 Slot Per Line" (desde session-001)

### Baixa Prioridade
- [ ] Add snippet vault transfer from clipboard history (desde session-001)
- [ ] Implement inotify-based textsrc access logging for data loss detection (desde session-001)
- [ ] Add auto-placement options for "1 Slot Per Line" (sequential fill vs manual per-line) (desde session-001)

## Decisões Recentes
- [session-001] Replace textsrc dependency entirely — hybrid monitor writes to ~/.cache/multiclip/history.json
- [session-001] Keep classic 30-slot system (LCtrl+LAlt copy, RCtrl+RAlt paste) sacred and untouched
- [session-001] Clipman and MultiClip must be one unified clipboard — history is primary data source
- [session-001] 15 documentation skills completed; implementation phase begins now
- [session-001] User's #1 priority: hybrid monitor replacing textsrc parser

## Bloqueadores Ativos
- textsrc data loss incident: file dropped from 9MB/80 entries to 8 entries during MultiClip operations — root cause unknown, must not happen again
- Boot service launches 2 instances on startup; single-instance guard (fcntl.flock) may be bypassed by timing
- venv path in start-multiclip.sh references missing ./venv/bin/python3 instead of ./.venv/bin/python3

## Convenções Estabelecidas
- Python 3.11, tkinter GUI
- Project root: /home/flintx/multiclip
- Core files: multiclip.py, gui/main_window.py, shared/*.py
- Skills outputs saved to docs/ and docs/skills/
- Standard-skill journal entries saved to standard-skill/

## Últimas Sessões
- session-001: 15 documentation skills executed (analyze, blueprint, c4-context, c4-component, deepdive, dev-tech-journal, diagramming, documentation, plan-author, prd, project-analyzer, software-architecture, data-structure-protocol, mermaid-diagrams, standard), handoff generated, ready for implementation

---

# Sessão 001 — 2026-05-26
**Slug:** multiclip-rehab-clipman-integration | **Duração:** ~240min | **Modelo:** claude-opus-4

## Tópicos
- Análise profunda do formato textsrc do Clipman (semicolon-delimited, escaped)
- Unificação Clipman + MultiClip como sistema de clipboard único
- Especificação completa de UI/UX: transfer modes, preview, Orderly mode
- Pipeline de 15 skills de documentação executadas contra o projeto
- Pre-compaction handoff para continuidade entre sessões
- Estratégia de teste para clipboard monitor antes de integração
- Data loss catastrófico no textsrc (9MB → 8 entries)
- Problemas de boot service: duplicação, display error, venv path

## Decisões
- Vamos usar hybrid clipboard monitor (polling + Ctrl+C hook) em vez de depender do textsrc
- A decisão foi manter o sistema clássico de 30 slots intacto enquanto adiciona novos modos
- Optamos por lazy loading de 50 itens por página para evitar lag na UI
- Seguiremos com test harness standalone antes de integrar no app principal
- Ficou decidido que MultiClip nunca mais escreve ou trunca o textsrc
- Definimos que ~/.cache/multiclip/history.json será o novo datastore primário

## Tarefas Concluídas
- [x] Analisar formato textsrc do Clipman (semicolons, escape sequences)
- [x] Executar pipeline de 15 skills de documentação
- [x] Criar test harness para clipboard monitor (test_clipboard_monitor.py)
- [x] Criar documento de instruções para teste manual de clipboard
- [x] Gerar HANDOFF.md para cold-start da próxima sessão
- [x] Fix invalid MIT-MAGIC-COOKIE-1 key (copiar Xauthority para /tmp)
- [x] Corrigir venv path no start-multiclip.sh
- [x] Criar diff-marker integration (diff_marker/ package)
- [x] Especificar UI/UX completo: Block Bundle, 1 Slot Per Line, preview, flash

## Tarefas Pendentes
- [ ] Implementar hybrid clipboard monitor integration (prioridade: alta)
- [ ] Substituir ClipmanParser textsrc por monitor híbrido → ~/.cache/multiclip/history.json (prioridade: alta)
- [ ] Implementar lazy-loaded pagination (50 itens/página) (prioridade: alta)
- [ ] Implementar Orderly mode com FIFO/LIFO e wrap-around no slot 30 (prioridade: média)
- [ ] Adicionar double-click preview/transfer dialog (prioridade: média)
- [ ] Implementar visual slot flash (~2 sec pulse) (prioridade: média)
- [ ] Renomear botões de transferência (Block Bundle, 1 Slot Per Line) (prioridade: média)
- [ ] Fix boot service duplication — uma única instância (prioridade: alta)
- [ ] Proteger textsrc contra data loss (inotify, read-only) (prioridade: alta)
- [ ] Adicionar transferência para snippet vault (prioridade: baixa)

## Arquivos Modificados
- `multiclip.py` — edit
- `gui/main_window.py` — edit
- `shared/clipboard_manager.py` — edit
- `shared/config_manager.py` — edit
- `shared/snippets_manager.py` — edit
- `diff_marker/__init__.py` — write
- `diff_marker/diff_interface.py` — write
- `diff_marker/diff_manager.py` — write
- `diff_marker/diff_types.py` — write
- `requirements.txt` — edit
- `setup.sh` — edit
- `run_multiclip.sh` — write
- `docs/` — 15+ skill outputs escritos
- `standard-skill/standard.created.from.chat.multiclip-rehab-clipman-integration.05-26.26.md` — write

## Descobertas
- textsrc é um live log sem documentação; parser deve usar tail-read para performance
- O data loss de textsrc correlaciona com operações de auto-refresh e transfer do MultiClip
- Inotify-tools pode logar todos os acessos ao textsrc para detecção de anomalias
- O sistema de 30 slots deve ser tratado como circular buffer no Orderly mode
- Lazy loading requer indexação de offsets no arquivo textsrc ou mudança para JSONL/JSON

## Erros Resolvidos
- MIT-MAGIC-COOKIE-1 invalid key: resolvido copiando ~/.Xauthority para /tmp/.Xauthority_multiclip
- Boot display connection error: resolvido com DISPLAY=:0 e Xauthority correto
- venv path incorreto: corrigido de ./venv/bin/python3 para ./.venv/bin/python3

## Questões em Aberto
- Qual a causa raiz do truncamento do textsrc? (correlação com MultiClip, mas não confirmado)
- O hybrid monitor capturará 100% dos eventos de cópia? (test harness em validação)
- Como o parser saberá onde começa cada página no textsrc sem carregar tudo?

## Dívida Técnica
- ClipmanParser ainda depende do textsrc — deve ser substituído completamente
- Boot service usa sysVinit init.d — considerar migração para systemd no futuro
- UI do history panel precisa de refactor para suportar paginação e lazy loading

## Métricas
- Input tokens: —
- Output tokens: —
- Cache tokens: —
- Mensagens: 56
- Tool calls: 200+

---
*Sessão anterior: Nenhuma (sessão inicial)*
