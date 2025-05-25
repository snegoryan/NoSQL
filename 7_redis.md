# ДЗ 7. Redis

## Домашнее задание
Redis
Цель:
В результате выполнения ДЗ вы поработаете с Redis.

Описание/Пошаговая инструкция выполнения домашнего задания:
Необходимо:
- сохранить большой JSON (~20МБ) в виде разных структур - строка, hset, zset, list;
- протестировать скорость сохранения и чтения;
- предоставить отчет.

---
Задание повышенной сложности*  
настроить редис кластер на 3х нодах с отказоустойчивостью, затюнить таймауты

Критерии оценки:

- задание выполнено - 10 баллов
- предложено красивое решение - плюс 2 балла
- выполнено задание со* - плюс 5 баллов

Минимальный порог: 10 баллов

---
## Основное задание (Работа с большим JSON)

### 1. Подготовка окружения

**Создадим `docker-compose.yml` для простого Redis:**
```yaml
version: '3'
services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - ./redis-data:/data
```

**Запустим: `docker-compose up -d`**
### 2. Генерация тестового JSON (~20MB)

**Создадим Python скрипт `generate_data.py`:**
```python
import json
import random
import string

def random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

data = {
    "users": [
        {
            "id": i,
            "name": random_string(10),
            "email": f"{random_string(5)}@example.com",
            "score": random.randint(0, 1000)
        }
        for i in range(250000)  # ~20MB при таких параметрах
    ]
}

with open('large_data.json', 'w') as f:
    json.dump(data, f)
```

**Проверим размер:**
```bash
ll -h large_data.json
-rw-r--r-- 1 root root 20M May  2 13:09 large_data.json
```
### 3. Загрузка данных в Redis
Будем использовать `redis-py` (Python-клиент для Redis).

**Установка зависимостей:**
```bash
pip install redis

Collecting redis
  Downloading redis-6.0.0-py3-none-any.whl (268 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 268.9/268.9 KB 2.9 MB/s eta 0:00:00
Collecting async-timeout>=4.0.3
  Downloading async_timeout-5.0.1-py3-none-any.whl (6.2 kB)
Installing collected packages: async-timeout, redis
Successfully installed async-timeout-5.0.1 redis-6.0.0
```

**Скрипт для загрузки данных (`test_redis.py`):**
```python
import json
import time
import redis

# Подключение
r = redis.Redis(host='localhost', port=6379, db=0)

# Загрузка данных
with open('large_data.json') as f:
    data = json.load(f)

users = data['users']

# 1. Тест STRING
start = time.time()
r.set('users:string', json.dumps(users))
string_write_time = time.time() - start

start = time.time()
string_data = r.get('users:string')
string_read_time = time.time() - start

# 2. Test HSET
start = time.time()
for user in users:
    r.hset('users:hset', user['id'], json.dumps(user))
hset_write_time = time.time() - start

start = time.time()
hset_data = r.hgetall('users:hset')
hset_read_time = time.time() - start

# 3. Test ZSET (по score)
start = time.time()
for user in users:
    r.zadd('users:zset', {json.dumps(user): user['score']})
zset_write_time = time.time() - start

start = time.time()
zset_data = r.zrange('users:zset', 0, -1)
zset_read_time = time.time() - start

# 4. Test LIST
start = time.time()
for user in users:
    r.rpush('users:list', json.dumps(user))
list_write_time = time.time() - start

start = time.time()
list_data = r.lrange('users:list', 0, -1)
list_read_time = time.time() - start

# Отчёт
print(f"STRING: write {string_write_time:.2f}s, read {string_read_time:.2f}s")
print(f"HSET: write {hset_write_time:.2f}s, read {hset_read_time:.2f}s")
print(f"ZSET: write {zset_write_time:.2f}s, read {zset_read_time:.2f}s")
print(f"LIST: write {list_write_time:.2f}s, read {list_read_time:.2f}s")
```

**Запуск теста:**
```bash
python3 test_redis.py
```

