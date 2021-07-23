Inductive bool: Type :=
| true
| false.


Definition negb (x: bool): bool :=
  match x with
  | true => false
  | false => true
  end.


Theorem double: forall x: bool, negb (negb x) = x.
Proof.
  destruct x.
  - simpl. reflexivity.
  - simpl. reflexivity.
Qed.

Inductive color: Type :=
| Red
| Green
| Blue.

Definition shift (x: color): color :=
  match x with
  | Red => Green
  | Green => Blue
  | Blue => Red
  end.

Theorem shift3: forall x: color, shift (shift (shift x)) = x.
Proof.
  destruct x.
  - simpl. reflexivity.
  - simpl. reflexivity.
  - simpl. reflexivity.
Qed.

Theorem shift4: forall (x: color) (b: bool), shift (shift (shift x)) = x /\ negb (negb b) = b.
  destruct b.
  { destruct x.
    { simpl. split.
      - set (my_id := Red).
        reflexivity.
      - reflexivity.
    }
    { simpl. split.
      - reflexivity.
      - reflexivity.
    }
    { simpl. split.
      - reflexivity.
      - reflexivity.
    }
  }
  { destruct x.
    { simpl. split.
      - reflexivity.
      - reflexivity.
    }
    { simpl. split.
      - reflexivity.
      - reflexivity.
    }
    { simpl. split.
      - reflexivity.
      - reflexivity.
    }
  }
Qed.


Theorem shift5: forall (b: bool), negb (negb (negb b)) = negb b.
Proof.
  assert (H: forall x, negb (negb x) = x).
  intros x.
  destruct x.
  simpl.
  reflexivity.
  simpl.
  reflexivity.
  intros b.
  rewrite -> H.
  reflexivity.
Qed.

Theorem shift6: forall (b: bool), negb (negb (negb b)) = negb b.
Proof.
  intros b.
  set (id1 := negb b).
  apply double.
Qed.

  


