## Домашнее задание

Масштабирование и отказоустойчивость Cassandra

Цель:
В результате выполнения ДЗ вы подготовите среду и развернете Cassandra кластер для дальнейшего изучения возможностей маштабирования и восстанавления Cassandra кластеров.

Описание/Пошаговая инструкция выполнения домашнего задания:
Необходимо:
- развернуть docker локально или в облаке
- поднять 3 узловый Cassandra кластер.
- Создать keyspase с 2-мя таблицами. Одна из таблиц должна иметь составной Partition key, как минимум одно поле - clustering key, как минимум одно поле не входящее в primiry key.
- Заполнить данными обе таблицы.
- Выполнить 2-3 варианта запроса использую WHERE
- Создать вторичный индекс на поле, не входящее в primiry key.
- (*) нагрузить кластер при помощи Cassandra Stress Tool (используя "How to use Apache Cassandra Stress Tool.pdf" из материалов).
      
Критерии оценки:
- задание выполнено - 10 баллов
- +5 баллов за задание со *
- предложено красивое решение - плюс 2 балла
---
### **1. Развёртывание 3-узлового кластера Cassandra в Docker**

Используем `docker-compose.yml` для автоматизации развёртывания:
```yaml
version: '3'

services:
  cassandra-node1:
    image: cassandra:4.1
    restart: always
    container_name: cassandra-node1
    hostname: cassandra-node1
    healthcheck:
        test: ["CMD", "cqlsh", "-e", "describe keyspaces" ]
        interval: 5s
        timeout: 5s
        retries: 60
    environment:
      - CASSANDRA_SEEDS=cassandra-node1,cassandra-node2
      - CASSANDRA_CLUSTER_NAME=MyCluster
      - CASSANDRA_DC=datacenter1
    ports:
      - "9042:9042"
    volumes:
      - cassandra-node1-etc:/etc/cassandra
      - cassandra-node1-data:/var/lib/cassandra
    networks:
      - cassandra-net

  cassandra-node2:
    image: cassandra:4.1
    restart: always
    container_name: cassandra-node2
    hostname: cassandra-node2
    healthcheck:
        test: ["CMD", "cqlsh", "-e", "describe keyspaces"]
        interval: 5s
        timeout: 5s
        retries: 60
    environment:
      - CASSANDRA_SEEDS=cassandra-node1,cassandra-node2
      - CASSANDRA_CLUSTER_NAME=MyCluster
      - CASSANDRA_DC=datacenter1
    ports:
      - "9043:9042"
    volumes:
      - cassandra-node2-etc:/etc/cassandra
      - cassandra-node2-data:/var/lib/cassandra
    depends_on:
      - cassandra-node1
    networks:
      - cassandra-net

  cassandra-node3:
    image: cassandra:4.1
    restart: always
    container_name: cassandra-node3
    hostname: cassandra-node3
    healthcheck:
        test: ["CMD", "cqlsh", "-e", "describe keyspaces" ]
        interval: 5s
        timeout: 5s
        retries: 60
    environment:
      - CASSANDRA_SEEDS=cassandra-node1,cassandra-node2
      - CASSANDRA_CLUSTER_NAME=MyCluster
      - CASSANDRA_DC=datacenter1
    ports:
      - "9044:9042"
    volumes:
      - cassandra-node3-etc:/etc/cassandra
      - cassandra-node3-data:/var/lib/cassandra
    depends_on:
      - cassandra-node2
    networks:
      - cassandra-net

volumes:
  cassandra-node1-etc:
  cassandra-node2-etc:
  cassandra-node3-etc:
  cassandra-node1-data:
  cassandra-node2-data:
  cassandra-node3-data:

networks:
  cassandra-net:
    driver: bridge
```

**Запуск:**
```bash
docker-compose up -d
```

**Проверка кластера:**
```bash
docker exec -it cassandra-node1 nodetool status
```

