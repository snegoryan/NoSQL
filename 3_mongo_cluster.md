## Домашнее задание 3

MongoDB 2

Цель:
В результате выполнения ДЗ вы настроите реплицирование и шардирование, аутентификацию в кластере и проверите отказоустойчивость.

Описание/Пошаговая инструкция выполнения домашнего задания:
Необходимо:

- построить шардированный кластер из 3 кластерных нод( по 3 инстанса с репликацией) и с кластером конфига(3 инстанса);
- добавить балансировку, нагрузить данными, выбрать хороший ключ шардирования, посмотреть как данные перебалансируются между шардами;
- поронять разные инстансы, посмотреть, что будет происходить, поднять обратно. Описать что произошло.

- настроить аутентификацию и многоролевой доступ;

Формат сдачи - readme с описанием алгоритма действий, результатами и проблемами.

Критерии оценки:
- задание выполнено - 10 баллов
- предложено красивое решение - плюс 2 балла  
    задание со * +5 баллов

Минимальный порог: 10 баллов

---
### **Отчёт о выполнении**

**Разворачиваем кластер MongoDB**
Будес разворачивать шардированный кластер MongoDB с репликацией и конфиг-серверами с помощью Docker Compose. Кластер состоит из:
- 3 шардов (каждый шард - репликасет из 3 нод)
- 3 конфиг-серверов
- 1 маршрутизатора (mongos)
## Шаг 1: Настройка кластера

### 1.1. Docker Compose файл

Создаём файл `docker-compose.yml` с описанием всех сервисов:
```yaml
services:
  # Конфиг серверы
  cfg1:
    image: mongo:latest
    container_name: cfg1
    hostname: cfg1
    command: mongod --configsvr --replSet configrs --bind_ip_all --port 40001
    ports:
      - 40001:40001
    networks:
      - myMongoNetwork
    volumes:
      - ./app/cfg1-data:/data/db
      - ./app/cfg1-config:/data/configdb

  cfg2:
    image: mongo:latest
    container_name: cfg2
    hostname: cfg2
    command: mongod --configsvr --replSet configrs --bind_ip_all --port 40002
    ports:
      - 40002:40002
    networks:
      - myMongoNetwork
    volumes:
      - ./app/cfg2-data:/data/db
      - ./app/cfg2-config:/data/configdb

  cfg3:
    image: mongo:latest
    container_name: cfg3
    hostname: cfg3
    command: mongod --configsvr --replSet configrs --bind_ip_all --port 40003
    ports:
      - 40003:40003
    networks:
      - myMongoNetwork
    volumes:
      - ./app/cfg3-data:/data/db
      - ./app/cfg3-config:/data/configdb

  # Шард 1
  shard1a:
    image: mongo:latest
    container_name: shard1a
    hostname: shard1a
    command: mongod --shardsvr --replSet shard1 --bind_ip_all --port 50001
    ports:
      - 50001:50001
    networks:
      - myMongoNetwork
    volumes:
      - ./app/shard1a-data:/data/db
      - ./app/shard1a-config:/data/configdb

  shard1b:
    image: mongo:latest
    container_name: shard1b
    hostname: shard1b
    command: mongod --shardsvr --replSet shard1 --bind_ip_all --port 50002
    ports:
      - 50002:50002
    networks:
      - myMongoNetwork
    volumes:
      - ./app/shard1b-data:/data/db
      - ./app/shard1b-config:/data/configdb

  shard1c:
    image: mongo:latest
    container_name: shard1c
    hostname: shard1c
    command: mongod --shardsvr --replSet shard1 --bind_ip_all --port 50003
    ports:
      - 50003:50003
    networks:
      - myMongoNetwork
    volumes:
      - ./app/shard1c-data:/data/db
      - ./app/shard1c-config:/data/configdb

  # Шард 2
  shard2a:
    image: mongo:latest
    container_name: shard2a
    hostname: shard2a
    command: mongod --shardsvr --replSet shard2 --bind_ip_all --port 50004
    ports:
      - 50004:50004
    networks:
      - myMongoNetwork
    volumes:
      - ./app/shard2a-data:/data/db
      - ./app/shard2a-config:/data/configdb

  shard2b:
    image: mongo:latest
    container_name: shard2b
    hostname: shard2b
    command: mongod --shardsvr --replSet shard2 --bind_ip_all --port 50005
    ports:
      - 50005:50005
    networks:
      - myMongoNetwork
    volumes:
      - ./app/shard2b-data:/data/db
      - ./app/shard2b-config:/data/configdb

  shard2c:
    image: mongo:latest
    container_name: shard2c
    hostname: shard2c
    command: mongod --shardsvr --replSet shard2 --bind_ip_all --port 50006
    ports:
      - 50006:50006
    networks:
      - myMongoNetwork
    volumes:
      - ./app/shard2c-data:/data/db
      - ./app/shard2c-config:/data/configdb

  # Шард 3
  shard3a:
    image: mongo:latest
    container_name: shard3a
    hostname: shard3a
    command: mongod --shardsvr --replSet shard3 --bind_ip_all --port 50007
    ports:
      - 50007:50007
    networks:
      - myMongoNetwork
    volumes:
      - ./app/shard3a-data:/data/db
      - ./app/shard3a-config:/data/configdb

  shard3b:
    image: mongo:latest
    container_name: shard3b
    hostname: shard3b
    command: mongod --shardsvr --replSet shard3 --bind_ip_all --port 50008
    ports:
      - 50008:50008
    networks:
      - myMongoNetwork
    volumes:
      - ./app/shard3b-data:/data/db
      - ./app/shard3b-config:/data/configdb

  shard3c:
    image: mongo:latest
    container_name: shard3c
    hostname: shard3c
    command: mongod --shardsvr --replSet shard3 --bind_ip_all --port 50009
    ports:
      - 50009:50009
    networks:
      - myMongoNetwork
    volumes:
      - ./app/shard3c-data:/data/db
      - ./app/shard3c-config:/data/configdb

  # Маршрутизатор mongos
  mongos:
    image: mongo:latest
    container_name: mongos
    hostname: mongos
    command: mongos --configdb configrs/cfg1:40001,cfg2:40002,cfg3:40003 --bind_ip_all --port 60000
    ports:
      - 60000:60000
    networks:
      - myMongoNetwork
    depends_on:
      - cfg1
      - cfg2
      - cfg3
      - shard1a
      - shard1b
      - shard1c
      - shard2a
      - shard2b
      - shard2c
      - shard3a
      - shard3b
      - shard3c

networks:
  myMongoNetwork:
    driver: bridge
```

