# [IUM] Predykcja czasu dostawy zamówienia - mikroserwis

Mikroserwis napisany został przy użyciu [FastAPI](https://fastapi.tiangolo.com/). Aby go uruchomić potrzebne są następujące moduły:

* fastapi
* uvicorn[standard]

Przygotowany mikroserwis odpowiada na 2 zapytania typu POST: `predict` i `admin`. 

## Zapytanie `predict`
Zapytanie `predict` pozwala na uzyskanie predykcji dla zadanych danych wejściowych. Dane wejściowe są następujące:

* identyfikator klienta (typ: int)
* nazwa miasta, do którego należy dostarczyć zamówienie (typ: string)
* identyfikator firmy kurierskiej (typ: int)
* numer dnia tygodnia zakupu liczony od 0 (typ: int)
* godzina zakupu - najlepiej w formacie "hh:mm:ss" (typ: string)

Zapytanie zwraca przedwidywany czas dostawy w godzinach.

## Zapytanie `admin`
Zapytanie `admin` pozwala na zarządzanie mikroserwisem poprzez rozpoczynanie kolejnych eksperymentów. Dane wejściowe są następujące:

* login - pozwala na realizację bardzo prostego mechanizmu uwierzytelniania (typ: string)
* hasło - pozwala na realizację bardzo prostego mechanizmu uwierzytelniania (typ: string)
* ścieżka do pierwszego modelu (typ: string)
* informacja, czy pierszy model pochodzi z biblioteki `keras` - jest to informacja konieczna do poprawnego otwarcia pliku z modelem (typ: int, 0 oznacza "nie", 1 oznacza "tak")

Ponadto, zapytanie to ma atrybuty opcjonalne, które umożliwiają przeprowadzenie eksperymentu A/B. Są to:

* ścieżka do drugiego modelu (typ: string)
* informacja, czy drugi model pochodzi z biblioteki `keras` (typ: int)

Zapytanie zwraca informację, czy udało się rozpocząc nowy eksperyment.

## Zawartość logów
Rozpoczęcie nowego eksperymentu przy pomocy zapytania `admin` tworzy nowy log, do którego zapisywane są dane podczas odpowiedzi na zapytanie `predict`. W logu znajdują się następujące informacje: 

* data i godzina odpowiedzi na zapytanie `predict`
* wszystkie dane wysłane za pomocą zapytania `predict`
* identyfikator modelu użytego do wyznaczenia predykcji (0 oznacza pierwszy model, a 1 drugi)
* wyznaczona predykcja czasu dostawy w godzinach

## Przykładowy eksperyment
Do wykazania, że mikroserwis działa, przeprowadzono przykładowy eksperyment. Poniżej przedstawiono jego kroki:

1. Uruchomiono mikroserwis komendą `uvicorn main:app`.
2. Za pomocą [graficznego interfejsu do FastAPI](http://127.0.0.1:8000/docs) wykonano zapytanie `admin`. Pierszym modelem był przygotowany model bazowy, a drugim model docelowy.
3. Za pomocą skryptu `send_requests.py` wysłano zapytania typu `predict` dotyczące zbioru testowego.
4. Za pomocą skryptu `analyze_log.py` przeanalizowano powstały log. Zwrócił on następujące informacje:  

        First  model rmse: 17.99698372734838
        Second model rmse: 14.931883426249822

    Dane te mogą nieznacznie odbiegać od tych wyznaczonych w trakcie modelowania. Spowodowane jest to tym, iż w trakcie modelowania każdy element zbioru testowego został sprawdzony na obydwu modelach, a tu tylko na jednym z nich.

5. Wyniki eksperymentu potwierdzają, iż model docelowy jest lepszy od bazowego.

## Materiały pokazujące, że implementacja mikroserwisu działa
W tej sekcji zamieszczone zostały zrzuty ekranu z [graficznego interfejsu do FastAPI](http://127.0.0.1:8000/docs), przy pomocy którego wykonano zapytania obydwu typów.

### Zapytanie `admin`
Przygotowano następujące zapytanie:

![Nie udało się wczytać zrzutu ekranu z zapytaniem \"admin\"](images/admin_request_body.png "Zapytanie \"admin\"")

Otrzymano następującą odpowiedź:

![Nie udało się wczytać zrzutu ekranu z odpowiedzią na zapytanie \"admin\"](images/admin_response.png "Odpowiedź na zapytanie \"admin\"")

### Zapytanie `predict`
Przygotowano następujące zapytanie:

![Nie udało się wczytać zrzutu ekranu z zapytaniem \"predict\"](images/predict_request_body.png "Zapytanie \"predict\"")

Otrzymano następującą odpowiedź:

![Nie udało się wczytać zrzutu ekranu z odpowiedzią na zapytanie \"predict\"](images/predict_response.png "Odpowiedź na zapytanie \"predict\"")