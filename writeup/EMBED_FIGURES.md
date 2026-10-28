# Figürleri Kaggle Writeup gövdesine gömme

Kaggle'ın "Insert Image" penceresi tarayıcıda yerel dosya seçici açtığı için otomasyonla gömemedim. Galeride 7 figür zaten yayında. Gövdeye gömmek için:

1. Writeup > Edit. Gövdede figürün geçtiği paragrafın altına imleci koy.
2. Araç çubuğunda "Insert Image" > "Upload image from computer" > `figs/figN_*.png` (3200x1800 PNG).
3. Kaggle şu satırı üretir: `![](https://storage.googleapis.com/kaggle-media/...)`. Alt metni doldur.
4. Önerilen yerler (bölüm başlığından hemen sonra):
   - Fig 1: "2. What the Combine data measures"
   - Fig 2: "Reliability" paragrafından sonra
   - Fig 4: "4. Result" ilk paragrafından sonra
   - Fig 5: "Stress tests" paragrafından sonra
   - Fig 3: "8. Drill numbers do not travel"
   - Fig 6: "Hierarchical shrinkage" paragrafından sonra
   - Fig 7: "9. Out-of-time check"

Markdown şablonu (URL'ler yükleme sonrası gelir):

```markdown
![Fig. 4: Pressure rate vs Combine top speed](URL)
*Fig. 4. Adjusted pressure rate by Combine top speed. Band = 95% player-cluster bootstrap CI.*
```

HTML ile boyut sabitlemek istersen:

```html
<img src="URL" alt="Fig. 4" width="100%">
```

Not: Gövdeye gömülen görsel, galeriyle aynı dosyayı kullanır; kelime sayımına girmez. Gövdede şu an 1.942 kelime var (alıntı satırı dahil), alt yazı eklersen limitin (2.000) altında kalmaya dikkat et.

## Figür üretim kodu
Notebook'un Part 4 hücreleri (`notebook_source.py`, "Part 4. Figures" bölümü). `save()` fonksiyonu her figürü 16:9 (3200x1800 px), lacivert broadcast bannerlı ve kaynak satırlı çıkarır:

```python
def save(fig, name, right=None):
    n = name.split("_")[0].replace("fig", "")
    fig.set_size_inches(16, 9); fig.tight_layout(rect=[0.0, 0.05, 1, 0.915])
    if right: fig.subplots_adjust(right=right)
    fig.add_artist(plt.Rectangle((0, 0.94), 1, 0.06, transform=fig.transFigure, color="#0b2a4a", zorder=0))
    fig.add_artist(plt.Rectangle((0, 0.94), 0.006, 0.06, transform=fig.transFigure, color=ORANGE, zorder=1))
    fig.text(0.018, 0.97, f"SPEED TRAVELS  |  FIG. {n}", color="white", fontsize=17, fontweight="bold", va="center")
    fig.text(0.99, 0.97, "NFL BIG DATA BOWL 2027  |  COMBINE 10 Hz TRACKING VS. GAME PASS RUSH", color="#9fc3ee", fontsize=11.5, ha="right", va="center")
    fig.text(0.012, 0.012, "Source: NFL Big Data Bowl 2027 competition data. Models: GEE-logit clustered by rusher unless noted.", fontsize=9.5, color=MUTED)
    fig.savefig(f"{FIG}/{name}", dpi=200, facecolor=SURF); plt.show()
```
