# Repro 3: even the mutation gate stayed silent

Against the APS repo (any clone):

    git clone https://github.com/unclebob/Acceptance-Pipeline-Specification
    cd Acceptance-Pipeline-Specification
    ../Tools/unclebob/mutator/mutator bb/src/aps/heldout.clj   # or your local mutator

Observed (2026-11-12): 41 mutation sites, 0 killed, 0 survived, 41
uncovered, score n/a. The mutation gate, the classic anti-oracle tool,
reported a clean-looking table while in fact it saw nothing: the coverage
hand-off for this layer is not wired. A green gate with no vision is a
silent-but-valid failure in the gate itself.
