# Wnioskowanie z danych niekompletnych: zbiory przybliżone i imputacja kNN
Natalia Choszczyk, Aleksandra Samsel

Dokumentacja końcowa projektu z przedmiotu Metody Eksploracji Danych (MED).

## 1. Wprowadzenie i definicja problemu

### 1.1. Dane niekompletne

W danych rzeczywistych część wartości atrybutów jest nieznana. Powody są różne:

- pomiaru nie wykonano albo był zbyt kosztowny,
- respondent nie odpowiedział na pytanie,
- wartość zgubiono przy przetwarzaniu.

Większość metod klasyfikacji zakłada, że tabela jest kompletna. Dane z brakami trzeba więc najpierw przekształcić albo użyć metody, która działa bezpośrednio na brakach.

W projekcie wartość brakującą oznaczamy symbolem `*` (w kodzie `NaN`). Zakładamy, jak Kryszkiewicz (1998), że prawdziwa wartość należy do dziedziny atrybutu, ale nie wiemy, która.

### 1.2. Mechanizm braków

Little i Rubin wyróżniają trzy mechanizmy powstawania braków:

- **MCAR** (*missing completely at random*): brak nie zależy od żadnych danych,
- **MAR** (*missing at random*): brak zależy tylko od wartości znanych,
- **MNAR** (*missing not at random*): brak zależy od samej nieznanej wartości.

Eksperymenty z symulowanymi brakami używają mechanizmu MCAR. Z kompletnej tabeli losowo usuwamy zadany ułamek wartości atrybutów, a każda znana wartość ma to samo prawdopodobieństwo usunięcia. Klasa nigdy nie jest usuwana. Ten sam schemat stosują Troyanskaya i in. (2001). Mechanizm braków naturalnych w zbiorach UCI nie jest znany.

### 1.3. Definicja problemu

Dana jest tablica decyzyjna DT = (O, AT ∪ {d}):

- O to skończony zbiór obiektów (rekordów),
- AT to zbiór atrybutów warunkowych,
- d to atrybut decyzyjny (klasa), który nie ma braków.

Wartości atrybutów warunkowych mogą być nieznane. Zadanie polega na nauczeniu klasyfikatora na części obiektów i przewidywaniu klasy pozostałych obiektów, które także mogą mieć braki.

### 1.4. Cel projektu

Projekt łączy dwa warianty tematu „Wnioskowanie z niepełnych danych i wiedzy częściowej”:

- **7.1:** zbiory przybliżone dla danych niekompletnych (Kryszkiewicz 1998),
- **7.3:** imputacja kNN (Troyanskaya i in. 2001).

Porównujemy 4 strategie postępowania z brakami:

| Nr | Strategia |
|---|---|
| S1 | Zbiory przybliżone z relacją tolerancji na surowych danych |
| S2 | Usunięcie niepełnych rekordów treningowych, potem S1 |
| S3 | Imputacja średnią lub modą, potem S1 |
| S4 | Imputacja kNN, potem S1 |

Wszystkie strategie używają tego samego klasyfikatora regułowego ze zbiorów przybliżonych. Różnica wyników pokazuje więc tylko wpływ sposobu obsługi braków.

Zgodnie z treścią zadania badamy:

- odporność algorytmu na różny poziom niekompletności danych (0–50% braków),
- jakość wnioskowania przy różnych strategiach obsługi braków,
- czas wykonania dla różnych wartości parametrów (k, liczba przedziałów dyskretyzacji, odsetek braków),
- wpływ parametrów na wyniki,
- skalowalność względem liczby rekordów i liczby atrybutów.

Testy wykonujemy na 6 publicznych zbiorach danych z repozytorium UCI.

## 2. Charakterystyka algorytmów

### 2.1. Zbiory przybliżone dla danych niekompletnych (Kryszkiewicz 1998)

#### Relacja tolerancji

