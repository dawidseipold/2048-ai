# Projekt AI do Gry 2048

## 📜 Spis Treści
1. [Wprowadzenie](#1-wprowadzenie)
2. [Twórcy Projektu AI](#2-twórcy-projektu-ai)
3. [Oryginalna Gra 2048 (Autorzy)](#3-oryginalna-gra-2048-autorzy)
4. [Wymagania i Instalacja](#4-wymagania-i-instalacja)
5. [Struktura Projektu](#5-struktura-projektu)
6. [Uruchomienie / Prezentacja](#6-uruchomienie--prezentacja)
    * [6.1. Tryb Interaktywny (CLI Demo AI)](#61-tryb-interaktywny-cli-demo-ai)
    * [6.2. Uruchamianie Eksperymentów (Benchmarki)](#62-uruchamianie-eksperymentów-benchmarki)
    * [6.3. Generowanie Wykresów Wyników](#63-generowanie-wykresów-wyników)
    * [6.4. Tuning Wag Heurystyki](#64-tuning-wag-heurystyki)
    * [6.5. Badanie Wpływu Cech Heurystyki (Ablacja)](#65-badanie-wpływu-cech-heurystyki-ablacja)
7. [Charakterystyka Agentów AI](#7-charakterystyka-agentów-ai)
    * [7.1. Greedy Agent](#71-greedy-agent)
    * [7.2. Expectimax Agent](#72-expectimax-agent)
8. [Funkcja Heurystyczna](#8-funkcja-heurystyczna)
9. [Wyniki i Wnioski](#9-wyniki-i-wnioski)
10. [Dalszy Rozwój](#10-dalszy-rozwój)

---

## 1. Wprowadzenie

Ten projekt implementuje Agenta Sztucznej Inteligencji do klasycznej gry logicznej 2048. Wykorzystujemy algorytm **Expectimax** z szeregiem zaawansowanych optymalizacji, aby agent potrafił podejmować inteligentne decyzje w celu osiągnięcia jak najwyższego wyniku i kafelka 2048. Projekt skupia się na budowie solidnej architektury AI, metodologii eksperymentalnej (benchmarki, tuning) oraz wizualizacji wyników.

Gra bazuje na popularnej wersji 2048 w Pythonie z interfejsem graficznym Tkinter, jednak nasz agent AI operuje na "headless" wersji logiki, aby umożliwić szybkie i powtarzalne eksperymenty.

## 2. Twórcy Projektu AI

*   [Dawid Seipold](https://github.com/DAWID_SEIPOLD_GITHUB) - [Twoja Rola]
*   [Dawid Janowicz](https://github.com/DAWID_JANOWICZ_GITHUB) - [Jego Rola]
*   [Mateusz Groszewski](https://github.com/MATEUSZ_GROSZEWSKI_GITHUB) - [Jego Rola]

_(Proszę uzupełnić linki do profili GitHub i opisy ról!)_

## 3. Oryginalna Gra 2048 (Autorzy)

Nasza implementacja AI wykorzystuje logikę gry z repozytorium 2048-python, które jest Pythonową wersją popularnej gry 2048.

### 2048 Python

[![Run on Repl.it](https://repl.it/badge/github/yangshun/2048-python)](https://repl.it/github/yangshun/2048-python)

> **⚠️NOTE⚠️**: We won't be accepting any contributions/changes to the project anymore. It is now readonly.

Based on the popular game [2048](https://github.com/gabrielecirulli/2048) by Gabriele Cirulli. The game's objective is to slide numbered tiles on a grid to combine them to create a tile with the number 2048. Here is a Python version that uses TKinter!

![screenshot](src/game/img/screenshot.png)

To start the game, run:

```bash
python3 puzzle.py
```

**Oryginalni Twórcy 2048 Python (Tkinter):**
*   [Yanghun Tay](http://github.com/yangshun)
*   [Emmanuel Goh](http://github.com/emman27)

## 4. Wymagania i Instalacja

Projekt wymaga Pythona 3.10+ oraz kilku bibliotek do AI, analizy danych i formatowania kodu.

1.  **Klonowanie repozytorium:**
    ```bash
    git clone [LINK_DO_TWOJEGO_REPO]
    cd [NAZWA_TWOJEGO_FOLDERU_PROJEKTU]
    ```
2.  **Utworzenie i aktywacja wirtualnego środowiska (`venv`):**
    ```bash
    python -m venv .venv
    # Na Windows (CMD/PowerShell):
    .venv\Scripts\activate
    # Na macOS/Linux:
    source .venv/bin/activate
    ```
3.  **Instalacja zależności:**
    Upewnij się, że w katalogu głównym projektu masz plik `requirements.txt` (możesz go wygenerować komendą `pip freeze > requirements.txt`).
    ```bash
    pip install -r requirements.txt
    ```
4.  **Instalacja haków `pre-commit` (zalecane dla deweloperów):**
    Automatyczne formatowanie kodu (`black`, `isort`) i sprawdzanie stylu (`flake8`) przed każdym commitem.
    ```bash
    pre-commit install
    ```

## 5. Struktura Projektu

```text
project-root/
├── .venv/                         # Wirtualne środowisko Pythona
├── pyproject.toml                 # Konfiguracja black/isort/flake8
├── .pre-commit-config.yaml        # Konfiguracja haków Git
├── README.md                      # Ten plik
├── requirements.txt               # Lista zależności Pythona
├── src/                           # Główny kod źródłowy AI
│   ├── agents/                    # Implementacje agentów (Greedy, Expectimax)
│   ├── game/                      # Logika gry (constants, logic, state - nasz wrapper)
│   ├── heuristics/                # Funkcje heurystyczne i wagi
│   │   └── weights/               # Pliki JSON z konfiguracjami wag
│   └── utils/                     # Pomocnicze narzędzia (np. logger)
├── scripts/                       # Skrypty do uruchamiania: demo, benchmarki, tuning, wykresy
│   ├── run_one.py                 # Tryb interaktywny / demo CLI
│   ├── run_experiment.py          # Uruchamianie wielu gier (benchmarki)
│   ├── tune_weights.py            # Skrypt do tuningu wag heurystyki
│   ├── ablation_study.py          # Skrypt do badania wpływu cech heurystyki
│   └── plot_results.py            # Generowanie wykresów z wyników
├── tests/                         # Testy jednostkowe i integracyjne
│   └── integration_test.py
└── results/                       # Katalog na wszystkie wyniki eksperymentów i wykresy
    ├── tuning_greedy/
    ├── ablation_greedy/
    └── plots/
```

## 6. Uruchomienie / Prezentacja

Poniżej znajdują się kluczowe komendy do uruchomienia projektu w różnych trybach, wraz z przykładami i opisem, idealne do prezentacji. **Uruchamiaj wszystkie komendy z katalogu głównego projektu.**

### 6.1. Tryb Interaktywny (CLI Demo AI)

Uruchamia agenta AI grającego w 2048 w konsoli. Pozwala na obserwację ruchów AI w czasie rzeczywistym lub krok po kroku.

*   **Komenda:** `python -m src.scripts.run_one [OPCJE]`
*   **Ważne opcje:**
    *   `--agent_type [greedy|expectimax]`: Wybór agenta.
    *   `--weights [nazwa_wagi.json]`: Nazwa pliku JSON z wagami z `src/heuristics/weights/` (bez rozszerzenia `.json`).
    *   `--mode [live|step]`: `live` (ciągła gra), `step` (po każdym ruchu czeka na Enter).
    *   `--delay [sekundy]`: Opóźnienie między ruchami w trybie `live` (np. `0.1` dla 10 FPS).
    *   `--seed [liczba]`: Seed dla generatora liczb losowych (dla powtarzalności).
    *   `--max_depth [liczba]`, `--time_limit_ms [ms]`, `--adaptive_depth`, etc.: Specyficzne dla Expectimaxa (dodawane bezpośrednio do konstruktora agenta w `run_one.py`).

*   **Przykłady dla prezentacji:**

    1.  **Szybki demo Greedy Agenta (tryb `live`, domyślne wagi):**
        ```bash
        python -m src.scripts.run_one --agent_type greedy --weights balanced --delay 0.1 --seed 42 --mode live
        ```
        _(Obserwuj, jak agent Greedy osiąga kafelki 256/512. Jest szybki, ale ma krótszą perspektywę.)_

    2.  **Demo Expectimax Agenta (tryb `live`, tuned wagi, głębsze przeszukiwanie):**
        ```bash
        # Zakłada, że masz już finalne wagi i parametry z tuningu Expectimaxa
        python -m src.scripts.run_one --agent_type expectimax --weights tuned_expectimax_final --delay 0.05 --seed 123 --mode live --max_depth 5 --time_limit_ms 50
        ```
        _(W tym miejscu podaj Wasze *finalne* parametry Expectimaxa. Obserwuj lepsze ułożenia planszy i wyższe kafelki, ale być może wolniejsze ruchy.)_

    3.  **Debugowanie / Prezentacja strategii (tryb `step`):**
        ```bash
        python -m src.scripts.run_one --agent_type expectimax --weights tuned_expectimax_final --mode step --seed 123 --max_depth 5 --time_limit_ms 50
        ```
        _(Po każdym ruchu możesz omówić, dlaczego AI podjęło taką decyzję, bazując na heurystyce i przeszukiwaniu. Aby kontynuować, naciśnij `Enter`. Aby wyjść, naciśnij `q` i `Enter`.)_

### 6.2. Uruchamianie Eksperymentów (Benchmarki)

Skrypt `run_experiment.py` służy do automatycznego uruchamiania wielu gier i zebrania statystyk (średni wynik, rozkład max tile, czasy decyzji) do plików CSV i JSON.

*   **Komenda:** `python -m src.scripts.run_experiment [OPCJE]`
*   **Ważne opcje:**
    *   `--num_games [liczba]`: Ile gier uruchomić.
    *   `--agent_type [greedy|expectimax]`: Wybór agenta.
    *   `--weights [nazwa_wagi]`: Nazwa pliku JSON z wagami.
    *   `--start_seed [liczba]`: Początkowy seed (kolejne gry używają `start_seed + i`).
    *   `--output_dir [ścieżka]`: Folder do zapisu wyników (CSV i JSON).
    *   `--log_full_games`: Zapisuje pełny log JSON dla każdej gry (szczegółowe stany planszy po każdym ruchu).
    *   `--max_depth [liczba]`, `--time_limit_ms [ms]`, `--adaptive_depth`, etc.: Specyficzne dla Expectimaxa.

*   **Przykłady dla prezentacji:**

    1.  **Porównanie Greedy vs. Expectimax (finalne benchmarki):**
        _(Przed prezentacją uruchomić i mieć wygenerowane CSV-ki!)_
        ```bash
        # Benchmark Greedy Agenta (z najlepszymi tuningowanymi wagami)
        python -m src.scripts.run_experiment --num_games 100 --agent_type greedy --weights tuned_greedy_best_score --start_seed 1 --output_dir results/benchmark_greedy_final

        # Benchmark Expectimax Agenta (z wybranymi finalnymi parametrami)
        python -m src.scripts.run_experiment --num_games 100 --agent_type expectimax --weights tuned_expectimax_final --max_depth 5 --time_limit_ms 40 --cache_maxsize 100000 --start_seed 101 --output_dir results/benchmark_expectimax_final
        ```
        _(Podczas prezentacji możecie pokazać konsolę z `Experiment Summary` z wynikami obu agentów, podkreślając, jak Expectimax bije Greedy.)_

### 6.3. Generowanie Wykresów Wyników

Skrypt `plot_results.py` służy do wizualizacji zebranych danych z benchmarków, tworząc czytelne wykresy PNG.

*   **Komenda:** `python -m src.scripts.plot_results [PLIKI_CSV] --output_dir [FOLDER_WYKRESÓW]`
*   **Ważne opcje:**
    *   `[PLIKI_CSV]`: Jedna lub wiele ścieżek do plików CSV (można używać wildcard `*`).
    *   `--output_dir [ścieżka]`: Folder do zapisu wygenerowanych wykresów PNG.

*   **Przykłady dla prezentacji:**

    1.  **Wykresy porównawcze finalnych agentów:**
        _(Pokażcie folder z wygenerowanymi PNG i omówcie je podczas prezentacji.)_
        ```bash
        python -m src.scripts.plot_results results/benchmark_greedy_final/*.csv results/benchmark_expectimax_final/*.csv --output_dir results/plots/final_comparison
        ```
        _(Wygeneruje wykresy porównawcze wyników, rozkładu max tile i czasów decyzji dla obu agentów.)_

    2.  **Analiza wpływu limitu czasu na Expectimax (np. 20ms vs 40ms vs 80ms):**
        _(Zakłada, że macie już te CSV-ki z eksperymentów Osoby C, Dzień 4.)_
        ```bash
        python -m src.scripts.plot_results results/exp_time_limit_20ms/*.csv results/exp_time_limit_40ms/*.csv results/exp_time_limit_80ms/*.csv --output_dir results/plots/time_limit_analysis
        ```
        _(Pokażcie, jak zwiększanie czasu wpływa na score i czy agent faktycznie osiąga ten limit.)_

### 6.4. Tuning Wag Heurystyki

Skrypt `tune_weights.py` pozwala na automatyczne generowanie i testowanie wielu konfiguracji wag heurystyki.

*   **Komenda:** `python -m src.scripts.tune_weights [OPCJE]`
*   **Przykład:**
    ```bash
    python -m src.scripts.tune_weights --num_configs 30 --games_per_config 20 --agent_type greedy --base_weights balanced --variance_percent 20 --output_dir results/tuning_greedy_demo
    ```
    _(Pokażcie podczas prezentacji, jak ten skrypt działa i jak wybieraliście najlepsze wagi.)_

### 6.5. Badanie Wpływu Cech Heurystyki (Ablacja)

Skrypt `ablation_study.py` służy do badania, jak bardzo każda cecha heurystyki wpływa na ogólny wynik agenta.

*   **Komenda:** `python -m src.scripts.ablation_study [OPCJE]`
*   **Przykład:**
    ```bash
    python -m src.scripts.ablation_study --num_games 50 --output_dir results/ablation_greedy_demo
    ```
    _(Pokażcie wyniki, aby udowodnić, które cechy są najbardziej wartościowe dla Waszej heurystyki.)_

---

## 7. Charakterystyka Agentów AI

### 7.1. Greedy Agent
*   **Opis:** Najprostszy agent bazujący na heurystyce. Podejmuje decyzję o ruchu, która **natychmiastowo** (po jednym kroku, bez spawnu) maksymalizuje wartość funkcji heurystycznej. Nie patrzy w przyszłość poza jeden ruch.
*   **Zastosowanie:** Służy jako szybki baseline do porównań. Jest bardzo szybki, ale jego strategie są ograniczone.

### 7.2. Expectimax Agent
*   **Opis:** Algorytm przeszukujący drzewo gry, będący rozszerzeniem algorytmu Minimax dla gier z elementami losowymi (takimi jak pojawianie się nowych kafelków w 2048).
    *   **Węzły MAX (Agent):** Wybiera ruch, który maksymalizuje oczekiwaną wartość dla gracza.
    *   **Węzły CHANCE (Środowisko):** Oblicza średnią ważoną wszystkich możliwych wyników losowych zdarzeń (np. pojawienie się kafelka 2 lub 4 na pustym polu).
*   **Kluczowe Optymalizacje:**
    *   **Adaptive Depth:** Dynamicznie dostosowuje głębokość przeszukiwania. Gdy plansza jest pełna i opcji jest mało, przeszukuje głębiej. Gdy jest wiele pustych pól, przeszukuje płycej, aby zachować szybkość.
    *   **Move Ordering:** Sortuje potencjalne ruchy na podstawie wstępnej oceny heurystycznej (np. 1-ply), dzięki czemu algorytm najpierw bada najbardziej obiecujące ścieżki, potencjalnie szybciej znajdując optymalne rozwiązanie.
    *   **Memoizacja (LRU Cache):** Przechowuje wyniki już obliczonych (odwiedzonych) stanów planszy, co zapobiega ponownemu przeliczaniu tych samych fragmentów drzewa gry i znacznie przyspiesza działanie algorytmu.
    *   **Limit Czasu i Fallback:** Ogranicza maksymalny czas, jaki agent może poświęcić na podjęcie decyzji. W przypadku przekroczenia limitu, agent awaryjnie wybiera ruch sugerowany przez prostszego Greedy Agenta, zapewniając ciągłość działania.
*   **Zastosowanie:** Jest głównym agentem AI, oferującym znacznie lepszą jakość gry i wyższe wyniki dzięki zaawansowanemu planowaniu.

## 8. Funkcja Heurystyczna

Nasza heurystyka to funkcja `evaluate()`, która przypisuje wartość liczbową danemu stanowi planszy. Im wyższa wartość, tym lepiej oceniany jest dany stan. Jest ona podstawą dla obu agentów (Greedy używa jej bezpośrednio, Expectimax jako funkcji oceny liści drzewa przeszukiwania).

*   **Składowe (Cechy):**
    *   `empty_tiles` (Liczba pustych pól): Premiuje plansze z dużą ilością wolnego miejsca, co zwiększa elastyczność i potencjał do dalszych ruchów.
    *   `monotonicity` (Monotoniczność): Ocenia, czy płytki w wierszach i kolumnach są uporządkowane (np. zawsze rosnąco lub malejąco). Promuje układanie płytek w "łańcuchy" lub "węże", ułatwiając łączenie.
    *   `smoothness` (Gładkość): Kara za duże różnice wartości (w skali logarytmicznej) między sąsiadującymi kafelkami. Niskie wartości `smoothness` oznaczają, że podobne kafelki są blisko siebie, co ułatwia ich łączenie.
    *   `max_in_corner` (Maksymalna płytka w rogu): Daje duży bonus, jeśli największa wartość na planszy znajduje się w jednym z rogów. Jest to sprawdzona strategia w 2048, pomagająca utrzymać największy kafelek poza centrum, gdzie mógłby zostać zablokowany.
*   **Metoda oceny:** Wszystkie cechy są łączone w jeden wynik poprzez sumę ważoną. Wagi zostały starannie dostrojone.
*   **Tuning i Walidacja:**
    *   Wagi były systematycznie dostrajane za pomocą **random search** (`scripts/tune_weights.py`).
    *   Wpływ poszczególnych cech został zweryfikowany przez **feature ablation study** (`scripts/ablation_study.py`), co pozwoliło zidentyfikować najistotniejsze komponenty heurystyki.

## 9. Wyniki i Wnioski

_(Ta sekcja zostanie uzupełniona na końcu, po podsumowaniu wszystkich eksperymentów i analiz. W skrócie powinna zawierać):_

*   **Porównanie agentów:** Jak Expectimax wypada na tle Greedy (średni wynik, max tile, % osiągniętych 2048).
*   **Optymalne parametry:** Rekomendowane wartości dla `max_depth`, `time_limit_ms` dla Expectimaxa, wraz z uzasadnieniem.
*   **Wpływ optymalizacji:** Jak adaptive depth, move ordering i memoizacja poprawiły wydajność Expectimaxa.
*   **Najważniejsze cechy heurystyki:** Które cechy okazały się najbardziej decydujące.
*   **Generalne wnioski:** Co udało się osiągnąć i jakie strategie okazały się kluczowe.

## 10. Dalszy Rozwój

*   Implementacja bardziej zaawansowanych algorytmów przeszukiwania (np. Monte Carlo Tree Search, Alpha-Beta Pruning z Iterative Deepening).
*   Uczenie funkcji oceny za pomocą algorytmów uczenia maszynowego (np. Reinforcement Learning, n-tuple networks).
*   Wizualizacja drzewa przeszukiwania lub heatmapy dla poszczególnych ruchów Expectimaxa.
*   Integracja z GUI Tkinter, aby agent mógł grać w oryginalnej wersji gry.