# ContextLens

> **Test, profile, and optimize the context your LLM actually needs.**

**Document status:** Draft v0.1  
**Project type:** Open-source AI developer infrastructure  
**Primary language (proposed):** TypeScript  
**Interfaces:** SDK, CLI, CI integration

---

# 1. Executive Summary

Modern LLM applications send increasingly complex context to models: system instructions, user messages, conversation history, RAG documents, tool definitions, tool results, memory, and few-shot examples.

Teams can measure token usage, but a harder question remains:

> **Does the model actually need all of this context to produce the required behavior?**

ContextLens is a developer tool that captures an LLM execution, decomposes its effective context into logical segments, performs controlled re-execution experiments, and identifies opportunities to reduce context while preserving user-defined behavior.

```text
Capture LLM execution
        ↓
Profile context and token usage
        ↓
Define expected behavior
        ↓
Run controlled context-removal experiments
        ↓
Compare resulting behavior
        ↓
Identify removable or compressible context
        ↓
Generate optimization recommendations
```

ContextLens treats the model as a black box. It does not require access to model weights, attention scores, or internal activations.

> **Find the context your LLM actually needs—and catch context efficiency regressions before they reach production.**

---

# 2. Problem Statement

## 2.1 The effective context problem

A production LLM request may contain:

```text
System Instructions
Few-shot Examples
Conversation History
Retrieved Documents
Memory
Tool Definitions
Tool Results
Current User Request
        ↓
       LLM
        ↓
     Response
```

Over time, context tends to grow because developers add more information to improve quality or handle edge cases.

This creates:

1. Higher inference cost
2. Higher latency
3. Context-window pressure
4. Duplicate information
5. Stale information
6. Lower signal-to-noise ratio
7. Prompt changes that increase cost without measurable quality improvements

Existing tools can answer:

> How many tokens did we use?

Some can answer:

> Where did those tokens come from?

ContextLens focuses on the harder question:

> **What can we safely remove?**

---

# 3. Product Vision

## Long-term vision

ContextLens should become a performance-testing layer for LLM applications.

Traditional software engineering has:

```text
Unit Tests
Integration Tests
Performance Tests
CPU Profilers
Memory Profilers
```

LLM applications need:

```text
Behavior Tests
Context Profiles
Token Regression Tests
Cost Regression Tests
Context Minimization
```

The long-term vision is:

> **No significant LLM context change should reach production without understanding its cost and behavioral impact.**

---

# 4. Product Principles

## 4.1 Black-box first

ContextLens operates through:

```text
Modified Input
      ↓
LLM Execution
      ↓
Observed Output
      ↓
Behavior Evaluation
```

No model internals are required.

## 4.2 Behavior over textual equality

Two responses can differ textually while accomplishing the same task. Optimization should therefore use task-specific behavioral contracts.

## 4.3 Explicit uncertainty

ContextLens must not claim:

> “These tokens caused the response.”

Instead:

> “Removing this context preserved the configured behavior under the executed experiments.”

## 4.4 Local-first

LLM context can contain proprietary code, customer data, internal documents, and secrets. Core operation should therefore be local by default.

## 4.5 Framework-agnostic core

Provider and framework integrations should feed one common internal representation.

---

# 5. Target Users

## Primary

### AI Engineers
Engineers building production LLM applications.

### Backend Engineers
Engineers responsible for AI cost, latency, and production infrastructure.

### Prompt / AI Application Engineers
People responsible for prompt templates and context construction.

## Secondary

- Platform engineering teams
- ML infrastructure teams
- AI reliability teams

---

# 6. Core User Journey

## Step 1: Instrument the LLM application

```typescript
import { ContextLens } from "@contextlens/sdk";

const lens = new ContextLens();

const result = await lens.run({
  context: [
    lens.system(systemPrompt),
    lens.history(conversationHistory),
    lens.retrieval(retrievedDocuments),
    lens.user(userQuestion)
  ],

  execute: (input) => llmCall(input)
});
```

ContextLens captures:

- Model configuration
- Context segments
- Original request
- Original response
- Token usage
- Timing

