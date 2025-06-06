# ДЗ 11. Elasticsearch

## Домашнее задание
Знакомство с ElasticSearch

Цель:
В результате выполнения ДЗ вы научитесь разворачивать ES в AWS и использовать полнотекстовый нечеткий поиск

Описание/Пошаговая инструкция выполнения домашнего задания:
Развернуть Instance ES – желательно в AWS  
Создать в ES индекс, в нём должно быть обязательное поле text типа string  
Создать для индекса pattern  
Добавить в индекс как минимум 3 документа желательно со следующим содержанием:  
«моя мама мыла посуду а кот жевал сосиски»  
«рама была отмыта и вылизана котом»  
«мама мыла раму»  
Написать запрос нечеткого поиска к этой коллекции документов по ключу «мама ела сосиски»  
Расшарить коллекцию postman (желательно сдавать в таком формате)  
Прислать ссылку на коллекцию

Критерии оценки:
- задание выполнено - 10 баллов
- предложено красивое решение - плюс 2 балла
Минимальный порог: 10 баллов
-----

***Примечание В данной работе ElasticSearch заменён на Opensearch.***
***Запросы будут выполняться через `Dashboards Dev Tools`.***
### 1. Развертывание OpenSearch в Docker

Разворачивать OpenSearch будем при помощи следующего docker-compose файла.

Помимо OpenSearch сразу развернём отдельный контейнер с Opensearch Dashboards
```yaml
services:

  opensearch:
    container_name: opensearch
    image: opensearchproject/opensearch:latest
    environment:
      - discovery.type=single-node
      - bootstrap.memory_lock=true # along with the memlock settings below, disables swapping
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m" # minimum and maximum Java heap size, recommend setting both to 50% of system RAM
      - "OPENSEARCH_INITIAL_ADMIN_PASSWORD=Developer@123"
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536 # maximum number of open files for the OpenSearch user, set to at least 65536 on modern systems
        hard: 65536
    ports:
      - 9200:9200
      - 9600:9600 # required for Performance Analyzer
    expose:
      - "9200"
    networks:
      - opensearch-net

  dashboards:
    image: opensearchproject/opensearch-dashboards:latest
    container_name: opensearch-dashboards
    ports:
      - 5601:5601
    expose:
      - "5601"
    environment:
      OPENSEARCH_HOSTS: '["https://opensearch:9200"]'
    depends_on:
      - opensearch
    networks:
      - opensearch-net

networks:
  opensearch-net:
    driver: bridge
```

Запускаем
```bash
docker-compose up -d
```

Проверяем через `curl` запрос:
```bash
curl -X GET https://localhost:9200 -ku admin:Developer@123 --insecure
{
  "name" : "9ef36dc4f7e9",
  "cluster_name" : "docker-cluster",
  "cluster_uuid" : "qbTRVgQPTDanY9BlTGZIdA",
  "version" : {
    "distribution" : "opensearch",
    "number" : "3.0.0",
    "build_type" : "tar",
    "build_hash" : "dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9",
    "build_date" : "2025-05-03T06:25:26.379676844Z",
    "build_snapshot" : false,
    "lucene_version" : "10.1.0",
    "minimum_wire_compatibility_version" : "2.19.0",
    "minimum_index_compatibility_version" : "2.0.0"
  },
  "tagline" : "The OpenSearch Project: https://opensearch.org/"
}
```

#### **2. Создание индекса с маппингом**

**Далее запросы буду выполнять через `Dev Tools` в `Dashboards`** 

Создадим индекс `my_first_index` с полем `my_text_field` типа `text` (для полнотекстового поиска):
```bash
PUT /my_first_index
{
  "settings": {
    "index": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  },
  "mappings": {
    "properties": {
      "my_text_field": {
        "type": "text",
        "analyzer": "russian"
      }
    }
  }
}
```

**Параметры `settings`**
**`number_of_shards`** - Количество **шардов** (сегментов индекса). Для теста используем 1.
**`number_of_replicas`** - Количество **реплик** (копий шардов для отказоустойчивости). В нашем случае без реплик, мы используем одну ноду.

