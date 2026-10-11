# The Aphelion Deep — Tuning and Design Claims (v0.1)

Balance knobs and the machine-checkable claims that guard them. The claims are
evaluated by the Monte-Carlo harness (`gamespec.sim`) via
`simulation/test_sim_claims.py`, so a regression in balance fails the run.

```yaml
tuning:
  id: reactor_pressure
  affected_mechanics: [mechanism.advance_reactor, mechanism.stabilise_reactor]
  intended_directional_effect: raising containment_needed or lowering max_phase makes the clock harder to beat
  bounds: containment_needed 2..4; max_phase 5..7
  maturity: provisional

# The cooperative clock must actually threaten naive play — it should neither be a
# free win nor near-hopeless under a policy that plays with no skill.
design_claim:
  id: naive_play_is_threatened
  claim: a naive baseline neither trivially wins nor is near-hopeless
  metric: win_rate
  bound: "< 0.65"
  runs: 600
  policy: naive
  supports: [game.stabilise_the_reactor]

design_claim:
  id: real_jeopardy
  claim: the reactor defeats naive play a meaningful share of the time
  metric: defeat_rate
  bound: "> 0.2"
  runs: 600
  policy: naive
  supports: [automation.reactor_countdown]
```