W klasycznej teorii zbiorów przybliżonych (Pawlak 1991) obiekty x i y są nierozróżnialne względem zbioru atrybutów A ⊆ AT, gdy mają te same wartości wszystkich atrybutów z A. Relacja nierozróżnialności IND(A) jest relacją równoważności i dzieli O na rozłączne klasy.

Przy brakach nie wiemy, czy dwa obiekty mają tę samą wartość. Kryszkiewicz zastępuje więc IND(A) relacją podobieństwa:

SIM(A) = {(x, y) ∈ O × O : ∀a ∈ A, a(x) = a(y) ∨ a(x) = * ∨ a(y) = *}.

Obiekty x i y są podobne, gdy nie da się z pewnością powiedzieć, że się różnią. SIM(A) jest zwrotna i symetryczna, ale nie musi być przechodnia, więc jest relacją tolerancji. Zachodzi też SIM(A) = ∩_{a ∈ A} SIM({a}) (własność 2.1).

Klasa tolerancji obiektu x to zbiór obiektów do niego podobnych:

S_A(x) = {y ∈ O : (x, y) ∈ SIM(A)}.

W odróżnieniu od klas równoważności klasy tolerancji mogą na siebie nachodzić i nie tworzą podziału O.

#### Aproksymacje

Dla zbioru obiektów X ⊆ O i zbioru atrybutów A:

- dolna aproksymacja A̲X = {x ∈ O : S_A(x) ⊆ X} to obiekty, które na pewno należą do X,
- górna aproksymacja ĀX = {x ∈ O : S_A(x) ∩ X ≠ ∅} to obiekty, które mogą należeć do X.

Zachodzi A̲X ⊆ X ⊆ ĀX.

#### Decyzja uogólniona

Decyzja uogólniona obiektu x to zbiór decyzji obiektów do niego podobnych:

∂_A(x) = {i : i = d(y), y ∈ S_A(x)}.

Tablica jest spójna (deterministyczna), gdy |∂_AT(x)| = 1 dla każdego x. W przeciwnym razie jest niespójna.

#### Przykład

Tablica 2 z artykułu opisuje 6 samochodów. Atrybuty to cena (P), przebieg (M), rozmiar (S) i prędkość maksymalna (X), a decyzja to przyspieszenie (d):

| Samochód | P | M | S | X | d |
|---|---|---|---|---|---|
| 1 | high | high | full | low | good |
| 2 | low | * | full | low | good |
| 3 | * | * | compact | high | poor |
| 4 | high | * | full | high | good |
| 5 | * | * | full | high | excel. |
| 6 | low | high | full | * | good |

Klasy tolerancji to:

- S(1) = {1},
- S(2) = {2, 6},
- S(3) = {3},
- S(4) = {4, 5},
- S(5) = {4, 5, 6},
- S(6) = {2, 5, 6}.

Decyzje uogólnione to {good} dla obiektów 1 i 2, {poor} dla obiektu 3 oraz {good, excel.} dla obiektów 4, 5 i 6. Dla klasy X_good = {1, 2, 4, 6} dolna aproksymacja to {1, 2}, a górna to {1, 2, 4, 5, 6}.

#### Redukty

Redukt względny tablicy decyzyjnej to minimalny zbiór atrybutów A ⊆ AT, który zachowuje decyzję uogólnioną wszystkich obiektów: ∂_A = ∂_AT. Redukt względny dla obiektu x to minimalny A ⊆ AT, dla którego ∂_A(x) = ∂_AT(x). Redukty dla obiektów pozwalają budować krótsze reguły.

Redukty wyznacza się z funkcji rozróżnialności. Niech α_AT(x, y) będzie zbiorem atrybutów a, dla których (x, y) ∉ SIM({a}), czyli a(x) ≠ *, a(y) ≠ * i a(x) ≠ a(y). Funkcja rozróżnialności dla obiektu x ma postać:

Δ*(x) = Π_{y : d(y) ∉ ∂_AT(x)} Σ α_AT(x, y),