**Параметры `mappings`**
**`type` - `text`** Поле содержит текстовые данные, которые будут анализироваться для полнотекстового поиска
**`analyzer` - `russian`** 
Анализатор для русского языка:  
• Разбивает текст на слова  
• Приводит слова к нижнему регистру  
• Учитывает стоп-слова ("моя", "а")  
• Применяет **стемминг** (отбрасывает окончания: "мыла" → "мыл")

Выполняем запрос, индекс успешно создан:
```json
{
  "acknowledged": true,
  "shards_acknowledged": true,
  "index": "my_first_index"
}
```

### 3. Добавление документов

Добавим 3 документа через `_bulk` запрос:
```bash
POST /_bulk
{ "index" : { "_index" : "my_first_index", "_id" : "1" } }
{ "my_text_field" : "моя мама мыла посуду а кот жевал сосиски" }
{ "index" : { "_index" : "my_first_index", "_id" : "2" } }
{ "my_text_field" : "рама была отмыта и вылизана котом" }
{ "index" : { "_index" : "my_first_index", "_id" : "3" } }
{ "my_text_field" : "мама мыла раму" }
```

Все документы успешно добавлены:
```json
{
  "took": 47,
  "errors": false,
  "items": [
    {
      "index": {
        "_index": "my_first_index",
        "_id": "1",
        "_version": 2,
        "result": "updated",
        "_shards": {
          "total": 1,
          "successful": 1,
          "failed": 0
        },
        "_seq_no": 1,
        "_primary_term": 1,
        "status": 200
      }
    },
    {
      "index": {
        "_index": "my_first_index",
        "_id": "2",
        "_version": 1,
        "result": "created",
        "_shards": {
          "total": 1,
          "successful": 1,
          "failed": 0
        },
        "_seq_no": 2,
        "_primary_term": 1,
        "status": 201
      }
    },
    {
      "index": {
        "_index": "my_first_index",
        "_id": "3",
        "_version": 1,
        "result": "created",
        "_shards": {
          "total": 1,
          "successful": 1,
          "failed": 0
        },
        "_seq_no": 3,
        "_primary_term": 1,
        "status": 201
      }
    }
  ]
}
```

### 4. Нечеткий поиск

Выполним поиск "**мама ела сосиски**" *без* учетом опечаток:
```bash
GET /my_first_index/_search
{
  "query": {
    "match": {
      "my_text_field": {
        "query": "мама ела сосиски"
      }
    }
  }
}
```

Получаем ответ из двух документов
**"моя мама мыла посуду а кот жевал сосиски"**
**"мама мыла раму"**:
```json
{
  "took": 2,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 2,
      "relation": "eq"
    },
    "max_score": 0.5698135,
    "hits": [
      {
        "_index": "my_first_index",
        "_id": "1",
        "_score": 0.5698135,
        "_source": {
          "my_text_field": "моя мама мыла посуду а кот жевал сосиски"
        }
      },
      {
        "_index": "my_first_index",
        "_id": "3",
        "_score": 0.2444019,
        "_source": {
          "my_text_field": "мама мыла раму"
        }
      }
    ]
  }
}
```

Выполним поиск "**мама ела сосиски**" уже c учетом опечаток, для этого в запрос добавим параметр `"fuzziness": "AUTO"`:
```bash
GET /my_first_index/_search
{
  "query": {
    "match": {
      "my_text_field": {
        "query": "мама ела сосиски",
        "fuzziness": "AUTO"        
      }
    }
  }
}
```

**В ответе получаем все 3 документа:**
```json
{
  "took": 6,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 3,
      "relation": "eq"
    },
    "max_score": 0.5698135,
    "hits": [
      {
        "_index": "my_first_index",
        "_id": "1",
        "_score": 0.5698135,
        "_source": {
          "my_text_field": "моя мама мыла посуду а кот жевал сосиски"
        }
      },
      {
        "_index": "my_first_index",
        "_id": "3",
        "_score": 0.4073365,
        "_source": {
          "my_text_field": "мама мыла раму"
        }
      },
      {
        "_index": "my_first_index",
        "_id": "2",
        "_score": 0.14705287,
        "_source": {
          "my_text_field": "рама была отмыта и вылизана котом"
        }
      }
    ]
  }
}
```
