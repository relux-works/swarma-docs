"""
Bounded explicit-state model of the integration fragment of the protocol:
candidate -> attestations -> integration record -> atomic advance of main.

Participants: task A (full behaviour: contract may change, records may carry a stale epoch)
and task B (interferer: it only integrates and thereby moves the head).
Bounds: contract versions of A <= 2; lease epochs <= 2; one integration record per task at a time,
each record may be delivered up to twice (redelivery). All interleavings are explored (BFS).

Rules, each of which can be switched off to obtain a counterexample:
  cas      advance only if the current head equals the record base M
  epoch    the record must carry the current lease epoch
  contract attestations must reference the task's current contract version
  bind_I   attestations must be bound to the exact candidate I (otherwise: to the revision R)
Invariant, checked at every advance of main: the head advances to a candidate built over the head
at that moment; the attestation is bound to that candidate and references the task's current contract
version; the record carries the current epoch; no record is applied twice.
"""
from collections import deque

MAX_C, MAX_E, MAX_DELIVER = 2, 2, 2

# per task: (revision, candidate_base, att, contract, integrated, record)
#   att    = None | (target, c) with target = ('I', base) | ('R',)
#   record = None | (base, c, epoch, delivered)
# global: (head, epoch, A, B, violation)
def initial():
    return (0, 1, (False, None, None, 1, False, None), (False, None, None, 1, False, None), None)

def task_succ(tk, head, epoch, R, full):
    rev, cb, att, c, integ, rec = tk
    out = []
    if integ:
        return out
    if not rev:
        out.append(("submit", (True, cb, att, c, integ, rec)))
    if rev and cb != head:
        out.append(("build_candidate", (rev, head, att, c, integ, rec)))
    if cb is not None:
        target = ("I", cb) if R["bind_I"] else ("R", cb)   # without bind_I the attestation only remembers the base it was made on
        a = (target, c)
        if att != a:
            out.append(("attest", (rev, cb, a, c, integ, rec)))
    if full and c < MAX_C:
        out.append(("change_contract", (rev, cb, att, c + 1, integ, rec)))
    if cb is not None and att is not None and rec is None:
        eps = range(1, epoch + 1) if full else [epoch]
        for ep in eps:
            out.append(("propose", (rev, cb, att, c, integ, (cb, c, ep, 0))))
    return out

def deliver(tk, head, epoch, R):
    """returns (accepted, new_task_state, violation_or_None)"""
    rev, cb, att, c, integ, rec = tk
    base, rc, ep, dc = rec
    rec2 = (base, rc, ep, dc + 1)
    consumed = rec2 if dc + 1 < MAX_DELIVER else None
    ok = att is not None
    if ok and R["epoch"] and ep != epoch: ok = False
    if ok and R["cas"] and base != head: ok = False
    if ok and R["contract"] and att[1] != c: ok = False
    if ok:
        if R["bind_I"]:
            if att[0] != ("I", base): ok = False
        else:
            if att[0][0] != "R": ok = False           # bound to the revision only: base is not checked
    if not ok:
        return False, (rev, cb, att, c, integ, consumed), None
    if integ:
        return True, (rev, cb, att, c, integ, consumed), "record applied twice"
    v = None
    if base != head or cb != head: v = "advance to a candidate not built over the current head"
    elif att[0][1] != head: v = "attestation made on a different base than the integrated candidate"
    elif att[1] != c: v = "attestation references a superseded contract version"
    elif ep != epoch: v = "record from a stale lease epoch advanced main"
    return True, (rev, cb, att, c, True, consumed), v

def successors(s, R):
    head, epoch, A, B, viol = s
    out = []
    for name, A2 in task_succ(A, head, epoch, R, full=True):
        out.append((name + "(A)", (head, epoch, A2, B, viol)))
    for name, B2 in task_succ(B, head, epoch, R, full=False):
        out.append((name + "(B)", (head, epoch, A, B2, viol)))
    if epoch < MAX_E:
        out.append(("epoch_change", (head, epoch + 1, A, B, viol)))
    for label, tk, other in (("A", A, B), ("B", B, A)):
        if tk[5] is not None:
            acc, tk2, v = deliver(tk, head, epoch, R)
            h2 = head + 1 if acc and not tk[4] else head
            st = (h2, epoch, tk2, other, v) if label == "A" else (h2, epoch, other, tk2, v)
            out.append((("deliver" if acc else "deliver_rejected") + f"({label})", st))
    return out

def explore(R):
    init = initial(); parents = {init: None}; q = deque([init]); n = 0
    while q:
        s = q.popleft(); n += 1
        if s[4]:
            trace, cur = [], s
            while parents[cur] is not None:
                name, prev = parents[cur]; trace.append(name); cur = prev
            return n, s[4], list(reversed(trace))
        for name, nxt in successors(s, R):
            if nxt not in parents:
                parents[nxt] = (name, s); q.append(nxt)
    return n, None, None

if __name__ == "__main__":
    full = dict(cas=True, epoch=True, contract=True, bind_I=True)
    n, v, _ = explore(full)
    print(f"full rules: reachable states={n}, violation={v}")
    for r in full:
        rules = dict(full); rules[r] = False
        n, v, trace = explore(rules)
        print(f"without {r:8s}: states explored={n}, violation={v}")
        if trace:
            print("   trace:", " -> ".join(trace))

