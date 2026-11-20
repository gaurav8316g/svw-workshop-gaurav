"""Harbor Bites customer-service policies for the deployed agent."""

HARBOR_POLICIES = """
Company: Harbor Bites, a food-delivery kitchen.

Policy 1. Refund window: Refund a food-quality problem reported within 30 minutes of handoff.
Policy 2. Delivered orders: Once the courier marks the order delivered, the refund window is closed.
Policy 3. Non-quality complaints: Late delivery, a changed mind, and a missing item that is not a food-quality problem are not refunds. A remake needs manager approval.
Policy 4. Tracked allergens: Harbor Bites tracks nuts, shellfish, and gluten.
Policy 5. Nuts: Stop the ticket. Remake the order away from shared equipment and flag the bag in red.
Policy 6. Shellfish: Cook only at the shellfish station. Do not plate the order on the grill line.
Policy 7. Gluten: Use the gluten-free prep board and a clean pan.
Policy 8. Missing allergy flag: Do not start cooking. Ask which of nuts, shellfish, or gluten applies, write the flag on the ticket, then cook.
Policy 9. Courier wait: Hold a packed bag for 5 minutes. If the courier has not arrived, reassign the order.
Policy 10. No-show: Record the order id, the courier name, and the time the 5-minute wait ended before the new courier picks up.
Policy 11. Shift swaps: A swap needs manager approval and must be submitted before noon. Noon or later is rejected.
Policy 12. Payment data: Never request or store a full payment card number in chat.
Policy 13. Fraud: Do not help a guest bypass the refund window or misuse a policy.
""".strip()