**Стартуем кластер:**
```bash
.\mongodb-sharded-cluster>docker compose up -d
[+] Running 14/14
 ✔ Network mongodb-sharded-cluster_myMongoNetwork  Created 0.0s
 ✔ Container shard3b                               Started 1.2s
 ✔ Container cfg3                                  Started 1.0s
 ✔ Container shard1a                               Started 1.0s
 ✔ Container cfg1                                  Started 1.8s
 ✔ Container shard2c                               Started 1.1s
 ✔ Container shard3a                               Started 1.6s
 ✔ Container shard1c                               Started 0.8s
 ✔ Container shard1b                               Started 1.1s
 ✔ Container shard2b                               Started 1.5s
 ✔ Container shard2a                               Started 1.7s
 ✔ Container shard3c                               Started 1.5s
 ✔ Container cfg2                                  Started 1.6s
 ✔ Container mongos                                Started 1.8s
```

### 1.2. Инициализация репликасетов
После запуска контейнеров (`docker compose up -d`) инициализируем репликасеты:
1. Конфиг-серверы:
```javascript
   rs.initiate({
    _id: "configrs",
    configsvr: true,
    members: [{
            _id: 0,
            host: "cfg1:40001"
        }, {
            _id: 1,
            host: "cfg2:40002"
        }, {
            _id: 2,
            host: "cfg3:40003"
        }
    ]
})
```
2. Шард 1:
```javascript
rs.initiate({
    _id: "shard1",
    members: [{
            _id: 0,
            host: "shard1a:50001"
        }, {
            _id: 1,
            host: "shard1b:50002"
        }, {
            _id: 2,
            host: "shard1c:50003"
        }
    ]
})
```
3. Шард 2:
```javascript
rs.initiate({
    _id: "shard2",
    members: [{
            _id: 0,
            host: "shard2a:50004"
        }, {
            _id: 1,
            host: "shard2b:50005"
        }, {
            _id: 2,
            host: "shard2c:50006"
        }
    ]
})
```
3. Шард 3:
```javascript
rs.initiate({
    _id: "shard3",
    members: [{
            _id: 0,
            host: "shard3a:50007"
        }, {
            _id: 1,
            host: "shard3b:50008"
        }, {
            _id: 2,
            host: "shard3c:50009"
        }
    ]
})
```
### 1.3. Добавление шардов в кластер
Подключимся к `mongos` и добавим шарды:
```bash
[direct: mongos] test> sh.addShard("shard1/shard1a:50001,shard1b:50002,shard1c:50003");
{
  shardAdded: 'shard1',
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1743324673, i: 5 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1743324673, i: 5 })
}
[direct: mongos] test> sh.addShard("shard2/shard2a:50004,shard2b:50005,shard2c:50006");
{
  shardAdded: 'shard2',
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1743324688, i: 24 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1743324688, i: 18 })
}
[direct: mongos] test> sh.addShard("shard3/shard3a:50007,shard3b:50008,shard3c:50009");
{
  shardAdded: 'shard3',
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1743324696, i: 17 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1743324696, i: 17 })
}
```
## Шаг 2: Настройка шардирования и загрузка данных
### 2.1. Включение шардирования для базы данных
```bash
[direct: mongos] test> use testdb;
switched to db testdb
[direct: mongos] testdb> sh.enableSharding("testdb");
{
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1743324823, i: 8 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1743324823, i: 5 })
}
```
### 2.2. Подготовка тестовых данных
Делаем js-скрипт для генерации тестовых данных:
```javascript
for (let i = 1; i <= 10000; i++) {
  db.users.insertOne({
    user_id: i,
    name: `User ${i}`,
    email: `user${i}@example.com`,
    age: Math.floor(Math.random() * 50) + 18,
    created_at: new Date()
  });
  if (i % 1000 === 0) print(`Inserted ${i} documents`);
}
```
Закидываем скрипт в контейнер `mongos`
```bash
./mongodb-sharded-cluster>docker cp insert_data.js mongos:/insert_data.js
Successfully copied 2.05kB to mongos:/insert_data.js
```
### 2.3. Выбор ключа шардирования и создание индекса

Хэш-шардирование будет по полю `user_id`:
```bash
[direct: mongos] testdb> db.createCollection("users");
{ ok: 1 }
[direct: mongos] testdb> db.users.createIndex({user_id: "hashed"});
user_id_hashed
[direct: mongos] testdb> sh.shardCollection("testdb.users", {user_id: "hashed"});
{
  collectionsharded: 'testdb.users',
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1743325117, i: 14 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1743325117, i: 14 })
}
```

