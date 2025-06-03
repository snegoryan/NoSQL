# ДЗ 9. Сравнение Neo4j с неграфовыми БД
## Домашнее задание
Сравнение с неграфовыми БД

Цель:
В результате выполнения ДЗ вы поймете зачем и когда может понадобиться графовая база данных.

Описание/Пошаговая инструкция выполнения домашнего задания:
1. Придумать 2-3 варианта, когда применима графовая база данных. Можно даже абзац на контекст каждого примера.
2. Воспользоваться моделью, данными и командами из лекции или одним из своих примеров из пункта 1 и реализовать аналог в любой выбранной БД (реляционной или нет - на выбор). Сравнить команды.  
Написать, что удобнее было сделать в выбранной БД, а что в Neo4j и привести примеры.

Критерии оценки:
- задание выполнено - 10 баллов
- предложено красивое решение - плюс 2 балла
Минимальный порог: 10 баллов

---

### **1. Примеры применения графовой БД (Neo4j)**

**1.1. Социальная сеть (друзья, рекомендации)**  
В социальных сетях важно быстро находить связи между пользователями (друзья, подписчики, общие интересы). В графовой БД можно эффективно искать пути (например, "друзья друзей"), а в реляционной БД для этого потребуются сложные JOIN-запросы.

**1.2. Рекомендательная система (кино, товары)**  
Если нужно предлагать пользователям товары или фильмы на основе поведения других похожих пользователей, графовая БД позволяет легко находить связи (например, "пользователи, которые купили X, также купили Y"). В реляционной БД это требует множества промежуточных таблиц.

**1.3. Анализ мошенничества (финансовые транзакции)**  
Графы помогают выявлять подозрительные схемы (например, цепочки транзакций между связанными аккаунтами). В SQL подобные запросы будут медленными из-за необходимости множества соединений.
### **2. Основные операции в Neo4j и PostgreSQL**

#### 2.1. Создание данных

**Neo4j:**
```cypher
CREATE (p1:Person {name: 'Alice', age: 30})
CREATE (p2:Person {name: 'Bob', age: 25})
CREATE (p3:Person {name: 'Alex', age: 35})
CREATE (p4:Person {name: 'Charlie', age: 28})
CREATE (p1)-[:FRIENDS_WITH]->(p2)
CREATE (p2)-[:FRIENDS_WITH]->(p3)
CREATE (p1)-[:FRIENDS_WITH]->(p4)
```

**PostgreSQL**
```sql
CREATE TABLE person (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    age INT
);

CREATE TABLE friendship (
    person_id INT REFERENCES person(id),
    friend_id INT REFERENCES person(id),
    PRIMARY KEY (person_id, friend_id)
);

INSERT INTO person (name, age) VALUES ('Alice', 30), ('Bob', 25), ('Alex', 35), ('Charlie', 28);
INSERT INTO friendship (person_id, friend_id) VALUES (1, 2);
INSERT INTO friendship (person_id, friend_id) VALUES (2, 3);
INSERT INTO friendship (person_id, friend_id) VALUES (1, 4);
```

#### 2.2. Поиск данных

**Neo4j поиск друзей `Alice`**
```cypher
MATCH (p:Person {name: 'Alice'})-[:FRIENDS_WITH]->(friend)
RETURN friend.name;
```

**PostgreSQL**
```sql
SELECT p2.name 
FROM friendship f
JOIN person p1 ON f.person_id = p1.id
JOIN person p2 ON f.friend_id = p2.id
WHERE p1.name = 'Alice';
```
#### 2.3. Поиск друзей 2-го круга

**Neo4j**
```cypher
MATCH (p:Person {name: 'Alice'})-[:FRIENDS_WITH*2]->(friend_of_friend)
RETURN friend_of_friend.name;
```

**PostgreSQL**
```sql
WITH RECURSIVE friend_path AS (
    SELECT friend_id, 1 AS depth
    FROM friendship
    WHERE person_id = (SELECT id FROM person WHERE name = 'Alice')
    
    UNION ALL
    
    SELECT f.friend_id, fp.depth + 1
    FROM friendship f
    JOIN friend_path fp ON f.person_id = fp.friend_id
    WHERE fp.depth < 2
)
SELECT p.name
FROM friend_path fp
JOIN person p ON fp.friend_id = p.id
WHERE fp.depth = 2;
```

