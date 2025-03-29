## OTUS NoSQL Домашнее задание 2

**MongoDB**

**Цель:**
В результате выполнения ДЗ вы научитесь разворачивать MongoDB, заполнять данными и делать запросы.

Описание/Пошаговая инструкция выполнения домашнего задания:

**Необходимо:**
- установить MongoDB одним из способов: ВМ, докер;
- заполнить данными;
- написать несколько запросов на выборку и обновление данных

Сдача ДЗ осуществляется в виде миниотчета.

---

Задание повышенной сложности*  
создать индексы и сравнить производительность.

Критерии оценки:

Критерии оценки:

- задание выполнено - 10 баллов
- предложено красивое решение - плюс 2 балла
- выполнено задание со* - плюс 5 баллов

Минимальный порог: 10 баллов

---
### **Отчёт о выполнении**

## **Установка MongoDB**

В качестве среды исполнения будет использоваться Docker, хост - Win машина.
### **1. Шаги развёртывания:**
1. Запускаем MongoDB в Docker:
``` bash
> docker run --name mongodb -d -p 27017:27017 mongo:latest
```
2. Проверяем запуск контейнера:   
``` bash
> docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS                      NAMES  
24617c37fe73   mongo:latest   "docker-entrypoint.s…"   9 seconds ago   Up 9 seconds   0.0.0.0:27017->27017/tcp   mongodb
```
3. Подключаемся к контейнеру и запускаем `mongosh`:
```bash
> docker exec -it mongodb mongosh
```
4. Делаем первый запрос, запрашиваем список БД
```bash
test> show dbs
admin   40.00 KiB
config  60.00 KiB
local   40.00 KiB
test>
```
## **2. Заполнение данными**
1. Создадим БД `university`
```bash
test> use university
switched to db university
university>
```

2. Сделаем одиночный `Insert` данных в коллекцию `students` 
```bash
university> db.students.insertOne( { name: "Иван Иванов", age: 20, course: "Информатика", grades: [4, 5, 5]})
{
  acknowledged: true,
  insertedId: ObjectId('67e7beaaf6434d4e936b140b')
}
university>
```
3. Теперь сделаем множественный `Insert` данных в коллекцию `students`
```bash
university> db.students.insertMany([
...   { name: "Петр Петров", age: 21, course: "Математика", grades: [3, 4, 5] },
...   { name: "Анна Сидорова", age: 19, course: "Физика", grades: [5, 5, 5] },
...   { name: "Мария Кузнецова", age: 22, course: "Информатика", grades: [4, 3, 4] },
...   { name: "Алексей Смирнов", age: 20, course: "Математика", grades: [5, 4, 3] }
... ])
{
  acknowledged: true,
  insertedIds: {
    '0': ObjectId('67e7bf40f6434d4e936b140c'),
    '1': ObjectId('67e7bf40f6434d4e936b140d'),
    '2': ObjectId('67e7bf40f6434d4e936b140e'),
    '3': ObjectId('67e7bf40f6434d4e936b140f')
  }
}
university>
```
## **3. Запросы на выборку**

#### 1. Найти всех студентов, изучающих "Информатику":

```bash
university> db.students.find({ course: "Информатика" })
```
**Результат:**  
Найдены 2 студента: Иван Иванов и Мария Кузнецова.
```bash
[
  {
    _id: ObjectId('67e7beaaf6434d4e936b140b'),
    name: 'Иван Иванов',
    age: 20,
    course: 'Информатика',
    grades: [ 4, 5, 5 ]
  },
  {
    _id: ObjectId('67e7bf40f6434d4e936b140e'),
    name: 'Мария Кузнецова',
    age: 22,
    course: 'Информатика',
    grades: [ 4, 3, 4 ]
  }
]
```
#### 2. Найти студентов старше 20 лет:

```bash
university> db.students.find({ age: { $gt: 20 } })
```