gdzie iloczyn oznacza koniunkcję, a suma alternatywę zmiennych odpowiadających atrybutom. Implikanty pierwsze Δ*(x) to redukty względne dla x. Funkcja rozróżnialności całej tablicy Δ* to koniunkcja po wszystkich parach (x, y) z d(y) ∉ ∂_AT(x).

Kryszkiewicz zauważa, że dla tablic niekompletnych funkcja rozróżnialności ma od razu postać koniunkcyjną (CNF). Znalezienie wszystkich implikantów pierwszych jest jednak wykładnicze w liczbie atrybutów. Dlatego w implementacji używamy heurystyki zachłannej. Problem to pokrycie zbioru: każde α_AT(x, y) musi zawierać co najmniej jeden wybrany atrybut. W każdym kroku dodajemy atrybut, który pokrywa najwięcej niepokrytych α, a na końcu usuwamy atrybuty zbędne.

Dla tablicy 2 reduktem względnym jest {S, X}. Reduktem dla obiektów 1 i 2 jest {X}, a dla obiektów 3–6 jest {S}.

#### Reguły decyzyjne

Reguła optymalna dla obiektu x z reduktem względnym A ma postać:

∧_{a ∈ A} (a, a(x)) → ∨_{w ∈ ∂_AT(x)} (d, w).

Część decyzyjna reguły optymalnej jest zawsze równa decyzji uogólnionej obiektu. Problem budowy reguł sprowadza się więc do redukcji atrybutów warunkowych. Reguła jest pewna, gdy |∂_AT(x)| = 1. W przeciwnym razie jest możliwa.

Z reduktów tablicy 2 powstają trzy reguły zamiast sześciu:

- (X, low) → (d, good),
- (S, compact) → (d, poor),
- (S, full) → (d, good) ∨ (d, excel.).

Reguły pozostają prawdziwe po zastąpieniu dowolnych braków dowolnymi wartościami.

#### Porównanie z innymi metodami (rozdz. 6 artykułu)

Kryszkiewicz porównuje swoje podejście z dwiema metodami z systemu LERS:

- **Zastępowanie przykładów:** obiekt z brakiem zastępuje się zbiorem obiektów z każdą możliwą wartością. Metoda daje wszystkie reguły pewne w pierwotnej tablicy.
- **Usuwanie przykładów:** obiekty z brakami się usuwa. Metoda może dać fałszywe reguły pewne, czyli pewne w tablicy po usunięciu, ale niepewne w pierwotnej.

Reguły deterministyczne metody tolerancyjnej są podzbiorem reguł pewnych pierwotnej tablicy. Strategia S2 w naszym projekcie odpowiada usuwaniu przykładów.

#### Klasyfikacja nowych obiektów

Artykuł nie opisuje klasyfikacji nowych obiektów. Stosujemy dopasowanie zgodne z relacją tolerancji: reguła pasuje do obiektu z, gdy dla każdego warunku (a, v) zachodzi a(z) = v albo a(z) = *. Każda pasująca reguła głosuje na decyzje ze swojej prawej strony z wagą równą swojemu wsparciu. Gdy żadna reguła nie pasuje, wynikiem jest najczęstsza klasa.

#### Dyskretyzacja

Relacja tolerancji wymaga atrybutów symbolicznych. Atrybuty liczbowe dzielimy na przedziały o równej liczności (kwantyle), domyślnie 4. Punkty podziału wyznaczamy tylko ze znanych wartości zbioru treningowego. Brak pozostaje brakiem.

### 2.2. Imputacja kNN (Troyanskaya i in. 2001)

Troyanskaya i in. porównali trzy metody uzupełniania braków w danych z mikromacierzy DNA:

- KNNimpute (k najbliższych sąsiadów),
- SVDimpute (rozkład według wartości szczególnych),
- średnią z wiersza (*row average*).

KNNimpute okazała się najdokładniejsza i najbardziej odporna na rosnący odsetek braków.

