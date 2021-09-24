Inductive day: Type :=
| monday
| tuesday
| wednesday
| thursday
| friday
| saturday
| sunday.


Definition next_weekday (d: day): day :=
  match d with
  | monday => tuesday
  | tuesday => wednesday
  | wednesday => thursday
  | thursday => friday                   
  | friday => monday
  | saturday => monday
  | sunday => monday
  end.

Compute (next_weekday friday).


Example test_next_weekday:
  (next_weekday (next_weekday saturday)) = tuesday.
simpl. reflexivity. Qed.


Inductive bool: Type :=
| true
| false.


Definition negb (x: bool): bool :=
  match x with
  | true => false
  | false => true
  end.

Definition andb (x: bool) (y: bool): bool :=
  match x, y with
  | true, true => true
  | true, false => false
  | false, true => false
  | false, false => false
  end.

Definition orb (x: bool) (y: bool) : bool :=
  match x, y with
  | true, true => true
  | true, false => true
  | false, true => true
  | false, false => false
  end.

Example test_orb1: (orb true false) = true.
simpl. reflexivity. Qed.

Example test_orb2: (orb false false) = false.
simpl. reflexivity. Qed.

Example test_orb3: (orb false true) = true.
simpl. reflexivity. Qed.

Example test_orb4: (orb true true) = true.
simpl. reflexivity. Qed.

Notation "x || y" := (orb x y).
Notation "x && y" := (andb x y).

Example test_orb5: (false || false || true) = true.
simpl. reflexivity. Qed.

Definition nandb (x: bool) (y: bool) :=
  negb (andb x y).


Example test_nandb1: (nandb true false) = true.
unfold nandb. simpl. reflexivity. Qed.


Example test_nandb2: (nandb false false) = true.
unfold nandb. simpl. reflexivity. Qed.

Example test_nandb3: (nandb false true) = true.
unfold nandb. simpl. reflexivity. Qed.

Example test_nandb4: (nandb true true) = false.
unfold nandb. simpl. reflexivity. Qed.

Definition andb3 (b1: bool) (b2: bool) (b3: bool): bool :=
  b1 && b2 && b3.

Example test_andb31: (andb3 true true false) = false.
unfold andb3. simpl. reflexivity. Qed.

Example test_andb32: (andb3 false true true) = false.
unfold andb3. simpl. reflexivity. Qed.

Example test_andb33: (andb3 true false true) = false.
unfold andb3. simpl. reflexivity. Qed.

Example test_andb34: (andb3 true false true) = false.
unfold andb3. simpl. reflexivity. Qed.


Check true.

Check (negb false).

Check negb.

Inductive rgb: Type :=
| red
| green
| blue.


Inductive color: Type :=
| black
| white
| primary: rgb -> color.


Check black.
Print  color.


Definition monochrome (c: color) : bool :=
  match c with
  | black => true
  | white => true
  | primary _ => false
  end.


Example check_monochrome: monochrome (primary red) = false.
unfold monochrome. reflexivity. Qed.


Definition isred (c: color) : bool :=
  match c with
  | primary red => true
  | _ => false
  end.


Example check_isred: isred (black) = false.
unfold isred. reflexivity. Qed.

Example check_isred1: isred (primary green) = false.
unfold isred. reflexivity. Qed.

Example check_isred2: isred (primary red) = true.
unfold isred. reflexivity. Qed.

Inductive bit: Type :=
| B0
| B1.

Inductive nybble: Type :=
| bits (b0 b1 b2 b3 : bit).

Check (bits B1 B0 B1 B0).

Check  (bits B1 B0 B1 B0).

Definition all_zero (nb: nybble): bool :=
  match nb with
  | (bits B0 B0 B0 B0) => true
  | (bits _ _ _ _) => false
  end.


Example check_all_zero: all_zero (bits B0 B1 B0 B1) = false.
unfold all_zero. reflexivity. Qed.

Example check_all_zero1: all_zero (bits B0 B0 B0 B0) = true.
unfold all_zero. reflexivity. Qed.


Compute (all_zero (bits B1 B0 B1 B0)).

Compute (all_zero (bits B0 B0 B0 B0)).


