"""Review 3 of note 22: the class 1034 example of §6.2, with my own code.
Usage: python -I review23_n22_c1034.py > review23_n22_c1034.log"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review23_n22_lib as L
x = (3, 0, -2, 0, 3, -2)
cut, ok, _ = L.cut(x, 3000, cap=400000)
print(f"V'(x) cut at level 3000: {len(cut)} quivers, complete {ok}; x in no far region by the direct test: {L.direct_no_far_region(x)}")
lo = min(cut.values()); bot = sorted(c for c, l in cut.items() if l == lo)
print(f"   bottom: level {lo}, {len(bot)} quivers, least {bot[0]}, least mirrored {min(L.canon(L.neg(c)) for c in bot)}")
for Nn in (4, 6, 10, 20, 40, 100):
    y = (Nn, 0, -(Nn - 2), -3, 2, -3)
    c = L.canon(y)
    z = L.mutate(y, 0)
    print(f"   N = {Nn}: corridor quiver {y} in the cut: {c in cut}; step at 0 allowed: {L.allowed(y, 0)}; "
          f"mu_0 = {z}, level {L.level(z)} (N^2 = {Nn*Nn}); in the cut: {L.canon(z) in cut if L.level(z) <= 3000 else 'above the cut'}; "
          f"steps from mu_0: " + ", ".join(f"{m}: {'up-exit' if L.strict_up_exit(z, m) else ('in cut' if L.canon(L.mutate(z, m)) in cut else 'level ' + str(L.level(L.mutate(z, m))))}" for m in range(4)))