**Отчёт**:
```bash
STRING: write 0.39s, read 0.17s
HSET: write 47.79s, read 1.10s
ZSET: write 50.15s, read 0.62s
LIST: write 44.33s, read 0.52s
```

- **String** будет самым быстрым для записи/чтения, но неудобным для частичных операций.
- **HSET/ZSET/LIST** медленнее, но позволяют работать с элементами по отдельности.
#### **Выводы:**

- **String** — лучший вариант, если нужна максимальная скорость и не требуется доступ к частям данных.
- **HSET** — хорош, если нужен доступ по ключам.
- **ZSET** — подходит для ранжированных данных.
- **LIST** — оптимален для последовательностей (например, логов).

### **4. Redis Cluster \***

#### **1. Создаём `docker-compose.yml`**

**Следующий файл развернёт 3 ноды Redis в режиме кластера *без реплик*:**
**Добавляем опцию `--cluster-node-timeout 5000` – таймаут отклика ноды (5 сек).**
```yaml
version: '3.8'

services:
  redis-node1:
    image: redis:latest
    container_name: redis-node1
    ports:
      - "7001:6379"
    command: redis-server --cluster-enabled yes --cluster-config-file nodes-node-1.conf --cluster-node-timeout 5000 --appendonly yes
    volumes:
      - redis-data-1:/data

  redis-node2:
    image: redis:latest
    container_name: redis-node2
    ports:
      - "7002:6379"
    command: redis-server --cluster-enabled yes --cluster-config-file nodes-node-2.conf --cluster-node-timeout 5000 --appendonly yes
    volumes:
      - redis-data-2:/data

  redis-node3:
    image: redis:latest
    container_name: redis-node3
    ports:
      - "7003:6379"
    command: redis-server --cluster-enabled yes --cluster-config-file nodes-node-3.conf --cluster-node-timeout 5000 --appendonly yes
    volumes:
      - redis-data-3:/data

volumes:
  redis-data-1:
  redis-data-2:
  redis-data-3:
```

#### **2. Запуск кластера**
```bash
docker-compose -f docker-compose-cluster.yml up -d

[+] Running 6/6
 ✔ Volume "redis_redis-data-3"  Created   0.0s
 ✔ Volume "redis_redis-data-1"  Created   0.0s
 ✔ Volume "redis_redis-data-2"  Created   0.0s
 ✔ Container redis-node2        Started   0.4s
 ✔ Container redis-node3        Started   0.4s
 ✔ Container redis-node1        Started   0.4s
```

#### **3. Инициализация кластера**

Подключаемся к одной из нод и создаём кластер:
```bash
docker exec -it redis-node1 bash
```

Создаём кластер:
```bash
redis-cli --cluster create 172.18.0.5:6379 172.18.0.4:6379 172.18.0.3:6379 --cluster-replicas 0 # Без реплик (для теста)

>>> Performing hash slots allocation on 3 nodes...
Master[0] -> Slots 0 - 5460
Master[1] -> Slots 5461 - 10922
Master[2] -> Slots 10923 - 16383
M: 60b4252be86cb8aca34469d10141711df8f2dbaf 172.18.0.5:6379
   slots:[0-5460] (5461 slots) master
M: fb8711dd40ce16e2d0eac1477af998b640c35ff5 172.18.0.4:6379
   slots:[5461-10922] (5462 slots) master
M: 258a71ac7fc15089fb444eedb844abcc65eb19b2 172.18.0.3:6379
   slots:[10923-16383] (5461 slots) master
Can I set the above configuration? (type 'yes' to accept): yes
>>> Nodes configuration updated
>>> Assign a different config epoch to each node
>>> Sending CLUSTER MEET messages to join the cluster
Waiting for the cluster to join

>>> Performing Cluster Check (using node 172.18.0.5:6379)
M: 60b4252be86cb8aca34469d10141711df8f2dbaf 172.18.0.5:6379
   slots:[0-5460] (5461 slots) master
M: fb8711dd40ce16e2d0eac1477af998b640c35ff5 172.18.0.4:6379
   slots:[5461-10922] (5462 slots) master
M: 258a71ac7fc15089fb444eedb844abcc65eb19b2 172.18.0.3:6379
   slots:[10923-16383] (5461 slots) master
[OK] All nodes agree about slots configuration.
>>> Check for open slots...
>>> Check slots coverage...
[OK] All 16384 slots covered.
```
#### **4. Проверка состояния кластера**

