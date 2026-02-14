# Wyniki eksperymentu tokenizacji

5 tokenizerow x 7 jezykow x 100 zdan z artykulow Wikipedia PL

## Zrodla danych

**Korpus**: 100 zdan z artykulow polskiej Wikipedii

**Tlumaczenie**: Google Translate via deep_translator

**Data generacji**: 2026-02-13 15:55:14

**Artykuly zrodlowe:**

- [Sztuczna inteligencja](https://pl.wikipedia.org/wiki/Sztuczna_inteligencja) (technologia) — 34 zdan
- [Fotosynteza](https://pl.wikipedia.org/wiki/Fotosynteza) (nauka) — 33 zdan
- [Bitwa pod Grunwaldem](https://pl.wikipedia.org/wiki/Bitwa_pod_Grunwaldem) (historia) — 33 zdan


## Sredni narzut tokenizacji vs angielski (%)

| Jezyk | tiktoken (GPT-4) | APT4 (Bielik v3) | TinyLlama (Llama 2) | Qwen 2.5 | multilingual-e5-large |
|-------|--------|--------|--------|--------|--------|
| **PL** (Polish) | +75.6% (38) | -31.1% (13) | +57.8% (32) | +65.8% (35) | +12.1% (17) |
| **DE** (German) | +50.1% (23) | +34.5% (21) | +37.0% (22) | +48.3% (23) | +13.8% (15) |
| **AR** (Arabic) | +180.7% (61) | +334.4% (79) | +216.6% (70) | +55.7% (30) | +13.0% (20) |
| **HY** (Armenian) | +773.5% (263) | +432.9% (120) | +357.9% (133) | +368.4% (137) | +34.3% (26) |
| **JA** (Japanese) | +115.1% (44) | +249.3% (83) | +110.3% (48) | +39.2% (29) | +11.9% (25) |
| **ZH** (Chinese) | +66.3% (30) | +140.8% (45) | +77.1% (33) | -5.8% (18) | -8.9% (21) |

## Analiza dlugosci znakowej tekstu

| Jezyk | Srednia dl. (znaki) | Sredni narzut znakowy vs EN |
|-------|---------------------|----------------------------|
| **EN** (English) | 132 | - |
| **PL** (Polish) | 132 | +1.5% |
| **DE** (German) | 146 | +11.1% |
| **AR** (Arabic) | 113 | -13.3% |
| **HY** (Armenian) | 136 | +4.5% |
| **JA** (Japanese) | 58 | -54.2% |
| **ZH** (Chinese) | 43 | -66.2% |

## Znormalizowany narzut tokenizacji vs angielski (%) — tokens/char

| Jezyk | tiktoken (GPT-4) | APT4 (Bielik v3) | TinyLlama (Llama 2) | Qwen 2.5 | multilingual-e5-large |
|-------|--------|--------|--------|--------|--------|
| **PL** (Polish) | +72.8% (29) | -31.7% (13) | +55.7% (26) | +63.3% (26) | +10.9% (13) |
| **DE** (German) | +35.5% (18) | +21.1% (14) | +23.9% (19) | +34.0% (19) | +2.9% (12) |
| **AR** (Arabic) | +226.9% (65) | +407.3% (90) | +270.2% (80) | +81.5% (33) | +31.4% (22) |
| **HY** (Armenian) | +734.1% (210) | +412.3% (106) | +338.1% (106) | +347.6% (108) | +29.5% (26) |
| **JA** (Japanese) | +394.3% (121) | +694.1% (175) | +383.8% (125) | +215.9% (66) | +151.2% (46) |
| **ZH** (Chinese) | +432.9% (139) | +671.5% (198) | +471.2% (160) | +194.6% (54) | +182.8% (57) |

## Ranking jezykow (od najtanszego do najdrozszego)

### tiktoken (GPT-4)

1. **DE** (German): +50.1%
2. **ZH** (Chinese): +66.3%
3. **PL** (Polish): +75.6%
4. **JA** (Japanese): +115.1%
5. **AR** (Arabic): +180.7%
6. **HY** (Armenian): +773.5%

### APT4 (Bielik v3)

1. **PL** (Polish): -31.1%
2. **DE** (German): +34.5%
3. **ZH** (Chinese): +140.8%
4. **JA** (Japanese): +249.3%
5. **AR** (Arabic): +334.4%
6. **HY** (Armenian): +432.9%

### TinyLlama (Llama 2)

1. **DE** (German): +37.0%
2. **PL** (Polish): +57.8%
3. **ZH** (Chinese): +77.1%
4. **JA** (Japanese): +110.3%
5. **AR** (Arabic): +216.6%
6. **HY** (Armenian): +357.9%

### Qwen 2.5

1. **ZH** (Chinese): -5.8%
2. **JA** (Japanese): +39.2%
3. **DE** (German): +48.3%
4. **AR** (Arabic): +55.7%
5. **PL** (Polish): +65.8%
6. **HY** (Armenian): +368.4%

### multilingual-e5-large

1. **ZH** (Chinese): -8.9%
2. **JA** (Japanese): +11.9%
3. **PL** (Polish): +12.1%
4. **AR** (Arabic): +13.0%
5. **DE** (German): +13.8%
6. **HY** (Armenian): +34.3%


## Wizualizacja tokenow (tiktoken GPT-4, wybrane zdania)

### Zdanie: s001

**EN** (33 tokenow):
> `As` | ` of` | ` ` | `202` | `5` | `,` | ` L` | `LM` | `s` | ` are` | ` susceptible` | ` to` | ` generating` | ` false` | ` information` | ` called` | ` halluc` | `inations` | `,` | ` and` | ` the` | ` problem` | ` can` | ` get` | ` worse` | ` as` | ` these` | ` models` | ` are` | ` used` | ` to` | ` reason` | `.`

**PL** (66 tokenow):
> `Wed` | `ług` | ` stan` | `u` | ` na` | ` ` | `202` | `5` | ` ro` | `k` | ` L` | `LM` | `-y` | ` są` | ` pod` | `at` | `ne` | ` na` | ` gener` | `owanie` | ` fa` | `ł` | `s` | `zy` | `w` | `ych` | ` inform` | `acji` | ` n` | `azy` | `w` | `anych` | ` hal` | `uc` | `yn` | `ac` | `j` | `ami` | `,` | ` a` | ...

### Zdanie: s002

**EN** (44 tokenow):
> `Art` | `ificial` | ` intelligence` | ` was` | ` dealt` | ` with` | `,` | ` among` | ` others` | `,` | ` by` | `:` | ` Marvin` | ` M` | `insky` | `,` | ` John` | ` McCarthy` | `,` | ` Alan` | ` Turing` | `,` | ` Edward` | ` Fe` | `igen` | `baum` | `,` | ` Raj` | ` Red` | `dy` | `,` | ` Jude` | `a` | ` Pearl` | `,` | ` Allen` | ` New` | `ell` | `,` | ` Herbert` | ...

**PL** (48 tokenow):
> `S` | `zt` | `uc` | `zn` | `ą` | ` intelig` | `enc` | `ją` | ` zaj` | `m` | `ow` | `ali` | ` się` | ` m` | `.in` | `.` | ` Marvin` | ` M` | `insky` | `,` | ` John` | ` McCarthy` | `,` | ` Alan` | ` Turing` | `,` | ` Edward` | ` Fe` | `igen` | `baum` | `,` | ` Raj` | ` Red` | `dy` | `,` | ` Jude` | `a` | ` Pearl` | `,` | ` Allen` | ...

### Zdanie: s003

**EN** (24 tokenow):
> `AI` | ` algorithms` | ` can` | ` analyze` | ` large` | ` amounts` | ` of` | ` data` | ` faster` | ` and` | ` more` | ` accurately` | ` than` | ` humans` | `,` | ` which` | ` could` | ` bring` | ` benefits` | ` to` | ` patients` | ` and` | ` doctors` | `.`

**PL** (45 tokenow):
> `Alg` | `ory` | `t` | `my` | ` SI` | ` mog` | `ą` | ` anal` | `iz` | `ować` | ` du` | `że` | ` il` | `ości` | ` danych` | ` szy` | `bc` | `iej` | ` i` | ` dok` | `ład` | `niej` | ` niż` | ` lud` | `zie` | `,` | ` co` | ` może` | ` prz` | `yn` | `ie` | `ść` | ` kor` | `zy` | `ści` | ` dla` | ` pac` | `j` | `ent` | `ów` | ...


## Kluczowe wnioski

- **tiktoken (GPT-4)**: polski tekst potrzebuje srednio **+75.6%** (std=38) wiecej tokenow niz angielski
- **APT4 (Bielik v3)**: polski tekst potrzebuje srednio **-31.1%** (std=13) wiecej tokenow niz angielski
- **TinyLlama (Llama 2)**: polski tekst potrzebuje srednio **+57.8%** (std=32) wiecej tokenow niz angielski
- **Qwen 2.5**: polski tekst potrzebuje srednio **+65.8%** (std=35) wiecej tokenow niz angielski
- **multilingual-e5-large**: polski tekst potrzebuje srednio **+12.1%** (std=17) wiecej tokenow niz angielski

- Qwen 2.5 (specjalizowany w chinskim): narzut ZH = -5.8% vs srednia pozostalych = +68.8%

### Dekompozycja narzutu (PL vs EN)

Relacja multiplikatywna: (1 + surowy narzut) = (1 + narzut znakowy) x (1 + narzut znormalizowany)

- **tiktoken (GPT-4)**: surowy +75.6%, z czego narzut znakowy +1.5%, znormalizowany (tokenizer) +72.8%
- **APT4 (Bielik v3)**: surowy -31.1%, z czego narzut znakowy +1.5%, znormalizowany (tokenizer) -31.7%
- **TinyLlama (Llama 2)**: surowy +57.8%, z czego narzut znakowy +1.5%, znormalizowany (tokenizer) +55.7%
- **Qwen 2.5**: surowy +65.8%, z czego narzut znakowy +1.5%, znormalizowany (tokenizer) +63.3%
- **multilingual-e5-large**: surowy +12.1%, z czego narzut znakowy +1.5%, znormalizowany (tokenizer) +10.9%