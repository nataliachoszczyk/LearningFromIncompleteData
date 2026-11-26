# Zadanie projektowe MED

Strona przedmiotu: https://leon.pw.edu.pl/course/view.php?id=2333

## Temat

**Wnioskowanie z niepełnych danych i wiedzy częściowej.** Implementacja wybranego podejścia do klasyfikacji lub wnioskowania przy brakujących danych, np. z wykorzystaniem zbiorów przybliżonych, reguł decyzyjnych dla danych niekompletnych albo porównania z metodami imputacji.

Cele szczegółowe: ocena odporności algorytmu na różny poziom niekompletności danych oraz porównanie jakości wnioskowania przy różnych strategiach obsługi braków.

Nasz projekt łączy dwa warianty:

- **7.1. Rough-set dla danych niekompletnych:** Kryszkiewicz, M. (1998). Rough set approach to incomplete information systems. *Information Sciences*, 112(1–4), 39–49.
- **7.3. Imputacja kNN:** Troyanskaya, O., Cantor, M., Sherlock, G., Brown, P., Hastie, T., Tibshirani, R., Botstein, D., Altman, R. B. (2001). Missing value estimation methods for DNA microarrays. *Bioinformatics*, 17(6), 520–525.

## Cel projektu

Celem projektu jest zbadanie własności zaimplementowanego przez siebie algorytmu:

- czas wykonania dla różnych wartości parametrów wejściowych,
- wpływ zmiany wartości parametrów na uzyskiwane wyniki,
- skalowalność algorytmu względem rozmiaru danych (liczby rekordów oraz liczby atrybutów),
- oraz cele szczegółowe, jeśli są podane w opisie zadania.

Testy należy przeprowadzić dla kilku zbiorów danych.

## Środowisko deweloperskie

Wybór języka programowania oraz narzędzi i bibliotek należy do wykonawcy zadania, ograniczeniem jest tu legalność wykorzystania wybranych narzędzi/bibliotek do realizacji projektów studenckich. Preferowane są popularne języki programowania.

## Liczność grup

Zadania są pomyślane jako jednoosobowe (chyba, że wskazano inaczej), jednak istnieje możliwość ich realizacji w grupie maksymalnie dwuosobowej. W takim przypadku należy ustalić z prowadzącym zakres zadania projektowego.

## Ważne daty

**26.11.2026 – termin wyboru tematu projektu.**

- Proszę przesłać emailem swoje preferencje projektowe, w temacie wiadomości proszę dodać [projekt MED].
- Proszę uwzględnić w wiadomości 3 preferowane tematy w kolejności preferencji. Projekty zostaną przydzielone zgodnie z kolejnością zgłoszeń i preferencjami.
- Dla projektów realizowanych przez zespoły proszę o adresowanie wiadomości do wszystkich członków zespołu.
- Osoby, które nie prześlą preferencji w wyznaczonym terminie zostaną przypisane do tematu projektu arbitralnie wybranego przez prowadzącego.

**17.12.2026 – kluczowe elementy rozwiązania/projekt implementacji (część 1).** Powinien zawierać informacje m.in. o strukturze implementacji (funkcje, klasy) z odniesieniem do konkretnych kroków implementowanego algorytmu, strukturach danych wykorzystywanych do przechowywania danych źródłowych oraz struktur wykorzystywanych w implementacji algorytmu oraz ocenę efektywności proponowanego rozwiązania. Projekt implementacji nie jest implementacją.

Kluczowe elementy rozwiązania należy przedstawić osobiście w trakcie spotkania w terminie konsultacji projektowych. Przedstawienie obejmuje:

- przedstawienie zakresu, wybranych technologii do realizacji zadania oraz planów testów w formie prezentacji (np. w formacie .ppt);
- omówienie projektu implementacji algorytmu (należy przygotować odpowiednią dokumentację).

Przed prezentacją należy uzgodnić z prowadzącym dokładny termin oraz wgrać odpowiednio wcześniej dokumentację projektu implementacji algorytmu.

**21.01.2027 – ostateczny termin oddania całego projektu (część 2)** w terminie konsultacji projektowych. Oddanie projektu obejmuje:

- prezentację pokazującą główne zagadnienia związane z realizowanym projektem – należy przygotować prezentację (np. w formacie .ppt);
- pokaz działania oprogramowania;
- rozmowę dotyczącą testów, uzyskanych wyników i wniosków.

Przed oddaniem projektu należy uzgodnić z prowadzącym dokładny termin oraz wgrać odpowiednio wcześniej dokumentację projektu implementacji algorytmu.

## Zasady zaliczenia projektu

Maksymalna liczba punktów z części 1 wynosi 15, a z części 2 wynosi 30 (sumaryczna maksymalna liczba punktów do uzyskania z obu części wynosi 45). Uzyskane z projektu punkty zostaną przeliczone na procent całkowitej możliwej do uzyskania liczby punktów. Wartość ta będzie podstawą do wyliczenia oceny końcowej.

## Dokumentacja

Dokumentacja końcowa powinna zawierać następujące rozdziały:

1. Wprowadzenie i definicja problemu
2. Charakterystyka proponowanego algorytmu/rozwiązania z odniesieniem do literatury
3. Opis implementacji
4. Instrukcja użytkownika (jak uruchomić/korzystać z implementacji)
5. Charakterystyka wykorzystywanych zbiorów danych
6. Wyniki eksperymentów pokazujących właściwości proponowanego rozwiązania
7. Wnioski
8. Bibliografia
9. Kod źródłowy w osobnym pliku(ach).

Eksperymenty należy przeprowadzić z wykorzystaniem publicznie dostępnych zbiorów danych, np.:

- https://archive.ics.uci.edu/datasets
- http://fimi.uantwerpen.be/data/
- https://github.com/deric/clustering-benchmark
- http://www.philippe-fournier-viger.com/spmf/index.php?link=datasets.php

Obydwie części dokumentacji należy zamieścić na serwerze https://leon.pw.edu.pl/course/view.php?id=2333 w terminach przedstawionych powyżej.