#### 2.4. Обновление данных

**Neo4j**
```cypher
MATCH (p:Person {name: 'Alice'})
SET p.age = 31
RETURN p;
```

**PostgreSQL**
```sql
UPDATE person SET age = 31 WHERE name = 'Alice';
```

#### 2.5. Удаление данных

**Neo4j**
```cypher
MATCH (p:Person {name: 'Bob'})
DETACH DELETE p;  // Удаляет узел и все связи
```

**PostgreSQL**
```sql
DELETE FROM friendship WHERE person_id = (SELECT id FROM person WHERE name = 'Bob') OR friend_id = (SELECT id FROM person WHERE name = 'Bob');
DELETE FROM person WHERE name = 'Bob';
```

### **3. Сложные запросы (глубокий обход графа)**

#### 3.1. Поиск всех возможных путей между людьми

**Neo4j**
```cypher
MATCH path = (p1:Person {name: 'Alice'})-[:FRIENDS_WITH*]->(p2:Person {name: 'Charlie'})
RETURN path;
```

**PostgreSQL**
```sql
WITH RECURSIVE all_paths AS (
    SELECT 
        ARRAY[person_id, friend_id] AS path,
        friend_id AS last_node,
        1 AS depth
    FROM friendship
    WHERE person_id = (SELECT id FROM person WHERE name = 'Alice')
    
    UNION ALL
    
    SELECT 
        path || f.friend_id,
        f.friend_id,
        ap.depth + 1
    FROM friendship f
    JOIN all_paths ap ON f.person_id = ap.last_node
    WHERE NOT f.friend_id = ANY(path)  -- Чтобы избежать циклов
    AND ap.depth < 5  -- Ограничение глубины
)
SELECT path 
FROM all_paths
WHERE last_node = (SELECT id FROM person WHERE name = 'Charlie');
```

#### 3.2. Рекомендации друзей (кто дружит с моими друзьями, но не со мной)

**Neo4j**
```cypher
MATCH (me:Person {name: 'Alice'})-[:FRIENDS_WITH]->(friend)-[:FRIENDS_WITH]->(recommended)
WHERE NOT (me)-[:FRIENDS_WITH]->(recommended)
RETURN recommended.name;
```

**PostgreSQL**
```sql
SELECT DISTINCT p3.name
FROM friendship f1
JOIN friendship f2 ON f1.friend_id = f2.person_id
JOIN person p1 ON f1.person_id = p1.id
JOIN person p2 ON f1.friend_id = p2.id
JOIN person p3 ON f2.friend_id = p3.id
WHERE p1.name = 'Alice'
AND NOT EXISTS (
    SELECT 1 FROM friendship f3 
    WHERE f3.person_id = p1.id AND f3.friend_id = p3.id
);
```

### **4. Сравнение Neo4j и реляционной БД**

| **Аспект**             | **Neo4j (графовая)**                         | **PostgreSQL (реляционная)**              |
| ---------------------- | -------------------------------------------- | ----------------------------------------- |
| **Поиск связей**       | Просто и быстро (`MATCH` с указанием связей) | Требует JOIN-ов и подзапросов             |
| **Глубина запросов**   | Легко искать связи любой глубины (`*2..5`)   | Сложно, нужны рекурсивные запросы (CTE)   |
| **Гибкость структуры** | Можно добавлять связи без изменения схемы    | Требует ALTER TABLE или новых таблиц      |
| **Сложные агрегации**  | Менее удобно (нет GROUP BY как в SQL)        | Оптимизировано для аналитики (SUM, COUNT) |

**Вывод:**
Neo4j лучше подходит для задач, где важны связи между данными (соцсети, рекомендации, фрод-аналитика). Реляционные БД (PostgreSQL) удобнее для структурированных данных с четкой схемой и сложными аналитическими запросами.