**Загружаем данные**
```bash
>docker exec -it mongos mongosh --host mongos:60000 testdb --file /insert_data.js

Inserted 1000 documents
Inserted 2000 documents
Inserted 3000 documents
Inserted 4000 documents
Inserted 5000 documents
Inserted 6000 documents
Inserted 7000 documents
Inserted 8000 documents
Inserted 9000 documents
Inserted 10000 documents
```
### 2.4. Проверка распределения данных
Проверяем, как распределились данные между шардами:
```bash
[direct: mongos] testdb> db.users.getShardDistribution()
Shard shard3 at shard3/shard3a:50007,shard3b:50008,shard3c:50009
{
  data: '378KiB',
  docs: 3350,
  chunks: 1,
  'estimated data per chunk': '378KiB',
  'estimated docs per chunk': 3350
}
---
Shard shard1 at shard1/shard1a:50001,shard1b:50002,shard1c:50003
{
  data: '380KiB',
  docs: 3366,
  chunks: 1,
  'estimated data per chunk': '380KiB',
  'estimated docs per chunk': 3366
}
---
Shard shard2 at shard2/shard2a:50004,shard2b:50005,shard2c:50006
{
  data: '371KiB',
  docs: 3284,
  chunks: 1,
  'estimated data per chunk': '371KiB',
  'estimated docs per chunk': 3284
}
---
Totals
{
  data: '1.1MiB',
  docs: 10000,
  chunks: 3,
  'Shard shard3': [
    '33.5 % data',
    '33.5 % docs in cluster',
    '115B avg obj size on shard'
  ],
  'Shard shard1': [
    '33.65 % data',
    '33.66 % docs in cluster',
    '115B avg obj size on shard'
  ],
  'Shard shard2': [
    '32.83 % data',
    '32.84 % docs in cluster',
    '115B avg obj size on shard'
  ]
}
```
**Данные распределены равномерно по трём шардам.**
## Шаг 3: Тестирование отказоустойчивости
### 3.1. Остановка первичной ноды шарда 1
```bash
docker stop shard1a
```
Проверяем
```bash
docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED        STATUS          PORTS                                 NAMES
a8076f9b07eb   mongo:latest   "docker-entrypoint.s…"   19 hours ago   Up 26 minutes   27017/tcp, 0.0.0.0:60000->60000/tcp   mongos
8c2b3949d96f   mongo:latest   "docker-entrypoint.s…"   19 hours ago   Up 26 minutes   27017/tcp, 0.0.0.0:50007->50007/tcp   shard3a
8c91aa375579   mongo:latest   "docker-entrypoint.s…"   19 hours ago   Up 26 minutes   27017/tcp, 0.0.0.0:50002->50002/tcp   shard1b
642a090dc4e1   mongo:latest   "docker-entrypoint.s…"   19 hours ago   Up 26 minutes   27017/tcp, 0.0.0.0:40002->40002/tcp   cfg2
6aa845585528   mongo:latest   "docker-entrypoint.s…"   19 hours ago   Up 26 minutes   27017/tcp, 0.0.0.0:50008->50008/tcp   shard3b
1b24af2878a2   mongo:latest   "docker-entrypoint.s…"   19 hours ago   Up 26 minutes   27017/tcp, 0.0.0.0:50006->50006/tcp   shard2c
a2b03a2c196b   mongo:latest   "docker-entrypoint.s…"   19 hours ago   Up 26 minutes   27017/tcp, 0.0.0.0:50009->50009/tcp   shard3c
fed1ab86c880   mongo:latest   "docker-entrypoint.s…"   19 hours ago   Up 26 minutes   27017/tcp, 0.0.0.0:40003->40003/tcp   cfg3
01c117553049   mongo:latest   "docker-entrypoint.s…"   19 hours ago   Up 26 minutes   27017/tcp, 0.0.0.0:50004->50004/tcp   shard2a
c3a59856f123   mongo:latest   "docker-entrypoint.s…"   19 hours ago   Up 26 minutes   27017/tcp, 0.0.0.0:50003->50003/tcp   shard1c
df21598769b7   mongo:latest   "docker-entrypoint.s…"   19 hours ago   Up 26 minutes   27017/tcp, 0.0.0.0:40001->40001/tcp   cfg1
54c89912e17f   mongo:latest   "docker-entrypoint.s…"   19 hours ago   Up 26 minutes   27017/tcp, 0.0.0.0:50005->50005/tcp   shard2b
```
Шард shard1a остановлен.
### 3.2. Проверка репликации