## Step 2: Profile

```bash
contextlens profile run-001
```

Example:

```text
CONTEXT PROFILE

Total Input Tokens: 48,231

System Instructions       8,421  17.5%
Conversation History     15,932  33.0%
Retrieved Documents      18,442  38.2%
Tool Results              5,436  11.3%
```

## Step 3: Define behavioral expectations

```typescript
const evaluator = new ContextLens.StructuredEvaluator({
  requiredFields: ["category", "eligible"],
  compare: "semantic"
});
```

Possible evaluators:

- Exact output
- Structured JSON equality
- Classification equality
- Semantic similarity
- Tool-call equivalence
- Custom function

## Step 4: Minimize

```bash
contextlens minimize run-001 --budget 30
```

ContextLens runs controlled experiments.

```text
Experiment #1
Remove: Conversation turns 1-8
Result: ✓ Behavior preserved
```

```text
Experiment #2
Remove: Retrieved documents 1-5
Result: ✗ Behavior changed
```

## Step 5: Review recommendations

```text
CONTEXT OPTIMIZATION REPORT

Original: 48,231 tokens
Reduced:  29,442 tokens
Reduction: 38.9%

REMOVE
- Conversation turns 1-8
  Savings: 7,112 tokens

REMOVE
- Retrieved document #4
  Savings: 4,932 tokens

SUMMARIZE
- Tool results 1-3
  Estimated savings: 2,000 tokens
```

---

# 7. Functional Requirements

## FR-1: Context Capture

Capture:

- Model provider
- Model name
- Model parameters
- Input context
- Context segment boundaries
- Output
- Usage information
- Execution metadata

## FR-2: Context Segmentation

Supported segment types:

```text
SYSTEM
USER
CONVERSATION
RETRIEVAL
TOOL_DEFINITION
TOOL_RESULT
MEMORY
EXAMPLE
CUSTOM
```

Segments may contain child segments.

## FR-3: Token Profiling

Calculate token counts per segment and aggregate.

## FR-4: Controlled Re-execution

Generate modified context versions and execute them against the configured model.

## FR-5: Behavioral Evaluation

Compare candidate output with the original output or an expected result.

## FR-6: Context Minimization

Search for lower-cost context configurations that preserve behavior.

## FR-7: Recommendations

Generate:

- Remove
- Keep
- Summarize
- Deduplicate
- Investigate

## FR-8: Reports

Support terminal, JSON, and Markdown reports.

## FR-9: CI Integration

Support pass/fail checks for:

- Token regressions
- Cost regressions
- Behavioral regressions

---

# 8. Non-Functional Requirements

- Minimize expensive model experiments
- Local-first privacy
- Reproducible captured runs
- Pluggable providers and evaluators
- Every recommendation must contain experimental evidence

---

# 9. High-Level Architecture

```text
                    USER APPLICATION
                           │
                           ▼
                  ┌────────────────┐
                  │ ContextLens SDK│
                  └───────┬────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │ Context Model  │
                  │ Normalization  │
                  └───────┬────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │ Local Run Store│
                  └───────┬────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │ ContextLens CLI│
                  └───────┬────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
       Profile       Minimization      Evaluator
       Engine          Engine
                          │
                          ▼
                     LLM Provider
                          │
                          ▼
                       Reports
```

---

# 10. Low-Level Design

## 10.1 Proposed Repository Structure

```text
contextlens/
├── packages/
│   ├── core/
│   ├── sdk/
│   ├── cli/
│   ├── evaluator/
│   ├── optimizer/
│   ├── provider-openai/
│   └── github-action/
├── examples/
│   ├── basic/
│   ├── rag/
│   └── structured-output/
├── benchmarks/
└── docs/
```

## 10.2 ContextRun

```typescript
interface ContextRun {
  id: string;
  createdAt: string;
  model: ModelConfig;
  segments: ContextSegment[];
  originalRequest: unknown;
  originalResponse: CapturedResponse;
  usage?: TokenUsage;
  metadata?: Record<string, unknown>;
}
```

## 10.3 ModelConfig