```bash
redis-cli cluster nodes

258a71ac7fc15089fb444eedb844abcc65eb19b2 172.18.0.3:6379@16379 master - 0 1746196405813 3 connected 10923-16383
fb8711dd40ce16e2d0eac1477af998b640c35ff5 172.18.0.4:6379@16379 myself,master - 0 0 2 connected 5461-10922
60b4252be86cb8aca34469d10141711df8f2dbaf 172.18.0.5:6379@16379 master - 0 1746196406817 1 connected 0-5460
```

```bash
redis-cli cluster info

cluster_state:ok
cluster_slots_assigned:16384
cluster_slots_ok:16384
cluster_slots_pfail:0
cluster_slots_fail:0
cluster_known_nodes:3
cluster_size:3
cluster_current_epoch:3
cluster_my_epoch:1
cluster_stats_messages_ping_sent:348
cluster_stats_messages_pong_sent:340
cluster_stats_messages_sent:688
cluster_stats_messages_ping_received:338
cluster_stats_messages_pong_received:348
cluster_stats_messages_meet_received:2
cluster_stats_messages_received:688
total_cluster_links_buffer_limit_exceeded:0
```
#### **5. Тестирование кластера**

**Пробуем записать данные:**
```bash
redis-cli -c
127.0.0.1:6379> set string:1 mystrvalue
-> Redirected to slot [11261] located at 172.18.0.3:6379
OK
172.18.0.3:6379> get string:1
"mystrvalue"
```
**Успешно записали и прочитали**

**Останавливаем одну ноду:**
```bash
docker stop redis-node2
```
**Проверяем:**
```bash
redis-cli cluster nodes
b741a7189379c621d7709e6ffe4f8f7119790f86 172.18.0.4:6379@16379 master - 0 1746197978364 2 connected 5461-10922
ff6f14f324d0cf225bbfd35e1268053cf8ac87ca 172.18.0.5:6379@16379 myself,master - 0 0 1 connected 0-5460
2b8aacefe86da7907f2c42705ca5d0d31034bb1c 172.18.0.3:6379@16379 master,fail - 1746197758947 1746197756935 3 connected 10923-16383
```
 **Нода `redis-node2` помечена как `fail`**

**Пробуем прочитать:**
```bash
get string:1
(error) CLUSTERDOWN The cluster is down
```

**Ошибка, кластер в состоянии `down`**
Получаем **ожидаемое** поведение кластера, т.к. фактор репликации 0 `--cluster-replicas 0`
Для дальнейшего расширения можно добавить реплики, изменив фактор репликации `--cluster-replicas 1` при создании кластера, но для этого потребуется ещё 3 ноды редиса.
### **5. Отказоустойчивый Redis Cluster**

#### **1. Создаём `docker-compose.yml` (6 нод: 3 мастера + 3 реплики)**

**Следующий файл развернёт Redis в режиме кластера  из 6 нод: 3 мастера + 3 реплики**:

```yaml
version: '3.8'

services:
  redis-node1:
    image: redis:latest
    container_name: redis-node1
    ports:
      - "7001:6379"
    command: >
      redis-server
      --cluster-enabled yes
      --cluster-config-file nodes-node-1.conf
      --cluster-node-timeout 5000
      --appendonly yes
    volumes:
      - redis-data-1:/data
    networks:
      - redis-cluster-net

  redis-node2:
    image: redis:latest
    container_name: redis-node2
    ports:
      - "7002:6379"
    command: >
      redis-server
      --cluster-enabled yes
      --cluster-config-file nodes-node-2.conf
      --cluster-node-timeout 5000
      --appendonly yes
    volumes:
      - redis-data-2:/data
    networks:
      - redis-cluster-net

  redis-node3:
    image: redis:latest
    container_name: redis-node3
    ports:
      - "7003:6379"
    command: >
      redis-server
      --cluster-enabled yes
      --cluster-config-file nodes-node-3.conf
      --cluster-node-timeout 5000
      --appendonly yes
    volumes:
      - redis-data-3:/data
    networks:
      - redis-cluster-net

  redis-node4:
    image: redis:latest
    container_name: redis-node4
    ports:
      - "7004:6379"
    command: >
      redis-server
      --cluster-enabled yes
      --cluster-config-file nodes-node-4.conf
      --cluster-node-timeout 5000
      --appendonly yes
    volumes:
      - redis-data-4:/data
    networks:
      - redis-cluster-net

  redis-node5:
    image: redis:latest
    container_name: redis-node5
    ports:
      - "7005:6379"
    command: >
      redis-server
      --cluster-enabled yes
      --cluster-config-file nodes-node-5.conf
      --cluster-node-timeout 5000
      --appendonly yes
    volumes:
      - redis-data-5:/data
    networks:
      - redis-cluster-net

  redis-node6:
    image: redis:latest
    container_name: redis-node6
    ports:
      - "7006:6379"
    command: >
      redis-server
      --cluster-enabled yes
      --cluster-config-file nodes-node-6.conf
      --cluster-node-timeout 5000
      --appendonly yes
    volumes:
      - redis-data-6:/data
    networks:
      - redis-cluster-net

    networks:
      - redis-cluster-net

volumes:
  redis-data-1:
  redis-data-2:
  redis-data-3:
  redis-data-4:
  redis-data-5:
  redis-data-6:

networks:
  redis-cluster-net:
    driver: bridge
```

### **2. Запуск и проверка кластера**

**Запускаем кластер:**
```bash
docker-compose up -d

[+] Running 13/13
 ✔ Network cluster2_redis-cluster-net  Created                                                                                                  0.1s
 ✔ Volume "cluster2_redis-data-3"      Created                                                                                                  0.0s
 ✔ Volume "cluster2_redis-data-4"      Created                                                                                                  0.0s
 ✔ Volume "cluster2_redis-data-5"      Created                                                                                                  0.0s
 ✔ Volume "cluster2_redis-data-6"      Created                                                                                                  0.0s
 ✔ Volume "cluster2_redis-data-1"      Created                                                                                                  0.0s
 ✔ Volume "cluster2_redis-data-2"      Created                                                                                                  0.0s
 ✔ Container redis-node4               Started                                                                                                  0.8s
 ✔ Container redis-node2               Started                                                                                                  0.8s
 ✔ Container redis-node6               Started                                                                                                  0.7s
 ✔ Container redis-node1               Started                                                                                                  0.7s
 ✔ Container redis-node5               Started                                                                                                  0.8s
 ✔ Container redis-node3               Started                                                                                                  0.7s
```
#### **3. Инициализация кластера**

Подключаемся к одной из нод и создаём кластер:
```bash
docker exec -it redis-node1 bash
```