#### Algorytm

Niech rekord x ma brak w atrybucie a. Algorytm ma trzy kroki:

1. Wśród rekordów, które mają wartość atrybutu a, znajdź k rekordów najbardziej podobnych do x na pozostałych atrybutach.
2. Policz średnią ważoną ich wartości a. Wkład każdego sąsiada jest ważony jego podobieństwem do x.
3. Wstaw średnią jako oszacowanie a(x).

Autorzy sprawdzili korelację Pearsona, odległość euklidesową i minimalizację wariancji. Wybrali odległość euklidesową, bo po logarytmowaniu danych była wystarczająco dokładna. Najlepsze wyniki dawało k = 10–20. Błąd był mało wrażliwy na k w tym zakresie. Złożoność obliczeniowa to O(m²n) dla m genów i n eksperymentów.

#### Ocena błędu

Z kompletnej macierzy autorzy usuwali losowo 1–20% wartości, uzupełniali je i porównywali z oryginałem. Miarą był znormalizowany błąd RMS: pierwiastek średniego kwadratu różnicy między macierzą uzupełnioną a oryginalną, podzielony przez średnią wartość kompletnych danych.

#### Adaptacja do danych mieszanych

Artykuł dotyczy wyłącznie danych liczbowych. Nasze zbiory mają atrybuty liczbowe i symboliczne, więc wprowadzamy cztery zmiany:

| Element | Artykuł | Projekt |
|---|---|---|
| Odległość | euklidesowa | Gowera: \|x_a − y_a\| / rozstęp(a) dla atrybutu liczbowego, 0 lub 1 dla symbolicznego, średnia po atrybutach znanych w obu rekordach |
| Waga sąsiada | „ważona podobieństwem”, bez wzoru | 1 / odległość |
| Oszacowanie | średnia ważona | średnia ważona (liczbowe), ważona moda (symboliczne) |
| Normalizacja błędu | przez średnią całej macierzy | błąd każdego atrybutu dzielony przez jego odchylenie standardowe; dla symbolicznych odsetek błędów |

*Row average* to w artykule średnia z wiersza (genu) po wszystkich eksperymentach. U nas atrybuty jednego rekordu mają różne znaczenia, więc odpowiednikiem jest średnia (lub moda) atrybutu, czyli kolumny.

## 3. Opis implementacji

*Rozdział w przygotowaniu (osoba B). Podstawą jest projekt implementacji w `docs/DESIGN.md`.*

## 4. Instrukcja użytkownika

*Rozdział w przygotowaniu (osoba B).*

## 5. Charakterystyka zbiorów danych

### 5.1. Wybór zbiorów

Używamy 6 publicznych zbiorów z UCI Machine Learning Repository (licencja CC BY 4.0). Wybór pokrywa różne typy atrybutów, rozmiary i rodzaje braków:

| Zbiór | Rekordy | Atrybuty | Liczbowe | Brakujące komórki | Niepełne rekordy | Klasy | Rozkład klas |
|---|---|---|---|---|---|---|---|
| `voting` | 435 | 16 | 0 | 5,63% | 46,7% | 2 | democrat 267, republican 168 |
| `hepatitis` | 155 | 19 | 6 | 5,67% | 48,4% | 2 | live 123, die 32 |
| `mushroom` | 8124 | 22 | 0 | 1,39% | 30,5% | 2 | edible 4208, poisonous 3916 |
| `car` | 1728 | 6 | 0 | 0% | 0% | 4 | unacc 1210, acc 384, good 69, vgood 65 |
| `wdbc` | 569 | 30 | 30 | 0% | 0% | 2 | benign 357, malignant 212 |
| `adult` | 48842 | 14 | 6 | 0,95% | 7,4% | 2 | ≤50K 37155, >50K 11687 |

