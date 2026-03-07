#!/bin/bash
# fix-ui-readability.sh
# Run on GCP: bash fix-ui-readability.sh
# Fixes: dark text, invisible borders, tiny dropdown arrow, poor contrast

set -e
DOCS="/home/g623dks/docs"

echo "=== Backing up files ==="
cp "$DOCS/index.html" "$DOCS/index.html.bak2"
cp "$DOCS/reviewer.html" "$DOCS/reviewer.html.bak2"
cp "$DOCS/home.html" "$DOCS/home.html.bak2"

echo "=== Fixing index.html ==="

# 1. Brighten text colors (t2 was too dark gray, t3 was nearly invisible)
sed -i 's/--t1:#F0F4F8/--t1:#FFFFFF/g' "$DOCS/index.html"
sed -i 's/--t2:#A0AEC0/--t2:#D0D7E0/g' "$DOCS/index.html"
sed -i 's/--t3:#5A6578/--t3:#8B95A5/g' "$DOCS/index.html"

# 2. Make borders visible
sed -i 's/--border:rgba(255,255,255,.05)/--border:rgba(255,255,255,.12)/g' "$DOCS/index.html"

# 3. Brighten accent colors for better pop
sed -i 's/--accent:#34D1B4/--accent:#3DE8C8/g' "$DOCS/index.html"
sed -i 's/--accent-dim:rgba(52,209,180,.08)/--accent-dim:rgba(61,232,200,.12)/g' "$DOCS/index.html"
sed -i 's/--accent-border:rgba(52,209,180,.15)/--accent-border:rgba(61,232,200,.28)/g' "$DOCS/index.html"

# 4. Fix dropdown arrow SVG (was dark gray #5A6578, now bright white)
sed -i "s/fill='%235A6578'/fill='%23D0D7E0'/g" "$DOCS/index.html"

# 5. Make dropdown arrow bigger (10x10 -> 12x12) and reposition
sed -i "s/width='10' height='10'/width='14' height='14'/g" "$DOCS/index.html"

# 6. Increase field label size
sed -i 's/\.field-label{font-size:\.76rem/.field-label{font-size:.88rem/g' "$DOCS/index.html"

# 7. Increase input/select/textarea font size
sed -i 's/\.input,\.sel,\.ta{width:100%;font-family:var(--fb);font-size:\.875rem/.input,.sel,.ta{width:100%;font-family:var(--fb);font-size:1rem/g' "$DOCS/index.html"

# 8. Increase page heading size
sed -i 's/\.page-head h1{font-family:var(--fd);font-size:1\.6rem/.page-head h1{font-family:var(--fd);font-size:1.85rem/g' "$DOCS/index.html"

# 9. Increase subtitle size
sed -i 's/\.page-head p{color:var(--t3);font-size:\.9rem/.page-head p{color:var(--t2);font-size:1rem/g' "$DOCS/index.html"

# 10. Make topbar brand bigger
sed -i 's/\.brand{font-family:var(--fd);font-size:1rem/.brand{font-family:var(--fd);font-size:1.15rem/g' "$DOCS/index.html"

# 11. Make badge text bigger
sed -i 's/\.badge{display:inline-flex;align-items:center;gap:5px;font-size:\.63rem/.badge{display:inline-flex;align-items:center;gap:5px;font-size:.75rem/g' "$DOCS/index.html"

# 12. Make upload button text bigger
sed -i 's/\.upload-btn{display:inline-flex;align-items:center;gap:5px;font-family:var(--fb);font-size:\.76rem/.upload-btn{display:inline-flex;align-items:center;gap:5px;font-family:var(--fb);font-size:.88rem/g' "$DOCS/index.html"

# 13. Brighten score-val and result text
sed -i 's/\.score-val{position:relative;z-index:1;font-family:var(--fd);font-size:2\.6rem/.score-val{position:relative;z-index:1;font-family:var(--fd);font-size:3rem/g' "$DOCS/index.html"

# 14. Make topbar username bigger
sed -i 's/\.topbar-user{display:flex;align-items:center;gap:7px;font-size:\.78rem/.topbar-user{display:flex;align-items:center;gap:7px;font-size:.9rem/g' "$DOCS/index.html"

# 15. Make back-link brighter and bigger
sed -i 's/\.back-link{display:inline-flex;align-items:center;gap:5px;font-size:\.78rem;font-weight:500;color:var(--t3)/.back-link{display:inline-flex;align-items:center;gap:5px;font-size:.88rem;font-weight:500;color:var(--t2)/g' "$DOCS/index.html"