**Видим 3 узла в статусе `UN`**
```bash
# docker exec -it cassandra-node1 nodetool status
Datacenter: datacenter1
=======================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address     Load        Tokens  Owns (effective)  Host ID                               Rack
UN  172.18.0.4  128.16 KiB  16      63.9%             ea5bbcec-59dd-41fd-897f-18ef69300ce4  rack1
UN  172.18.0.3  104.35 KiB  16      70.1%             f42dc473-2e36-4e5b-9b74-bdc186f24a17  rack1
UN  172.18.0.2  109.4 KiB   16      66.0%             0b20b33b-b22c-46e0-bd37-174629a03711  rack1
```
### **2. Создание Keyspace и таблиц**

Подключаемся к узлу через `cqlsh`:
```bash
docker exec -it cassandra-node1 cqlsh
```

**Keyspace с репликацией 3 (для отказоустойчивости):**
```sql
CREATE KEYSPACE IF NOT EXISTS my_keyspace 
WITH replication = {
  'class': 'NetworkTopologyStrategy', 
  'datacenter1': 3 
};
```

**Таблица 1: Составной Partition Key + Clustering Key**
```sql
USE my_keyspace;

CREATE TABLE orders (
    user_id UUID,
    order_id UUID,
    order_date TIMESTAMP,
    product_name TEXT,
    price DECIMAL,
    PRIMARY KEY ((user_id, order_id), order_date)
    )
WITH CLUSTERING ORDER BY (order_date DESC);
```

**Таблица 2: Простой Primary Key + дополнительное поле**
```sql
CREATE TABLE products (
    product_id UUID PRIMARY KEY,
    name TEXT,
    category TEXT,
    in_stock BOOLEAN
);
```

### **3. Заполнение данными**
```sql
-- Для orders
INSERT INTO orders (user_id, order_id, order_date, product_name, price) 
VALUES (uuid(), uuid(), toTimestamp(now()), 'Laptop', 999.99);

INSERT INTO orders (user_id, order_id, order_date, product_name, price) 
VALUES (uuid(), uuid(), toTimestamp(now()), 'Smartphone', 699.99);

-- Для products
INSERT INTO products (product_id, name, category, in_stock) 
VALUES (uuid(), 'Laptop', 'Electronics', true);

INSERT INTO products (product_id, name, category, in_stock) 
VALUES (uuid(), 'Book', 'Education', false);
```
### **4. Запросы с WHERE**

Примеры запросов для таблицы `orders`:
```sql
-- Включаем вывод в вертикальном режиме
EXPAND ON

-- По составному ключу (обязательно все части Partition Key)
SELECT * FROM orders 
WHERE user_id = b1c9786a-53d6-4089-8c4d-10c6f0d6f211 
AND order_id = f31fc280-3980-4c0d-a736-661564464f12;

@ Row 1
--------------+--------------------------------------
 user_id      | b1c9786a-53d6-4089-8c4d-10c6f0d6f211
 order_id     | f31fc280-3980-4c0d-a736-661564464f12
 order_date   | 2025-04-17 15:15:53.050000+0000
 price        | 699.99
 product_name | Smartphone

(1 rows)

-- По Clustering Key с фильтром
SELECT * FROM orders 
WHERE user_id = b1c9786a-53d6-4089-8c4d-10c6f0d6f211 
AND order_id = f31fc280-3980-4c0d-a736-661564464f12
AND order_date > '2024-04-01';

@ Row 1
--------------+--------------------------------------
 user_id      | b1c9786a-53d6-4089-8c4d-10c6f0d6f211
 order_id     | f31fc280-3980-4c0d-a736-661564464f12
 order_date   | 2025-04-17 15:15:53.050000+0000
 price        | 699.99
 product_name | Smartphone

(1 rows)

-- Ошибка (нельзя фильтровать только по Clustering Key без Partition Key):
SELECT * FROM orders WHERE order_date > '2025-04-01'; -- Не сработает!
InvalidRequest: Error from server: code=2200 [Invalid query] message="Cannot execute this query as it might involve data filtering and thus may have unpredictable performance. If you want to execute this query despite the performance unpredictability, use ALLOW FILTERING"
```
### **5. Вторичный индекс**

