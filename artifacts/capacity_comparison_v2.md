| Strategy | Capacity | Subscribers contacted | Churners identified | Recall@K | Precision@K | Lift@K |
|---|---:|---:|---:|---:|---:|---:|
| Random expected | 5% | 8,746 | 476.32 expected | 5.00% | 5.45% | 1.000 |
| Business Rule | 5% | 8,746 | 2664 | 27.96% | 30.46% | 5.593 |
| Logistic Regression (post-hoc) | 5% | 8,746 | 3876 | 40.68% | 44.32% | 8.137 |
| HistGradientBoosting | 5% | 8,746 | 3993 | 41.91% | 45.66% | 8.383 |
| Random expected | 10% | 17,493 | 952.69 expected | 10.00% | 5.45% | 1.000 |
| Business Rule | 10% | 17,493 | 5327 | 55.91% | 30.45% | 5.592 |
| Logistic Regression (post-hoc) | 10% | 17,493 | 5845 | 61.35% | 33.41% | 6.135 |
| HistGradientBoosting | 10% | 17,493 | 5968 | 62.64% | 34.12% | 6.264 |
| Random expected | 20% | 34,986 | 1905.39 expected | 20.00% | 5.45% | 1.000 |
| Business Rule | 20% | 34,986 | 6612 | 69.40% | 18.90% | 3.470 |
| Logistic Regression (post-hoc) | 20% | 34,986 | 6793 | 71.30% | 19.42% | 3.565 |
| HistGradientBoosting | 20% | 34,986 | 7410 | 77.78% | 21.18% | 3.889 |

Recall differences in percentage points (not relative percentages).

| Capacity | Logistic vs Rule | HGB vs Rule | HGB vs Logistic |
|---|---:|---:|---:|
| 5% | +12.72 pp | +13.95 pp | +1.23 pp |
| 10% | +5.44 pp | +6.73 pp | +1.29 pp |
| 20% | +1.90 pp | +8.38 pp | +6.48 pp |
