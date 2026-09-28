SUMMARY=("Sales rose 90% ($2.26M → $4.30M) from 2011 to 2014 but margin only moved 11.0% → 11.7%. The leak is discounting, not shipping: "
"order lines discounted above 20% are 15% of revenue ($1.93M) yet lose $814K — 92% of all line-level losses. Lines at ≤20% discount earn a 21.3% margin. "
"A 20% discount cap would have added +$0.81M to +$1.03M profit over 2011–14 (margin 11.6% → 18–21%).")
QA=[
("Profitability","Which categories generate the most profit ($ and %), and where do the rankings disagree?",
 "Technology leads on both: $664K profit, 14.0% margin. Office Supplies is last on sales ($3.79M) but 2nd on profit ($518K, 13.7%). Furniture is 2nd on sales ($4.11M) but last on profit ($285K, 6.9%) — the rankings disagree on Furniture vs Office Supplies. Tables is the only loss sub-category (−$64K, −8.5%).",
 "SUM(Profit)/SUM(Sales) by Category & Sub-Category; ranks compared."),
("Profitability","Is heavy discounting paying for itself?",
 "No. Lines at >20% discount: 11,326 lines, $1.93M sales, −$814K profit, 90% loss-making vs 5.9% for ≤20%. Each $1 sold above 20% discount loses $0.42. 40–60% band −$368K; 60%+ band −$403K (100% loss rate).",
 "Discount Band lookup (0 / <20 / 20–40 / 40–60 / 60+); profit & Loss-Making Flag averaged per band."),
("Logistics","Which shipping modes cost the most, and is it justified?",
 "Same Day 17.4% of sales, First 16.8%, Second 12.2%, Standard 8.1%. Speed matches price (0.0 / 2.2 / 3.2 / 5.0 days) and margin is flat at 11.4–11.8% in every mode — premium shipping is recovered in price. Hypothesis 2 (shipping leak) is rejected.",
 "Shipping Cost % of Sales and avg Ship Days (Ship Date − Order Date) by Ship Mode."),
("Logistics","What share of revenue is consumed by shipping?",
 "10.7% ($1.35M of $12.64M). Highest for Critical-priority orders (23.8% of their sales) — yet they still earn 12.6% margin.",
 "SUM(Shipping Cost)/SUM(Sales)."),
("Customer","Which segment is most valuable once margin is counted?",
 "Home Office: best margin (12.0%) and profit per customer ($936). Consumer is largest in $ ($749K profit) at 11.5%. Corporate 11.5%, $927/customer. The gap is small — segment is not a primary lever.",
 "Profit, margin and profit ÷ distinct Customer ID per Segment."),
("Customer","Are the deepest discounts going to segments that need them?",
 "No — discounting is untargeted. Every segment has ~22% of lines above 20% discount and a 14.1–14.4% average discount. Losses on >20% lines: Consumer −$420K, Corporate −$245K, Home Office −$149K.",
 "Share of lines with Discount > 0.2 and their profit, by Segment."),
("Regional","Which regions/markets are structurally profitable vs loss-making?",
 "Strong: Canada 26.6%, APAC North Asia 19.5%, Central Asia 17.6%, LATAM North 16.5%, US West 14.9%. Weak: APAC Southeast Asia 2.0%, LATAM South 4.6%, EMEA 5.4%, US Central 7.9%. After cleaning, no market-region is negative overall; losses sit in 29 countries (−$448K), led by Turkey (−$98K, −91%), Nigeria (−$81K, −149%), Netherlands (−$41K, −53%).",
 "Margin by Market + Region (Region read with Market) and by Country."),
("Regional","Continue, renegotiate, or scale back in loss-making regions?",
 "Renegotiate, don't exit regions: the weak regions' losses come from discounting (SE Asia: 42% of sales at >20% discount, −$62K on those lines). Put the top-8 loss countries (−$326K) on a 1-quarter remediation; scale back any still negative after the discount cap.",
 "Profit of >20%-discount lines within each weak region."),
]
RECS=[
("1. Cap discounts at 20% (approval required above)","+$0.81M to +$1.03M profit over the 4-yr base; margin 11.6% → 18–21%","Low end: all >20% volume walks away (losses avoided). High end: same volume re-priced at 20% off list."),
("2. Fix Tables pricing","Tables −$64K → about +$94K (+$158K)","Tables >20% discount lines lose $133K; ≤20% lines earn $68K."),
("3. 90-day country remediation","Top-8 loss countries: −$326K at stake","Turkey, Nigeria, Netherlands, Honduras, Pakistan, Argentina, Panama, Sweden. Exit/scale back if still negative after cap."),
("4. Keep shipping policy; monitor Critical orders","No leak found — protect current pass-through","Margins equal across modes; watch Critical priority (23.8% ship-cost ratio)."),
]