```sql
-- Пробуем сделать запрос из `products` с условием по `category`
-- Получим ошибку
SELECT * FROM products WHERE category = 'Electronics';
InvalidRequest: Error from server: code=2200 [Invalid query] message="Cannot execute this query as it might involve data filtering and thus may have unpredictable performance. If you want to execute this query despite the performance unpredictability, use ALLOW FILTERING"

--Создадим индекс на поле `category` в таблице `products`
CREATE INDEX IF NOT EXISTS idx_category ON products (category);

-- Теперь можно выполнить:
SELECT * FROM products WHERE category = 'Electronics';

@ Row 1
------------+--------------------------------------
 product_id | 9f7ac211-be86-43b3-a492-1d862b1b4aad
 category   | Electronics
 in_stock   | True
 name       | Laptop

(1 rows)
```
## **Cassandra Stress Tool**

Инструмент входит в стандартную поставку Apache Cassandra, дополнительная установка не требуется.
###  **Шаг 1. Запуск в Docker**

1. Подключаемся к одному из узлов:
```bash
docker exec -it cassandra-node1 bash
```

2. Переходим в папку с `cassandra-stress`:
```
cd /opt/cassandra/tools/bin
```
### **Шаг 2: Подготовка схемы для тестирования**

Перед тестированием создадим отдельный `keqspace`  и таблицу, которые будут использоваться для нагрузки:
```sql
CREATE KEYSPACE IF NOT EXISTS stress_test 
WITH replication = {'class': 'NetworkTopologyStrategy', 'datacenter1': 3};

CREATE TABLE stress_test.users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    email TEXT,
    age INT
);
```
## **Шаг 3: Тестирование записи (Write Load Test)**

**Команда:**
```bash
./cassandra-stress write n=100000 cl=ONE -mode native cql3 -schema keyspace=stress_test -log file=stress_write.log -graph file=stress_write.html
```
**Параметры запуска:**
- `n=100000` - 100 000 операций записи
- `cl=ONE` - уровень согласованности `ONE`
- `-mode native cql3` - использование CQL (актуально для современных версий Cassandra)
- `-schema keyspace=stress_test` - тестируемая keyspace
- `-log file=stress_write.log` - сохранение логов в файл
- `-graph file=stress_write.html` -  отчёт в виде `html` страницы

## **Шаг 4: Тестирование чтения (Read Load Test)**

**Команда:**
```bash
./cassandra-stress read n=50000 cl=ONE -mode native cql3 -schema keyspace=stress_test -log file=stress_read.log -graph file=stress_read.html
```
**Параметры запуска:**
- `n=50000` - 50 000 операций чтения
- Остальные параметры аналогичны записи

## **Шаг 5: Смешанная нагрузка (Read + Write)**

```bash
./cassandra-stress mixed "ratio(write=2,read=8)" n=100000 cl=ONE -mode native cql3 -schema keyspace=stress_test -log file=stress_mixed.log -graph file=stress_mixed.html
```
**Параметры:**
- `ratio=(write=2,read=8)` - соотношение записей и чтений (20% запись, 80% чтение)

## **Шаг 6: Анализ результатов**

### **1. Логи инструмента**

Проверяем файлы:
- `stress_write.log` - статистика по записи
- `stress_read.log` - статистика по чтению
- `stress_mixed.log` - смешанная статистика

