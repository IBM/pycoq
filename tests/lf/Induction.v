(** * Induction: Proof by Induction *)

(** Before getting started, we need to import all of our
    definitions from the previous chapter: *)

From LF Require Export Basics.


(* Require Export Basics. *)

(** For the [Require Export] to work, Coq needs to be able to
    find a compiled version of [Basics.v], called [Basics.vo], in a directory
    associated with the prefix [LF].  This file is analogous to the [.class]
    files compiled from [.java] source files and the [.o] files compiled from
    [.c] files.

    First create a file named [_CoqProject] containing the following line
    (if you obtained the whole volume "Logical Foundations" as a single
    archive, a [_CoqProject] should already exist and you can skip this step):

      [-Q . LF]

    This maps the current directory ("[.]", which contains [Basics.v],
    [Induction.v], etc.) to the prefix (or "logical directory") "[LF]".
    PG and CoqIDE read [_CoqProject] automatically, so they know to where to
    look for the file [Basics.vo] corresponding to the library [LF.Basics].

    Once [_CoqProject] is thus created, there are various ways to build
    [Basics.vo]:

     - In Proof General: The compilation can be made to happen automatically
       when you submit the [Require] line above to PG, by setting the emacs
       variable [coq-compile-before-require] to [t].

     - In CoqIDE: Open [Basics.v]; then, in the "Compile" menu, click
       on "Compile Buffer".

     - From the command line: Generate a [Makefile] using the [coq_makefile]
       utility, that comes installed with Coq (if you obtained the whole
       volume as a single archive, a [Makefile] should already exist
       and you can skip this step):

         [coq_makefile -f _CoqProject *.v -o Makefile]

       Note: You should rerun that command whenever you add or remove Coq files
       to the directory.

       Then you can compile [Basics.v] by running [make] with the corresponding
       [.vo] file as a target:

         [make Basics.vo]

       All files in the directory can be compiled by giving no arguments:

         [make]

       Under the hood, [make] uses the Coq compiler, [coqc].  You can also
       run [coqc] directly:

         [coqc -Q . LF Basics.v]

       But [make] also calculates dependencies between source files to compile
       them in the right order, so [make] should generally be prefered over
       explicit [coqc].

    If you have trouble (e.g., if you get complaints about missing
    identifiers later in the file), it may be because the "load path"
    for Coq is not set up correctly.  The [Print LoadPath.] command
    may be helpful in sorting out such issues.

    In particular, if you see a message like

        [Compiled library Foo makes inconsistent assumptions over
        library Bar]

    check whether you have multiple installations of Coq on your machine.
    It may be that commands (like [coqc]) that you execute in a terminal
    window are getting a different version of Coq than commands executed by
    Proof General or CoqIDE.

    - Another common reason is that the library [Bar] was modified and
      recompiled without also recompiling [Foo] which depends on it.  Recompile
      [Foo], or everything if too many files are affected.  (Using the third
      solution above: [make clean; make].)

    One more tip for CoqIDE users: If you see messages like [Error:
    Unable to locate library Basics], a likely reason is
    inconsistencies between compiling things _within CoqIDE_ vs _using
    [coqc] from the command line_.  This typically happens when there
    are two incompatible versions of [coqc] installed on your
    system (one associated with CoqIDE, and one associated with [coqc]
    from the terminal).  The workaround for this situation is
    compiling using CoqIDE only (i.e. choosing "make" from the menu),
    and avoiding using [coqc] directly at all. *)