Module Test.

  Inductive bool: Type :=
  | FALSE
  | TRUE.
  

End Test.

Check Test.FALSE.

(* everything defined inside the module, outside gets module name prepended to variable name *)

Check (S (S (S O))).


Module NatPlayground.

  Inductive nat: Type :=
  | O: nat
  | S: nat -> nat.

  Check S O.
  Check S (S O).

  Definition is_zero (x: nat): bool :=
    match x with
    | O => true
    | _ => false
    end.

  Example check_zero0: is_zero O  = true.
  unfold is_zero. reflexivity. Qed.

  Example check_one1: is_zero (S O) = false.
  unfold is_zero. reflexivity. Qed.

  Definition pred (x: nat): nat :=
    match x with
    | S y => y
    | O => O
    end.

  Compute pred (S (S O)).

  Example test_pred: is_zero (pred (S O)) = true.
  unfold is_zero. simpl. reflexivity. Qed.

  Example test_pred2: is_zero (pred (pred (S (S O)))) = true.
  unfold is_zero. simpl. reflexivity. Qed.
  
  Check (S (S O)).

  Fixpoint evenb (n: nat): bool :=
    match n with
    | O => true
    | S O => false
    | S (S n1) => evenb n1
    end.

  Compute evenb (S (S (S O))).

  Example check_evenb: evenb (S (S (S (S (S O))))) = false.
  unfold evenb. reflexivity. Qed.

  Fixpoint add (n: nat) (m: nat): nat :=
    match n with
    | O => m
    | S n1 => add n1 (S m)
    end.

  Compute add (S (S O)) (S (S (S O))).

  Fixpoint mult (n: nat) (m: nat) :=
    match n with
    | O => O
    | S n1 => add m (mult n1 m)
    end.

  Compute mult (S (S (S O))) (S (S (S O))).

  Example check_evenb1: evenb (mult (S (S (S O))) (S (S (S O)))) = false.
  unfold evenb. simpl. reflexivity. Qed.

  Fixpoint apply (n: nat) (f: nat -> nat) (v: nat) :=
    match n with
    | O => v
    | S n1 => f (apply n1 f v)
    end.

  Notation "0" := O.
  Notation "1" := (S O).
  Notation "2" := (S (S O)).
  Notation "3" := (S (S (S O))).
  Notation "4" := (S (S (S (S O)))).
  Notation "5" := (S (S (S (S (S O))))).

  Example check_add: add 1 1  = S (S O).
  unfold add. reflexivity. Qed.


  Fixpoint sub (x: nat) (y: nat) :=
    match x, y with
    | n, O => n
    | O, m => O
    | S n, S m => sub n m
    end.


  Compute sub (S (S (S (S O)))) (S (S O)).

  Notation "x + y" := (add x y)
                        (at level 50, left associativity).

  Notation "x * y" := (mult x y)
                        (at level 40, left associativity).

  Check (0 + 1).

  Theorem add0: forall n: nat, add 0 n = n.
    intro n. unfold add. reflexivity. Qed.

  Theorem andb_commutative: forall b c: bool, andb b c = andb c b.
    intros b c.
    - destruct c.
      unfold andb.
      reflexivity.
      unfold andb.
      reflexivity.
  Qed.

  
      



  Theorem add01: forall n: nat, add n 0 = n.
    intro n. unfold add. (* пока не знаю как доказать *)
    destruct n.
    - reflexivity.
    - destruct n as [|nn]. Abort.  (* we need proof by induction, that is the  next chapter *)


  Theorem plus_id_example: forall c n m: nat, n = m -> c + n = c + m.
    intros c n m.
    intro h.
    rewrite -> h.
    reflexivity.
  Qed.



  


(** With this definition, 0 is represented by [O], 1 by [S O],
    2 by [S (S O)], and so on. *)

(** The clauses of this definition can be read:
      - [O] is a natural number (note that this is the letter "[O],"
        not the numeral "[0]").
      - [S] can be put in front of a natural number to yield another
        one -- if [n] is a natural number, then [S n] is too. *)