**Результат: найдено 2 студента**:  
```bash
[
  {
    _id: ObjectId('67e7bf40f6434d4e936b140c'),
    name: 'Петр Петров',
    age: 21,
    course: 'Математика',
    grades: [ 3, 4, 5 ]
  },
  {
    _id: ObjectId('67e7bf40f6434d4e936b140e'),
    name: 'Мария Кузнецова',
    age: 22,
    course: 'Информатика',
    grades: [ 4, 3, 4 ]
  }
]
```
#### 3. Найти студентов с оценкой 5:
```bash
university> db.students.find({ grades: 5 })
```
Результат найдены 4 студента:
```bash
[
  {
    _id: ObjectId('67e7beaaf6434d4e936b140b'),
    name: 'Иван Иванов',
    age: 20,
    course: 'Информатика',
    grades: [ 4, 5, 5 ]
  },
  {
    _id: ObjectId('67e7bf40f6434d4e936b140c'),
    name: 'Петр Петров',
    age: 21,
    course: 'Математика',
    grades: [ 3, 4, 5 ]
  },
  {
    _id: ObjectId('67e7bf40f6434d4e936b140d'),
    name: 'Анна Сидорова',
    age: 19,
    course: 'Физика',
    grades: [ 5, 5, 5 ]
  },
  {
    _id: ObjectId('67e7bf40f6434d4e936b140f'),
    name: 'Алексей Смирнов',
    age: 20,
    course: 'Математика',
    grades: [ 5, 4, 3 ]
  }
]
```
#### 4. Посчитать количество студентов с оценкой 3:
```bash
university> db.students.find({ grades: 3 }).count()
```
Результат: найдено 3 студента с оценкой 3
#### 5. Показать все курсы, на которых обучаются студенты
```bash
university> db.students.distinct( "course" )
```
Результат: Всего 3 курса
```bash
[ 'Информатика', 'Математика', 'Физика' ]
```
#### 6. Вывести имена и возраст студентов на курсе Математика
```bash
university> db.students.find({course: "Математика"}, { name: 1, age: 1, _id: 0})
```
Результат:
```bash
[
  { name: 'Петр Петров', age: 21 },
  { name: 'Алексей Смирнов', age: 20 }
]
```
#### 7. Отсортировать студентов по возрасту, вывести имена и возраст
```bash
students> db.students.find({}, {name: 1, age: 1, _id: 0}).sort({age: 1})
[
  { name: 'Анна Сидорова', age: 19 },
  { name: 'Иван Иванов', age: 20 },
  { name: 'Алексей Смирнов', age: 20 },
  { name: 'Мария Кузнецова', age: 22 }
]
```
## **4. Запросы на обновление**

#### **1. Увеличить возраст студента "Анна Сидорова" на 1:**

```bash
university> db.students.updateOne(
...   { name: "Анна Сидорова" },
...   { $inc: { age: 1 } }
... );
{
  acknowledged: true,
  insertedId: null,
  matchedCount: 1,
  modifiedCount: 1,
  upsertedCount: 0
}
university>
```
**Проверка:**
```bash
university> db.students.findOne({ name: "Анна Сидорова" })
{
  _id: ObjectId('67e7bf40f6434d4e936b140d'),
  name: 'Анна Сидорова',
  age: 20,
  course: 'Физика',
  grades: [ 5, 5, 5 ]
}
```

Теперь возраст = 20.
#### **2. Добавить новую оценку студенту "Петр Петров":**

```bash
university> db.students.updateOne(
...   { name: "Петр Петров" },
...   { $push: { grades: 4 } }
... );
{
  acknowledged: true,
  insertedId: null,
  matchedCount: 1,
  modifiedCount: 1,
  upsertedCount: 0
}
```

**Проверяем**:
```bash
university> db.students.findOne({ name: "Петр Петров" })
{
  _id: ObjectId('67e7bf40f6434d4e936b140c'),
  name: 'Петр Петров',
  age: 21,
  course: 'Математика',
  grades: [ 3, 4, 5, 4 ]
}
```

Теперь `grades` = `[3, 4, 5, 4]`.
## **6. Запросы на удаление**
Удалим студента `"Петр Петров"`:
```bash
students> db.students.deleteOne({name: "Петр Петров"})
{ acknowledged: true, deletedCount: 1 }
```
Проверяем:
```
students> db.students.find({name: "Петр Петров"}).count()
0
students> 
```
Количество документов = 0
## **5. Индексы и сравнение производительности (_задание повышенной сложности_)**