(* ################################################################# *)
(** * Proof by Induction *)

(** We proved in the last chapter that [0] is a neutral element
    for [+] on the left, using an easy argument based on
    simplification.  We also observed that proving the fact that it is
    also a neutral element on the _right_... *)

Theorem plus_n_O_firsttry: forall n: nat,
    n = n + 0.
Proof.
  intros n.
  simpl.
Abort.



Theorem plus_n_O_firsttry : forall n:nat,
  n = n + 0.

(** ... can't be done in the same simple way.  Just applying
  [reflexivity] doesn't work, since the [n] in [n + 0] is an arbitrary
  unknown number, so the [match] in the definition of [+] can't be
  simplified.  *)

Proof.
  intros n.
  simpl. (* Does nothing! *)
Abort.

(** And reasoning by cases using [destruct n] doesn't get us much
    further: the branch of the case analysis where we assume [n = 0]
    goes through fine, but in the branch where [n = S n'] for some [n'] we
    get stuck in exactly the same way. *)

Theorem plus_n_O_secondtry : forall n:nat,
  n = n + 0.
Proof.
  intros n. destruct n as [| n'] eqn:E.
  - (* n = 0 *)
    reflexivity. (* so far so good... *)
  - (* n = S n' *)
    simpl.       (* ...but here we are stuck again *)
Abort.

(** We could use [destruct n'] to get one step further, but,
    since [n] can be arbitrarily large, if we just go on like this
    we'll never finish. *)

(** To prove interesting facts about numbers, lists, and other
    inductively defined sets, we usually need a more powerful
    reasoning principle: _induction_.

    Recall (from high school, a discrete math course, etc.) the
    _principle of induction over natural numbers_: If [P(n)] is some
    proposition involving a natural number [n] and we want to show
    that [P] holds for all numbers [n], we can reason like this:
         - show that [P(O)] holds;
         - show that, for any [n'], if [P(n')] holds, then so does
           [P(S n')];
         - conclude that [P(n)] holds for all [n].

    In Coq, the steps are the same: we begin with the goal of proving
    [P(n)] for all [n] and break it down (by applying the [induction]
    tactic) into two separate subgoals: one where we must show [P(O)]
    and another where we must show [P(n') -> P(S n')].  Here's how
    this works for the theorem at hand: *)

Theorem plus_n_O: forall n: nat, n = n + 0.
  intros n. induction n as [| n1 IHn1].
  - simpl. reflexivity.
  - simpl. rewrite <- IHn1. reflexivity.
Qed.



Theorem minus_diag: forall n,
    minus n n = 0.
Proof.
  intros n. induction n as [| n1 IHn1].
  - simpl. reflexivity.
  - simpl. rewrite -> IHn1. reflexivity.
Qed.



Theorem mult_0_r: forall n: nat,
    n * 0 = 0.
Proof.
  intros n. induction n as [| n1 IHn1].
  - simpl. reflexivity.
  - simpl. rewrite -> IHn1. reflexivity.
Qed.

Theorem plus_n_Sm: forall n m: nat,  S (n + m) = n + (S m).
Proof.
  intros n m. induction n as [| n1 IHn1].
  - simpl. reflexivity.
  - simpl. rewrite -> IHn1. reflexivity.
Qed.


Theorem plus_comm: forall n m: nat, n + m = m + n.
Proof.
  intros n m. induction n as [|n1 IHn1].
  - rewrite <- plus_n_O. simpl. reflexivity.
  - rewrite <- plus_n_Sm. simpl. rewrite -> IHn1. reflexivity.
Qed.



Theorem plus_assoc: forall n m p: nat, n + (m + p) = (n + m) + p.
  intros n m p. induction n as [| n1 IHn1].
  - simpl. reflexivity.
  - simpl. rewrite -> IHn1. reflexivity.
Qed.



Fixpoint double (n: nat) :=
  match n with
  | O => 0
  | S n' => S (S (double n'))
  end.

Lemma double_plus: forall n, double n = n + n.
  intros n. induction n as [| n1 IHn1].
  - simpl. reflexivity.
  - simpl. rewrite -> IHn1. rewrite -> plus_n_Sm. reflexivity.
Qed.


Theorem evenb_S: forall n: nat,
    evenb (S n) = negb (evenb n).
Proof.
  intros n. induction n as [| n1 IHn1].
  - simpl. reflexivity.
  - rewrite -> IHn1. simpl. simpl. rewrite -> negb_involutive. reflexivity.
Qed.

(** **** Exercise: 1 star, standard (destruct_induction)  

    Briefly explain the difference between the tactics [destruct]
    and [induction].

 destruct: expands the definition of function
 induction: creates two subgoals to prove by induction. 
 *)

Definition manual_grade_for_destruct_induction : option (nat*string) := None.
(** [] *)


Theorem mult_0_plus': forall n m: nat,
    (0 + n) * m = n * m.
Proof.
  intros n m.
  assert (H: 0 + n = n). { reflexivity. }
                         rewrite -> H. reflexivity.
Qed.


(** For example, suppose we want to prove that [(n + m) + (p + q)
    = (m + n) + (p + q)]. The only difference between the two sides of
    the [=] is that the arguments [m] and [n] to the first inner [+]
    are swapped, so it seems we should be able to use the
    commutativity of addition ([plus_comm]) to rewrite one into the
    other.  However, the [rewrite] tactic is not very smart about
    _where_ it applies the rewrite.  There are three uses of [+] here,
    and it turns out that doing [rewrite -> plus_comm] will affect
    only the _outer_ one... *)


Theorem plus_rearrange_firsttry: forall n m p q: nat,
    (n + m) + (p + q) = (m + n) + (p + q).
Proof.
  intros n m p q. rewrite plus_comm.
Abort. (* does not work, coq rewrites the wrong plus! *)


Theorem plus_rearrange_secondtry: forall n m p q: nat,
    (n + m) + (p + q) = (m + n) + (p + q).
Proof.
  intros n m p q.
  assert (H: n + m = m + n). { rewrite -> plus_comm. reflexivity. }
                             rewrite -> H. reflexivity.
Qed.



(* 
    Because we are using Coq in this course, we will be working
    heavily with formal proofs.  But this doesn't mean we can
    completely forget about informal ones!  Formal proofs are useful
    in many ways, but they are _not_ very efficient ways of
    communicating ideas between human beings. *)

(** For example, here is a proof that addition is associative: *)

Theorem plus_assoc': forall n m p: nat,
    n + (m + p) = (n + m) + p.
Proof. intros n m p. induction n as [| n1 IHn1].
       - reflexivity.
       - simpl. rewrite -> IHn1. reflexivity.
Qed.

Theorem plus_assoc'': forall n m p: nat,
    n + (m + p) = (n + m) + p.
  intros n m p. induction n as [|n1 IHn1].
  - (* n = 0 *)
    reflexivity.
  - (* n = S n' *)
    simpl. rewrite -> IHn1. reflexivity.
Qed.


Theorem plus_comm1: forall n m: nat, n + m = m + n.
Proof. induction n as [|n1 IHn1].
       - simpl. induction m.
         { simpl. reflexivity. }
         { simpl. rewrite <- IHm. reflexivity. }
       - simpl. intros m. rewrite -> IHn1. simpl.
         induction m as [|m1 IHm1].
         { simpl. reflexivity. }
         { simpl. rewrite -> IHm1. reflexivity. }
Qed.

(* Do not modify the following line: *)
Definition manual_grade_for_plus_comm_informal : option (nat*string) := None.
(** [] *)



(* We'll prove that n + m = m + n by induction on n. 
  - first we'll need to show that 0 + m = m + 0. 
       this we'll show by induction on m
              - 0 + 0 = 0 + 0 follows from reflexivity
              - from 0 + m = m + 0  need to show that 0 + Sm = Sm + 0
                by def of + we have 0 + Sm = Sm
                and Sm + 0 = S(m + 0) = (by induction hypothesis) = Sm
 - now from n + m = m + n we'll show Sn + m = m + Sn
   by def of + we've got Sn + m = S(n + m)
   by induction hypothesis we have S(n + m) = S(m + n)
   need to show that S(m + n) = m + Sn
   we'll do induction on m:
     - prove that S(0 + n) = 0 + Sn; from def of + we've got Sn = Sn
     - now show that S(Sm + n) = Sm + Sn, indeed, by def of + we've got
     to show that S(S(m+n)) = S(m + Sn) which follows from induction hypothesis 
 *)





(** **** Exercise: 2 stars, standard, optional (eqb_refl_informal)  

    Write an informal proof of the following theorem, using the
    informal proof of [plus_assoc] as a model.  Don't just
    paraphrase the Coq tactics into English!

    Theorem: [true = n =? n] for any [n].


    [] *)
Fixpoint eqb (n m : nat) : bool :=
  match n with
  | O => match m with
         | O => true
         | S m' => false
         end
  | S n' => match m with
            | O => false
            | S m' => eqb n' m'
            end
  end.

Theorem eqb_refl: forall n, eqb n n = true.
Proof. induction n as [|n1 IHn1].
       - simpl. reflexivity.
       - simpl. rewrite -> IHn1. reflexivity.
Qed.



(* ################################################################# *)
(** * More Exercises *)

(** **** Exercise: 3 stars, standard, recommended (mult_comm)  

    Use [assert] to help prove this theorem.  You shouldn't need to
    use induction on [plus_swap]. *)

Theorem plus_swap : forall n m p : nat,
    n + (m + p) = m + (n + p).
Proof.
  intros n m p. rewrite -> plus_assoc. rewrite -> plus_assoc.
  assert (H: n + m = m + n). { rewrite -> plus_comm. reflexivity. }
                             rewrite -> H. reflexivity.
Qed.


Theorem mult_one: forall n: nat,  1 * n = n.
Proof.  simpl. intros n. rewrite plus_comm. simpl. reflexivity.
Qed.


Theorem mult_one1: forall n: nat,  n * 1 = n.
Proof. intros n. induction n.
       - simpl. reflexivity.
       -  simpl. rewrite -> IHn. reflexivity.
Qed.


Theorem mult_zero: forall n: nat, 0 * n = 0.
  intros n. simpl. reflexivity. Qed.

Theorem mult_zero1: forall n: nat,  n * 0 = 0.
  intros n. induction n.
  - simpl. reflexivity.
  - simpl. exact IHn. Qed.

Theorem aux_lemma: forall m n: nat, n * m + n = n * S m.
  intros m n. induction n.
  - simpl. reflexivity.
  - simpl. rewrite <- IHn.
    assert (H: m + (n * m + n) = m + n * m + n).
    { rewrite plus_assoc. reflexivity. }
    rewrite -> H. assert (H1: m + n * m + S n = S n + m + n * m).
    { rewrite plus_comm. rewrite plus_assoc. reflexivity. }
    rewrite -> H1. simpl. assert ( m + n * m + n = n + (m  + n * m)).
    { rewrite plus_comm.  reflexivity. }
    rewrite -> H0. simpl. assert ( n + (m + n * m) = (n + m) + n * m).
    { rewrite plus_assoc. reflexivity. }
    rewrite -> H2. reflexivity.
Qed.

  

  (* FILL IN HERE *)

(** Now prove commutativity of multiplication.  (You will probably
    need to define and prove a separate subsidiary theorem to be used
    in the proof of this one.  You may find that [plus_swap] comes in
    handy.) *)


Theorem mult_comm: forall m n: nat, m * n = n * m.
  intros m n. induction m. simpl.
  induction n. { simpl. reflexivity. }
               { simpl. exact IHn. }
               { simpl. rewrite -> IHm.
                 rewrite plus_comm. rewrite -> aux_lemma. reflexivity. }
Qed.




(** **** Exercise: 3 stars, standard, optional (more_exercises)  

    Take a piece of paper.  For each of the following theorems, first
    _think_ about whether (a) it can be proved using only
    simplification and rewriting, (b) it also requires case
    analysis ([destruct]), or (c) it also requires induction.  Write
    down your prediction.  Then fill in the proof.  (There is no need
    to turn in your piece of paper; this is just to encourage you to
    reflect before you hack!) *)



Theorem leb_refl : forall n:nat,   true = (n <=? n).
  induction n.
  - simpl. reflexivity.
  - simpl. exact IHn.
Qed.


Theorem zero_nbeq_S : forall n:nat,
  0 =? (S n) = false.
Proof.
  destruct n.
  - simpl. reflexivity.
  - simpl. reflexivity.
Qed.

Theorem andb_false_r : forall b : bool, andb b false = false.
Proof.
  destruct b.
  - simpl. reflexivity.
  - simpl. reflexivity.
Qed.


Theorem plus_ble_compat_l : forall n m p : nat,
  n <=? m = true -> (p + n) <=? (p + m) = true.
Proof.
  induction p.
  - intros. simpl. exact H.
  - simpl. exact IHp.
Qed.


Theorem S_nbeq_0: forall n: nat,  (S n ) =? 0 = false.
  intros. simpl. reflexivity.
Qed.


Theorem mult_1_l: forall n: nat,  1 * n = n.
  intros. simpl. rewrite <- plus_n_O. reflexivity.
Qed.



Theorem all3_spec : forall b c : bool,    orb
      (andb b c)
      (orb (negb b)
               (negb c))
    = true.
  destruct b.
  - destruct c. simpl. reflexivity.
    simpl. reflexivity.
  - destruct c. simpl. reflexivity.
    simpl. reflexivity.
Qed.

Theorem  mult_plus_distr_r: forall n m p: nat, (n + m) * p = (n * p) + (m * p).
  induction n.
  { induction m.
    - intros. simpl. reflexivity.
    - simpl. reflexivity.
  }
  { intros. simpl. rewrite -> IHn. rewrite -> plus_assoc. reflexivity. }
Qed.


Theorem mult_assoc: forall n m p: nat, n * (m * p) = (n * m) * p.
  induction n.
  { simpl. reflexivity. }
  { simpl. intros. rewrite -> IHn. rewrite mult_plus_distr_r. reflexivity. }
Qed.

(** **** Exercise: 2 stars, standard, optional (eqb_refl)  

    Prove the following theorem.  (Putting the [true] on the left-hand
    side of the equality may look odd, but this is how the theorem is
    stated in the Coq standard library, so we follow suit.  Rewriting
    works equally well in either direction, so we will have no problem
    using the theorem no matter which way we state it.) *)

Theorem eqb_refl': forall n: nat, true = (n =? n).
  intros. induction n.
  - simpl. reflexivity.
  - simpl. exact IHn. 
Qed.


(** **** Exercise: 2 stars, standard, optional (plus_swap')  

    The [replace] tactic allows you to specify a particular subterm to
   rewrite and what you want it rewritten to: [replace (t) with (u)]
   replaces (all copies of) expression [t] in the goal by expression
   [u], and generates [t = u] as an additional subgoal. This is often
   useful when a plain [rewrite] acts on the wrong part of the goal.

   Use the [replace] tactic to do a proof of [plus_swap'], just like
   [plus_swap] but without needing [assert (n + m = m + n)]. *)


Theorem plus_swap': forall n m p: nat, n + (m + p) = m + (n + p).
  intros. rewrite plus_assoc. rewrite plus_assoc.
  replace (n + m) with (m + n).
  - reflexivity.
  - rewrite plus_comm. reflexivity.
Qed.







(** **** Exercise: 3 stars, standard, recommended (binary_commute)  

    Recall the [incr] and [bin_to_nat] functions that you
    wrote for the [binary] exercise in the [Basics] chapter.  Prove
    that the following diagram commutes:

                            incr
              bin ----------------------> bin
               |                           |
    bin_to_nat |                           |  bin_to_nat
               |                           |
               v                           v
              nat ----------------------> nat
                             S

    That is, incrementing a binary number and then converting it to
    a (unary) natural number yields the same result as first converting
    it to a natural number and then incrementing.
    Name your theorem [bin_to_nat_pres_incr] ("pres" for "preserves").

    Before you start working on this exercise, copy the definitions
    from your solution to the [binary] exercise here so that this file
    can be graded on its own.  If you want to change your original
    definitions to make the property easier to prove, feel free to
    do so! *)

(* FILL IN HERE *)

(* Do not modify the following line: *)

Theorem S_plus: forall a b: nat, S (a + b) = a + S b.
  intros. induction a.
  - simpl. reflexivity.
  - simpl. rewrite -> IHa. reflexivity.
Qed.


Theorem binary_commute: forall n: bin, bin_to_nat (incr n) = S (bin_to_nat n).
  induction n.
  - simpl. reflexivity.
  - simpl. reflexivity.
  - simpl. assert (H: bin_to_nat (incr n) + 0 = bin_to_nat (incr n)).
    { rewrite <- plus_n_O. reflexivity. }
    assert (H1: bin_to_nat n + 0 = bin_to_nat n).
    { rewrite <- plus_n_O. reflexivity. }
    { rewrite -> H. rewrite H1.
      simpl. rewrite -> IHn. simpl.
      rewrite <- S_plus. reflexivity.
    }
Qed.

Definition manual_grade_for_binary_commute : option (nat*string) := None.
(** [] *)

(** **** Exercise: 5 stars, advanced (binary_inverse)  

    This is a further continuation of the previous exercises about
    binary numbers.  You may find you need to go back and change your
    earlier definitions to get things to work here.

    (a) First, write a function to convert natural numbers to binary
        numbers. *)

Fixpoint nat_to_bin (n: nat): bin :=
  match n with
  | O => Z
  | S n => incr (nat_to_bin n)
  end.


Theorem  helper_nat_bin: forall b: bin, bin_to_nat (incr b) = S (bin_to_nat b).
  intros. simpl.
  induction b.
  - simpl. reflexivity.
  - simpl. reflexivity.
  - simpl. rewrite <- plus_n_O. rewrite <- plus_n_O. simpl.
    rewrite IHb. rewrite <- S_plus. simpl. reflexivity.
Qed.

    
Theorem nat_bin_nat: forall n, bin_to_nat (nat_to_bin n) = n.
  intros. induction n.
  - simpl. reflexivity.
  - simpl. rewrite -> helper_nat_bin. rewrite -> IHn. reflexivity.
Qed.




(* Do not modify the following line: *)
Definition manual_grade_for_binary_inverse_a : option (nat*string) := None.

(** (b) One might naturally expect that we should also prove the
        opposite direction -- that starting with a binary number,
        converting to a natural, and then back to binary should yield
        the same number we started with.  However, this is not the
        case!  Explain (in a comment) what the problem is. *)

(* The problem is that we can add leading zeroes without changing the binary 
number *) 

Compute bin_to_nat (A (B Z)).             (* 2 *)
Compute bin_to_nat (A (B (A (A Z)))).

(* FILL IN HERE *)



(* it is very difficult to prove when normalization function is defined using the reverse

Fixpoint rev_bin_helper (b: bin) (acc: bin) :=
  match b with
  | Z => acc
  | A b => rev_bin_helper b (A acc)
  | B b => rev_bin_helper b (B acc)
  end.

Fixpoint rev_bin (b: bin) :=
  rev_bin_helper b Z.

Compute rev_bin (A (B (A (A Z)))).


Fixpoint rev_norm (b: bin) :=
  match b with
    | Z => Z
    | A b0 => rev_norm b0
    | B b0 => B b0
  end.


Fixpoint norm_old (b: bin) := rev_bin (rev_norm (rev_bin b)).
*)

Fixpoint norm (b: bin) :=
  match b with
  | Z => Z
  | A b1 => match norm b1 with
           | Z => Z
           | A b0 => A (norm b1)
           | B b0 => A (norm b1)
           end
  | B b1 => B (norm b1)
  end.


Theorem norm_B_comm: forall (b: bin), norm (B b) = B (norm b).
  intros b. simpl. reflexivity.
Qed.


Theorem incr_norm_A_b: forall (b: bin), incr (norm (A b)) = B (norm b).
  intros. simpl. destruct (norm b).
  { simpl. reflexivity. }
  { simpl. reflexivity. }
  { simpl. reflexivity. }
Qed.

Theorem norm_A_incr_B_b: forall (b: bin), norm (A (incr b)) = A (norm (incr b)).
  intros b.
  simpl norm at 1.
  induction b.
  { simpl. reflexivity. }
  { simpl. reflexivity. }
  { simpl incr at 1. simpl norm at 1. rewrite -> IHb.
    reflexivity.
  }
Qed.

Theorem incr_norm_comm: forall (b: bin), incr (norm b) = norm (incr b).
  intros b. induction b.
  { simpl. reflexivity. }
  { assert (H: incr (A b) = B b). {simpl. reflexivity. } rewrite -> H.
    rewrite -> norm_B_comm.
    rewrite -> incr_norm_A_b.
    reflexivity. }
  { assert (H: incr (B b) = A (incr b)). {simpl. reflexivity. } rewrite -> H.
    rewrite -> norm_B_comm.
    assert (H1: incr (B (norm b)) = A (incr (norm b))). {simpl. reflexivity. } rewrite -> H1.
    rewrite -> IHb. destruct b.
    { simpl. reflexivity. }
    { simpl. reflexivity. }
    { rewrite -> norm_A_incr_B_b. reflexivity. }
  }
Qed.



Theorem norm_nat_to_bin: forall (n: nat), norm (nat_to_bin n) = nat_to_bin n.
  intros. induction n.
  { simpl. reflexivity. }
  { simpl. rewrite <- incr_norm_comm. rewrite -> IHn. reflexivity. }
Qed.


Theorem A_incr_b: forall (b: bin), A (incr b) = incr (incr (A b)).
  simpl. reflexivity.
Qed.




Theorem norm_A_natbin_n: forall (n: nat), norm (A (nat_to_bin n)) = nat_to_bin (n + n).
  intros n.
  induction n.
  { simpl. reflexivity. }
  { simpl plus. rewrite -> plus_comm. simpl plus.
    simpl nat_to_bin at 2. simpl nat_to_bin at 1.
    rewrite <- IHn. rewrite -> incr_norm_comm. rewrite -> incr_norm_comm.
    rewrite <- A_incr_b. reflexivity.
  }
Qed.


Lemma norm_caseA: forall (b: bin), norm (norm b) = norm b -> norm (norm (A b)) = norm (A b).
  intros b. intros IHb.
  simpl norm at 3. rewrite <- IHb.
  simpl.
  destruct (norm b).
  - simpl. reflexivity.
  - simpl. reflexivity.
  - simpl. reflexivity.
Qed.


  
Theorem norm_norm: forall (b: bin), norm (norm b) = norm b.
  induction b.
  { simpl. reflexivity. }
  { revert IHb. revert b. exact norm_caseA. }
  { simpl. rewrite IHb. reflexivity. }
Qed.


    
Theorem bin_nat_bin: forall (b: bin), nat_to_bin (bin_to_nat b) = norm b.
  intros. induction b.
  { simpl. reflexivity. }
  { simpl bin_to_nat at 1.
    assert (H: (bin_to_nat b + 0) = bin_to_nat b).
    { rewrite <- plus_n_O. reflexivity. }
    rewrite -> H. rewrite <- norm_A_natbin_n.
    rewrite -> IHb.
    simpl. rewrite -> norm_norm. reflexivity.
  }
  { simpl bin_to_nat.
    assert (HH: (bin_to_nat b  + 0) = bin_to_nat b).
    { rewrite <- plus_n_O. reflexivity. }
    rewrite -> HH.
    simpl nat_to_bin. rewrite <- norm_A_natbin_n. simpl incr. simpl norm at 4.
    rewrite -> IHb. rewrite -> norm_norm. simpl.
    destruct (norm b).
    { simpl. reflexivity. }
    { simpl. reflexivity. }
    { simpl. reflexivity. }
  }
Qed.



(* Do not modify the following line: *)
Definition manual_grade_for_binary_inverse_b : option (nat*string) := None.

(** (c) Define a normalization function -- i.e., a function
        [normalize] going directly from [bin] to [bin] (i.e., _not_ by
        converting to [nat] and back) such that, for any binary number
        [b], converting [b] to a natural and then back to binary yields
        [(normalize b)].  Prove it.  (Warning: This part is a bit
        tricky -- you may end up defining several auxiliary lemmas.
        One good way to find out what you need is to start by trying
        to prove the main statement, see where you get stuck, and see
        if you can find a lemma -- perhaps requiring its own inductive
        proof -- that will allow the main proof to make progress.) Don't
        define thi using nat_to_bin and bin_to_nat! *)

(* FILL IN HERE *)

(* Do not modify the following line: *)
Definition manual_grade_for_binary_inverse_c : option (nat*string) := None.
(** [] *)


(* Wed Jan 9 12:02:44 EST 2019 *)