Подключился к одной из оставшихся нод шарда 1:
```bash
docker exec -it shard1b mongosh --host shard1b:50002 --eval 'rs.status()'
{
  set: 'shard1',
  date: ISODate('2025-03-30T10:29:54.275Z'),
  myState: 1,
  term: Long('4'),
  syncSourceHost: '',
  syncSourceId: -1,
  heartbeatIntervalMillis: Long('2000'),
  majorityVoteCount: 2,
  writeMajorityCount: 2,
  votingMembersCount: 3,
  writableVotingMembersCount: 3,
  optimes: {
    lastCommittedOpTime: { ts: Timestamp({ t: 1743330588, i: 1 }), t: Long('4') },
    lastCommittedWallTime: ISODate('2025-03-30T10:29:48.899Z'),
    readConcernMajorityOpTime: { ts: Timestamp({ t: 1743330588, i: 1 }), t: Long('4') },
    appliedOpTime: { ts: Timestamp({ t: 1743330588, i: 1 }), t: Long('4') },
    durableOpTime: { ts: Timestamp({ t: 1743330588, i: 1 }), t: Long('4') },
    writtenOpTime: { ts: Timestamp({ t: 1743330588, i: 1 }), t: Long('4') },
    lastAppliedWallTime: ISODate('2025-03-30T10:29:48.899Z'),
    lastDurableWallTime: ISODate('2025-03-30T10:29:48.899Z'),
    lastWrittenWallTime: ISODate('2025-03-30T10:29:48.899Z')
  },
  lastStableRecoveryTimestamp: Timestamp({ t: 1743330578, i: 1 }),
  electionCandidateMetrics: {
    lastElectionReason: 'stepUpRequestSkipDryRun',
    lastElectionDate: ISODate('2025-03-30T10:25:28.886Z'),
    electionTerm: Long('4'),
    lastCommittedOpTimeAtElection: { ts: Timestamp({ t: 1743330321, i: 1 }), t: Long('3') },
    lastSeenWrittenOpTimeAtElection: { ts: Timestamp({ t: 1743330321, i: 1 }), t: Long('3') },
    lastSeenOpTimeAtElection: { ts: Timestamp({ t: 1743330321, i: 1 }), t: Long('3') },
    numVotesNeeded: 2,
    priorityAtElection: 1,
    electionTimeoutMillis: Long('10000'),
    priorPrimaryMemberId: 0,
    numCatchUpOps: Long('0'),
    newTermStartDate: ISODate('2025-03-30T10:25:28.900Z'),
    wMajorityWriteAvailabilityDate: ISODate('2025-03-30T10:25:28.915Z')
  },
  electionParticipantMetrics: {
    votedForCandidate: true,
    electionTerm: Long('3'),
    lastVoteDate: ISODate('2025-03-30T10:01:01.739Z'),
    electionCandidateMemberId: 0,
    voteReason: '',
    lastWrittenOpTimeAtElection: { ts: Timestamp({ t: 1743328254, i: 1 }), t: Long('2') },
    maxWrittenOpTimeInSet: { ts: Timestamp({ t: 1743328254, i: 1 }), t: Long('2') },
    lastAppliedOpTimeAtElection: { ts: Timestamp({ t: 1743328254, i: 1 }), t: Long('2') },
    maxAppliedOpTimeInSet: { ts: Timestamp({ t: 1743328254, i: 1 }), t: Long('2') },
    priorityAtElection: 1
  },
  members: [
    {
      _id: 0,
      name: 'shard1a:50001',
      health: 0,
      state: 8,
      stateStr: '(not reachable/healthy)',
      uptime: 0,
      optime: { ts: Timestamp({ t: 0, i: 0 }), t: Long('-1') },
      optimeDurable: { ts: Timestamp({ t: 0, i: 0 }), t: Long('-1') },
      optimeWritten: { ts: Timestamp({ t: 0, i: 0 }), t: Long('-1') },
      optimeDate: ISODate('1970-01-01T00:00:00.000Z'),
      optimeDurableDate: ISODate('1970-01-01T00:00:00.000Z'),
      optimeWrittenDate: ISODate('1970-01-01T00:00:00.000Z'),
      lastAppliedWallTime: ISODate('2025-03-30T10:25:28.900Z'),
      lastDurableWallTime: ISODate('2025-03-30T10:25:28.900Z'),
      lastWrittenWallTime: ISODate('2025-03-30T10:25:28.900Z'),
      lastHeartbeat: ISODate('2025-03-30T10:29:42.388Z'),
      lastHeartbeatRecv: ISODate('2025-03-30T10:25:37.407Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: "Couldn't get a connection within the time limit",
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      configVersion: 1,
      configTerm: 4
    },
    {
      _id: 1,
      name: 'shard1b:50002',
      health: 1,
      state: 1,
      stateStr: 'PRIMARY',
      uptime: 1792,
      optime: { ts: Timestamp({ t: 1743330588, i: 1 }), t: Long('4') },
      optimeDate: ISODate('2025-03-30T10:29:48.000Z'),
      optimeWritten: { ts: Timestamp({ t: 1743330588, i: 1 }), t: Long('4') },
      optimeWrittenDate: ISODate('2025-03-30T10:29:48.000Z'),
      lastAppliedWallTime: ISODate('2025-03-30T10:29:48.899Z'),
      lastDurableWallTime: ISODate('2025-03-30T10:29:48.899Z'),
      lastWrittenWallTime: ISODate('2025-03-30T10:29:48.899Z'),
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      electionTime: Timestamp({ t: 1743330328, i: 2 }),
      electionDate: ISODate('2025-03-30T10:25:28.000Z'),
      configVersion: 1,
      configTerm: 4,
      self: true,
      lastHeartbeatMessage: ''
    },
    {
      _id: 2,
      name: 'shard1c:50003',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 1743,
      optime: { ts: Timestamp({ t: 1743330588, i: 1 }), t: Long('4') },
      optimeDurable: { ts: Timestamp({ t: 1743330588, i: 1 }), t: Long('4') },
      optimeWritten: { ts: Timestamp({ t: 1743330588, i: 1 }), t: Long('4') },
      optimeDate: ISODate('2025-03-30T10:29:48.000Z'),
      optimeDurableDate: ISODate('2025-03-30T10:29:48.000Z'),
      optimeWrittenDate: ISODate('2025-03-30T10:29:48.000Z'),
      lastAppliedWallTime: ISODate('2025-03-30T10:29:48.899Z'),
      lastDurableWallTime: ISODate('2025-03-30T10:29:48.899Z'),
      lastWrittenWallTime: ISODate('2025-03-30T10:29:48.899Z'),
      lastHeartbeat: ISODate('2025-03-30T10:29:52.942Z'),
      lastHeartbeatRecv: ISODate('2025-03-30T10:29:52.942Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'shard1b:50002',
      syncSourceId: 1,
      infoMessage: '',
      configVersion: 1,
      configTerm: 4
    }
  ],
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1743330589, i: 1 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1743330588, i: 1 })
}
```
Нода shard1b стала primary.
### 3.3. Проверка работы кластера
Попытка записи через `mongos`:
```bash
db.users.insertOne({user_id: 10001, name: "Test User", email: "testuser@test.com", age: 30});
{
  acknowledged: true,
  insertedId: ObjectId('67e91e645886e65c62e9f85f')
}
```
Запись успешная, кластер продолжает работать.
### 3.4. Восстановление ноды