Создаём кластер c 1 репликой:
```bash
redis-cli --cluster create \
        redis-node1:6379 \
        redis-node2:6379 \
        redis-node3:6379 \
        redis-node4:6379 \
        redis-node5:6379 \
        redis-node6:6379 \
        --cluster-replicas 1 \
        --cluster-yes
>>> Performing hash slots allocation on 6 nodes...
Master[0] -> Slots 0 - 5460
Master[1] -> Slots 5461 - 10922
Master[2] -> Slots 10923 - 16383
Adding replica redis-node5:6379 to redis-node1:6379
Adding replica redis-node6:6379 to redis-node2:6379
Adding replica redis-node4:6379 to redis-node3:6379
M: ecee59a737d52192034c74c506f5b4dde1b2e723 redis-node1:6379
   slots:[0-5460] (5461 slots) master
M: 2c2b8fdf689b83d38054c006994a553088ea8c45 redis-node2:6379
   slots:[5461-10922] (5462 slots) master
M: dc0aa6429f68162805372d8d1462e85864ed5efd redis-node3:6379
   slots:[10923-16383] (5461 slots) master
S: a39aa8cd40a4c294320d4cd0e4dab531f59051ff redis-node4:6379
   replicates dc0aa6429f68162805372d8d1462e85864ed5efd
S: f6909f589c7a4620206f9a75b60449a61699b10e redis-node5:6379
   replicates ecee59a737d52192034c74c506f5b4dde1b2e723
S: 8090fce2d83b865cddfd0c0998c33e6d431b7c00 redis-node6:6379
   replicates 2c2b8fdf689b83d38054c006994a553088ea8c45
>>> Nodes configuration updated
>>> Assign a different config epoch to each node
>>> Sending CLUSTER MEET messages to join the cluster
Waiting for the cluster to join
...
>>> Performing Cluster Check (using node redis-node1:6379)
M: ecee59a737d52192034c74c506f5b4dde1b2e723 redis-node1:6379
   slots:[0-5460] (5461 slots) master
   1 additional replica(s)
M: dc0aa6429f68162805372d8d1462e85864ed5efd 172.19.0.2:6379
   slots:[10923-16383] (5461 slots) master
   1 additional replica(s)
M: 2c2b8fdf689b83d38054c006994a553088ea8c45 172.19.0.7:6379
   slots:[5461-10922] (5462 slots) master
   1 additional replica(s)
S: 8090fce2d83b865cddfd0c0998c33e6d431b7c00 172.19.0.4:6379
   slots: (0 slots) slave
   replicates 2c2b8fdf689b83d38054c006994a553088ea8c45
S: f6909f589c7a4620206f9a75b60449a61699b10e 172.19.0.5:6379
   slots: (0 slots) slave
   replicates ecee59a737d52192034c74c506f5b4dde1b2e723
S: a39aa8cd40a4c294320d4cd0e4dab531f59051ff 172.19.0.6:6379
   slots: (0 slots) slave
   replicates dc0aa6429f68162805372d8d1462e85864ed5efd
[OK] All nodes agree about slots configuration.
>>> Check for open slots...
>>> Check slots coverage...
[OK] All 16384 slots covered.

```

**Проверяем состояние кластера:**
```bash
redis-cli cluster nodes
ecee59a737d52192034c74c506f5b4dde1b2e723 172.19.0.3:6379@16379 myself,master - 0 0 1 connected 0-5460
dc0aa6429f68162805372d8d1462e85864ed5efd 172.19.0.2:6379@16379 master - 0 1748174607635 3 connected 10923-16383
2c2b8fdf689b83d38054c006994a553088ea8c45 172.19.0.7:6379@16379 master - 0 1748174606626 2 connected 5461-10922
8090fce2d83b865cddfd0c0998c33e6d431b7c00 172.19.0.4:6379@16379 slave 2c2b8fdf689b83d38054c006994a553088ea8c45 0 1748174606000 2 connected
f6909f589c7a4620206f9a75b60449a61699b10e 172.19.0.5:6379@16379 slave ecee59a737d52192034c74c506f5b4dde1b2e723 0 1748174607131 1 connected
a39aa8cd40a4c294320d4cd0e4dab531f59051ff 172.19.0.6:6379@16379 slave dc0aa6429f68162805372d8d1462e85864ed5efd 0 1748174606124 3 connected

```
#### **4. Тестирование отказоустойчивости**

1. **Остановим мастер-ноду:**
```bash
docker stop redis-node1
```