```typescript
interface ModelConfig {
  provider: string;
  model: string;

  parameters: {
    temperature?: number;
    topP?: number;
    maxTokens?: number;
    seed?: number;
  };
}
```

## 10.4 ContextSegment

```typescript
interface ContextSegment {
  id: string;
  type: ContextSegmentType;
  content: unknown;
  tokenCount?: number;
  metadata?: SegmentMetadata;
  children?: ContextSegment[];
}
```

```typescript
type ContextSegmentType =
  | "system"
  | "user"
  | "conversation"
  | "retrieval"
  | "tool_definition"
  | "tool_result"
  | "memory"
  | "example"
  | "custom";
```

## 10.5 SegmentMetadata

```typescript
interface SegmentMetadata {
  source?: string;
  documentId?: string;
  messageIndex?: number;
  toolName?: string;
  timestamp?: string;
  tags?: string[];
}
```

---

# 11. Execution Adapter

The core should not depend on one LLM provider.

```typescript
interface ExecutionAdapter<Request, Response> {
  execute(request: Request): Promise<Response>;

  buildRequest(
    run: ContextRun,
    segments: ContextSegment[]
  ): Request;

  normalizeResponse(
    response: Response
  ): CapturedResponse;
}
```

The optimizer works against this abstraction.

---

# 12. Evaluator Interface

The evaluator decides whether behavior is preserved.

```typescript
interface BehaviorEvaluator {
  evaluate(
    original: CapturedResponse,
    candidate: CapturedResponse,
    context: EvaluationContext
  ): Promise<EvaluationResult>;
}
```

```typescript
interface EvaluationResult {
  equivalent: boolean;
  score: number;
  reasons?: string[];
  metadata?: Record<string, unknown>;
}
```

## Built-in evaluators

### ExactEvaluator

For deterministic outputs.

### JSONEvaluator

Modes:

```text
EXACT
REQUIRED_FIELDS
SCHEMA
SELECTED_PATHS
```

### ClassificationEvaluator

```text
original.label == candidate.label
```

### SemanticEvaluator

Semantic similarity with a configurable threshold.

### ToolCallEvaluator

Compare selected tools and optionally their arguments.

### CustomEvaluator

```typescript
const evaluator: BehaviorEvaluator = {
  async evaluate(original, candidate) {
    return {
      equivalent: customLogic(original, candidate),
      score: 1
    };
  }
};
```

---

# 13. Context Minimization Engine

## 13.1 Optimization Objective

Given:

```text
C = {c1, c2, ..., cn}
```

find:

```text
C' ⊆ C
```

that minimizes context cost while preserving behavior.

```text
minimize Cost(C')

subject to

E(
  Execute(C),
  Execute(C')
) ≥ threshold
```

Where:

- `Execute()` runs the model
- `E()` is the behavior evaluator
- `Cost()` initially represents input token count

## 13.2 Why brute force fails

For `n` segments there are `2^n` possible subsets.

For 30 segments:

```text
1,073,741,824
```

possible combinations.

Therefore ContextLens requires heuristic search.

---

# 14. Proposed V1 Optimization Algorithm

## Phase A: Deterministic preprocessing

Before spending model calls:

- Remove exact duplicates
- Detect empty segments
- Detect repeated conversation content
- Flag potentially superseded tool results

## Phase B: Hierarchical grouping

```text
ROOT
├── SYSTEM
├── CONVERSATION
│   ├── Turn 1
│   ├── Turn 2
│   └── Turn 3
├── RETRIEVAL
│   ├── Document 1
│   ├── Document 2
│   └── Document 3
└── TOOL_RESULTS
```

First test removing large groups.

If a group is removable, discard it.

If removal changes behavior, recursively investigate its children.

## Phase C: Delta debugging

For:

```text
[A, B, C, D, E, F]
```

test partitions:

```text
Remove [A, B, C]
Remove [D, E, F]
```

Then recursively explore the relevant region.

## Phase D: Greedy final pass

```text
for each remaining segment:
    temporarily remove segment
    execute candidate

    if behavior preserved:
        permanently remove
```

This produces a locally minimal context.

---