```bash
docker start shard1a
```
Проверили, что нода shard1a жива и успешно присоединилась к кластеру:
```bash
docker exec -it shard1b mongosh --host shard1b:50002 --eval 'rs.status()'
{
  set: 'shard1',
  date: ISODate('2025-03-30T10:40:09.071Z'),
  myState: 1,
  term: Long('4'),
  syncSourceHost: '',
  syncSourceId: -1,
  heartbeatIntervalMillis: Long('2000'),
  majorityVoteCount: 2,
  writeMajorityCount: 2,
  votingMembersCount: 3,
  writableVotingMembersCount: 3,
  optimes: {
    lastCommittedOpTime: { ts: Timestamp({ t: 1743331208, i: 1 }), t: Long('4') },
    lastCommittedWallTime: ISODate('2025-03-30T10:40:08.898Z'),
    readConcernMajorityOpTime: { ts: Timestamp({ t: 1743331208, i: 1 }), t: Long('4') },
    appliedOpTime: { ts: Timestamp({ t: 1743331208, i: 1 }), t: Long('4') },
    durableOpTime: { ts: Timestamp({ t: 1743331208, i: 1 }), t: Long('4') },
    writtenOpTime: { ts: Timestamp({ t: 1743331208, i: 1 }), t: Long('4') },
    lastAppliedWallTime: ISODate('2025-03-30T10:40:08.898Z'),
    lastDurableWallTime: ISODate('2025-03-30T10:40:08.898Z'),
    lastWrittenWallTime: ISODate('2025-03-30T10:40:08.898Z')
  },
  lastStableRecoveryTimestamp: Timestamp({ t: 1743331178, i: 1 }),
  electionCandidateMetrics: {
    lastElectionReason: 'stepUpRequestSkipDryRun',
    lastElectionDate: ISODate('2025-03-30T10:25:28.886Z'),
    electionTerm: Long('4'),
    lastCommittedOpTimeAtElection: { ts: Timestamp({ t: 1743330321, i: 1 }), t: Long('3') },
    lastSeenWrittenOpTimeAtElection: { ts: Timestamp({ t: 1743330321, i: 1 }), t: Long('3') },
    lastSeenOpTimeAtElection: { ts: Timestamp({ t: 1743330321, i: 1 }), t: Long('3') },
    numVotesNeeded: 2,
    priorityAtElection: 1,
    electionTimeoutMillis: Long('10000'),
    priorPrimaryMemberId: 0,
    numCatchUpOps: Long('0'),
    newTermStartDate: ISODate('2025-03-30T10:25:28.900Z'),
    wMajorityWriteAvailabilityDate: ISODate('2025-03-30T10:25:28.915Z')
  },
  electionParticipantMetrics: {
    votedForCandidate: true,
    electionTerm: Long('3'),
    lastVoteDate: ISODate('2025-03-30T10:01:01.739Z'),
    electionCandidateMemberId: 0,
    voteReason: '',
    lastWrittenOpTimeAtElection: { ts: Timestamp({ t: 1743328254, i: 1 }), t: Long('2') },
    maxWrittenOpTimeInSet: { ts: Timestamp({ t: 1743328254, i: 1 }), t: Long('2') },
    lastAppliedOpTimeAtElection: { ts: Timestamp({ t: 1743328254, i: 1 }), t: Long('2') },
    maxAppliedOpTimeInSet: { ts: Timestamp({ t: 1743328254, i: 1 }), t: Long('2') },
    priorityAtElection: 1
  },
  members: [
    {
      _id: 0,
      name: 'shard1a:50001',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 83,
      optime: { ts: Timestamp({ t: 1743331198, i: 1 }), t: Long('4') },
      optimeDurable: { ts: Timestamp({ t: 1743331198, i: 1 }), t: Long('4') },
      optimeWritten: { ts: Timestamp({ t: 1743331198, i: 1 }), t: Long('4') },
      optimeDate: ISODate('2025-03-30T10:39:58.000Z'),
      optimeDurableDate: ISODate('2025-03-30T10:39:58.000Z'),
      optimeWrittenDate: ISODate('2025-03-30T10:39:58.000Z'),
      lastAppliedWallTime: ISODate('2025-03-30T10:40:08.898Z'),
      lastDurableWallTime: ISODate('2025-03-30T10:40:08.898Z'),
      lastWrittenWallTime: ISODate('2025-03-30T10:40:08.898Z'),
      lastHeartbeat: ISODate('2025-03-30T10:40:07.131Z'),
      lastHeartbeatRecv: ISODate('2025-03-30T10:40:07.646Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'shard1c:50003',
      syncSourceId: 2,
      infoMessage: '',
      configVersion: 1,
      configTerm: 4
    },
    {
      _id: 1,
      name: 'shard1b:50002',
      health: 1,
      state: 1,
      stateStr: 'PRIMARY',
      uptime: 2407,
      optime: { ts: Timestamp({ t: 1743331208, i: 1 }), t: Long('4') },
      optimeDate: ISODate('2025-03-30T10:40:08.000Z'),
      optimeWritten: { ts: Timestamp({ t: 1743331208, i: 1 }), t: Long('4') },
      optimeWrittenDate: ISODate('2025-03-30T10:40:08.000Z'),
      lastAppliedWallTime: ISODate('2025-03-30T10:40:08.898Z'),
      lastDurableWallTime: ISODate('2025-03-30T10:40:08.898Z'),
      lastWrittenWallTime: ISODate('2025-03-30T10:40:08.898Z'),
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      electionTime: Timestamp({ t: 1743330328, i: 2 }),
      electionDate: ISODate('2025-03-30T10:25:28.000Z'),
      configVersion: 1,
      configTerm: 4,
      self: true,
      lastHeartbeatMessage: ''
    },
    {
      _id: 2,
      name: 'shard1c:50003',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 2357,
      optime: { ts: Timestamp({ t: 1743331198, i: 1 }), t: Long('4') },
      optimeDurable: { ts: Timestamp({ t: 1743331198, i: 1 }), t: Long('4') },
      optimeWritten: { ts: Timestamp({ t: 1743331198, i: 1 }), t: Long('4') },
      optimeDate: ISODate('2025-03-30T10:39:58.000Z'),
      optimeDurableDate: ISODate('2025-03-30T10:39:58.000Z'),
      optimeWrittenDate: ISODate('2025-03-30T10:39:58.000Z'),
      lastAppliedWallTime: ISODate('2025-03-30T10:40:08.898Z'),
      lastDurableWallTime: ISODate('2025-03-30T10:40:08.898Z'),
      lastWrittenWallTime: ISODate('2025-03-30T10:40:08.898Z'),
      lastHeartbeat: ISODate('2025-03-30T10:40:07.094Z'),
      lastHeartbeatRecv: ISODate('2025-03-30T10:40:07.093Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'shard1b:50002',
      syncSourceId: 1,
      infoMessage: '',
      configVersion: 1,
      configTerm: 4
    }
  ],
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1743331208, i: 1 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1743331208, i: 1 })
}
```
## Шаг 4: Настройка аутентификации 
### 4.1. Создание пользователей
Создадим пользователя dbAdmin.
Выполняем на ноде `mongos`:
```bash
use admin;

db.createUser({
  user: "dbAdmin",
  pwd: "admin123",
  roles: [{role: "dbAdminAnyDatabase", db: "admin"}]
});
```
### 4.2. Включение аутентификации
Создаём replica.key
```bash
openssl rand -base64 756 > replica.key
```
Обновим docker-compose.yml, добавив
- `--auth` и `--keyFile /replica.key` к командам `mongod` и `mongos`.
- `chmod 400 /replica.key` перед запуском `mongod` и `mongos`.
- определим `volume` с общим `/replica.key`
Пример конфигурации 1 ноды, остальные настроены аналогичным образом:
```yaml
services:
  # Конфиг серверы
  cfg1:
    image: mongo:latest
    container_name: cfg1
    hostname: cfg1
    command: sh -c "chmod 400 /replica.key && exec mongod  --auth --keyFile /replica.key --configsvr --replSet configrs --bind_ip_all --port 40001"
    ports:
      - 40001:40001
    networks:
      - myMongoNetwork
    volumes:
      - ./app/cfg1-data:/data/db
      - ./app/cfg1-config:/data/configdb
      - ./replica.key:/replica.key
```
### 4.3. Подключение к mongos роутеру с аутентификацией
Пробуем подключиться без пароля
```bash
mongosh --host mongos:60000
Current Mongosh Log ID: 67f14b170a4a2251336b140a
Connecting to:          mongodb://mongos:60000/?directConnection=true&appName=mongosh+2.4.2
MongoNetworkError: connect ECONNREFUSED 172.19.0.14:60000
```
Получаем ошибку `MongoNetworkError: connect ECONNREFUSED 172.19.0.14:60000`
Теперь подключаемся с логином\паролем:
```bash
mongosh --host mongos:60000 -u "dbAdmin" -p --authenticationDatabase "admin"
Enter password: ********
Current Mongosh Log ID: 67f14b5b479ef8697f6b140a
Connecting to:          mongodb://<credentials>@mongos:60000/?directConnection=true&authSource=admin&appName=mongosh+2.4.2
Using MongoDB:          8.0.6
Using Mongosh:          2.4.2

For mongosh info see: https://www.mongodb.com/docs/mongodb-shell/

------
   The server generated these startup warnings when booting
   2025-04-05T15:23:49.348+00:00: Access control is not enabled for the database. Read and write access to data and configuration is unrestricted
------

[direct: mongos] test>
```
**Успешный логин.**
## Шаг 5: Cоздание MongoDB кластера в трех разных ЦОДах с тестированием отказоустойчивочти

