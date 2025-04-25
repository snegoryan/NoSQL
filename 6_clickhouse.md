## Домашнее задание

Установка ClickHouse

Цель:
В результате выполнения ДЗ в разверните БД.

Описание/Пошаговая инструкция выполнения домашнего задания:
Необходимо, используя туториал [https://clickhouse.tech/docs/en/getting-started/tutorial/](https://clickhouse.tech/docs/en/getting-started/tutorial/ "https://clickhouse.tech/docs/en/getting-started/tutorial/")
- развернуть БД;
- выполнить импорт тестовой БД;
- выполнить несколько запросов и оценить скорость выполнения.
- \*развернуть дополнительно одну из тестовых БД [https://clickhouse.com/docs/en/getting-started/example-datasets](https://clickhouse.com/docs/en/getting-started/example-datasets "https://clickhouse.com/docs/en/getting-started/example-datasets") , протестировать скорость запросов
- \*\*развернуть Кликхаус в кластерном исполнении, создать распределенную таблицу, заполнить данными и протестировать скорость по сравнению с 1 инстансом  

Дз сдается в виде миниотчета.

Критерии оценки:
- задание выполнено - 10 баллов
- предложено красивое решение - плюс 2 балла  
    за задачу со * + 5 баллов  
    за задачу с ** + 10 баллов

Минимальный порог: 10 баллов

---
## **1. Развёртывание ClickHouse в Docker**

```bash
docker run -d --name my-clickhouse-server --ulimit nofile=262144:262144 clickhouse
```

**Проверяем:**
```bash
docker ps
CONTAINER ID   IMAGE        COMMAND            CREATED         STATUS         PORTS                          NAMES
4372884bb456   clickhouse   "/entrypoint.sh"   7 seconds ago   Up 5 seconds   8123/tcp, 9000/tcp, 9009/tcp   my-clickhouse-server
```

**Подключаемся к CH через `clickhouse-client` в контейнере:**
```bash
docker exec -it my-clickhouse-server clickhouse-client
```

**Создаём таблицу `trips`**
```sql
CREATE TABLE trips
(
    `trip_id` UInt32,
    `vendor_id` Enum8('1' = 1, '2' = 2, '3' = 3, '4' = 4, 'CMT' = 5, 'VTS' = 6, 'DDS' = 7, 'B02512' = 10, 'B02598' = 11, 'B02617' = 12, 'B02682' = 13, 'B02764' = 14, '' = 15),
    `pickup_date` Date,
    `pickup_datetime` DateTime,
    `dropoff_date` Date,
    `dropoff_datetime` DateTime,
    `store_and_fwd_flag` UInt8,
    `rate_code_id` UInt8,
    `pickup_longitude` Float64,
    `pickup_latitude` Float64,
    `dropoff_longitude` Float64,
    `dropoff_latitude` Float64,
    `passenger_count` UInt8,
    `trip_distance` Float64,
    `fare_amount` Float32,
    `extra` Float32,
    `mta_tax` Float32,
    `tip_amount` Float32,
    `tolls_amount` Float32,
    `ehail_fee` Float32,
    `improvement_surcharge` Float32,
    `total_amount` Float32,
    `payment_type` Enum8('UNK' = 0, 'CSH' = 1, 'CRE' = 2, 'NOC' = 3, 'DIS' = 4),
    `trip_type` UInt8,
    `pickup` FixedString(25),
    `dropoff` FixedString(25),
    `cab_type` Enum8('yellow' = 1, 'green' = 2, 'uber' = 3),
    `pickup_nyct2010_gid` Int8,
    `pickup_ctlabel` Float32,
    `pickup_borocode` Int8,
    `pickup_ct2010` String,
    `pickup_boroct2010` String,
    `pickup_cdeligibil` String,
    `pickup_ntacode` FixedString(4),
    `pickup_ntaname` String,
    `pickup_puma` UInt16,
    `dropoff_nyct2010_gid` UInt8,
    `dropoff_ctlabel` Float32,
    `dropoff_borocode` UInt8,
    `dropoff_ct2010` String,
    `dropoff_boroct2010` String,
    `dropoff_cdeligibil` String,
    `dropoff_ntacode` FixedString(4),
    `dropoff_ntaname` String,
    `dropoff_puma` UInt16
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(pickup_date)
ORDER BY pickup_datetime;
```

**Результат:**
```bash
Query id: 0f93805a-dfe8-403b-a562-4b5efeeaef15

Ok.

0 rows in set. Elapsed: 0.011 sec.
```

**Заливаем данные:**
```sql
INSERT INTO trips
SELECT * FROM s3(
    'https://datasets-documentation.s3.eu-west-3.amazonaws.com/nyc-taxi/trips_{1..2}.gz',
    'TabSeparatedWithNames', "
    `trip_id` UInt32,
    `vendor_id` Enum8('1' = 1, '2' = 2, '3' = 3, '4' = 4, 'CMT' = 5, 'VTS' = 6, 'DDS' = 7, 'B02512' = 10, 'B02598' = 11, 'B02617' = 12, 'B02682' = 13, 'B02764' = 14, '' = 15),
    `pickup_date` Date,
    `pickup_datetime` DateTime,
    `dropoff_date` Date,
    `dropoff_datetime` DateTime,
    `store_and_fwd_flag` UInt8,
    `rate_code_id` UInt8,
    `pickup_longitude` Float64,
    `pickup_latitude` Float64,
    `dropoff_longitude` Float64,
    `dropoff_latitude` Float64,
    `passenger_count` UInt8,
    `trip_distance` Float64,
    `fare_amount` Float32,
    `extra` Float32,
    `mta_tax` Float32,
    `tip_amount` Float32,
    `tolls_amount` Float32,
    `ehail_fee` Float32,
    `improvement_surcharge` Float32,
    `total_amount` Float32,
    `payment_type` Enum8('UNK' = 0, 'CSH' = 1, 'CRE' = 2, 'NOC' = 3, 'DIS' = 4),
    `trip_type` UInt8,
    `pickup` FixedString(25),
    `dropoff` FixedString(25),
    `cab_type` Enum8('yellow' = 1, 'green' = 2, 'uber' = 3),
    `pickup_nyct2010_gid` Int8,
    `pickup_ctlabel` Float32,
    `pickup_borocode` Int8,
    `pickup_ct2010` String,
    `pickup_boroct2010` String,
    `pickup_cdeligibil` String,
    `pickup_ntacode` FixedString(4),
    `pickup_ntaname` String,
    `pickup_puma` UInt16,
    `dropoff_nyct2010_gid` UInt8,
    `dropoff_ctlabel` Float32,
    `dropoff_borocode` UInt8,
    `dropoff_ct2010` String,
    `dropoff_boroct2010` String,
    `dropoff_cdeligibil` String,
    `dropoff_ntacode` FixedString(4),
    `dropoff_ntaname` String,
    `dropoff_puma` UInt16
") SETTINGS input_format_try_infer_datetimes = 0
```

**Успех:**
```bash
Query id: 271fa7d1-069b-4fcf-a689-2582914e632c

Ok.

0 rows in set. Elapsed: 9.622 sec. Processed 2.00 million rows, 163.07 MB (207.81 thousand rows/s., 16.95 MB/s.)
Peak memory usage: 974.88 MiB.
```

**Проверяем:**
```sql
SELECT count() FROM trips;

Query id: dc33be1a-2574-4947-8e73-3ef2366b661f

   ┌─count()─┐
1. │ 1999657 │ -- 2.00 million
   └─────────┘

1 row in set. Elapsed: 0.005 sec.

```
## 2. Анализируем данные

**Считаем среднее по `tip_amount`**
```sql
SELECT round(avg(tip_amount), 2)
FROM trips

Query id: 1c910579-fd42-4ff3-abe3-08b75036ccbd

   ┌─round(avg(tip_amount), 2)─┐
1. │                      1.68 │
   └───────────────────────────┘

1 row in set. Elapsed: 0.015 sec. Processed 2.00 million rows, 8.00 MB (132.46 million rows/s., 529.83 MB/s.)
Peak memory usage: 79.24 KiB.
```

**Считаем среднюю стоимость в зависимости от количества пассажиров:**
```sql
SELECT
    passenger_count,
    ceil(avg(total_amount), 2) AS average_total_amount
FROM trips
GROUP BY passenger_count

Query id: 92ebd88c-71ac-4437-9a21-63d89d952b69

    ┌─passenger_count─┬─average_total_amount─┐
 1. │               0 │                22.69 │
 2. │               1 │                15.97 │
 3. │               2 │                17.15 │
 4. │               3 │                16.76 │
 5. │               4 │                17.33 │
 6. │               5 │                16.35 │
 7. │               6 │                16.04 │
 8. │               7 │                 59.8 │
 9. │               8 │                36.41 │
10. │               9 │                 9.81 │
    └─────────────────┴──────────────────────┘

10 rows in set. Elapsed: 0.021 sec. Processed 2.00 million rows, 10.00 MB (93.87 million rows/s., 469.35 MB/s.)
Peak memory usage: 57.40 KiB.
```

**Считаем ежедневное количество подвозов в каждом районе:**
```sql
SELECT
    pickup_date,
    pickup_ntaname,
    SUM(1) AS number_of_trips
FROM trips
GROUP BY
    pickup_date,
    pickup_ntaname
ORDER BY pickup_date ASC

Query id: 74928348-1dd1-40fc-9a62-d565feaad93e
      ┌─pickup_date─┬─pickup_ntaname─────────────────────────────────────┬─number_of_trips─┐
   1. │  2015-07-01 │ Brooklyn Heights-Cobble Hill                       │              13 │
   2. │  2015-07-01 │ Old Astoria                                        │               5 │
   3. │  2015-07-01 │ Flushing                                           │               1 │
   4. │  2015-07-01 │ Yorkville                                          │             378 │
   5. │  2015-07-01 │ Gramercy                                           │             344 │
   6. │  2015-07-01 │ Fordham South                                      │               2 │
   7. │  2015-07-01 │ SoHo-TriBeCa-Civic Center-Little Italy             │             621 │
   8. │  2015-07-01 │ Park Slope-Gowanus                                 │              29 │
   9. │  2015-07-01 │ Bushwick South                                     │               5 │
  10. │  2015-07-01 │ park-cemetery-etc-Manhattan                        │             169 │
...................

Showed 1000 out of 8751 rows.

8751 rows in set. Elapsed: 0.059 sec. Processed 2.00 million rows, 64.32 MB (34.08 million rows/s., 1.10 GB/s.)
Peak memory usage: 16.69 MiB.
```

**Считаем продолжительность каждой поездки в минутах, а затем сгруппируйте результаты по продолжительности поездки:**
```sql
SELECT
    avg(tip_amount) AS avg_tip,
    avg(fare_amount) AS avg_fare,
    avg(passenger_count) AS avg_passenger,
    count() AS count,
    truncate(dateDiff('second', pickup_datetime, dropoff_datetime) / 60) AS trip_minutes
FROM trips
WHERE trip_minutes > 0
GROUP BY trip_minutes
ORDER BY trip_minutes DESC

Query id: 3bc4a51b-d328-4dbd-9ebb-4762cdae8aaa

     ┌──────────────avg_tip─┬───────────avg_fare─┬──────avg_passenger─┬──count─┬─trip_minutes─┐
  1. │   1.9600000381469727 │                  8 │                  1 │      1 │        27511 │
  2. │                    0 │                 12 │                  2 │      1 │        27500 │
  3. │    0.542166673981895 │ 19.716666666666665 │ 1.9166666666666667 │     60 │         1439 │
  4. │    0.902499997522682 │ 11.270625001192093 │            1.95625 │    160 │         1438 │
  5. │   0.9715789457909146 │ 13.646616541353383 │ 2.0526315789473686 │    133 │         1437 │
  6. │   0.9682692398245518 │ 14.134615384615385 │  2.076923076923077 │    104 │         1436 │
  7. │   1.1022105210705808 │ 13.778947368421052 │  2.042105263157895 │     95 │         1435 │
  8. │   0.8419117699651157 │ 12.441176470588236 │ 2.3529411764705883 │     68 │         1434 │
  9. │    0.894264710300109 │ 13.242647058823529 │  2.411764705882353 │     68 │         1433 │
 10. │   0.8565151565002672 │ 15.992424242424242 │  2.212121212121212 │     66 │         1432 │
.........................................

618 rows in set. Elapsed: 0.047 sec. Processed 2.00 million rows, 33.99 MB (42.86 million rows/s., 728.54 MB/s.)
Peak memory usage: 144.08 KiB.
```

**Считаем количество пикапов в каждом районе в разбивке по часам дня:**
```sql
SELECT
    pickup_ntaname,
    toHour(pickup_datetime) AS pickup_hour,
    SUM(1) AS pickups
FROM trips
WHERE pickup_ntaname != ''
GROUP BY
    pickup_ntaname,
    pickup_hour
ORDER BY
    pickup_ntaname ASC,
    pickup_hour ASC

Query id: 7dce605e-75cc-439b-b13e-5048418f3797

      ┌─pickup_ntaname───────────────────────────────────────────┬─pickup_hour─┬─pickups─┐
   1. │ Airport                                                  │           0 │    3509 │
   2. │ Airport                                                  │           1 │    1184 │
   3. │ Airport                                                  │           2 │     401 │
   4. │ Airport                                                  │           3 │     152 │
   5. │ Airport                                                  │           4 │     213 │
   6. │ Airport                                                  │           5 │     955 │
   7. │ Airport                                                  │           6 │    2161 │
   8. │ Airport                                                  │           7 │    3013 │
   9. │ Airport                                                  │           8 │    3601 │
  10. │ Airport                                                  │           9 │    3792 │
.........................................

Showed 1000 out of 3120 rows.

3120 rows in set. Elapsed: 0.066 sec. Processed 2.00 million rows, 68.32 MB (30.49 million rows/s., 1.04 GB/s.)
Peak memory usage: 16.61 MiB.
```

**Считаем поездки в аэропорты LaGuardia или JFK:**
```sql
SELECT
    pickup_datetime,
    dropoff_datetime,
    total_amount,
    pickup_nyct2010_gid,
    dropoff_nyct2010_gid,
    multiIf(dropoff_nyct2010_gid = 138, 'LGA', dropoff_nyct2010_gid = 132, 'JFK', NULL) AS airport_code,
    toYear(pickup_datetime) AS year,
    toDayOfMonth(pickup_datetime) AS day,
    toHour(pickup_datetime) AS hour
FROM trips
WHERE dropoff_nyct2010_gid IN (132, 138)
ORDER BY pickup_datetime ASC

Query id: 62647b94-086e-4aa7-8b34-3275f35f2d14
       ┌─────pickup_datetime─┬────dropoff_datetime─┬─total_amount─┬─pickup_nyct2010_gid─┬─dropoff_nyct2010_gid─┬─airport_code─┬─year─┬─day─┬─hour─┐
    1. │ 2015-07-01 00:04:14 │ 2015-07-01 00:15:29 │         13.3 │                 -34 │                  132 │ JFK          │ 2015 │   1 │    0 │
    2. │ 2015-07-01 00:09:42 │ 2015-07-01 00:12:55 │          6.8 │                  50 │                  138 │ LGA          │ 2015 │   1 │    0 │
    3. │ 2015-07-01 00:23:04 │ 2015-07-01 00:24:39 │          4.8 │                -125 │                  132 │ JFK          │ 2015 │   1 │    0 │
    4. │ 2015-07-01 00:27:51 │ 2015-07-01 00:39:02 │        14.72 │                -101 │                  138 │ LGA          │ 2015 │   1 │    0 │
    5. │ 2015-07-01 00:32:03 │ 2015-07-01 00:55:39 │        39.34 │                  48 │                  138 │ LGA          │ 2015 │   1 │    0 │
    6. │ 2015-07-01 00:34:12 │ 2015-07-01 00:40:48 │         9.95 │                 -93 │                  132 │ JFK          │ 2015 │   1 │    0 │
    7. │ 2015-07-01 00:38:26 │ 2015-07-01 00:49:00 │         13.3 │                 -11 │                  138 │ LGA          │ 2015 │   1 │    0 │
    8. │ 2015-07-01 00:41:48 │ 2015-07-01 00:44:45 │          6.3 │                 -94 │                  132 │ JFK          │ 2015 │   1 │    0 │
    9. │ 2015-07-01 01:06:18 │ 2015-07-01 01:14:43 │        11.76 │                  37 │                  132 │ JFK          │ 2015 │   1 │    1 │
   10. │ 2015-07-01 01:07:34 │ 2015-07-01 01:30:56 │         23.8 │                  42 │                  138 │ LGA          │ 2015 │   1 │    1 │
..............................

Showed 1000 out of 45299 rows.

45299 rows in set. Elapsed: 0.041 sec. Processed 2.00 million rows, 28.00 MB (49.11 million rows/s., 687.57 MB/s.)
Peak memory usage: 2.13 MiB.
```
### 3. Работа со словарём

**Создадим словарь `taxi_zone_dictionary`**
```sql
CREATE DICTIONARY taxi_zone_dictionary
(
    `LocationID` UInt16 DEFAULT 0,
    `Borough` String,
    `Zone` String,
    `service_zone` String
)
PRIMARY KEY LocationID
SOURCE(HTTP(URL 'https://datasets-documentation.s3.eu-west-3.amazonaws.com/nyc-taxi/taxi_zone_lookup.csv' FORMAT 'CSVWithNames'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(HASHED_ARRAY())

Query id: 80ed41b1-b218-4711-a4fe-d44c18360037

Ok.

0 rows in set. Elapsed: 0.008 sec.
```

**Проверяем наличие данных:**
```sql
SELECT *
FROM taxi_zone_dictionary

Query id: f338dd85-fac2-4cc6-a390-b1a70df4c664
     ┌─LocationID─┬─Borough───────┬─Zone──────────────────────────────────────────┬─service_zone─┐
  1. │         77 │ Brooklyn      │ East New York/Pennsylvania Avenue             │ Boro Zone    │
  2. │        106 │ Brooklyn      │ Gowanus                                       │ Boro Zone    │
  3. │        103 │ Manhattan     │ Governor's Island/Ellis Island/Liberty Island │ Yellow Zone  │
  4. │        179 │ Queens        │ Old Astoria                                   │ Boro Zone    │
  5. │        260 │ Queens        │ Woodside                                      │ Boro Zone    │
  6. │        205 │ Queens        │ Saint Albans                                  │ Boro Zone    │
  7. │         81 │ Bronx         │ Eastchester                                   │ Boro Zone    │
  8. │        261 │ Manhattan     │ World Trade Center                            │ Yellow Zone  │
  9. │         46 │ Bronx         │ City Island                                   │ Boro Zone    │
 10. │         18 │ Bronx         │ Bedford Park                                  │ Boro Zone    │
..............................................

265 rows in set. Elapsed: 0.272 sec.
```

**Воспользуемся функцией `dictGet` для получения значения из словаря**
```sql
SELECT dictGet('taxi_zone_dictionary', 'Borough', 132)

Query id: 72bea946-b652-40cf-a107-c6065cda5608

   ┌─dictGet('tax⋯ough', 132)─┐
1. │ Queens                   │
   └──────────────────────────┘

1 row in set. Elapsed: 0.006 sec.
```

**Воспользуемся ``dictHas``, чтобы проверить, присутствует ли ключ в словаре:**
```sql
SELECT dictHas('taxi_zone_dictionary', 132)

Query id: 30fa115b-fff3-40ed-854b-43a58eae306f

   ┌─dictHas('tax⋯nary', 132)─┐
1. │                        1 │
   └──────────────────────────┘

1 row in set. Elapsed: 0.003 sec.
```

**Используем `dictGet`, чтобы получить название района в запросе**
```sql
SELECT
    count(1) AS total,
    dictGetOrDefault('taxi_zone_dictionary', 'Borough', toUInt64(pickup_nyct2010_gid), 'Unknown') AS borough_name
FROM trips
WHERE (dropoff_nyct2010_gid = 132) OR (dropoff_nyct2010_gid = 138)
GROUP BY borough_name
ORDER BY total DESC

Query id: 0d84cd10-c9f7-4cdc-9d9f-e8dd43ad41d9

   ┌─total─┬─borough_name──┐
1. │ 23683 │ Unknown       │
2. │  7053 │ Manhattan     │
3. │  6828 │ Brooklyn      │
4. │  4458 │ Queens        │
5. │  2670 │ Bronx         │
6. │   554 │ Staten Island │
7. │    53 │ EWR           │
   └───────┴───────────────┘

7 rows in set. Elapsed: 0.020 sec. Processed 2.00 million rows, 4.00 MB (98.18 million rows/s., 196.37 MB/s.)
Peak memory usage: 108.66 KiB.
```

### 3. Join

**Простой join, который действует аналогично предыдущему запросу про аэропорт с использованием словаря:**
```sql
SELECT
    count(1) AS total,
    Borough
FROM trips
INNER JOIN taxi_zone_dictionary ON toUInt64(trips.pickup_nyct2010_gid) = taxi_zone_dictionary.LocationID
WHERE (dropoff_nyct2010_gid = 132) OR (dropoff_nyct2010_gid = 138)
GROUP BY Borough
ORDER BY total DESC

Query id: bc753c43-799b-4a23-b7c0-cf535016018e

   ┌─total─┬─Borough───────┐
1. │  7053 │ Manhattan     │
2. │  6828 │ Brooklyn      │
3. │  4458 │ Queens        │
4. │  2670 │ Bronx         │
5. │   554 │ Staten Island │
6. │    53 │ EWR           │
   └───────┴───────────────┘

6 rows in set. Elapsed: 0.049 sec. Processed 2.00 million rows, 4.00 MB (40.77 million rows/s., 81.54 MB/s.)
Peak memory usage: 110.12 KiB.
```
**Работает в 2 раза медленнее, чем запрос со словарём**

**Следующий запрос возвращает строки для 1000 поездок с наибольшей суммой чаевых, а затем выполняет внутреннее соединение каждой строки со словарем:**
```sql
SELECT *
FROM trips
INNER JOIN taxi_zone_dictionary ON trips.dropoff_nyct2010_gid = taxi_zone_dictionary.LocationID
WHERE tip_amount > 0
ORDER BY tip_amount DESC
LIMIT 1000

Query id: c60cdc85-54cf-4665-81fa-04da2768e071

1000 rows in set. Elapsed: 0.463 sec. Processed 2.00 million rows, 615.00 MB (4.32 million rows/s., 1.33 GB/s.)
Peak memory usage: 138.64 MiB.
```

## 4. \* Тестовая БД и сравнение производительности 
В качестве дополнительного набора данных будем использовать датасет `YouTube dataset of dislikes`, на нём же будем производить сравнение производительности с кластером.

Ограничим ресурсы контейнеру в `Docker` для имитации машины с `1 CPU` и `4Gb RAM` :
```bash
docker update --cpus=1 --memory=4g --memory-swap=4g my-clickhouse-server
```

**Создаём таблицу:**
```sql
CREATE TABLE youtube
(
    `id` String,
    `fetch_date` DateTime,
    `upload_date_str` String,
    `upload_date` Date,
    `title` String,
    `uploader_id` String,
    `uploader` String,
    `uploader_sub_count` Int64,
    `is_age_limit` Bool,
    `view_count` Int64,
    `like_count` Int64,
    `dislike_count` Int64,
    `is_crawlable` Bool,
    `has_subtitles` Bool,
    `is_ads_enabled` Bool,
    `is_comments_enabled` Bool,
    `description` String,
    `rich_metadata` Array(Tuple(
        call String,
        content String,
        subtitle String,
        title String,
        url String)),
    `super_titles` Array(Tuple(
        text String,
        url String)),
    `uploader_badges` String,
    `video_badges` String
)
ENGINE = MergeTree
ORDER BY (uploader, upload_date)

Query id: c0d131b9-dc4e-44a5-aac1-72adbb00238e

Ok.

0 rows in set. Elapsed: 0.016 sec.
```

**Наполняем таблицу данными, ограничимся загрузкой 10 млн записей:**
```sql
INSERT INTO youtube
SETTINGS input_format_null_as_default = 1
SELECT
    id,
    parseDateTimeBestEffortUSOrZero(toString(fetch_date)) AS fetch_date,
    upload_date AS upload_date_str,
    toDate(parseDateTimeBestEffortUSOrZero(CAST(upload_date, 'String'))) AS upload_date,
    ifNull(title, '') AS title,
    uploader_id,
    ifNull(uploader, '') AS uploader,
    uploader_sub_count,
    is_age_limit,
    view_count,
    like_count,
    dislike_count,
    is_crawlable,
    has_subtitles,
    is_ads_enabled,
    is_comments_enabled,
    ifNull(description, '') AS description,
    rich_metadata,
    super_titles,
    ifNull(uploader_badges, '') AS uploader_badges,
    ifNull(video_badges, '') AS video_badges
FROM s3('https://clickhouse-public-datasets.s3.amazonaws.com/youtube/original/files/*.zst', 'JSONLines')
LIMIT 10000000

Query id: fb36d44c-fef5-40e4-a647-f1b3526adad8

Ok.

0 rows in set. Elapsed: 208.453 sec. Processed 10.01 million rows, 2.67 GB (48.04 thousand rows/s., 12.79 MB/s.)
Peak memory usage: 807.03 MiB.
```

**Проверяем:**
```sql
SELECT formatReadableQuantity(count())
FROM youtube

Query id: 26ff9688-2be7-4011-bdf8-e325c0cead86

   ┌─formatReadab⋯ty(count())─┐
1. │ 10.00 million            │
   └──────────────────────────┘

1 row in set. Elapsed: 0.005 sec.
```

### Выполняем тестовые запросы

#### SQL 1. Посмотрим, сколько видео было загружено ClickHouse:
```sql
SELECT count()
FROM youtube
WHERE uploader = 'ClickHouse'

Query id: 9b7288de-394c-4023-92be-01ed8e86a1a9

   ┌─count()─┐
1. │       1 │
   └─────────┘

1 row in set. Elapsed: 0.019 sec. Processed 57.34 thousand rows, 1.43 MB (2.95 million rows/s., 73.70 MB/s.)
Peak memory usage: 15.07 KiB.
```
Так как поле `uploader` выбрано в качестве первого столбца первичного ключа, то CH просчитал не все 10 млн. записей, а только `57.34 thousand rows`
#### SQL 2. Посмотрим, что нравится и не нравится в видеороликах ClickHouse
```sql
SELECT
    title,
    like_count,
    dislike_count
FROM youtube
WHERE uploader = 'ClickHouse'
ORDER BY dislike_count DESC

Query id: 0aa85435-0ba8-4cca-a2fb-906bdc879fb9

   ┌─title──────────────────────────────────────────────────────────────────────────────────────┬─like_count─┬─dislike_count─┐
1. │ ClickHouse Online Meetup China, June 26, 2021: Cache Service by Jiaming Mai, Tencent Music │          1 │             0 │
   └────────────────────────────────────────────────────────────────────────────────────────────┴────────────┴───────────────┘

1 row in set. Elapsed: 0.019 sec. Processed 57.34 thousand rows, 2.03 MB (3.07 million rows/s., 108.57 MB/s.)
Peak memory usage: 64.00 B.
```
#### SQL 3. Поиск видеороликов с ClickHouse в полях названия или описания:
```sql
SELECT
    view_count,
    like_count,
    dislike_count,
    concat('https://youtu.be/', id) AS url,
    title
FROM youtube
WHERE (title ILIKE '%ClickHouse%') OR (description ILIKE '%ClickHouse%')
ORDER BY
    like_count DESC,
    view_count DESC

............

Query id: 46d14754-fc10-4d70-88fc-cf49c9a33844

8 rows in set. Elapsed: 19.308 sec. Processed 10.00 million rows, 4.50 GB (517.91 thousand rows/s., 233.31 MB/s.)
Peak memory usage: 34.95 MiB.
```
#### SQL 4.  Если кто-то отключает комментарии, это снижает вероятность того, что кто-то действительно нажмет "нравится" или "не нравится"?
```sql
SELECT
    concat('< ', formatReadableQuantity(view_range)) AS views,
    is_comments_enabled,
    total_clicks / num_views AS prob_like_dislike
FROM
(
    SELECT
        is_comments_enabled,
        power(10, CEILING(log10(view_count + 1))) AS view_range,
        sum(like_count + dislike_count) AS total_clicks,
        sum(view_count) AS num_views
    FROM youtube
    GROUP BY
        view_range,
        is_comments_enabled
)
WHERE view_range > 1
ORDER BY
    is_comments_enabled ASC,
    num_views ASC

Query id: 974b7a7d-dcae-4d3c-83c9-319c6e397057

    ┌─views─────────────┬─is_comments_enabled─┬─────prob_like_dislike─┐
 1. │ < 10.00           │ false               │   0.09573512435302614 │
 2. │ < 100.00          │ false               │    0.0685924784491475 │
 3. │ < 1.00 thousand   │ false               │   0.03384811174271608 │
 4. │ < 10.00 thousand  │ false               │  0.017318532507208412 │
 5. │ < 100.00 thousand │ false               │  0.013024057821623358 │
 6. │ < 1.00 billion    │ false               │  0.005485530960718546 │
 7. │ < 1.00 million    │ false               │  0.010491573201080014 │
 8. │ < 10.00 million   │ false               │   0.00781180966482265 │
 9. │ < 100.00 million  │ false               │  0.006066085486830841 │
10. │ < 10.00           │ true                │   0.09545561277001084 │
11. │ < 100.00          │ true                │   0.07399690690560747 │
12. │ < 1.00 thousand   │ true                │   0.03840628694536492 │
13. │ < 10.00 billion   │ true                │ 0.0029501506100682523 │
14. │ < 10.00 thousand  │ true                │  0.024749372697650825 │
15. │ < 1.00 billion    │ true                │ 0.0066456629588558715 │
16. │ < 100.00 thousand │ true                │  0.022559770594963068 │
17. │ < 100.00 million  │ true                │  0.011994964151233902 │
18. │ < 1.00 million    │ true                │  0.020650947955848913 │
19. │ < 10.00 million   │ true                │   0.01708940819240229 │
    └───────────────────┴─────────────────────┴───────────────────────┘

19 rows in set. Elapsed: 0.968 sec. Processed 10.00 million rows, 250.00 MB (10.33 million rows/s., 258.22 MB/s.)
Peak memory usage: 825.42 KiB.
```
#### SQL 5. Как меняется количество видео со временем
```sql
SELECT
    toStartOfMonth(toDateTime(upload_date)) AS month,
    uniq(uploader_id) AS uploaders,
    count() AS num_videos,
    sum(view_count) AS view_count
FROM youtube
GROUP BY month
ORDER BY month ASC

Query id: f5649ce7-e2d3-4dc3-b5cf-5ca4a338a94b

     ┌──────month─┬─uploaders─┬─num_videos─┬─view_count─┐
  1. │ 1970-01-01 │       738 │        738 │      25441 │
  2. │ 2005-06-01 │         1 │          1 │        940 │
  3. │ 2005-07-01 │         5 │          5 │      14473 │
  4. │ 2005-08-01 │        13 │         13 │     116677 │
  5. │ 2005-09-01 │        15 │         15 │     481672 │
  6. │ 2005-10-01 │        27 │         27 │     472238 │
  7. │ 2005-11-01 │        69 │         70 │    3850070 │
  8. │ 2005-12-01 │       120 │        122 │    3602368 │
  9. │ 2006-01-01 │       230 │        231 │    4904662 │
 10. │ 2006-02-01 │       315 │        318 │   12114988 │
..........................

218 rows in set. Elapsed: 3.393 sec. Processed 10.00 million rows, 430.00 MB (2.95 million rows/s., 126.72 MB/s.)
Peak memory usage: 66.11 MiB.
```
#### SQL 6. youtube добавил автоподбор субтитров в конце 2009 года - был ли тогда скачок
```sql
SELECT
    toStartOfMonth(upload_date) AS month,
    countIf(has_subtitles) / count() AS percent_subtitles,
    percent_subtitles - any(percent_subtitles) OVER (ORDER BY month ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING) AS previous
FROM youtube
GROUP BY month
ORDER BY month ASC

Query id: 19d5c8be-ac82-40b2-9e89-e99dffb769b2

     ┌──────month─┬────percent_subtitles─┬─────────────────previous─┐
  1. │ 1970-01-01 │ 0.006775067750677507 │     0.006775067750677507 │
  2. │ 2005-06-01 │                    0 │    -0.006775067750677507 │
  3. │ 2005-07-01 │                    0 │                        0 │
  4. │ 2005-08-01 │                    0 │                        0 │
  5. │ 2005-09-01 │                    0 │                        0 │
  6. │ 2005-10-01 │  0.14814814814814814 │      0.14814814814814814 │
  7. │ 2005-11-01 │  0.08571428571428572 │    -0.062433862433862425 │
  8. │ 2005-12-01 │  0.10655737704918032 │     0.020843091334894606 │
  9. │ 2006-01-01 │  0.06493506493506493 │     -0.04162231211411539 │
 10. │ 2006-02-01 │  0.10062893081761007 │      0.03569386588254514 │
....................................

218 rows in set. Elapsed: 0.170 sec. Processed 10.00 million rows, 30.00 MB (58.67 million rows/s., 176.00 MB/s.)
Peak memory usage: 61.35 KiB.
```
#### SQL 7. Лучшие загрузчики с течением времени
```sql
WITH uploaders AS
    (
        SELECT uploader
        FROM youtube
        GROUP BY uploader
        ORDER BY sum(view_count) DESC
        LIMIT 10
    )
SELECT
    month,
    uploader,
    sum(view_count) AS total_views,
    avg(dislike_count / like_count) AS like_to_dislike_ratio
FROM youtube
WHERE uploader IN (uploaders)
GROUP BY
    toStartOfMonth(upload_date) AS month,
    uploader
ORDER BY
    month ASC,
    total_views DESC

Query id: 1f49b88a-ba4a-4b30-8a19-84aa48b57a89

         ┌──────month─┬─uploader────────────────────────────────────────┬─total_views─┬─like_to_dislike_ratio─┐
 1. │ 2012-01-01 │ Third String Kicker                             │   430273077 │   0.42900716014755363 │
 2. │ 2012-04-01 │ SET India                                       │        3298 │     1.088235294117647 │
 3. │ 2012-09-01 │ SET India                                       │     1413755 │   0.26820276497695855 │
 4. │ 2012-10-01 │ SET India                                       │     5056434 │   0.41564056772253033 │
 5. │ 2012-12-01 │ SET India                                       │      148808 │   0.18316831683168316 │
     .................................

95 rows in set. Elapsed: 6.908 sec. Processed 10.51 million rows, 343.95 MB (1.52 million rows/s., 49.79 MB/s.)
Peak memory usage: 547.42 MiB.
```
#### SQL 8. Как меняется соотношение "нравится - не нравится" при увеличении количества просмотров?
```sql
SELECT
    concat('< ', formatReadableQuantity(view_range)) AS view_range,
    is_comments_enabled,
    round(like_ratio, 2) AS like_ratio
FROM
(
    SELECT
        power(10, CEILING(log10(view_count + 1))) AS view_range,
        is_comments_enabled,
        avg(like_count / dislike_count) AS like_ratio
    FROM youtube
    WHERE dislike_count > 0
    GROUP BY
        view_range,
        is_comments_enabled
    HAVING view_range > 1
    ORDER BY
        view_range ASC,
        is_comments_enabled ASC
)

Query id: db243c9e-4a80-4ddb-a0d6-aee77e275656

    ┌─view_range────────┬─is_comments_enabled─┬─like_ratio─┐
 1. │ < 10.00           │ false               │       0.64 │
 2. │ < 10.00           │ true                │       0.64 │
 3. │ < 100.00          │ false               │       3.15 │
 4. │ < 100.00          │ true                │       4.01 │
 5. │ < 1.00 thousand   │ false               │       9.09 │
 6. │ < 1.00 thousand   │ true                │      13.31 │
 7. │ < 10.00 thousand  │ false               │      19.11 │
 8. │ < 10.00 thousand  │ true                │      31.08 │
 9. │ < 100.00 thousand │ false               │      23.42 │
10. │ < 100.00 thousand │ true                │      42.13 │
11. │ < 1.00 million    │ false               │      19.33 │
12. │ < 1.00 million    │ true                │       37.3 │
13. │ < 10.00 million   │ false               │      12.11 │
14. │ < 10.00 million   │ true                │       30.7 │
15. │ < 100.00 million  │ false               │       7.36 │
16. │ < 100.00 million  │ true                │      24.14 │
17. │ < 1.00 billion    │ false               │       1.86 │
18. │ < 1.00 billion    │ true                │      17.25 │
19. │ < 10.00 billion   │ true                │       10.1 │
    └───────────────────┴─────────────────────┴────────────┘

19 rows in set. Elapsed: 0.578 sec. Processed 10.00 million rows, 250.00 MB (17.30 million rows/s., 432.50 MB/s.)
Peak memory usage: 20.26 KiB.
```
#### SQL 9. Как распределяются просмотры?
```sql
SELECT
    labels AS percentile,
    round(quantiles) AS views
FROM
(
    SELECT
        quantiles(0.999, 0.99, 0.95, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1)(view_count) AS quantiles,
        ['99.9th', '99th', '95th', '90th', '80th', '70th', '60th', '50th', '40th', '30th', '20th', '10th'] AS labels
    FROM youtube
)
ARRAY JOIN
    quantiles,
    labels

Query id: 366aa83f-77c0-4e6f-aa9a-831f725f2be1

    ┌─percentile─┬───views─┐
 1. │ 99.9th     │ 2034977 │
 2. │ 99th       │  216919 │
 3. │ 95th       │   21262 │
 4. │ 90th       │    5906 │
 5. │ 80th       │    1558 │
 6. │ 70th       │     639 │
 7. │ 60th       │     290 │
 8. │ 50th       │     150 │
 9. │ 40th       │      80 │
10. │ 30th       │      44 │
11. │ 20th       │      23 │
12. │ 10th       │      10 │
    └────────────┴─────────┘

12 rows in set. Elapsed: 0.139 sec. Processed 10.00 million rows, 80.00 MB (71.90 million rows/s., 575.22 MB/s.)
Peak memory usage: 10.91 KiB.
```

## 5. \*\* ClickHouse в кластере

**Развернём  3 ноды ClickHouse и 1 ноду Zookeper в Docker, используя docker-compose**
**Ограничим ноды CH в `1 CPU` и `4Gb RAM`**
```yaml
version: '3'

services:
  zookeeper:
    image: bitnami/zookeeper:latest
    hostname: zookeeper
    container_name: zookeeper
    networks:
      - ch_replicated
    environment:
      - ALLOW_ANONYMOUS_LOGIN=yes
      - ZOOKEEPER_CLIENT_PORT=2181
    ports:
      - 2182:2181
      - 2888:2888
      - 3888:3888 

  clickhouse1:
    image: clickhouse/clickhouse-server
    deploy:
      resources:
        limits:
          cpus: 1
          memory: 4g
    hostname: clickhouse1
    container_name: clickhouse1
    ports:
      - 8002:9000
      - 9123:8123
    volumes:
      - clickhouse1-etc:/etc/clickhouse-server
      - clickhouse1-data:/var/lib/clickhouse 
    ulimits:
      nproc: 65535
      nofile:
        soft: 262144
        hard: 262144
    networks:
      - ch_replicated
    depends_on:
      - zookeeper

  clickhouse2:
    image: clickhouse/clickhouse-server
    deploy:
      resources:
        limits:
          cpus: 1
          memory: 4g
    hostname: clickhouse2
    container_name: clickhouse2
    ports:
      - 8003:9000
      - 9124:8123
    volumes:
      - clickhouse2-etc:/etc/clickhouse-server
      - clickhouse2-data:/var/lib/clickhouse 
    ulimits:
      nproc: 65535
      nofile:
        soft: 262144
        hard: 262144
    networks:
      - ch_replicated
    depends_on:
      - zookeeper

  clickhouse3:
    image: clickhouse/clickhouse-server
    deploy:
      resources:
        limits:
          cpus: 1
          memory: 4g
    hostname: clickhouse3
    container_name: clickhouse3
    ports:
      - 8004:9000
      - 9125:8123
    volumes:
      - clickhouse3-etc:/etc/clickhouse-server
      - clickhouse3-data:/var/lib/clickhouse 
    ulimits:
      nproc: 65535
      nofile:
        soft: 262144
        hard: 262144
    networks:
      - ch_replicated
    depends_on:
      - zookeeper

volumes:
  clickhouse1-etc:
  clickhouse2-etc:
  clickhouse3-etc:
  clickhouse1-data:
  clickhouse2-data:
  clickhouse3-data:

networks:
  ch_replicated:
    driver: bridge
```

**Добавляем конфигурацию кластера из 3х шардов без реплик в `/etc/clickhouse-server/config.d/my_cluster.xml`**
```xml
<clickhouse>
	<remote_servers>
		<my_cluster>
			<shard>
				<replica>
					<host>clickhouse1</host>
					<port>9000</port>
					<user>default</user>
					<password>qwe123</password>
				</replica>
			</shard>
			<shard>
				<replica>
					<host>clickhouse2</host>
					<port>9000</port>
					<user>default</user>
					<password>qwe123</password>
				</replica>
			</shard>
			<shard>
				<replica>
					<host>clickhouse3</host>
					<port>9000</port>
					<user>default</user>
					<password>qwe123</password>
				</replica>
			</shard>
		</my_cluster>
	</remote_servers>
	<zookeeper>
		<node index="1">
			<host>zookeeper</host>
			<port>2181</port>
		</node>
	</zookeeper>
</clickhouse>
```

**Для пользователя `Default` разрешаем подключения из подсети CH в докере `172.18.0.0/16`**
**и прописываем пароль `qwe123`**
```xml
<clickhouse>
  <!-- Docs: <https://clickhouse.com/docs/operations/settings/settings_users/> -->
  <users>
    <default>
      <!-- User default is available only locally -->
      <networks>
        <ip>::1</ip>
        <ip>127.0.0.1</ip>
        <ip>172.18.0.0/16</ip>
      </networks>
      <password>qwe123</password>
    </default>
  </users>
</clickhouse>
```

**Распространяем конфиги на все ноды Клика и рестартим**.
**После перезагрузки коннектимся через клиент с использованием пароля и проверяем кластер:**
```bash
clickhouse1 :) show clusters

SHOW CLUSTERS

Query id: f841be15-9b38-436f-bb83-4818acd1c0cc

   ┌─cluster────┐
1. │ default    │
2. │ my_cluster │
   └────────────┘

2 rows in set. Elapsed: 0.003 sec.
```

**Создаём таблицу `youtube` на всём кластере `my_cluster`**
```sql
CREATE TABLE youtube ON CLUSTER my_cluster
(
    `id` String,
    `fetch_date` DateTime,
    `upload_date_str` String,
    `upload_date` Date,
    `title` String,
    `uploader_id` String,
    `uploader` String,
    `uploader_sub_count` Int64,
    `is_age_limit` Bool,
    `view_count` Int64,
    `like_count` Int64,
    `dislike_count` Int64,
    `is_crawlable` Bool,
    `has_subtitles` Bool,
    `is_ads_enabled` Bool,
    `is_comments_enabled` Bool,
    `description` String,
    `rich_metadata` Array(Tuple(
        call String,
        content String,
        subtitle String,
        title String,
        url String)),
    `super_titles` Array(Tuple(
        text String,
        url String)),
    `uploader_badges` String,
    `video_badges` String
)
ENGINE = MergeTree
ORDER BY (uploader, upload_date)

Query id: 1331a11d-8863-4e57-9b97-d6f119d05a7b

   ┌─host────────┬─port─┬─status─┬─error─┬─num_hosts_remaining─┬─num_hosts_active─┐
1. │ clickhouse2 │ 9000 │      0 │       │                   2 │                0 │
2. │ clickhouse1 │ 9000 │      0 │       │                   1 │                0 │
3. │ clickhouse3 │ 9000 │      0 │       │                   0 │                0 │
   └─────────────┴──────┴────────┴───────┴─────────────────────┴──────────────────┘

3 rows in set. Elapsed: 0.090 sec.
```

**Создаём ``distributed`` таблицу на всём кластере для доступа к данным на всех нодах:**
```sql
CREATE TABLE IF NOT EXISTS youtube_distrib ON CLUSTER my_cluster AS youtube
ENGINE = Distributed('my_cluster', 'default', 'youtube', rand())

Query id: 71393f8a-881a-4710-8586-f8cf722e3fa7

   ┌─host────────┬─port─┬─status─┬─error─┬─num_hosts_remaining─┬─num_hosts_active─┐
1. │ clickhouse2 │ 9000 │      0 │       │                   2 │                0 │
2. │ clickhouse3 │ 9000 │      0 │       │                   1 │                0 │
3. │ clickhouse1 │ 9000 │      0 │       │                   0 │                0 │
   └─────────────┴──────┴────────┴───────┴─────────────────────┴──────────────────┘

3 rows in set. Elapsed: 0.087 sec.
```

**Заливаем 10 млн записей:**
```sql
INSERT INTO youtube_distrib
SETTINGS input_format_null_as_default = 1
SELECT
    id,
    parseDateTimeBestEffortUSOrZero(toString(fetch_date)) AS fetch_date,
    upload_date AS upload_date_str,
    toDate(parseDateTimeBestEffortUSOrZero(CAST(upload_date, 'String'))) AS upload_date,
    ifNull(title, '') AS title,
    uploader_id,
    ifNull(uploader, '') AS uploader,
    uploader_sub_count,
    is_age_limit,
    view_count,
    like_count,
    dislike_count,
    is_crawlable,
    has_subtitles,
    is_ads_enabled,
    is_comments_enabled,
    ifNull(description, '') AS description,
    rich_metadata,
    super_titles,
    ifNull(uploader_badges, '') AS uploader_badges,
    ifNull(video_badges, '') AS video_badges
FROM s3('https://clickhouse-public-datasets.s3.amazonaws.com/youtube/original/files/*.zst', 'JSONLines')
LIMIT 10000000

Query id: 67287b0b-290f-4ca4-8004-0fb3b381c018

Ok.

0 rows in set. Elapsed: 214.744 sec. Processed 10.01 million rows, 2.67 GB (46.63 thousand rows/s., 12.42 MB/s.)
Peak memory usage: 913.67 MiB.
```

**Проверяем:**
```sql
SELECT count()
FROM youtube_distrib

Query id: 36fbfe24-b0c5-491f-b85d-aba327c75d5c

   ┌──count()─┐
1. │ 10000000 │ -- 10.00 million
   └──────────┘

1 row in set. Elapsed: 0.017 sec.
```

**Выполняем запросы в кластере как на сингл ноде, заменив в запросе таблицу `youtube` на `distributed` таблицу `youtube_distrib` и запишем результаты в таблицу:**

| SQL № | Single Node | Cluster    | **%** |
| :---- | :---------- | :--------- | ----- |
| 1     | 0.019 sec   | 0.019 sec  | 0%    |
| 2     | 0.019 sec   | 0.018 sec  | 0.5%  |
| 3     | 19.308 sec  | 10.340 sec | 46%   |
| 4     | 0.968 sec   | 0.795 sec  | 17%   |
| 5     | 3.393 sec   | 2.935 sec  | 13%   |
| 6     | 0.170 sec   | 0.115 sec  | 32%   |
| 7     | 6.908 sec   | 4.991 sec  | 27%   |
| 8     | 0.578 sec   | 0.273 sec  | 52%   |
| 9     | 0.139       | 0.094 sec  | 32%   |

### Выводы

Горизонтальное масштабирование кластера ClickHouse положительным образом сказывается на производительности.