# 15. Experiment Model

Every model experiment should be recorded.

```typescript
interface Experiment {
  id: string;
  runId: string;
  parentExperimentId?: string;
  removedSegmentIds: string[];
  addedSegmentIds?: string[];

  status:
    | "pending"
    | "running"
    | "completed"
    | "failed";

  response?: CapturedResponse;
  evaluation?: EvaluationResult;

  createdAt: string;
  completedAt?: string;
}
```

Experiment tree:

```text
Original
├── Remove Conversation
│   └── Failed
├── Remove Retrieval
│   └── Passed
└── Remove Tool Results
    └── Failed
```

---

# 16. Handling Model Non-Determinism

Different outputs can result from identical inputs.

## V1 strategy

Prefer:

```text
temperature = 0
seed = fixed, where supported
```

## Later

Run multiple samples and compare score distributions.

For V1, ContextLens should clearly state that results reflect the configured experimental conditions.

---

# 17. Recommendation Engine

Recommendations must be evidence-driven.

## REMOVE

Removing a segment preserved behavior.

## KEEP

Removing a segment changed behavior.

## SUMMARIZE

A segment is needed but is large. This is a later feature.

## DEDUPLICATE

Exact or near-identical context was found.

## INVESTIGATE

Experimental results were inconsistent.

---

# 18. CLI Design

## Initialize

```bash
contextlens init
```

## Profile

```bash
contextlens profile run-001
```

## Analyze

```bash
contextlens analyze run-001
```

## Minimize

```bash
contextlens minimize run-001   --budget 30   --evaluator semantic   --threshold 0.95
```

## Compare

```bash
contextlens compare baseline.json candidate.json
```

## Test

```bash
contextlens test
```

---

# 19. Configuration

```yaml
version: 1

model:
  temperature: 0

evaluation:
  type: structured

optimization:
  maxExperiments: 30

budgets:
  maxInputTokens: 50000
  maxCostPerRequest: 0.05
```

---

# 20. CI Integration

```text
Pull Request
      ↓
ContextLens Test Suite
      ↓
Compare Against Baseline
      ↓
Behavior: PASS
Tokens: +31%
Cost: +28%
      ↓
PR Check Result
```

Example:

```text
CONTEXT REGRESSION DETECTED

Test: refund-support-flow

Input tokens:
12,412 → 17,892
(+44.1%)

Behavior score:
0.971 → 0.972

Conclusion:
Cost increased without measurable behavioral improvement.
```

---

# 21. Storage

## MVP

Local JSON:

```text
.contextlens/
├── runs/
│   ├── run-001.json
│   └── run-002.json
└── experiments/
    ├── exp-001.json
    └── exp-002.json
```

## Future

SQLite for larger experiment sets and historical analysis.

---

# 22. Security and Privacy

V1 requirements:

- Local storage by default
- No telemetry by default
- No cloud upload requirement
- Explicit redaction configuration
- Secret masking in reports

Example:

```yaml
redaction:
  fields:
    - api_key
    - password

  patterns:
    - "Bearer .*"
```

---

# 23. MVP Scope

## Include

### SDK

- Explicit context segments
- Generic execution wrapper

### Core

- ContextRun
- ContextSegment
- Local JSON storage

### Provider

- One OpenAI-compatible adapter

### Evaluators

- Exact
- JSON
- Custom

### Optimizer

- Hierarchical removal
- Greedy minimization

### CLI

- profile
- minimize
- report

### Reports

- Terminal
- JSON
- Markdown

## Explicitly exclude

- Every model provider
- Framework integrations
- Web dashboard
- Cloud service
- Token-level attribution
- Attention analysis
- Shapley attribution
- Automatic prompt rewriting
- Automatic production optimization
- Full agent trajectory analysis

---

# 24. Benchmark Strategy

A credible project needs measurable claims.

Measure:

## Context reduction

```text
Original token count
vs
Reduced token count
```

## Behavioral preservation

```text
Original task score
vs
Reduced-context task score
```

## Experiment efficiency

```text
Number of model calls required
```

## Economic value

```text
Cost of analysis
vs
Expected recurring savings
```