| Zbiór | Rola w eksperymentach |
|---|---|
| `voting` | relacja tolerancji bezpośrednio na naturalnych brakach |
| `hepatitis` | porównanie strategii na małym zbiorze mieszanym z naturalnymi brakami |
| `mushroom` | skalowalność względem liczby rekordów i atrybutów, naturalne braki w jednym atrybucie |
| `car` | odporność na symulowane braki MCAR 5–50% |
| `wdbc` | błąd imputacji kNN dla różnych k, skalowalność względem liczby atrybutów |
| `adult` | czas działania dla dużej liczby rekordów |

### 5.2. Opis zbiorów

**Congressional Voting Records (`voting`).** Głosowania 435 kongresmenów USA z 1984 r. w 16 sprawach. Każdy atrybut ma wartości y (za) i n (przeciw). Wartość `?` oznacza brak głosu „za” lub „przeciw”: obecność bez głosu, wstrzymanie się z powodu konfliktu interesów albo nieobecność. Klasa to partia. W zbiorze 46,7% rekordów ma co najmniej jeden brak. Jeden rekord ma braki we wszystkich 16 atrybutach.

Opis zbioru zaznacza, że `?` nie oznacza wartości nieznanej, tylko trzecią postawę. Brak głosu może więc zależeć od poglądów kongresmena, co odpowiada mechanizmowi MNAR. W projekcie traktujemy `?` jako brak, bo właśnie taki przypadek naturalnych braków chcemy zbadać. Dla porównania można też potraktować `?` jako trzecią wartość atrybutu.

**Hepatitis (`hepatitis`).** Dane 155 pacjentów z zapaleniem wątroby. Zbiór ma 13 atrybutów binarnych (np. płeć, sterydy, zmęczenie, powiększona wątroba) i 6 liczbowych (wiek, bilirubina, fosfataza alkaliczna, SGOT, albumina, czas protrombinowy). Klasa to przeżycie (1 = zgon, 2 = przeżycie). Najwięcej braków ma czas protrombinowy (43% rekordów). Atrybuty liczbowe mają rozkłady skośne.

**Mushroom (`mushroom`).** Opisy 8124 hipotetycznych grzybów z 23 gatunków. Zbiór ma 22 atrybuty symboliczne (kształt i kolor kapelusza, zapach, blaszki, trzon, pierścień, siedlisko). Klasa to jadalny lub trujący. Wszystkie braki dotyczą atrybutu `stalk_root` (30,5% rekordów). Atrybut `veil_type` ma jedną wartość.

**Car Evaluation (`car`).** Ocena 1728 samochodów z hierarchicznego modelu decyzyjnego. Zbiór ma 6 atrybutów porządkowych: cena zakupu, koszt utrzymania, liczba drzwi, liczba osób, bagażnik i bezpieczeństwo. Klasa ma 4 wartości. Zbiór zawiera każdą kombinację wartości atrybutów dokładnie raz, więc atrybuty są niezależne. Dlatego sąsiedzi rekordu nie niosą informacji o jego brakującej wartości.

**Breast Cancer Wisconsin Diagnostic (`wdbc`).** Cechy jąder komórkowych z obrazów biopsji 569 guzów piersi. Dziesięć cech podstawowych to promień, tekstura, obwód, pole, gładkość, zwartość, wklęsłość, punkty wklęsłe, symetria i wymiar fraktalny. Każda cecha występuje w 3 wersjach: średnia, błąd standardowy i najgorsza wartość, co daje 30 atrybutów liczbowych. Klasa to łagodny lub złośliwy. Zbiór jest kompletny, a atrybuty są silnie skorelowane, co sprzyja imputacji kNN.

**Adult (`adult`).** Dane ze spisu ludności USA z 1994 r. o 48842 osobach (połączone pliki `adult.data` i `adult.test`). Zbiór ma 6 atrybutów liczbowych (wiek, waga próby, liczba lat nauki, zysk i strata kapitałowa, godziny pracy) i 8 symbolicznych (m.in. rodzaj zatrudnienia, wykształcenie, zawód, kraj). Klasa to dochód powyżej lub poniżej 50 tys. USD rocznie. Braki występują w atrybutach `workclass`, `occupation` i `native_country`.