## Архитектура кластера

Представим кластер MongoDB, развернутый в трех разных дата-центрах:

- **ЦОД 1** (Москва):
    - Конфиг-сервер: cfg1
    - Шард1 (репликасет): shard1a (PRIMARY), shard1b (SECONDARY)
    - Маршрутизатор: mongos1
- **ЦОД 2** (Санкт-Петербург):
    - Конфиг-сервер: cfg2
    - Шард2 (репликасет): shard2a (PRIMARY), shard2b (SECONDARY)
    - Маршрутизатор: mongos2
- **ЦОД 3** (Екатеринбург):
    - Конфиг-сервер: cfg3
    - Шард3 (репликасет): shard3a (PRIMARY), shard3b (SECONDARY)
    - Маршрутизатор: mongos3

## 5.1 Создадим docker-compose с новой архитектурой и разделением по ЦОД

```yaml
networks:
  moscow:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: moscow
  spb:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: spb
  ekb:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: ekb
  sharedNetwork:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: sharedNetwork

services:
  # Конфиг серверы в разных ЦОДах
  cfg1:
    image: mongo:latest
    container_name: cfg1
    hostname: cfg1
    command: mongod --configsvr --replSet configrs --bind_ip_all --port 40001
    ports:
      - 40001:40001
    networks:
      - sharedNetwork
      - moscow
    volumes:
      - ./app/cfg1-data:/data/db
      - ./app/cfg1-config:/data/configdb

  cfg2:
    image: mongo:latest
    container_name: cfg2
    hostname: cfg2
    command: mongod --configsvr --replSet configrs --bind_ip_all --port 40002
    ports:
      - 40002:40002
    networks:
      - sharedNetwork
      - spb
    volumes:
      - ./app/cfg2-data:/data/db
      - ./app/cfg2-config:/data/configdb   

  cfg3:
    image: mongo:latest
    container_name: cfg3
    hostname: cfg3
    command: mongod --configsvr --replSet configrs --bind_ip_all --port 40003
    ports:
      - 40003:40003
    networks:
      - sharedNetwork
      - ekb
    volumes:
      - ./app/cfg3-data:/data/db
      - ./app/cfg3-config:/data/configdb     

  # Шард 1 (Москва)
  shard1a:
    image: mongo:latest
    container_name: shard1a
    hostname: shard1a
    command: mongod --shardsvr --replSet shard1 --bind_ip_all --port 50001
    ports:
      - 50001:50001
    networks:
      - sharedNetwork
      - moscow
    volumes:
      - ./app/shard1a-data:/data/db
      - ./app/shard1a-config:/data/configdb     

  shard1b:
    image: mongo:latest
    container_name: shard1b
    hostname: shard1b
    command: mongod --shardsvr --replSet shard1 --bind_ip_all --port 50002
    ports:
      - 50002:50002
    networks:
      - sharedNetwork
      - moscow
    volumes:
      - ./app/shard1b-data:/data/db
      - ./app/shard1b-config:/data/configdb
      
  # Шард 2 (СПб)
  shard2a:
    image: mongo:latest
    container_name: shard2a
    hostname: shard2a
    command: mongod --shardsvr --replSet shard2 --bind_ip_all --port 50003
    ports:
      - 50003:50003
    networks:
      - sharedNetwork
      - spb
    volumes:
      - ./app/shard2a-data:/data/db
      - ./app/shard2a-config:/data/configdb

  shard2b:
    image: mongo:latest
    container_name: shard2b
    hostname: shard2b
    command: mongod --shardsvr --replSet shard2 --bind_ip_all --port 50004
    ports:
      - 50004:50004
    networks:
      - sharedNetwork
      - spb
    volumes:
      - ./app/shard2b-data:/data/db
      - ./app/shard2b-config:/data/configdb

  # Шард 3 (Екатеринбург)
  shard3a:
    image: mongo:latest
    container_name: shard3a
    hostname: shard3a
    command: mongod --shardsvr --replSet shard3 --bind_ip_all --port 50005
    ports:
      - 50005:50005
    networks:
      - sharedNetwork
      - ekb
    volumes:
      - ./app/shard3a-data:/data/db
      - ./app/shard3a-config:/data/configdb

  shard3b:
    image: mongo:latest
    container_name: shard3b
    hostname: shard3b
    command: mongod --shardsvr --replSet shard3 --bind_ip_all --port 50006
    ports:
      - 50006:50006
    networks:
      - sharedNetwork
      - ekb
    volumes:
      - ./app/shard3b-data:/data/db
      - ./app/shard3b-config:/data/configdb

  # Маршрутизаторы в каждом ЦОДЕ
  mongos1:
    image: mongo:latest
    container_name: mongos1
    hostname: mongos1
    command: mongos --configdb configrs/cfg1:40001,cfg2:40002,cfg3:40003 --bind_ip_all --port 60001
    networks:
      - sharedNetwork
      - moscow
    ports:
      - 60001:60001
    volumes:
      - ./app/mongos1-data:/data/db
      - ./app/mongos1-config:/data/configdb
      
    depends_on:
      - cfg1
      - cfg2
      - cfg3

  mongos2:
    image: mongo:latest
    container_name: mongos2
    hostname: mongos2
    command: mongos --configdb configrs/cfg1:40001,cfg2:40002,cfg3:40003 --bind_ip_all --port 60002
    networks:
      - sharedNetwork
      - spb
    ports:
      - 60002:60002
    volumes:
      - ./app/mongos2-data:/data/db
      - ./app/mongos2-config:/data/configdb
      
  mongos3:
    image: mongo:latest
    container_name: mongos3
    hostname: mongos3
    command: mongos --configdb configrs/cfg1:40001,cfg2:40002,cfg3:40003 --bind_ip_all --port 60003
    networks:
      - sharedNetwork
      - ekb
    ports:
      - 60003:60003
    volumes:
      - ./app/mongos3-data:/data/db
      - ./app/mongos3-config:/data/configdb
```