A potential project claim:

> ContextLens reduced effective context by X% across representative workloads while preserving at least Y% of configured behavioral metrics within a budget of N experiments.

---

# 25. Key Risks

## Risk 1: Analysis costs more than savings

Mitigation:

- Experiment budgets
- Hierarchical pruning
- Deterministic preprocessing

## Risk 2: False confidence

A segment unnecessary for one request may matter for another.

Mitigation:

- Scope results to observed workloads
- Add multi-trace analysis later

## Risk 3: Model non-determinism

Mitigation:

- Temperature zero in MVP
- Reproducibility metadata

## Risk 4: Context interactions

Two segments may matter only together.

Mitigation:

- Group testing
- Hierarchical search
- Avoid perfect attribution claims

## Risk 5: Integration friction

Mitigation:

- Explicit SDK API first
- Automatic wrappers later

---

# 26. Roadmap

## V1 — Context Profiler and Minimizer

Goal:

> Prove that ContextLens can find behavior-preserving context reductions.

Features:

- Explicit instrumentation
- One provider adapter
- CLI
- Basic evaluators
- Hierarchical minimization

## V1.5 — Production integrations

- OpenAI SDK wrapper
- Framework integrations
- OpenTelemetry import

## V2 — Context regression testing

- Baselines
- Test suites
- Cost budgets
- CI integration

## V3 — Multi-trace learning

```text
1,000 production traces
        ↓
Find recurring context patterns
        ↓
Identify consistently irrelevant information
        ↓
Recommend global context policies
```

## V4 — Automated context optimization

Potentially generate:

- Retention policies
- Summarization policies
- Retrieval filters
- Caching opportunities

---

# 27. Competitive Positioning

ContextLens is not:

- Another LLM observability tool
- Another token counter
- Another generic prompt optimizer
- A model-attribution research library

It is:

> **A context efficiency testing tool for LLM applications.**

Core workflow:

```text
CAPTURE
   ↓
PROFILE
   ↓
EXPERIMENT
   ↓
VERIFY
   ↓
MINIMIZE
   ↓
PREVENT REGRESSIONS
```

---

# 28. Relationship to Deja

## Deja

```text
Capture interaction
      ↓
Replay consistently
      ↓
Test system behavior
```

## ContextLens

```text
Capture LLM execution
      ↓
Modify context systematically
      ↓
Replay variations
      ↓
Find efficient context
```

Deja asks:

> **Can this interaction be reliably reproduced?**

ContextLens asks:

> **How much of this interaction's context is actually necessary?**

---

# 29. Open Questions

## Q1: What is the default definition of behavior preservation?

Recommendation: there should be no universal definition. Require an evaluator, with convenient built-ins.

## Q2: Should ContextLens execute experiments automatically?

V1 answer: yes, within an explicit experiment budget.

## Q3: Wrapper or explicit SDK first?

Recommendation: explicit SDK first because context provenance is clearer.

## Q4: Should optimization work across multiple requests?

Not in V1. First prove single-execution minimization.

## Q5: Should summaries be generated automatically?

Not in V1. First reliably identify unnecessary context.

---

# 30. Success Criteria for V1

V1 succeeds if it can:

1. Capture a real LLM execution.
2. Represent context using explicit logical boundaries.
3. Profile token distribution.
4. Remove and replay context segments automatically.
5. Evaluate behavioral preservation.
6. Find meaningful context reductions.
7. Produce reproducible reports.
8. Complete analysis within a configurable experiment budget.

The desired measurable claim is:

> **ContextLens reduced effective context by X% on representative LLM workloads while preserving the configured behavioral contract.**

---

# 31. Final Product Definition

# ContextLens

**Tagline:**

> **Find the context your LLM actually needs.**

**One-line description:**

> ContextLens is an open-source testing and optimization tool that profiles LLM context, runs controlled context-removal experiments, and identifies ways to reduce tokens and cost while preserving application behavior.

The core idea is simple:

```text
Don't ask:

"How many tokens am I using?"

Ask:

"Which context can I remove without breaking the behavior I care about?"
```
