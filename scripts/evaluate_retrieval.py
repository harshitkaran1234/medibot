"""Compare dense-only vs hybrid retrieval on a small labelled test set.

A question counts as answered at rank r if the r-th retrieved chunk contains ALL of its
`must_contain` strings (i.e. the chunk actually holds the answer, not just the topic).

    poetry run python scripts/evaluate_retrieval.py
"""

from dataclasses import dataclass

from langchain_qdrant import RetrievalMode

from medibot.core.rbac import Role
from medibot.core.retrieval import retrieve


@dataclass
class EvalCase:
    role: Role
    question: str
    must_contain: list[str]
    kind: str  # "exact" (codes, drug names, ids) or "conceptual" (paraphrased)


EVAL_SET: list[EvalCase] = [
    # --- exact terms: codes, drug names, identifiers ---
    EvalCase(
        Role.BILLING_EXECUTIVE,
        "Is pre-authorisation required for E11.9?",
        ["E11.9, Pre-auth"],
        "exact",
    ),
    EvalCase(
        Role.BILLING_EXECUTIVE,
        "What is the package rate for PROC-CARD-03?",
        ["PROC-CARD-03, Package"],
        "exact",
    ),
    EvalCase(
        Role.BILLING_EXECUTIVE,
        "How should we respond to a rejection under EXCL-04?",
        ["EXCL-04"],
        "exact",
    ),
    EvalCase(
        Role.BILLING_EXECUTIVE,
        "What is the TPA contact number for United India?",
        ["1800-425-3333"],
        "exact",
    ),
    EvalCase(
        Role.TECHNICIAN,
        "What does fault code F-12 mean on the infusion pump?",
        ["F-12, Meaning = Drug library"],
        "exact",
    ),
    EvalCase(
        Role.TECHNICIAN,
        "What does error E-04 mean on the SterilPro 3000 autoclave?",
        ["E-04, Meaning = Steam generator"],
        "exact",
    ),
    EvalCase(
        Role.TECHNICIAN,
        "What occlusion pressure alarm threshold should be used for venous lines?",
        ["Venous lines"],
        "exact",
    ),
    EvalCase(
        Role.DOCTOR,
        "What is the standard dose of Piperacillin-Tazobactam?",
        ["Piperacillin-Tazobactam, Standard Dose"],
        "exact",
    ),
    EvalCase(
        Role.DOCTOR,
        "How should Meropenem be dosed when eGFR is below 30?",
        ["Meropenem, eGFR < 30"],
        "exact",
    ),
    EvalCase(
        Role.DOCTOR, "What is the critical value for potassium?", ["Potassium, Critical"], "exact"
    ),
    EvalCase(
        Role.NURSE,
        "What cannula gauge should be used for a paediatric patient under 5 kg?",
        ["Paediatric < 5 kg, Recommended Gauge"],
        "exact",
    ),
    # --- conceptual / paraphrased: the question does not reuse the document's wording ---
    EvalCase(
        Role.DOCTOR,
        "What is the first-line drug for high blood pressure?",
        ["Amlodipine 5 mg OD"],
        "conceptual",
    ),
    EvalCase(
        Role.DOCTOR,
        "Which antibiotics raise INR in a patient on warfarin?",
        ["Warfarin + Metronidazole"],
        "conceptual",
    ),
    EvalCase(
        Role.NURSE,
        "How long should I rub my hands with alcohol sanitiser?",
        ["alcohol-based hand rub 20-30 seconds"],
        "conceptual",
    ),
    EvalCase(
        Role.NURSE,
        "What should I do right after pricking myself with a used needle?",
        ["Encourage the wound to bleed"],
        "conceptual",
    ),
    EvalCase(
        Role.NURSE,
        "How often must a restrained patient's limb be checked?",
        ["Neurovascular check every 2 hours"],
        "conceptual",
    ),
    EvalCase(
        Role.NURSE,
        "Which bin do glass vials and needles go into?",
        ["Glassware & sharps"],
        "conceptual",
    ),
    EvalCase(
        Role.TECHNICIAN,
        "The portable x-ray detector shows a blank image, what should I check?",
        ["X-ray panel image blank"],
        "conceptual",
    ),
    EvalCase(
        Role.BILLING_EXECUTIVE,
        "What extra verification is needed for a claim above two lakh rupees?",
        ["Mandatory dual-check"],
        "conceptual",
    ),
    EvalCase(
        Role.NURSE, "Who do I phone if a colleague collapses at work?", ["7777"], "conceptual"
    ),
    EvalCase(
        Role.TECHNICIAN,
        "How much notice must clinical staff give before resigning?",
        ["60 days for clinical staff"],
        "conceptual",
    ),
    EvalCase(
        Role.BILLING_EXECUTIVE,
        "Can I accept an expensive gift from a vendor?",
        ["above ₹2,000 must be refused"],
        "conceptual",
    ),
]


def first_hit_rank(case: EvalCase, mode: RetrievalMode, k: int = 10) -> int | None:
    for rank, doc in enumerate(retrieve(case.question, case.role, k=k, mode=mode), start=1):
        if all(text in doc.page_content for text in case.must_contain):
            return rank
    return None


def summarise(ranks: list[int | None]) -> str:
    def hit_at(k: int) -> float:
        return sum(r is not None and r <= k for r in ranks) / len(ranks)

    mrr = sum(1 / r for r in ranks if r) / len(ranks)
    return f"Hit@1 {hit_at(1):.2f}  Hit@3 {hit_at(3):.2f}  Hit@10 {hit_at(10):.2f}  MRR {mrr:.3f}"


def main() -> None:
    modes = (RetrievalMode.DENSE, RetrievalMode.HYBRID)
    ranks: dict[RetrievalMode, list[int | None]] = {mode: [] for mode in modes}

    print(f"{'kind':<11} {'role':<18} {'question':<66} dense  hybrid")
    for case in EVAL_SET:
        row = [first_hit_rank(case, mode) for mode in modes]
        for mode, rank in zip(modes, row):
            ranks[mode].append(rank)
        cells = [str(r) if r else "-" for r in row]
        question = case.question[:64]
        print(f"{case.kind:<11} {case.role.value:<18} {question:<66} {cells[0]:>5}  {cells[1]:>6}")

    for kind in ("exact", "conceptual", None):
        idx = [i for i, c in enumerate(EVAL_SET) if kind is None or c.kind == kind]
        print(f"\n[{kind or 'all'}] ({len(idx)} questions)")
        for mode in modes:
            print(f"  {mode.value:<7} {summarise([ranks[mode][i] for i in idx])}")


if __name__ == "__main__":
    main()