Для более наглядного процесса, нам необходимо заполнить коллекцию большим количеством данных, нежели 5 записей в предыдущих примерах.
В качестве датасета будем использовать коллекцию `companies`:
[mongodb-json-files/datasets/companies.json at master · ozlerhakan/mongodb-json-files](https://github.com/ozlerhakan/mongodb-json-files/blob/master/datasets/companies.json)

Запустим контейнер с примонтированной шарой хост машины, где размещён файл с коллекцией:
```bash
docker run -v ./app::/usr/share/mongo --name mongo -d -p 27017:27017 mongo:latest
```
Импортируем коллекцию `companies` в БД `indexes`
```bash
> docker exec -it mongo mongoimport --db indexes --collection companies --file /usr/share/mongo/companies.json  
2025-03-29T10:42:58.581+0000    connected to: mongodb://localhost/
2025-03-29T10:43:01.158+0000    18801 document(s) imported successfully. 0 document(s) failed to import.
```
Проверяем наличие БД `indexes`
```bash
test> show dbs
admin    40.00 KiB
config   12.00 KiB
indexes  31.48 MiB
local    40.00 KiB
```
Переключаемся на `indexes`
```bash
test> use indexes
switched to db indexes
```
Делаем пробный запрос данных:
```bash
indexes> db.companies.find({}).limit(1)
[
  {
    _id: ObjectId('52cdef7c4bab8bd675297d8b'),
    name: 'AdventNet',
    permalink: 'abc3',
    crunchbase_url: 'http://www.crunchbase.com/company/adventnet',
    homepage_url: 'http://adventnet.com',
    blog_url: '',
    blog_feed_url: '',
    twitter_username: 'manageengine',
    category_code: 'enterprise',
    number_of_employees: 600,
    founded_year: 1996,
    deadpooled_year: 2,
    tag_list: '',
    alias_list: 'Zoho ManageEngine ',
    email_address: 'pr@adventnet.com',
    phone_number: '925-924-9500',
    description: 'Server Management Software',
    created_at: ISODate('2007-05-25T19:24:22.000Z'),
    updated_at: 'Wed Oct 31 18:26:09 UTC 2012',
    overview: '<p>AdventNet is now <a href="/company/zoho-manageengine" title="Zoho ManageEngine" rel="nofollow">Zoho ManageEngin
e</a>.</p>\n' +
      '\n' +
      '<p>Founded in 1996, AdventNet has served a diverse range of enterprise IT, networking and telecom customers.</p>\n' +     
      '\n' +
      '<p>AdventNet supplies server and network management software.</p>',
    image: {
      available_sizes: [
        [
          [ 150, 55 ],
          'assets/images/resized/0001/9732/19732v1-max-150x150.png'
        ],
        [
          [ 150, 55 ],
          'assets/images/resized/0001/9732/19732v1-max-250x250.png'
        ],
        [
          [ 150, 55 ],
          'assets/images/resized/0001/9732/19732v1-max-450x450.png'
        ]
      ]
    },
    products: [],
    relationships: [
      {
        is_past: true,
        title: 'CEO and Co-Founder',
        person: {
          first_name: 'Sridhar',
          last_name: 'Vembu',
          permalink: 'sridhar-vembu'
        }
      },
      {
        is_past: true,
        title: 'VP of Business Dev',
        person: {
          first_name: 'Neil',
          last_name: 'Butani',
          permalink: 'neil-butani'
        }
      },
      {
        is_past: true,
        title: 'Usabiliy Engineer',
        person: {
          first_name: 'Bharath',
          last_name: 'Balasubramanian',
          permalink: 'bharath-balasibramanian'
        }
      },
      {
        is_past: true,
        title: 'Director of Engineering',
        person: {
          first_name: 'Rajendran',
          last_name: 'Dandapani',
          permalink: 'rajendran-dandapani'
        }
      },
      {
        is_past: true,
        title: 'Market Analyst',
        person: {
          first_name: 'Aravind',
          last_name: 'Natarajan',
          permalink: 'aravind-natarajan'
        }
      },
      {
        is_past: true,
        title: 'Director of Product Management',
        person: {
          first_name: 'Hyther',
          last_name: 'Nizam',
          permalink: 'hyther-nizam'
        }
      },
      {
        is_past: true,
        title: 'Western Regional OEM Sales Manager',
        person: {
          first_name: 'Ian',
          last_name: 'Wenig',
          permalink: 'ian-wenig'
        }
      }
    ],
    competitions: [],
    providerships: [
      {
        title: 'DHFH',
        is_past: true,
        provider: { name: 'A Small Orange', permalink: 'a-small-orange' }
      }
    ],
    total_money_raised: '$0',
    funding_rounds: [],
    investments: [],
    acquisition: null,
    acquisitions: [],
    offices: [
      {
        description: 'Headquarters',
        address1: '4900 Hopyard Rd.',
        address2: 'Suite 310',
        zip_code: '94588',
        city: 'Pleasanton',
        state_code: 'CA',
        country_code: 'USA',
        latitude: 37.692934,
        longitude: -121.904945
      }
    ],
    milestones: [],
    video_embeds: [],
    screenshots: [
      {
        available_sizes: [
          [
            [ 150, 94 ],
            'assets/images/resized/0004/3400/43400v1-max-150x150.png'
          ],
          [
            [ 250, 156 ],
            'assets/images/resized/0004/3400/43400v1-max-250x250.png'
          ],
          [
            [ 450, 282 ],
            'assets/images/resized/0004/3400/43400v1-max-450x450.png'
          ]
        ],
        attribution: null
      }
    ],
    external_links: [],
    partners: []
  }
]
```

### **Сравнение скорости запроса без индекса и с индексом**

Сделаем выборку компаний с категорией `consulting` и количеством сотрудников больше 1000
```bash
db.companies.find({$and: [{category_code : "consulting"},{ number_of_employees: {$gte: 1000}}]})
```
#### **Без индекса:**

```bash
indexes> db.companies.find({$and: [{category_code : "consulting"},{ number_of_employees: {$gte: 1000}}]}).explain("executionStats
")
{
  explainVersion: '1',
  queryPlanner: {
    namespace: 'indexes.companies',
    parsedQuery: {
      '$and': [
        { category_code: { '$eq': 'consulting' } },
        { number_of_employees: { '$gte': 1000 } }
      ]
    },
    indexFilterSet: false,
    queryHash: '9BE5E83E',
    planCacheShapeHash: '9BE5E83E',
    planCacheKey: '3AD6417E',
    optimizationTimeMillis: 0,
    maxIndexedOrSolutionsReached: false,
    maxIndexedAndSolutionsReached: false,
    maxScansToExplodeReached: false,
    prunedSimilarIndexes: false,
    winningPlan: {
      isCached: false,
      stage: 'COLLSCAN',
      filter: {
        '$and': [
          { category_code: { '$eq': 'consulting' } },
          { number_of_employees: { '$gte': 1000 } }
        ]
      },
      direction: 'forward'
    },
    rejectedPlans: []
  },
  executionStats: {
    executionSuccess: true,
    nReturned: 17,
    executionTimeMillis: 9,
    totalKeysExamined: 0,
    totalDocsExamined: 18801,
    executionStages: {
      isCached: false,
      stage: 'COLLSCAN',
      filter: {
        '$and': [
          { category_code: { '$eq': 'consulting' } },
          { number_of_employees: { '$gte': 1000 } }
        ]
      },
      nReturned: 17,
      executionTimeMillisEstimate: 0,
      works: 18802,
      advanced: 17,
      needTime: 18784,
      needYield: 0,
      saveState: 0,
      restoreState: 0,
      isEOF: 1,
      direction: 'forward',
      docsExamined: 18801
    }
  },
  queryShapeHash: '10670D60295539A15DA8C2DC9AD13910BCB277C49CBB0A660ABBD5E0A31D4ED8',
  command: {
    find: 'companies',
    filter: {
      '$and': [
        { category_code: 'consulting' },
        { number_of_employees: { '$gte': 1000 } }
      ]
    },
    '$db': 'indexes'
  },
  serverInfo: {
    host: 'b7d96e1ecfbd',
    port: 27017,
    version: '8.0.5',
    gitVersion: 'cb9e2e5e552ee39dea1e39d7859336456d0c9820'
  },
  serverParameters: {
    internalQueryFacetBufferSizeBytes: 104857600,
    internalQueryFacetMaxOutputDocSizeBytes: 104857600,
    internalLookupStageIntermediateDocumentMaxSizeBytes: 104857600,
    internalDocumentSourceGroupMaxMemoryBytes: 104857600,
    internalQueryMaxBlockingSortMemoryUsageBytes: 104857600,
    internalQueryProhibitBlockingMergeOnMongoS: 0,
    internalQueryMaxAddToSetBytes: 104857600,
    internalDocumentSourceSetWindowFieldsMaxMemoryBytes: 104857600,
    internalQueryFrameworkControl: 'trySbeRestricted',
    internalQueryPlannerIgnoreIndexWithCollationForRegex: 1
  },
  ok: 1
}
```

**Статистика:**
- `executionTimeMillis`: ~9 мс
- `totalDocsExamined`: 18801
- `stage:` COLLSCAN

#### ***Создадим составной индекс по полям `category_code` и `number_of_employees`:***

```bash
indexes> db.companies.createIndex({category_code: 1, number_of_employees: 1})
category_code_1_number_of_employees_1
```
#### **С индексом:**
```bash
indexes> db.companies.find({$and: [{category_code : "consulting"},{ number_of_employees: {$gte: 1000}}]}).explain("executionStats")
{
  explainVersion: '1',
  queryPlanner: {
    namespace: 'indexes.companies',
    parsedQuery: {
      '$and': [
        { category_code: { '$eq': 'consulting' } },
        { number_of_employees: { '$gte': 1000 } }
      ]
    },
    indexFilterSet: false,
    queryHash: '9BE5E83E',
    planCacheShapeHash: '9BE5E83E',
    planCacheKey: '9D89A8C8',
    optimizationTimeMillis: 0,
    maxIndexedOrSolutionsReached: false,
    maxIndexedAndSolutionsReached: false,
    maxScansToExplodeReached: false,
    prunedSimilarIndexes: false,
    winningPlan: {
      isCached: false,
      stage: 'FETCH',
      inputStage: {
        stage: 'IXSCAN',
        keyPattern: { category_code: 1, number_of_employees: 1 },
        indexName: 'category_code_1_number_of_employees_1',
        isMultiKey: false,
        multiKeyPaths: { category_code: [], number_of_employees: [] },
        isUnique: false,
        isSparse: false,
        isPartial: false,
        indexVersion: 2,
        direction: 'forward',
        indexBounds: {
          category_code: [ '["consulting", "consulting"]' ],
          number_of_employees: [ '[1000, inf.0]' ]
        }
      }
    },
    rejectedPlans: []
  },
  executionStats: {
    executionSuccess: true,
    nReturned: 17,
    executionTimeMillis: 0,
    totalKeysExamined: 17,
    totalDocsExamined: 17,
    executionStages: {
      isCached: false,
      stage: 'FETCH',
      nReturned: 17,
      executionTimeMillisEstimate: 0,
      works: 18,
      advanced: 17,
      needTime: 0,
      needYield: 0,
      saveState: 0,
      restoreState: 0,
      isEOF: 1,
      docsExamined: 17,
      alreadyHasObj: 0,
      inputStage: {
        stage: 'IXSCAN',
        nReturned: 17,
        executionTimeMillisEstimate: 0,
        works: 18,
        advanced: 17,
        needTime: 0,
        needYield: 0,
        saveState: 0,
        restoreState: 0,
        isEOF: 1,
        keyPattern: { category_code: 1, number_of_employees: 1 },
        indexName: 'category_code_1_number_of_employees_1',
        isMultiKey: false,
        multiKeyPaths: { category_code: [], number_of_employees: [] },
        isUnique: false,
        isSparse: false,
        isPartial: false,
        indexVersion: 2,
        direction: 'forward',
        indexBounds: {
          category_code: [ '["consulting", "consulting"]' ],
          number_of_employees: [ '[1000, inf.0]' ]
        },
        keysExamined: 17,
        seeks: 1,
        dupsTested: 0,
        dupsDropped: 0
      }
    }
  },
  queryShapeHash: '10670D60295539A15DA8C2DC9AD13910BCB277C49CBB0A660ABBD5E0A31D4ED8',
  command: {
    find: 'companies',
    filter: {
      '$and': [
        { category_code: 'consulting' },
        { number_of_employees: { '$gte': 1000 } }
      ]
    },
    '$db': 'indexes'
  },
  serverInfo: {
    host: 'b7d96e1ecfbd',
    port: 27017,
    version: '8.0.5',
    gitVersion: 'cb9e2e5e552ee39dea1e39d7859336456d0c9820'
  },
  serverParameters: {
    internalQueryFacetBufferSizeBytes: 104857600,
    internalQueryFacetMaxOutputDocSizeBytes: 104857600,
    internalLookupStageIntermediateDocumentMaxSizeBytes: 104857600,
    internalDocumentSourceGroupMaxMemoryBytes: 104857600,
    internalQueryMaxBlockingSortMemoryUsageBytes: 104857600,
    internalQueryProhibitBlockingMergeOnMongoS: 0,
    internalQueryMaxAddToSetBytes: 104857600,
    internalDocumentSourceSetWindowFieldsMaxMemoryBytes: 104857600,
    internalQueryFrameworkControl: 'trySbeRestricted',
    internalQueryPlannerIgnoreIndexWithCollationForRegex: 1
  },
  ok: 1
}
```

**Статистика:**
- `executionTimeMillis`: **~0 мс**
- `totalDocsExamined`: **17**
- `stage:` **IXSCAN**

**Вывод:**  
Индекс ускорил поиск, так как MongoDB не перебирала все документы, а сразу нашла нужные.
