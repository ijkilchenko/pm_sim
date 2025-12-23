import math
from functools import lru_cache

class Event:
    def __init__(self):
        pass

    def calculate_payout(self, budget_remaining, T, best_bid_UP):
        win_prob = (best_bid_UP + 0.5) / 100
        
        @lru_cache(maxsize=None)
        def solve(t_rem, budget, n_up, n_down, b_up, bids_up, bids_down):
            open_bids_UP = dict(bids_up)
            open_bids_DOWN = dict(bids_down)
            
            # 1. Handle fills
            b_down = 100 - 1 - b_up
            if b_up in open_bids_UP:
                n_up += open_bids_UP[b_up]
                open_bids_UP[b_up] = 0
            if b_down in open_bids_DOWN:
                n_down += open_bids_DOWN[b_down]
                open_bids_DOWN[b_down] = 0

            # 2. Terminal Case
            if t_rem == 0:
                unfilled = sum(p * c for p, c in open_bids_UP.items()) + sum(p * c for p, c in open_bids_DOWN.items())
                return (n_up * 100 * win_prob) + (n_down * 100 * (1 - win_prob)) + unfilled + budget

            # 3. Recursive Strategy Optimization
            best_ev = -1.0
            best_action = None
            
            # Actions: (split_ratio, dist_up, dist_down)
            # To keep it simple but "more freedom", we explore split and distance
            for split in [0.0, 0.25, 0.5, 0.75, 1.0]:
                for dist in [1, 2, 3, 4, 5]: # Place 1c or 2c below best bid
                    b_up_action = min(b_up - dist, 99)
                    b_down_action = min(b_down - dist, 99)
                    
                    budget_UP = int(budget * split)
                    budget_DOWN = budget - budget_UP
                    
                    q_up = budget_UP // b_up_action if b_up_action > 0 else 0
                    q_down = budget_DOWN // b_down_action if b_down_action > 0 else 0
                    
                    rem_budget = budget - (q_up * b_up_action) - (q_down * b_down_action)
                    
                    sim_bids_up = dict(open_bids_UP)
                    if q_up > 0: sim_bids_up[b_up_action] = sim_bids_up.get(b_up_action, 0) + q_up
                    
                    sim_bids_down = dict(open_bids_DOWN)
                    if q_down > 0: sim_bids_down[b_down_action] = sim_bids_down.get(b_down_action, 0) + q_down
                    
                    # Expected value across transitions
                    ev_action = 0
                    for trans in [-1, 0, 1]:
                        ev_action += solve(
                            t_rem - 1, rem_budget, n_up, n_down, b_up + trans,
                            tuple(sorted((p, c) for p, c in sim_bids_up.items() if c > 0)),
                            tuple(sorted((p, c) for p, c in sim_bids_down.items() if c > 0))
                        )
                    ev_action /= 3.0
                    
                    if ev_action > best_ev:
                        best_ev = ev_action
                        best_action = (split, dist)
            
            return best_ev if t_rem < T else (best_ev, best_action)

        return solve(T, budget_remaining, 0, 0, best_bid_UP, (), ())

if __name__ == "__main__":
    event = Event()
    budget = 1000
    start_price = 49
    
    print(f"Optimizing strategy for Budget={budget}, StartPrice={start_price}")
    for t in [1, 2, 5, 10, 20, 25, 30]:
        max_ev, (split, dist) = event.calculate_payout(budget, T=t, best_bid_UP=start_price)
        print(f"T={t}: Best Split={split:.2f}, Best Distance={dist}c, Max EV={max_ev:.2f}")