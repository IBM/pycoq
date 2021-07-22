Theorem th1: forall A B: Prop, A -> A -> (A->B) -> B.
Proof.
  intros A B.
  intros a0 a1.
  intros ab.
  apply ab.
  exact a1.
Qed.
