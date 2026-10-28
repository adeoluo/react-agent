# Data Card - ReAct Agent

The agent ships one small, synthetic data asset: the knowledge base behind the `search`
tool. There is no training data and nothing is downloaded.

## search knowledge base (`src/react_agent/tools/search.py`)

- **Provenance:** hand-authored for this project as a fixed in-memory dictionary of a few
  short, general-knowledge facts (capitals, a mountain, programming terms).
- **Composition:** roughly seven entries, each a keyword mapped to a one-sentence passage.
- **Purpose:** to give the `search` tool deterministic, offline behavior that resembles a
  real search tool from the agent's perspective.
- **Licensing:** authored by this repository; MIT.
- **Known biases and gaps:** tiny, English, general-knowledge only; it is a demonstration
  fixture, not a real corpus, and will return "No results." for anything outside it.

## Ethical considerations

The knowledge base contains no personal, sensitive, or copyrighted content. Users who
replace `search` with real retrieval take on the data governance of whatever source they
connect.