# 5.2 Запуск и инициализация

**Стартуем docker-compose**
`docker-compose up -d`

**Инициализируем конфиг серверы**
```bash
docker-compose exec cfg1 mongosh --host cfg1:40001 --eval 
rs.initiate({
  _id: "configrs",
  configsvr: true,
  members: [
    {_id: 0, host: "cfg1:40001"},
    {_id: 1, host: "cfg2:40002"},
    {_id: 2, host: "cfg3:40003"}
  ]
})
```

**Инициализируем шарды**
```bash
docker-compose exec shard1a mongosh --host shard1a:50001 --eval 
rs.initiate({
  _id: "shard1",
  members: [
    {_id: 0, host: "shard1a:50001", priority: 3},
    {_id: 1, host: "shard1b:50002", priority: 2}
  ]
})

docker-compose exec shard2a mongosh --host shard2a:50003 --eval 
rs.initiate({
  _id: "shard2",
  members: [
    {_id: 0, host: "shard2a:50003", priority: 3},
    {_id: 1, host: "shard2b:50004", priority: 2}
  ]
})

docker-compose exec shard3a mongosh --host shard3a:50005 --eval 
rs.initiate({
  _id: "shard3",
  members: [
    {_id: 0, host: "shard3a:50005", priority: 3},
    {_id: 1, host: "shard3b:50006", priority: 2}
  ]
})
```
**Добавляем шарды в кластер**
```bash
docker-compose exec mongos1 mongosh --host mongos1:60001 --eval 
sh.addShard("shard1/shard1a:50001,shard1b:50002");
sh.addShard("shard2/shard2a:50003,shard2b:50004");
sh.addShard("shard3/shard3a:50005,shard3b:50006");
```
**Включаем шардирование для тестовой БД**
```bash
docker-compose exec mongos1 mongosh --host mongos1:60001 --eval 
use testdb;
sh.enableSharding("testdb");
db.createCollection("splitBrainTest");
sh.shardCollection("testdb.splitBrainTest", {_id: "hashed"});
```
**Проверяем статусы**
```bash
docker-compose exec mongos1 mongosh --host mongos1:60001 --eval 
sh.status();
docker-compose exec mongos2 mongosh --host mongos2:60002 --eval 
sh.status();
docker-compose exec mongos3 mongosh --host mongos3:60003 --eval 
sh.status();
```
# 5.3 Тест отвала сети

**Эмулируем отвал ЦОД в СПБ и остальными ЦОДами**
```bash
docker network disconnect mongo-split_sharedNetwork mongos2
docker network disconnect mongo-split_sharedNetwork shard2a
docker network disconnect mongo-split_sharedNetwork shard2b
```

**Пишем данные в Москве** - успешная запись
```bash
docker-compose exec mongos1 mongosh --host mongos1:60001 testdb --eval 
db.splitBrainTest.insertOne({location: "Moscow", time: new Date()});
{
  acknowledged: true,
  insertedId: ObjectId('67f2607de6c996facd6b140b')
}
```
**Пишем данные в СПБ** - ошибка
```bash
docker-compose exec mongos2 mongosh --host mongos2:60002 testdb --eval 
db.splitBrainTest.insertOne({location: "Spb", time: new Date()});
MongoServerError: Write results unavailable from failing to target a host in the shard shard3 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard3
```
**Проверяем статус шарда2 - ошибка**
```bash
sh.status()
MongoServerError[FailedToSatisfyReadPreference]: Encountered non-retryable error during query :: caused by :: Could not find host matching read preference { mode: "primary" } for set configrs
```
**Пишем данные в ЕКБ** - успешная запись
```bash
docker-compose exec mongos3 mongosh --host mongos3:60003 testdb --eval 
db.splitBrainTest.insertOne({location: "Ekb", time: new Date()});
{
  acknowledged: true,
  insertedId: ObjectId('67f26211258ce8c19b6b140b')
}
```

**Пробуем прочитать данные** - ошибка
```bash
# Проверяем данные
docker-compose exec mongos1 mongosh --host mongos1:60001 testdb --eval 
db.splitBrainTest.find().toArray();
MongoServerError[FailedToSatisfyReadPreference]: Encountered non-retryable error during query :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard2
```
**Восстанавливаем сеть**
```bash
docker network connect mongo-split_sharedNetwork mongos2
docker network connect mongo-split_sharedNetwork shard2a
docker network connect mongo-split_sharedNetwork shard2b
```

**Проверяем данные**
```bash
docker-compose exec mongos1 mongosh --host mongos1:60001 testdb --eval 
db.splitBrainTest.find().toArray();
[
  {
    _id: ObjectId('67f2607de6c996facd6b140b'),
    location: 'Moscow',
    time: ISODate('2025-04-06T11:07:41.235Z')
  },
  {
    _id: ObjectId('67f26211258ce8c19b6b140b'),
    location: 'Ekb',
    time: ISODate('2025-04-06T11:14:25.881Z')
  }
]
```

**Пробуем сделать запись в СПБ** - успех
```bash
docker-compose exec mongos2 mongosh --host mongos2:60002 testdb --eval 
db.splitBrainTest.insertOne({location: "Spb", time: new Date()});
{
  acknowledged: true,
  insertedId: ObjectId('67f263caa2e14c0cc26b140b')
}
```

## 5.4 Создадим docker-compose с новой архитектурой и разделим по ЦОД репликасеты

Отредактируем `yaml` добавим 1 реплику и разделим реплики по трём ЦОДП
Пример шарда с репликами по разным цодам, остальные шарды сделаны по подобию:
```yaml
# Москва
shard1a:
    image: mongo:latest
    container_name: shard1a
    hostname: shard1a
    command: mongod --shardsvr --replSet shard1 --bind_ip_all --port 50001
    ports:
      - 50001:50001
    networks:
      - sharedNetwork
      - moscow
    volumes:
      - ./app/shard1a-data:/data/db
      - ./app/shard1a-config:/data/configdb     
# Питер
  shard1b:
    image: mongo:latest
    container_name: shard1b
    hostname: shard1b
    command: mongod --shardsvr --replSet shard1 --bind_ip_all --port 50002
    ports:
      - 50002:50002
    networks:
      - sharedNetwork
      - spb
    volumes:
      - ./app/shard1b-data:/data/db
      - ./app/shard1b-config:/data/configdb
 # Екат     
  shard1c:
    image: mongo:latest
    container_name: shard1c
    hostname: shard1c
    command: mongod --shardsvr --replSet shard1 --bind_ip_all --port 50003
    ports:
      - 50003:50003
    networks:
      - sharedNetwork
      - spb
    volumes:
      - ./app/shard1c-data:/data/db
      - ./app/shard1c-config:/data/configdb
```
## 5.5 Запуск и инициализация кластера