**Пример вывода:**
```bash
Results:
Op rate                   :    8,744 op/s  [READ: 7,005 op/s, WRITE: 1,740 op/s]
Partition rate            :    8,744 pk/s  [READ: 7,005 pk/s, WRITE: 1,740 pk/s]
Row rate                  :    8,744 row/s [READ: 7,005 row/s, WRITE: 1,740 row/s]
Latency mean              :   20.2 ms [READ: 19.9 ms, WRITE: 21.1 ms]
Latency median            :   12.9 ms [READ: 12.7 ms, WRITE: 13.4 ms]
Latency 95th percentile   :   60.8 ms [READ: 60.1 ms, WRITE: 63.5 ms]
Latency 99th percentile   :  112.7 ms [READ: 111.7 ms, WRITE: 116.7 ms]
Latency 99.9th percentile :  193.3 ms [READ: 191.5 ms, WRITE: 213.6 ms]
Latency max               :  441.7 ms [READ: 428.3 ms, WRITE: 441.7 ms]
Total partitions          :    100,000 [READ: 80,104, WRITE: 19,896]
Total errors              :          0 [READ: 0, WRITE: 0]
Total GC count            : 0
Total GC memory           : 0.000 KiB
Total GC time             :    0.0 seconds
Avg GC time               :    NaN ms
StdDev GC time            :    0.0 ms
Total operation time      : 00:00:11

Improvement over 121 threadCount: -3%
```

Проверяем файлы:
- `stress_write.html` - отчёт по записи
- `stress_read.html` - отчёт по чтению
- `stress_mixed.html` - отчёт по смешанной статистике
**Пример отчёта в виде `html`**
![[stress_report_example.png]]
### **2. Мониторинг кластера**

- **Через `nodetool`:**
    `docker exec -it cassandra-node1 nodetool tpstats`
    Покажет загрузку потоков (ThreadPool).
 ```bash
Pool Name                      Active Pending Completed Blocked All time blocked
MutationStage                  0      0       707041    0       0
ReadStage                      0      0       277       0       0
CompactionExecutor             0      0       53        0       0
MemtableReclaimMemory          0      0       12        0       0
PendingRangeCalculator         0      0       4         0       0
GossipStage                    0      0       582       0       0
SecondaryIndexManagement       0      0       1         0       0
HintsDispatcher                0      0       0         0       0
MigrationStage                 0      0       0         0       0
MemtablePostFlush              0      0       32        0       0
PerDiskMemtableFlushWriter_0   0      0       10        0       0
ValidationExecutor             0      0       0         0       0
Sampler                        0      0       0         0       0
ViewBuildExecutor              0      0       0         0       0
MemtableFlushWriter            0      0       12        0       0
CacheCleanupExecutor           0      0       0         0       0
Native-Transport-Auth-Requests 0      0       0         0       0
Native-Transport-Requests      0      0       391       0       0
```
    
- **Через `nodetool cfstats`:**
    
    `docker exec -it cassandra-node1 nodetool cfstats stress_test.users`
    
    Статистика по таблице:   
```bash
Total number of tables: 49
----------------
Keyspace : stress_test
        Read Count: 0
        Read Latency: NaN ms
        Write Count: 701851
        Write Latency: 0.020822724481407023 ms
        Pending Flushes: 0
                Table: users
                SSTable count: 0
                Old SSTable count: 0
                Space used (live): 0
                Space used (total): 0
                Space used by snapshots (total): 0
                Off heap memory used (total): 0
                SSTable Compression Ratio: -1.0
                Number of partitions (estimate): 0
                Memtable cell count: 0
                Memtable data size: 0
                Memtable off heap memory used: 0
                Memtable switch count: 0
                Speculative retries: 0
                Local read count: 0
                Local read latency: NaN ms
                Local write count: 0
                Local write latency: NaN ms
                Pending flushes: 0
                Percent repaired: 100.0
                Bytes repaired: 0.000KiB
                Bytes unrepaired: 0.000KiB
                Bytes pending repair: 0.000KiB
                Bloom filter false positives: 0
                Bloom filter false ratio: 0.00000
                Bloom filter space used: 0
                Bloom filter off heap memory used: 0
                Index summary off heap memory used: 0
                Compression metadata off heap memory used: 0
                Compacted partition minimum bytes: 0
                Compacted partition maximum bytes: 0
                Compacted partition mean bytes: 0
                Average live cells per slice (last five minutes): NaN
                Maximum live cells per slice (last five minutes): 0
                Average tombstones per slice (last five minutes): NaN
                Maximum tombstones per slice (last five minutes): 0
                Dropped Mutations: 0
                Droppable tombstone ratio: 0.00000
```