2. **Проверяем кластер:** 
```bash
docker exec -it redis-node4 redis-cli cluster nodes
8090fce2d83b865cddfd0c0998c33e6d431b7c00 172.19.0.4:6379@16379 slave 2c2b8fdf689b83d38054c006994a553088ea8c45 0 1748174790000 2 connected
dc0aa6429f68162805372d8d1462e85864ed5efd 172.19.0.2:6379@16379 master - 0 1748174791245 3 connected 10923-16383
ecee59a737d52192034c74c506f5b4dde1b2e723 172.19.0.3:6379@16379 master,fail - 1748174762038 1748174759522 1 connected
f6909f589c7a4620206f9a75b60449a61699b10e 172.19.0.5:6379@16379 master - 0 1748174790241 7 connected 0-5460
2c2b8fdf689b83d38054c006994a553088ea8c45 172.19.0.7:6379@16379 master - 0 1748174789000 2 connected 5461-10922
a39aa8cd40a4c294320d4cd0e4dab531f59051ff 172.19.0.6:6379@16379 myself,slave dc0aa6429f68162805372d8d1462e85864ed5efd 0 0 3 connected
```
- Реплика (`redis-node4`) стала новым мастером для слотов `0-5460`.
- Старая мастер-нода (`redis-node1`) помечена как `fail`.

3. **Восстанавливаем ноду**
```bash
docker start redis-node1
```

`redis-node1` стала репликой нового мастера (`redis-node4`).
```bash
docker exec -it redis-node4 redis-cli cluster nodes
8090fce2d83b865cddfd0c0998c33e6d431b7c00 172.19.0.4:6379@16379 slave 2c2b8fdf689b83d38054c006994a553088ea8c45 0 1748175061599 2 connected
dc0aa6429f68162805372d8d1462e85864ed5efd 172.19.0.2:6379@16379 master - 0 1748175062209 3 connected 10923-16383
ecee59a737d52192034c74c506f5b4dde1b2e723 172.19.0.3:6379@16379 slave f6909f589c7a4620206f9a75b60449a61699b10e 0 1748175061196 7 connected
f6909f589c7a4620206f9a75b60449a61699b10e 172.19.0.5:6379@16379 master - 0 1748175061700 7 connected 0-5460
2c2b8fdf689b83d38054c006994a553088ea8c45 172.19.0.7:6379@16379 master - 0 1748175061197 2 connected 5461-10922
a39aa8cd40a4c294320d4cd0e4dab531f59051ff 172.19.0.6:6379@16379 myself,slave dc0aa6429f68162805372d8d1462e85864ed5efd 0 0 3 connected
```

4. **Теперь запишем данные:**
```bash
docker exec -it redis-node4 redis-cli -c
127.0.0.1:6379> set string:1 mystrvalue
-> Redirected to slot [11261] located at 172.19.0.2:6379
OK
```
Данные записаны на `master` ноду `redis-node3`

5. **Останавливаем `redis-node3`**
```bash
docker stop redis-node3
```

Проверяем кластер, `redis-node3` - fail:
```bash
docker exec -it redis-node1 redis-cli cluster nodes
ecee59a737d52192034c74c506f5b4dde1b2e723 172.19.0.3:6379@16379 myself,slave f6909f589c7a4620206f9a75b60449a61699b10e 0 0 7 connected
a39aa8cd40a4c294320d4cd0e4dab531f59051ff 172.19.0.6:6379@16379 master - 0 1748176092026 8 connected 10923-16383
8090fce2d83b865cddfd0c0998c33e6d431b7c00 172.19.0.4:6379@16379 slave 2c2b8fdf689b83d38054c006994a553088ea8c45 0 1748176093234 2 connected
f6909f589c7a4620206f9a75b60449a61699b10e 172.19.0.5:6379@16379 master - 0 1748176092000 7 connected 0-5460
2c2b8fdf689b83d38054c006994a553088ea8c45 172.19.0.7:6379@16379 master - 0 1748176092227 2 connected 5461-10922
dc0aa6429f68162805372d8d1462e85864ed5efd 172.19.0.2:6379@16379 master,fail - 1748176065538 1748176063022 3 connected
```

6. **Пробуем прочитать данные:**
```bash
docker exec -it redis-node4 redis-cli -c
127.0.0.1:6379> get string:1
"mystrvalue"
```

**Данные доступны, кластер продолжил работу не смотря на потерю ноды `redis-node3`**
**Нода `redis-node4` стала новым мастером и продолжила отдавать данные.**