# 16. Lighten backgrounds slightly for more contrast
sed -i 's/--bg-in:#0A0D14/--bg-in:#0E1219/g' "$DOCS/index.html"
sed -i 's/--bg2:#0D1017/--bg2:#111620/g' "$DOCS/index.html"
sed -i 's/--bg3:#141821/--bg3:#1A1F2B/g' "$DOCS/index.html"


echo "=== Fixing reviewer.html ==="

# Same color fixes
sed -i 's/--t1:#F0F4F8/--t1:#FFFFFF/g' "$DOCS/reviewer.html"
sed -i 's/--t2:#A0AEC0/--t2:#D0D7E0/g' "$DOCS/reviewer.html"
sed -i 's/--t3:#5A6578/--t3:#8B95A5/g' "$DOCS/reviewer.html"
sed -i 's/--border:rgba(255,255,255,.05)/--border:rgba(255,255,255,.12)/g' "$DOCS/reviewer.html"
sed -i 's/--accent:#34D1B4/--accent:#3DE8C8/g' "$DOCS/reviewer.html"
sed -i 's/--accent-dim:rgba(52,209,180,.08)/--accent-dim:rgba(61,232,200,.12)/g' "$DOCS/reviewer.html"
sed -i 's/--accent-border:rgba(52,209,180,.15)/--accent-border:rgba(61,232,200,.28)/g' "$DOCS/reviewer.html"
sed -i 's/--bg-in:#0A0D14/--bg-in:#0E1219/g' "$DOCS/reviewer.html"
sed -i 's/--bg2:#0D1017/--bg2:#111620/g' "$DOCS/reviewer.html"
sed -i 's/--bg3:#141821/--bg3:#1A1F2B/g' "$DOCS/reviewer.html"

# Brighten green/amber for reviewer badges
sed -i 's/--green-dim:rgba(34,197,94,.08)/--green-dim:rgba(34,197,94,.14)/g' "$DOCS/reviewer.html"
sed -i 's/--green-border:rgba(34,197,94,.18)/--green-border:rgba(34,197,94,.32)/g' "$DOCS/reviewer.html"
sed -i 's/--amber-dim:rgba(245,158,11,.08)/--amber-dim:rgba(245,158,11,.14)/g' "$DOCS/reviewer.html"
sed -i 's/--amber-border:rgba(245,158,11,.18)/--amber-border:rgba(245,158,11,.32)/g' "$DOCS/reviewer.html"

# Make table header text bigger and brighter
sed -i 's/thead th{position:sticky;top:52px;background:var(--bg3);padding:11px 14px;font-size:\.65rem;font-weight:600;text-transform:uppercase;letter-spacing:\.08em;color:var(--t3)/thead th{position:sticky;top:52px;background:var(--bg3);padding:13px 14px;font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--t2)/g' "$DOCS/reviewer.html"

# Make table cell text bigger
sed -i 's/td{padding:14px;border-bottom:1px solid var(--border);vertical-align:top;font-size:\.85rem}/td{padding:14px;border-bottom:1px solid var(--border);vertical-align:top;font-size:.95rem;color:var(--t1)}/g' "$DOCS/reviewer.html"

# Make AI score bigger
sed -i 's/\.ai-score{font-family:var(--fd);font-size:1\.6rem/.ai-score{font-family:var(--fd);font-size:1.9rem/g' "$DOCS/reviewer.html"

# Make AI reason text brighter
sed -i 's/\.ai-reason{font-size:\.72rem;color:var(--t3)/.ai-reason{font-size:.8rem;color:var(--t2)/g' "$DOCS/reviewer.html"

# Make page heading bigger
sed -i 's/\.page-head h1{font-family:var(--fd);font-size:1\.4rem/.page-head h1{font-family:var(--fd);font-size:1.75rem/g' "$DOCS/reviewer.html"

# Make decision buttons bigger
sed -i 's/\.d-btn{font-family:var(--fb);font-size:\.75rem/.d-btn{font-family:var(--fb);font-size:.85rem/g' "$DOCS/reviewer.html"

# Make comment area text bigger
sed -i 's/\.comment-area{font-family:var(--fb);font-size:\.78rem/.comment-area{font-family:var(--fb);font-size:.88rem/g' "$DOCS/reviewer.html"

# Make submit button bigger
sed -i 's/\.btn-submit{font-family:var(--fb);font-size:\.78rem/.btn-submit{font-family:var(--fb);font-size:.88rem/g' "$DOCS/reviewer.html"

# Make read button bigger
sed -i 's/\.btn-read{font-family:var(--fb);font-size:\.72rem/.btn-read{font-family:var(--fb);font-size:.85rem/g' "$DOCS/reviewer.html"

# Make cell-id bigger
sed -i 's/\.cell-id{font-weight:700;font-variant-numeric:tabular-nums;font-size:\.9rem/.cell-id{font-weight:700;font-variant-numeric:tabular-nums;font-size:1.05rem/g' "$DOCS/reviewer.html"

