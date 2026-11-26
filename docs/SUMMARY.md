# Projekt implementacji

Projekt z przedmiotu Metody Eksploracji Danych (MED), część 1: wnioskowanie z danych niekompletnych.

Dokument opisuje całą implementację, także moduły, które jeszcze nie powstały (oznaczone „planowane”).

## 1. Zakres

Projekt porównuje 4 strategie postępowania z brakującymi wartościami w zadaniu klasyfikacji:

| Nr | Strategia | Źródło |
|---|---|---|
| S1 | Zbiory przybliżone z relacją tolerancji na surowych danych | Kryszkiewicz (1998) |
| S2 | Usunięcie niepełnych rekordów treningowych, potem S1 | Kryszkiewicz (1998), rozdz. 6 (*removing examples' method*) |
| S3 | Imputacja średnią lub modą, potem S1 | metoda bazowa (*row average* u Troyanskiej i in.) |
| S4 | Imputacja kNN, potem S1 | Troyanskaya i in. (2001) |

Wszystkie 4 strategie używają tego samego klasyfikatora: reguł decyzyjnych z modelu zbiorów przybliżonych. Porównanie pokazuje więc tylko wpływ sposobu obsługi braków.

Testy mierzą:

- jakość klasyfikacji i imputacji przy różnym odsetku braków (0–50%),
- wpływ parametrów (k w kNN, liczba przedziałów dyskretyzacji),
- czas działania i skalowalność względem liczby rekordów i liczby atrybutów.

## 2. Technologie

| Element | Wybór | Uzasadnienie |
|---|---|---|
| Język | Python 3.12 (lokalnie), 3.13 (Kaggle) | popularny, dobre biblioteki do tabel i tablic |
| Tabele | pandas | wczytywanie plików UCI, typy kolumn |
| Tablice | numpy | operacje wektorowe, zbiory bitowe na `uint64` |
| Testy | pytest | krótkie testy każdego modułu |
| Obliczenia | Kaggle CPU (4 rdzenie, 30 GB RAM) | lokalny komputer jest słaby |
| Kontrola wersji | git, GitHub (publiczne repozytorium) | kernele Kaggle klonują kod |

Projekt nie używa gotowych bibliotek do zbiorów przybliżonych ani do imputacji. Wszystkie algorytmy są naszą implementacją.

## 3. Struktura implementacji

```
src/
  data.py        wczytanie 6 zbiorów danych we wspólnej postaci
  missing.py     symulacja braków (MCAR)
  impute.py      imputacja kNN, imputacja średnią/modą, błąd imputacji
  rough.py       dyskretyzacja, klasy tolerancji, aproksymacje, decyzja uogólniona,
                 redukty i reguły decyzyjne (planowane)
  classify.py    klasyfikator regułowy (planowany)
  experiment.py  4 strategie z walidacją krzyżową (planowany)
tests/
  test_core.py   testy wszystkich modułów
jobs/runs/       jeden folder na każde zadanie Kaggle (run.py, kernel-metadata.json, małe wyniki)
```

Przepływ danych:

```
load_dataset --> add_mcar --> [S2: usunięcie | S3: impute_mean_mode | S4: impute_knn] -->
cut_points / discretize --> encode --> tolerance_classes --> generalized_decision -->
redukty względne dla obiektów --> reguły decyzyjne --> klasyfikacja --> dokładność
```

### 3.1. `src/data.py`

| Funkcja | Opis |
|---|---|
| `download_all(out)` | Pobiera 6 archiwów zip z UCI. Zapisuje `manifest.json` z rozmiarami i skrótami SHA-256. |
| `data_dir()` | Znajduje dane na Kaggle (`/kaggle/input`) albo lokalnie (`data/`). |
| `load_dataset(name)` | Zwraca zbiór we wspólnej postaci (rozdz. 4.1). |
| `numeric_attributes(df)` | Zwraca nazwy atrybutów liczbowych. |

`SPECS` to słownik z opisem każdego zbioru: pliki, nazwy kolumn, kolumna klasy, kolumny liczbowe.

### 3.2. `src/missing.py`

| Funkcja | Opis |
|---|---|
| `add_mcar(df, fraction, seed)` | Losowo usuwa zadany ułamek znanych wartości atrybutów. Każda wartość ma to samo prawdopodobieństwo usunięcia (MCAR). Klasa się nie zmienia. Zwraca nową tabelę i maskę usuniętych wartości. |

To ten sam schemat, którego używają Troyanskaya i in.: z kompletnych danych usuwa się losowo 1–20% wartości, a potem porównuje oszacowania z prawdziwymi wartościami.

### 3.3. `src/impute.py`

| Funkcja | Krok u Troyanskiej i in. (2001) | Opis |
|---|---|---|
| `impute_mean_mode(df)` | metoda bazowa (*row average*) | Średnia dla atrybutu liczbowego, moda dla symbolicznego. |
| `_encode(df)` | przygotowanie | Wartości liczbowe jako float, symboliczne jako kody kategorii, `NaN` dla braku. |
| `_gower_distances(values, is_numeric, rows)` | 1. podobieństwo do innych rekordów | Odległość Gowera po atrybutach znanych w obu rekordach (rozdz. 5.1). |
| `impute_knn(df, k)` | 2. K najbliższych rekordów, które mają wartość brakującego atrybutu; 3. średnia ważona | Waga 1/odległość. Średnia ważona (liczbowe), ważona moda (symboliczne). Gdy brak sąsiadów: średnia/moda. |
| `imputation_error(true, imputed, removed)` | ocena (*normalized RMS error*) | `nrmse` dla atrybutów liczbowych, `error_rate` dla symbolicznych. |

### 3.4. `src/rough.py`

Oznaczenia za Kryszkiewicz (1998). Tablica decyzyjna to DT = (O, AT ∪ {d}), a `*` oznacza wartość brakującą.

| Funkcja | Definicja u Kryszkiewicz (1998) | Opis |
|---|---|---|
| `cut_points(df, bins)`, `discretize(df, cuts)` | przygotowanie (artykuł zakłada tylko wartości symboliczne) | Przedziały o równej liczności wyznaczone ze znanych wartości. |
| `encode(df)` | DT = (O, AT ∪ {d}) | Macierz kodów, -1 oznacza `*`. Wektor kodów decyzji. |
| `pack`, `unpack`, `count` | zbiory obiektów | Zbiory bitowe ze słów `uint64` (rozdz. 4.2). |
| `tolerance_classes(codes, A)` | SIM(A) = {(x, y) ∈ O × O: ∀a ∈ A, a(x) = a(y) ∨ a(x) = * ∨ a(y) = *}, S_A(x) = {y ∈ O: (x, y) ∈ SIM(A)} | Klasa tolerancji każdego obiektu jako zbiór bitowy (rozdz. 5.2). |
| `lower_approximation(classes, X)` | A̲X = {x ∈ O: S_A(x) ⊆ X} | Operacje bitowe na każdym wierszu. |
| `upper_approximation(classes, X)` | ĀX = {x ∈ O: S_A(x) ∩ X ≠ ∅} | Operacje bitowe na każdym wierszu. |
| `generalized_decision(classes, d)` | ∂_A(x) = {i: i = d(y), y ∈ S_A(x)} | Macierz logiczna obiekty × decyzje. |
| `discernibility(codes, general, x)` (planowana, B1) | α_AT(x, y) = {a ∈ AT: (x, y) ∉ SIM({a})}, czyli a(x) ≠ *, a(y) ≠ * i a(x) ≠ a(y); tylko dla y z d(y) ∉ ∂_AT(x) | Wiersz x macierzy rozróżnialności jako maska atrybutów (`uint64`) dla każdego y. |
| `local_reduct(codes, general, x)` (planowana, B1) | redukt względny dla x: minimalny A ⊆ AT, dla którego ∂_A(x) = ∂_AT(x); implikant pierwszy funkcji Δ*(x) = Π_{y: d(y) ∉ ∂_AT(x)} Σ α_AT(x, y) | Zachłanne pokrycie zbioru: dodaje atrybut, który występuje w największej liczbie niepokrytych α. Potem usuwa atrybuty zbędne. |
| `reduct(codes, general)` (planowana, B1) | redukt względny DT: minimalny A ⊆ AT, dla którego ∂_A = ∂_AT; implikant pierwszy Δ* = Π_{(x, y): d(y) ∉ ∂_AT(x)} Σ α_AT(x, y) | Ta sama metoda zachłanna na wszystkich parach (x, y). |
| `rules(codes, d, general)` (planowana, B2) | reguła optymalna dla x: ∧_{a ∈ A} (a, a(x)) → ∨_{w ∈ ∂_AT(x)} (d, w), gdzie A to redukt względny dla x | Jedna reguła z reduktu każdego obiektu. Warunek (a, *) jest zawsze spełniony, więc go pomijamy. Reguła jest pewna, gdy \|∂_AT(x)\| = 1, w przeciwnym razie jest możliwa. Duplikaty reguł łączymy, a ich wsparcia sumujemy. |

Wyznaczenie wszystkich reduktów wymaga wszystkich implikantów pierwszych. Jest to wykładnicze w liczbie atrybutów, dlatego projekt używa heurystyki zachłannej.

### 3.5. `src/classify.py` (planowany, B3)

| Funkcja | Opis |
|---|---|
| `RuleClassifier(bins)` | Przechowuje punkty podziału, reguły i najczęstszą klasę zbioru treningowego. |
| `fit(df)` | `cut_points`, `discretize`, `encode`, `tolerance_classes`, `generalized_decision`, `rules`. |
| `predict(df)` | Reguła pasuje do rekordu z, jeśli dla każdego warunku (a, v) zachodzi a(z) = v albo a(z) = `*`. Każda pasująca reguła dodaje swoje wsparcie każdej decyzji ze swojej prawej strony. Wygrywa decyzja z największą sumą. Gdy żadna reguła nie pasuje, wynikiem jest najczęstsza klasa. |

### 3.6. `src/experiment.py` (planowany, B4)

| Funkcja | Opis |
|---|---|
| `prepare(train, test, strategy, k)` | Stosuje S1–S4 (rozdz. 1). S2 usuwa tylko rekordy treningowe. S3 i S4 imputują atrybuty wszystkich rekordów, ale nie używają klasy. |
| `evaluate(name, fraction, strategy, seed, folds=10, k=10, bins=4)` | `add_mcar`, stratyfikowana walidacja krzyżowa, `prepare`, `RuleClassifier`. Zwraca dokładność, pokrycie (odsetek rekordów testowych, do których pasuje jakaś reguła), liczbę reguł i czas. |

## 4. Struktury danych

### 4.1. Dane źródłowe

`load_dataset` zwraca `pandas.DataFrame`:

- jeden wiersz to jeden rekord, jedna kolumna to jeden atrybut, kolumna `class` jest ostatnia,
- atrybut liczbowy ma typ `float64`, brak to `NaN`,
- atrybut symboliczny i klasa mają typ `category`, brak to `NaN` (kod -1).

| Zbiór | Rekordy | Atrybuty (liczbowe) | Brakujące komórki | Niepełne rekordy | Klasy |
|---|---|---|---|---|---|
| `voting` | 435 | 16 (0) | 5,63% | 46,7% | 2 |
| `hepatitis` | 155 | 19 (6) | 5,67% | 48,4% | 2 |
| `mushroom` | 8124 | 22 (0) | 1,39% | 30,5% | 2 |
| `car` | 1728 | 6 (0) | 0% | 0% | 4 |
| `wdbc` | 569 | 30 (30) | 0% | 0% | 2 |
| `adult` | 48842 | 14 (6) | 0,95% | 7,4% | 2 |

Maska z `add_mcar` to logiczna tablica `numpy` (rekordy × atrybuty). Wskazuje pozycje prawdziwych wartości dla `imputation_error`.

### 4.2. Struktury danych algorytmów

| Struktura | Typ i kształt | Pamięć | Użycie |
|---|---|---|---|
| kody atrybutów | `int32`, n × m, -1 to `*` | 4nm B | wszystkie funkcje zbiorów przybliżonych |
| kody decyzji | `int32`, n | 4n B | decyzja uogólniona, reguły |
| zbiór obiektów | `uint64`, ⌈n/64⌉ słów, bit y to obiekt y | n/8 B | X, S_A(x), klasy decyzyjne |
| klasy tolerancji | `uint64`, n × ⌈n/64⌉ | n²/8 B (`adult`: 299 MB) | aproksymacje, decyzja uogólniona |
| T(a, v) | `uint64`, (liczba wartości + 1) × ⌈n/64⌉ dla każdego atrybutu | suma wartości × n/8 B | budowa klas tolerancji |
| decyzja uogólniona | `bool`, n × liczba decyzji | n × liczba decyzji B | redukty, reguły |
| wiersz macierzy rozróżnialności | `uint64`, n, bit a to atrybut a (m ≤ 64) | 8n B | redukt względny dla obiektu |
| reguła | warunki (indeks atrybutu, kod wartości), zbiór decyzji (maska bitowa), wsparcie | mała | klasyfikator |
| blok odległości kNN | `float64`, blok × n | najwyżej 5 mln wartości (40 MB) | imputacja kNN |

Zbiory bitowe przyspieszają liczenie klas tolerancji: jedno AND dwóch słów 64-bitowych porównuje 64 obiekty naraz. Liczność zbioru daje `numpy.bitwise_count`.

## 5. Algorytmy

### 5.1. Imputacja kNN (Troyanskaya i in. 2001)

Dla każdego rekordu x z brakami:

1. Policz odległość od x do wszystkich rekordów. Odległość używa tylko atrybutów znanych w obu rekordach. Odległość Gowera: |x_a − y_a| / rozstęp(a) dla atrybutu liczbowego, 0 albo 1 dla symbolicznego, średnia po wspólnych atrybutach.
2. Dla każdego brakującego atrybutu a wybierz k najbliższych rekordów, które mają wartość a.
3. Oszacuj a(x) jako średnią ważoną (liczbowe) albo ważoną modę (symboliczne) z k wartości. Waga to 1/odległość.

Różnice względem artykułu:

- Artykuł dotyczy tylko danych liczbowych (ekspresja genów) i używa odległości euklidesowej. Nasze zbiory są mieszane, dlatego używamy odległości Gowera.
- Artykuł mówi tylko, że wkład sąsiada jest „ważony podobieństwem”, i nie podaje wzoru. My używamy wagi 1/odległość.
- *Row average* w artykule to średnia z wiersza (genu) po wszystkich eksperymentach. U nas atrybuty mają różne znaczenia, więc średnia z rekordu nie ma sensu. Odpowiednikiem jest średnia/moda atrybutu (kolumny).
- Artykuł dzieli błąd RMS przez średnią wartość całej kompletnej macierzy. Nasze atrybuty mają różne skale, więc błąd każdego atrybutu dzielimy przez jego odchylenie standardowe.

Artykuł podaje złożoność O(m²n) dla m genów i n eksperymentów, a najlepsze wyniki daje k = 10–20. To zgadza się z naszą złożonością O(n_inc · n · m) (rozdz. 6).

### 5.2. Klasy tolerancji (Kryszkiewicz 1998)

Własność 2.1 z artykułu: SIM(A) = ∩_{a ∈ A} SIM({a}). Na niej opiera się algorytm. Dla każdego atrybutu a i wartości v budujemy zbiór bitowy T(a, v) = {y: a(y) = v albo a(y) = *}. Wtedy:

S_A(x) = ∩_{a ∈ A, a(x) ≠ *} T(a, a(x)).

Macierz powstaje blokami wierszy, więc tablice pomocnicze zajmują mało pamięci.

### 5.3. Redukty i reguły (planowane)

1. Policz ∂_AT(x) dla każdego obiektu.
2. Dla każdego obiektu x policz α_AT(x, y) dla y z d(y) ∉ ∂_AT(x), jako maski atrybutów.
3. Znajdź redukt względny dla x metodą zachłannego pokrycia zbioru.
4. Zbuduj regułę x z jego reduktu i z ∂_AT(x).

Według Kryszkiewicz (rozdz. 6) reguły deterministyczne tej metody są pewne w każdym uzupełnieniu tablicy. Metoda usuwania przykładów (S2) może natomiast dać fałszywe reguły pewne. Eksperymenty sprawdzą ten efekt.

## 6. Efektywność

Oznaczenia: n to liczba rekordów, m liczba atrybutów, n_inc liczba niepełnych rekordów, k liczba sąsiadów, D liczba decyzji.

| Operacja | Czas | Pamięć |
|---|---|---|
| `load_dataset` | O(nm) | O(nm) |
| `add_mcar` | O(nm) | O(nm) |
| `impute_mean_mode` | O(nm) | O(nm) |
| `impute_knn` | O(n_inc · n · m) | O(blok · n) |
| `tolerance_classes` | O(m · n²/64) | O(n²/8) |
| aproksymacja jednego zbioru | O(n²/64) | O(n) |
| `generalized_decision` | O(D · n²/64) | O(nD) |
| redukt względny jednego obiektu (planowany) | O(nm + nm²) | O(n) |
| reguły wszystkich obiektów (planowane) | O(n²m²) | O(nm) |
| `predict` dla t rekordów (planowany) | O(t · liczba reguł · m) | O(t · liczba reguł / 8) |

Klasy tolerancji nie są wąskim gardłem. Najwolniejsza jest imputacja kNN, gdy wiele rekordów jest niepełnych. Wśród kroków planowanych najwolniejsze są reguły dla wszystkich obiektów, dlatego dla `adult` trzeba będzie użyć próbki rekordów.

### 6.1. Zmierzone czasy

Zadanie `timing` (`jobs/runs/2026-11-26_03_timing/`) zmierzyło czasy na Kaggle CPU (4 rdzenie, Python 3.13, numpy 2.1.3). Każda wartość to mediana z 3 ziaren. Odsetek braków MCAR wynosi 10%, k = 10.

Liczba rekordów (`adult`, rekordy kompletne, 14 atrybutów):

| Rekordy | kNN (s) | Klasy tolerancji (s) | Średnia \|S(x)\| |
|---|---|---|---|
| 1000 | 0,17 | 0,001 | 1,8 |
| 2000 | 0,62 | 0,003 | 2,8 |
| 5000 | 4,7 | 0,011 | 5,0 |
| 10000 | 18,7 | 0,063 | 9,3 |
| 20000 | 82,5 | 0,37 | 17,2 |
| 45222 | 434 | 1,76 | 38,4 |

Przy wzroście z 20000 do 45222 rekordów (× 2,26) czas kNN rośnie × 5,3, a czas klas tolerancji × 4,8. Oba wyniki zgadzają się z O(n²), bo 2,26² = 5,1. Dla porównania: Troyanskaya i in. podają 3,23 min dla 6153 genów i 14 eksperymentów przy 10% braków (C++, Pentium III 500 MHz).

Liczba atrybutów (`wdbc` 569 rekordów, `mushroom` 8124 rekordy):

| Zbiór | Atrybuty | kNN (s) | Klasy tolerancji (s) | Średnia \|S(x)\| |
|---|---|---|---|---|
| `wdbc` | 5 / 10 / 20 / 30 | 0,015 / 0,035 / 0,086 / 0,128 | 0,0004 / 0,0006 / 0,0013 / 0,0016 | 21,4 / 2,5 / 1,0 / 1,0 |
| `mushroom` | 5 / 10 / 15 / 22 | 2,7 / 6,8 / 12,1 / 18,1 | 0,016 / 0,025 / 0,039 / 0,050 | 233 / 84 / 19,5 / 6,5 |

Czas rośnie w przybliżeniu liniowo z m. Im więcej atrybutów, tym mniejsze klasy tolerancji.

Odsetek braków (`car` 1728 rekordów, `mushroom` 8124 rekordy):

| Odsetek | 0% | 10% | 20% | 30% | 40% | 50% |
|---|---|---|---|---|---|---|
| `car` kNN (s) | 0,004 | 0,10 | 0,21 | 0,28 | 0,31 | 0,33 |
| `car` średnia \|S(x)\| | 1 | 10 | 47 | 134 | 297 | 535 |
| `mushroom` kNN (s) | 5,5 | 18,2 | 21,7 | 24,8 | 27,8 | 30,9 |
| `mushroom` średnia \|S(x)\| | 1 | 6,5 | 26 | 78 | 212 | 563 |

- Czas kNN rośnie z liczbą niepełnych rekordów n_inc.
- Czas klas tolerancji nie zależy od odsetka braków (`car` 0,001 s, `mushroom` 0,05 s).
- Klasy tolerancji rosną bardzo szybko z odsetkiem braków. Przy 50% jedna klasa w `car` obejmuje 31% wszystkich rekordów. Decyzja uogólniona ma wtedy więcej wartości, a reguły stają się mniej pewne.

Liczba sąsiadów k = 1–50 nie wpływa na czas kNN (`wdbc`: 0,13 s dla każdego k). Kosztowne jest liczenie odległości, a nie wybór sąsiadów.

## 7. Plan testów

### 7.1. Testy kodu (`tests/test_core.py`)

- `load_dataset`: liczby rekordów, atrybutów i atrybutów liczbowych zgadzają się z opisami UCI.
- `add_mcar`: ułamek usuniętych wartości jest poprawny, klasa i typy się nie zmieniają, to samo ziarno daje tę samą tabelę.
- `impute_knn`: po imputacji nie ma braków, typy się nie zmieniają, błąd jest mniejszy niż dla średniej/mody.
- `tolerance_classes`: dla tablicy 2 z Kryszkiewicz (1998) dostajemy klasy tolerancji, decyzje uogólnione i aproksymacje z przykładów 2.1 i 4.1. Na 4 zbiorach zbiory bitowe są identyczne z bezpośrednim liczeniem SIM.
- Planowane: redukty i reguły dla tablicy 2 zgadzają się z przykładami 4.2 i 5.2. Redukt DT to {Size, Max-Speed}, redukt względny obiektów 1–2 to {Max-Speed}, a obiektów 3–6 to {Size}. Reguły to (X, low) → (d, good), (S, compact) → (d, poor), (S, full) → (d, good) ∨ (d, excel.).

### 7.2. Eksperymenty (Kaggle CPU)

| Badanie | Zbiory | Parametry | Miary |
|---|---|---|---|
| Odporność na braki | wszystkie 6 (`adult`: próbka) | MCAR 0, 5, 10, 20, 30, 40, 50%; strategie S1–S4 | dokładność, pokrycie, liczba reguł |
| Naturalne braki | `voting`, `hepatitis`, `mushroom`, `adult` | strategie S1–S4 | dokładność, pokrycie |
| Jakość imputacji | `wdbc`, `hepatitis`, `voting`, `car` | MCAR 5–50%; k = 1, 5, 10, 20, 50 | nrmse, odsetek błędów |
| Dyskretyzacja | `wdbc`, `hepatitis` | 2, 3, 4, 6, 8 przedziałów | dokładność |
| Skalowalność (rekordy) | `adult` | 1000–45222 rekordów | czas |
| Skalowalność (atrybuty) | `wdbc`, `mushroom` | 5–30 atrybutów | czas |

Każdy wynik to średnia z co najmniej 5 ziaren `add_mcar` i stratyfikowanej 10-krotnej walidacji krzyżowej.

## 8. Bibliografia

- Kryszkiewicz, M. (1998). Rough set approach to incomplete information systems. *Information Sciences*, 112(1–4), 39–49.
- Troyanskaya, O., Cantor, M., Sherlock, G., Brown, P., Hastie, T., Tibshirani, R., Botstein, D., Altman, R. B. (2001). Missing value estimation methods for DNA microarrays. *Bioinformatics*, 17(6), 520–525.
- Dua, D., Graff, C. (2019). UCI Machine Learning Repository. University of California, Irvine.