### 5.3. Wstępne przygotowanie

Funkcja `load_dataset` sprowadza każdy zbiór do wspólnej postaci:

- jeden wiersz na rekord, kolumna `class` na końcu,
- brak to `NaN`; w plikach UCI brak oznacza `?`,
- atrybuty liczbowe mają typ `float64`, symboliczne i klasa typ `category`,
- w `adult` usuwamy pierwszy wiersz pliku testowego i kropkę na końcu klasy (np. `<=50K.`),
- w `wdbc` pomijamy kolumnę identyfikatora.

### 5.4. Obserwacje wstępne

- **Wrażliwość na rekordy z wieloma brakami.** W `voting` rekord z 16 brakami jest podobny do wszystkich rekordów. Należy więc do każdej klasy tolerancji, a jego klasa wchodzi do decyzji uogólnionej każdego obiektu. W efekcie tylko 33% rekordów ma jednoznaczną decyzję. Po usunięciu rekordów z co najmniej 8 brakami ten odsetek rośnie do 98%.
- **Wzrost klas tolerancji.** Przy symulowanych brakach MCAR średnia liczność klasy tolerancji w `car` wynosi 1 przy 0% braków, 134 przy 30% i 535 przy 50%.
- **Jakość imputacji zależy od struktury danych.** Na `wdbc` i `voting` kNN ma wyraźnie mniejszy błąd niż średnia lub moda. Na `car` (atrybuty niezależne) kNN nie jest lepszy od mody.

## 6. Wyniki eksperymentów

*Rozdział w przygotowaniu (osoba B). Zmierzone czasy algorytmów są w rozdz. 6.1 dokumentu `docs/DESIGN.md`.*

## 7. Wnioski

*Rozdział w przygotowaniu (osoba B).*

## 8. Bibliografia

1. Kryszkiewicz, M. (1998). Rough set approach to incomplete information systems. *Information Sciences*, 112(1–4), 39–49.
2. Troyanskaya, O., Cantor, M., Sherlock, G., Brown, P., Hastie, T., Tibshirani, R., Botstein, D., Altman, R. B. (2001). Missing value estimation methods for DNA microarrays. *Bioinformatics*, 17(6), 520–525.
3. Pawlak, Z. (1991). *Rough Sets: Theoretical Aspects of Reasoning about Data*. Kluwer Academic Publishers, Dordrecht.
4. Little, R. J. A., Rubin, D. B. (2019). *Statistical Analysis with Missing Data* (3rd ed.). Wiley.
5. Gower, J. C. (1971). A general coefficient of similarity and some of its properties. *Biometrics*, 27(4), 857–871.
6. Chmielewski, M. R., Grzymała-Busse, J. W., Peterson, N. W., Than, S. (1993). The rule induction system LERS – a version for personal computers. *Foundations of Computing and Decision Sciences*, 18(3–4), 181–212.
7. Dua, D., Graff, C. (2019). UCI Machine Learning Repository. University of California, Irvine. https://archive.ics.uci.edu
8. Zbiory danych UCI (strony zbiorów w UCI Machine Learning Repository):
   - Congressional Voting Records: https://archive.ics.uci.edu/dataset/105
   - Hepatitis: https://archive.ics.uci.edu/dataset/46
   - Mushroom: https://archive.ics.uci.edu/dataset/73
   - Car Evaluation: https://archive.ics.uci.edu/dataset/19
   - Breast Cancer Wisconsin (Diagnostic): https://archive.ics.uci.edu/dataset/17
   - Adult: https://archive.ics.uci.edu/dataset/2

## 9. Kod źródłowy

*Rozdział w przygotowaniu (osoba B). Kod jest w folderze `src/`, testy w `tests/`.*