# Make cell-prompt brighter
sed -i 's/\.cell-prompt{font-size:\.72rem;color:var(--t3)/.cell-prompt{font-size:.82rem;color:var(--t2)/g' "$DOCS/reviewer.html"

# Make stat chips bigger
sed -i 's/\.stat-chip{display:flex;align-items:center;gap:5px;font-size:\.72rem/.stat-chip{display:flex;align-items:center;gap:5px;font-size:.85rem/g' "$DOCS/reviewer.html"

# Make topbar elements bigger (same as index)
sed -i 's/\.brand{font-family:var(--fd);font-size:1rem/.brand{font-family:var(--fd);font-size:1.15rem/g' "$DOCS/reviewer.html"
sed -i 's/\.topbar-user{display:flex;align-items:center;gap:7px;font-size:\.78rem/.topbar-user{display:flex;align-items:center;gap:7px;font-size:.9rem/g' "$DOCS/reviewer.html"
sed -i 's/\.back-link{display:inline-flex;align-items:center;gap:5px;font-size:\.78rem;font-weight:500;color:var(--t3)/.back-link{display:inline-flex;align-items:center;gap:5px;font-size:.88rem;font-weight:500;color:var(--t2)/g' "$DOCS/reviewer.html"

# Make badge text bigger in reviewer
sed -i 's/\.badge{display:inline-flex;align-items:center;font-size:\.63rem/.badge{display:inline-flex;align-items:center;font-size:.75rem/g' "$DOCS/reviewer.html"

# Modal text brighter
sed -i 's/\.modal-essay{font-size:\.9rem;line-height:1\.85;color:var(--t2)/.modal-essay{font-size:1rem;line-height:1.85;color:var(--t1)/g' "$DOCS/reviewer.html"


echo "=== Fixing home.html ==="

# Same base color fixes
sed -i 's/--t1:#F0F4F8/--t1:#FFFFFF/g' "$DOCS/home.html"
sed -i 's/--t2:#A0AEC0/--t2:#D0D7E0/g' "$DOCS/home.html"
sed -i 's/--t3:#5A6578/--t3:#8B95A5/g' "$DOCS/home.html"
sed -i 's/--border:rgba(255,255,255,.05)/--border:rgba(255,255,255,.12)/g' "$DOCS/home.html"
sed -i 's/--accent:#34D1B4/--accent:#3DE8C8/g' "$DOCS/home.html"
sed -i 's/--accent-dim:rgba(52,209,180,.08)/--accent-dim:rgba(61,232,200,.12)/g' "$DOCS/home.html"
sed -i 's/--accent-border:rgba(52,209,180,.15)/--accent-border:rgba(61,232,200,.28)/g' "$DOCS/home.html"
sed -i 's/--bg2:#0D1017/--bg2:#111620/g' "$DOCS/home.html"
sed -i 's/--bg3:#141821/--bg3:#1A1F2B/g' "$DOCS/home.html"

# Make portal card description text brighter
sed -i 's/\.portal .desc{color:var(--t2);font-size:\.875rem/.portal .desc{color:var(--t1);font-size:.95rem/g' "$DOCS/home.html"

# Make feature text brighter
sed -i 's/\.feat p{font-size:\.78rem;color:var(--t3)/.feat p{font-size:.85rem;color:var(--t2)/g' "$DOCS/home.html"

# Make feature heading bigger
sed -i 's/\.feat h3{font-size:\.875rem/.feat h3{font-size:1rem/g' "$DOCS/home.html"

# Make tech strip brighter
sed -i 's/\.tech span{font-size:\.7rem;font-weight:600;color:var(--t3);letter-spacing:\.07em;text-transform:uppercase;opacity:\.55/.tech span{font-size:.78rem;font-weight:600;color:var(--t2);letter-spacing:.07em;text-transform:uppercase;opacity:.75/g' "$DOCS/home.html"

# Modal input placeholder brighter
sed -i 's/\.modal-field input::placeholder{color:var(--t3)/.modal-field input::placeholder{color:var(--t2)}/g' "$DOCS/home.html"

# Stat numbers stay bright
sed -i 's/\.stat-num{font-family:var(--fd);font-size:1\.75rem/.stat-num{font-family:var(--fd);font-size:2rem/g' "$DOCS/home.html"


echo ""
echo "=== ALL DONE ==="
echo "Now push to GitHub:"
echo ""
echo "  cd /home/g623dks && git add docs/ && git commit -m 'fix: improve UI readability - brighter text, visible borders, bigger fonts' && git push origin main"
echo ""
echo "GitHub Pages will update in ~1 min."
