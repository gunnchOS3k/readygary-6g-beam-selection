# ReadyGary as optional Gate 2 provider

ReadyGary is optional for Gate 2. When beam outputs are unavailable, the
integrated Edge→7GC→SpectrumX→NTN path continues and states that beam actions
were not used.

When available, AI-RAN may attach optional fields:

- candidate_beams
- selected_beam
- expected_sinr_db
- beam_switch_cost_ms
- model_runtime_ms

Evidence labels must remain honest. Toy benchmark paths are not field evidence.
