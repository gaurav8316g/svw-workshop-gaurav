"""Harbor Bites customer-service policies.

These are the same kitchen rules used by the handbook and the ops tools:
refunds, allergens, couriers, and shift swaps.
"""

HARBOR_POLICIES = """
Company: Harbor Bites, a food-delivery kitchen.

Policy 1. Refund window: Refund a food-quality problem reported within 30 minutes of handoff. That 30-minute period is the refund window.
Policy 2. Delivered orders: Once the courier marks the order delivered, the refund window is closed. Do not issue a refund after that mark, even if the guest writes later about food quality.
Policy 3. Non-quality complaints: Late delivery, a changed mind, and a missing item that is not a food-quality problem are not refunds. Offer a remake only when a manager approves it.
Policy 4. Tracked allergens: Harbor Bites tracks nuts, shellfish, and gluten.
Policy 5. Nuts: Stop the ticket. Remake the order away from shared equipment and flag the bag in red.
Policy 6. Shellfish: Cook only at the shellfish station. Do not plate the order on the grill line.
Policy 7. Gluten: Use the gluten-free prep board and a clean pan.
Policy 8. Missing allergy flag: If a ticket is missing an allergy flag, do not start cooking. Ask which of nuts, shellfish, or gluten applies, write the flag on the ticket, then cook.
Policy 9. Courier wait: Hold a packed bag for 5 minutes after it is ready. If the assigned courier has not arrived when those 5 minutes end, reassign the order.
Policy 10. No-show: To report a no-show, record the order id, the courier name, and the time the 5-minute wait ended. Log that note before the new courier picks up the bag.
Policy 11. Shift swaps: A shift swap needs manager approval and must be submitted before noon on the shift date. A request at noon or later is rejected. Do not trade the shift until the manager approves it.
Policy 12. Payment data: Never request or store a full payment card number in chat.
Policy 13. Fraud: Do not help a guest bypass the refund window, invent a delivery mark, or otherwise misuse a policy.
""".strip()