```bash
# Запускаем контейнеры
docker-compose up -d

# Инициализируем конфиг серверы
docker-compose exec cfg1 mongosh --host cfg1:40001 --eval 
rs.initiate({
  _id: "configrs",
  configsvr: true,
  members: [
    {_id: 0, host: "cfg1:40001"},
    {_id: 1, host: "cfg2:40002"},
    {_id: 2, host: "cfg3:40003"}
  ]
});
exit;

# Инициализируем шарды
docker-compose exec shard1a mongosh --host shard1a:50001 --eval 
rs.initiate({
  _id: "shard1",
  members: [
    {_id: 0, host: "shard1a:50001", priority: 3},
    {_id: 1, host: "shard1b:50002", priority: 2},
	{_id: 2, host: "shard1c:50003", priority: 1}
  ]
});
exit;

docker-compose exec shard2a mongosh --host shard2a:50004 --eval 
rs.initiate({
  _id: "shard2",
  members: [
    {_id: 0, host: "shard2a:50004", priority: 3},
    {_id: 1, host: "shard2b:50005", priority: 2},
    {_id: 2, host: "shard2c:50006", priority: 1}
  ]
});
exit;

docker-compose exec shard3a mongosh --host shard3a:50007 --eval 
rs.initiate({
  _id: "shard3",
  members: [
    {_id: 0, host: "shard3a:50007", priority: 3},
    {_id: 1, host: "shard3b:50008", priority: 2},
    {_id: 2, host: "shard3c:50009", priority: 1}
  ]
});
exit;

# Добавляем шарды в кластер
docker-compose exec mongos1 mongosh --host mongos1:60001 --eval 
sh.addShard("shard1/shard1a:50001,shard1b:50002,shard1c:50003");
sh.addShard("shard2/shard2a:50004,shard2b:50005,shard2c:50006");
sh.addShard("shard3/shard3a:50007,shard3b:50008,shard3c:50009");
exit; 

# Включаем шардирование для тестовой БД
docker-compose exec mongos1 mongosh --host mongos1:60001 --eval 
use testdb;
sh.enableSharding("testdb");
db.createCollection("splitBrainTest");
sh.shardCollection("testdb.splitBrainTest", {_id: "hashed"});
```
## 5.6 Тест отвала ЦОД
```bash
# Эмулируем отвал ЦОД в МСК
docker network disconnect mongo-avail_sharedNetwork mongos1
docker network disconnect mongo-avail_sharedNetwork shard1a
docker network disconnect mongo-avail_sharedNetwork shard2a
docker network disconnect mongo-avail_sharedNetwork shard3a

# Пишем данные в Москве - ошибка
docker-compose exec mongos1 mongosh --host mongos1:60001 testdb --eval 
db.splitBrainTest.insertOne({location: "Moscow", time: new Date()});
MongoServerError: Write results unavailable from failing to target a host in the shard shard3 :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard3

# Пишем данные в СПБ - успех
docker-compose exec mongos2 mongosh --host mongos2:60002 testdb --eval 
db.splitBrainTest.insertOne({location: "Spb", time: new Date()});
{
  acknowledged: true,
  insertedId: ObjectId('67f26dbf81a6e350ba6b140b')
}

# Пишем данные в ЕКБ - успех
docker-compose exec mongos3 mongosh --host mongos3:60003 testdb --eval 
db.splitBrainTest.insertOne({location: "Ekb", time: new Date()});
{
  acknowledged: true,
  insertedId: ObjectId('67f26dfb346860283a6b140b')
}

# Пробуем прочитать в МСК - ошибка
docker-compose exec mongos1 mongosh --host mongos1:60001 testdb --eval 
db.splitBrainTest.find().toArray();
MongoServerError[FailedToSatisfyReadPreference]: Encountered non-retryable error during query :: caused by :: Could not find host matching read preference { mode: "primary" } for set shard3

# Пробуем прочитать в СПБ - успех
docker-compose exec mongos2 mongosh --host mongos2:60002 testdb --eval 
db.splitBrainTest.find().toArray();
[
  {
    _id: ObjectId('67f26dbf81a6e350ba6b140b'),
    location: 'Spb',
    time: ISODate('2025-04-06T12:04:15.097Z')
  },
  {
    _id: ObjectId('67f26dfb346860283a6b140b'),
    location: 'Ekb',
    time: ISODate('2025-04-06T12:05:15.743Z')
  }
]

# Восстанавливаем сеть ЦОД в МСК
docker network connect mongo-avail_sharedNetwork mongos1
docker network connect mongo-avail_sharedNetwork shard1a
docker network connect mongo-avail_sharedNetwork shard2a
docker network connect mongo-avail_sharedNetwork shard3a

# Пробуем прочитать в МСК - успех
docker-compose exec mongos1 mongosh --host mongos1:60001 testdb --eval db.splitBrainTest.find().toArray();
[
  {
    _id: ObjectId('67f26dbf81a6e350ba6b140b'),
    location: 'Spb',
    time: ISODate('2025-04-06T12:04:15.097Z')
  },
  {
    _id: ObjectId('67f26dfb346860283a6b140b'),
    location: 'Ekb',
    time: ISODate('2025-04-06T12:05:15.743Z')
  }
]
```
**Кластер полностью восстановлен**
## Выводы
1. Архитектура кластера с репликами в одном ЦОД - не лучшая практика
2. Отказоустойчивости можно добиться, если располагать реплики в разных цодах - при разрыве связи между ЦОДами кластер продолжит работу
3. Каждая часть может выбрать своего лидера, что приводит к конфликту данных
4. Настройка приоритетов реплик помогает минимизировать риск Split-Brain
5. Использование writeConcern: majority предотвращает потерю данных
   
Для production-окружения рекомендуется:
- Использовать нечетное количество ЦОДов
- Настроить мониторинг состояния кластера
- Реализовать автоматическое обнаружение и обработку сетевых разрывов
- Регулярно тестировать отказоустойчивость