(** Again, let's look at this in a little more detail.  The definition
    of [nat] says how expressions in the set [nat] can be built:

    - [O] and [S] are constructors;
    - the expression [O] belongs to the set [nat];
    - if [n] is an expression belonging to the set [nat], then [S n]
      is also an expression belonging to the set [nat]; and
    - expressions formed in these two ways are the only ones belonging
      to the set [nat]. *)

(** The same rules apply for our definitions of [day], [bool],
    [color], etc.

    The above conditions are the precise force of the [Inductive]
    declaration.  They imply that the expression [O], the expression
    [S O], the expression [S (S O)], the expression [S (S (S O))], and
    so on all belong to the set [nat], while other expressions built
    from data constructors, like [true], [andb true false], [S (S
    false)], and [O (O (O S))] do not.

    A critical point here is that what we've done so far is just to
    define a _representation_ of numbers: a way of writing them down.
    The names [O] and [S] are arbitrary, and at this point they have
    no special meaning -- they are just two different marks that we
    can use to write down numbers (together with a rule that says any
    [nat] will be written as some string of [S] marks followed by an
    [O]).  If we like, we can write essentially the same definition
    this way: *)

Inductive nat' : Type :=
  | stop
  | tick (foo : nat').

(** The _interpretation_ of these marks comes from how we use them to
    compute. *)

(** We can do this by writing functions that pattern match on
    representations of natural numbers just as we did above with
    booleans and days -- for example, here is the predecessor
    function: *)

(* 
Definition pred (n : nat) : nat :=
  match n with
    | O => O
    | S n' => n'
  end.
 *)

(** The second branch can be read: "if [n] has the form [S n']
    for some [n'], then return [n']."  *)

End NatPlayground.

(** Because natural numbers are such a pervasive form of data,
    Coq provides a tiny bit of built-in magic for parsing and printing
    them: ordinary decimal numerals can be used as an alternative to
    the "unary" notation defined by the constructors [S] and [O].  Coq
    prints numbers in decimal form by default: *)

Check (S (S (S (S O)))).
  (* ===> 4 : nat *)

Definition minustwo (n : nat) : nat :=
  match n with
    | O => O
    | S O => O
    | S (S n') => n'
  end.

Compute (minustwo 4).
  (* ===> 2 : nat *)

(** The constructor [S] has the type [nat -> nat], just like
    [pred] and functions like [minustwo]: *)

Check S.
Check pred.
Check minustwo.

(** These are all things that can be applied to a number to yield a
    number.  However, there is a fundamental difference between the
    first one and the other two: functions like [pred] and [minustwo]
    come with _computation rules_ -- e.g., the definition of [pred]
    says that [pred 2] can be simplified to [1] -- while the
    definition of [S] has no such behavior attached.  Although it is
    like a function in the sense that it can be applied to an
    argument, it does not _do_ anything at all!  It is just a way of
    writing down numbers.  (Think about standard decimal numerals: the
    numeral [1] is not a computation; it's a piece of data.  When we
    write [111] to mean the number one hundred and eleven, we are
    using [1], three times, to write down a concrete representation of
    a number.)

    For most function definitions over numbers, just pattern matching
    is not enough: we also need recursion.  For example, to check that
    a number [n] is even, we may need to recursively check whether
    [n-2] is even.  To write such functions, we use the keyword
    [Fixpoint]. *)

Fixpoint evenb (n:nat) : bool :=
  match n with
  | O        => true
  | S O      => false
  | S (S n') => evenb n'
  end.

(** We can define [oddb] by a similar [Fixpoint] declaration, but here
    is a simpler definition: *)

Definition oddb (n:nat) : bool   :=   negb (evenb n).

Example test_oddb1:    oddb 1 = true.
Proof. simpl. reflexivity.  Qed.
Example test_oddb2:    oddb 4 = false.
Proof. simpl. reflexivity.  Qed.

(** (You will notice if you step through these proofs that
    [simpl] actually has no effect on the goal -- all of the work is
    done by [reflexivity].  We'll see more about why that is shortly.)

    Naturally, we can also define multi-argument functions by
    recursion.  *)

Module NatPlayground2.

Fixpoint plus (n : nat) (m : nat) : nat :=
  match n with
    | O => m
    | S n' => S (plus n' m)
  end.

(** Adding three to two now gives us five, as we'd expect. *)

Compute (plus 3 2).

(** The simplification that Coq performs to reach this conclusion can
    be visualized as follows: *)

(*  [plus (S (S (S O))) (S (S O))]
==> [S (plus (S (S O)) (S (S O)))]
      by the second clause of the [match]
==> [S (S (plus (S O) (S (S O))))]
      by the second clause of the [match]
==> [S (S (S (plus O (S (S O)))))]
      by the second clause of the [match]
==> [S (S (S (S (S O))))]
      by the first clause of the [match]
*)

(** As a notational convenience, if two or more arguments have
    the same type, they can be written together.  In the following
    definition, [(n m : nat)] means just the same as if we had written
    [(n : nat) (m : nat)]. *)

Fixpoint mult (n m : nat) : nat :=
  match n with
    | O => O
    | S n' => plus m (mult n' m)
  end.

Example test_mult1: (mult 3 3) = 9.
Proof. simpl. reflexivity.  Qed.

(** You can match two expressions at once by putting a comma
    between them: *)

Fixpoint minus (n m:nat) : nat :=
  match n, m with
  | O   , _    => O
  | S _ , O    => n
  | S n', S m' => minus n' m'
  end.

End NatPlayground2.

Fixpoint exp (base power : nat) : nat :=
  match power with
    | O => S O
    | S p => mult base (exp base p)
  end.

Notation "x + y" := (plus x y)
                       (at level 50, left associativity)
                       : nat_scope.
Notation "x - y" := (minus x y)
                       (at level 50, left associativity)
                       : nat_scope.
Notation "x * y" := (mult x y)
                       (at level 40, left associativity)
                       : nat_scope.

(** **** Exercise: 1 star, standard (factorial)  

    Recall the standard mathematical factorial function:

       factorial(0)  =  1
       factorial(n)  =  n * factorial(n-1)     (if n>0)

    Translate this into Coq. *)

Fixpoint factorial (n: nat): nat :=
  match n with
  | O => 1
  | S n => mult (plus n 1) (factorial n)
  end.

Example test_factorial1: (factorial 3) = 6.
unfold factorial. simpl. reflexivity. Qed.

Example test_factorial2: (factorial 5) = (10 * 12).
unfold factorial.
 unfold plus. 
unfold mult. simpl. reflexivity. Qed.


Check ((0 + 1) + 1).

(** (The [level], [associativity], and [nat_scope] annotations
    control how these notations are treated by Coq's parser.  The
    details are not important for our purposes, but interested readers
    can refer to the "More on Notation" section at the end of this
    chapter.)

    Note that these do not change the definitions we've already made:
    they are simply instructions to the Coq parser to accept [x + y]
    in place of [plus x y] and, conversely, to the Coq pretty-printer
    to display [plus x y] as [x + y]. *)

(** When we say that Coq comes with almost nothing built-in, we really
    mean it: even equality testing is a user-defined operation!

    Here is a function [eqb], which tests natural numbers for
    [eq]uality, yielding a [b]oolean.  Note the use of nested
    [match]es (we could also have used a simultaneous match, as we did
    in [minus].) *)

Fixpoint eqb (n m: nat): bool :=
  match n with
  | O => match m with
         | O => true
         | S m' => false
         end
  | S n1 => match m with
            | O => false
            | S m1 => eqb n1 m1
            end
  end.

Fixpoint leb (n m: nat): bool :=
  match n with
  | O => true
  | S n1 =>
    match m with
    | O => false
    | S m1 => leb n1 m1
    end
  end.

Example test_leqb1: (leb 2 2) = true.
unfold leb. reflexivity. Qed.

Example test_leb2: (leb 2 4) = true.
unfold leb. reflexivity. Qed.

Example test_leb3: (leb 4 2) = false.
unfold leb. simpl. reflexivity. Qed.


Notation "x =? y" := (eqb x y) (at level 70): nat_scope.

Notation "x <=? y" := (leb x y) (at level 70): nat_scope.

Example test_leb3': (4 <=? 2) = false.
unfold leb. reflexivity. Qed.


Definition ltb (n m: nat): bool :=
  andb (leb n m) (negb (eqb n m)).


Notation "x <? y" := (ltb x y) (at level 70): nat_scope.

Example test_ltb1: (ltb 2 2) = false.
unfold ltb. unfold andb. unfold negb. unfold eqb. simpl. reflexivity. Qed.


Example test_ltb2: (ltb 2 4) = true.
unfold ltb. simpl. reflexivity. Qed.

Example test_ltb3: (ltb 4 2) = false.
unfold ltb. simpl. reflexivity. Qed.



Theorem plus_0_n: forall n: nat, 0 + n = n.
  simpl. reflexivity. Qed.


Theorem plus_id_example: forall n m: nat, n = m -> n + n = m + m.
  intros n m.
  intros H.
  rewrite H.
  reflexivity.
Qed.


Theorem plus_1_l: forall n:nat, 1 + n = S n.
  intro n.
  unfold plus.
  reflexivity.
Qed.


Theorem mult_0_1: forall n:nat, 0 * n = 0.
  intros n.
  unfold mult.
  reflexivity.
Qed.


Theorem plus_id_exercise: forall n m o: nat,
    n = m -> m = o -> n + m = m + o.
  intros n m o.
  intros h1 h2.
  rewrite h1.
  rewrite h2.
  reflexivity.
Qed.


Theorem mult_0_plus: forall n m: nat,
    (0 + n) * m = n * m.
  intros n m.
  unfold plus.
  reflexivity.
Qed.

Theorem mult_S_1: forall n m: nat,
    m = S n -> m * (1 + n) = m * m.
  intros n m.
  intros H.
  unfold plus.
  rewrite -> H.
  reflexivity.
Qed.


Theorem plus_1_neq_0_first_try: forall n: nat,
    (n + 1) =? 0 = false.
  intros n.
  unfold eqb.
  simpl.
  destruct n as [| n1].
  -  simpl.
     reflexivity.
  -  simpl.
    reflexivity.
Qed.



(*     There are no hard and fast rules for how proofs should be
    formatted in Coq -- in particular, where lines should be broken
    and how sections of the proof should be indented to indicate their
    nested structure.  However, if the places where multiple subgoals
    are generated are marked with explicit bullets at the beginning of
    lines, then the proof will be readable almost no matter what
    choices are made about other aspects of layout.

    This is also a good place to mention one other piece of somewhat
    obvious advice about line lengths.  Beginning Coq users sometimes
    tend to the extremes, either writing each tactic on its own line
    or writing entire proofs on one line.  Good style lies somewhere
    in the middle.  One reasonable convention is to limit yourself to
    80-character lines.

    The [destruct] tactic can be used with any inductively defined
    datatype.  For example, we use it next to prove that boolean
    negation is involutive -- i.e., that negation is its own
    inverse. *)

Theorem negb_involutive: forall b: bool,
    negb (negb b) = b.
  intros b. destruct b. unfold negb. reflexivity.
  unfold negb. reflexivity. Qed.

Theorem andb_commutative: forall b c, andb b c = andb c b.
  intros b c. destruct c. reflexivity. reflexivity. Qed.


Theorem andb_commutative1: forall b c, andb b c = andb c b.
  intros b c. destruct b eqn:Eb.
  { destruct c eqn:Ec.
    { reflexivity. } 
    { reflexivity. } }
  { destruct c eqn:Ec.
    { reflexivity. }
    { reflexivity. } }
  Qed.


Theorem andb3_exchange:
  forall b c d, andb (andb b c) d = andb (andb b d) c.
  intros b c d. destruct b eqn:Eb.
  - destruct c eqn:Ec.
    { destruct d eqn:Ed.
      reflexivity.
      reflexivity. }
    { destruct d eqn:Ed.
      reflexivity.
      reflexivity. }
  - destruct c eqn:Ec.
    { destruct d eqn:Ed.
      - reflexivity.
      - reflexivity.
    }
    { destruct d eqn:Ed.
      - reflexivity.
      - reflexivity.
    }
Qed.



(** Since curly braces mark both the beginning and the end of a
    proof, they can be used for multiple subgoal levels, as this
    example shows. Furthermore, curly braces allow us to reuse the
    same bullet shapes at multiple levels in a proof: *)


(** Before closing the chapter, let's mention one final
    convenience.  As you may have noticed, many proofs perform case
    analysis on a variable right after introducing it:

       intros x y. destruct y as [|y] eqn:E.

    This pattern is so common that Coq provides a shorthand for it: we
    can perform case analysis on a variable when introducing it by
    using an intro pattern instead of a variable name. For instance,
    here is a shorter proof of the [plus_1_neq_0] theorem
    above.  (You'll also note one downside of this shorthand: we lose
    the equation recording the assumption we are making in each
    subgoal, which we previously got from the [eqn:E] annotation.) *)


Theorem plus_1_neq_00: forall n: nat,
    (n + 1) =? 0 = false.
Proof.
  intros [|n].
  - reflexivity.
  - reflexivity.
Qed.


(** If there are no arguments to name, we can just write [[]]. *)

Theorem andb_comm:
  forall b c, andb b c = andb c b.
Proof.
  intros [] [].
  - reflexivity.
  - reflexivity.
  - reflexivity.
  - reflexivity.
Qed.



Theorem andb_true_elim2: forall b c: bool,
    andb b c = true -> c = true.
Proof.
  intros b c.  destruct c eqn:Ec.
  - destruct b eqn: Eb.
    intro H.
    reflexivity.
    intro H.
    reflexivity.
  -  destruct b.
     unfold andb.
     intro H.
     exact H.
     unfold andb.
     intro H.
     exact H.
Qed.

Print andb_true_elim2.

(** **** Exercise: 2 stars, standard (andb_true_elim2)  

    Prove the following claim, marking cases (and subcases) with
    bullets when you use [destruct]. *)

(** **** Exercise: 1 star, standard (zero_nbeq_plus_1)  *)

Theorem zero_nbeq_plus_1: forall n: nat,
    0 =? (n + 1) = false.
  intros n. simpl. unfold plus. simpl. destruct n.
  - reflexivity.
  - reflexivity.
Qed.

  

(* ================================================================= *)
(** ** More on Notation (Optional) *)

(** (In general, sections marked Optional are not needed to follow the
    rest of the book, except possibly other Optional sections.  On a
    first reading, you might want to skim these sections so that you
    know what's there for future reference.)

    Recall the notation definitions for infix plus and times: *)



Notation "x + y" := (plus x y)
                      (at level 50, left associativity).

Notation "x * y" := (mult x y)
                      (at level 40, left associativity).

(* precedence level from 0 to 100, 0 is the highest precedence *)


(* ================================================================= *)
(** ** Fixpoints and Structural Recursion (Optional) *)

(** Here is a copy of the definition of addition: *)



Fixpoint plus' (n : nat) (m : nat) : nat :=
  match n with
  | O => m
  | S n' => S (plus' n' m)
  end.

(** When Coq checks this definition, it notes that [plus'] is
    "decreasing on 1st argument."  What this means is that we are
    performing a _structural recursion_ over the argument [n] -- i.e.,
    that we make recursive calls only on strictly smaller values of
    [n].  This implies that all calls to [plus'] will eventually
    terminate.  Coq demands that some argument of _every_ [Fixpoint]
    definition is "decreasing."

    This requirement is a fundamental feature of Coq's design: In
    particular, it guarantees that every function that can be defined
    in Coq will terminate on all inputs.  However, because Coq's
    "decreasing analysis" is not very sophisticated, it is sometimes
    necessary to write functions in slightly unnatural ways. *)

(** **** Exercise: 2 stars, standard, optional (decreasing)  

    To get a concrete sense of this, find a way to write a sensible
    [Fixpoint] definition (of a simple function on numbers, say) that
    _does_ terminate on all inputs, but that Coq will reject because
    of this restriction.  (If you choose to turn in this optional
    exercise as part of a homework assignment, make sure you comment
    out your solution so that it doesn't cause Coq to reject the whole
    file!) *)

(* FILL IN HERE 

    [] *)

(* ################################################################# *)
(** * More Exercises *)

(** Each SF chapter comes with a tester file (e.g.  [BasicsTest.v]),
    containing scripts that check most of the exercises. You can run
    [make BasicsTest.vo] in a terminal and check its output to make
    sure you didn't miss anything. *)

(** **** Exercise: 1 star, standard (indentity_fn_applied_twice)  

    Use the tactics you have learned so far to prove the following
    theorem about boolean functions. *)


Theorem identity_fn_applied_twice:
  forall (f: bool -> bool),
    (forall (x: bool), f x = x) ->
    forall (b: bool), f (f b) = b.
  intros. rewrite H. rewrite H. reflexivity. Qed.




(* FILL IN HERE *)
(* The [Import] statement on the next line tells Coq to use the
   standard library String module.  We'll use strings more in later
   chapters, but for the moment we just need syntax for literal
   strings for the grader comments. *)
From Coq Require Export String.

(* Do not modify the following line: *)
Definition manual_grade_for_negation_fn_applied_twice : option (nat*string) := None.
(** [] *)

(** **** Exercise: 3 stars, standard, optional (andb_eq_orb)  

    Prove the following theorem.  (Hint: This one can be a bit tricky,
    depending on how you approach it.  You will probably need both
    [destruct] and [rewrite], but destructing everything in sight is
    not the best way.) *)

Theorem andb_eq_orb:
  forall (b c : bool),    (andb b c = orb b c) -> b = c.
Proof.
  intros b c.
  destruct b eqn:Eb.
  - destruct c.
    { simpl. intros. reflexivity. }
    { simpl. intros. rewrite H. reflexivity. }
  - destruct c.
    { simpl. intros. rewrite H. reflexivity. }
    { simpl. reflexivity. }
Qed.





    

(** [] *)

(** **** Exercise: 3 stars, standard (binary)  

    We can generalize our unary representation of natural numbers to
    the more efficient binary representation by treating a binary
    number as a sequence of constructors [A] and [B] (representing 0s
    and 1s), terminated by a [Z]. For comparison, in the unary
    representation, a number is a sequence of [S]s terminated by an
    [O].

    For example:

        decimal            binary                           unary
           0                   Z                              O
           1                 B Z                            S O
           2              A (B Z)                        S (S O)
           3              B (B Z)                     S (S (S O))
           4           A (A (B Z))                 S (S (S (S O)))
           5           B (A (B Z))              S (S (S (S (S O))))
           6           A (B (B Z))           S (S (S (S (S (S O)))))
           7           B (B (B Z))        S (S (S (S (S (S (S O))))))
           8        A (A (A (B Z)))    S (S (S (S (S (S (S (S O)))))))

    Note that the low-order bit is on the left and the high-order bit
    is on the right -- the opposite of the way binary numbers are
    usually written.  This choice makes them easier to manipulate. *)
Inductive bin: Type :=
| Z
| A (n: bin)
| B (n: bin).


(** (a) Complete the definitions below of an increment function [incr]
        for binary numbers, and a function [bin_to_nat] to convert
        binary numbers to unary numbers. *)

(* Fixpoint incr (m:bin) : bin
  (* REPLACE THIS LINE WITH ":= _your_definition_ ." *). Admitted. *)


Fixpoint incr (m: bin): bin :=
  match m with
  | Z => B Z
  | A n => B n
  | B n => A (incr n)
  end.

Fixpoint apply (n: nat) (f: bin -> bin) (v: bin) :=
  match n with
    | O => v
    | S n1 => f (apply n1 f v)
  end.

Compute apply 12 incr Z.


        
             

(**    (b) Write five unit tests [test_bin_incr1], [test_bin_incr2], etc.
        for your increment and binary-to-unary functions.  (A "unit
        test" in Coq is a specific [Example] that can be proved with
        just [reflexivity], as we've done for several of our
        definitions.)  Notice that incrementing a binary number and
        then converting it to unary should yield the same result as
        first converting it to unary and then incrementing. *)

(* FILL IN HERE *)


Fixpoint bin_to_nat (m: bin): nat :=
  match m with
  | Z => O
  | A n => mult 2 (bin_to_nat n)
  | B n => plus 1 (mult 2 (bin_to_nat n))
  end.

Compute bin_to_nat (apply 12 incr Z).




(* Do not modify the following line: *)
Definition manual_grade_for_binary : option (nat*string) := None.
(** [] *)

(* Wed Jan 9 12:02:44 EST 2019 *)
