# Система автоматизированного синтеза и анализа речи

## Общее описание

Система синтеза и распознавания речи на основе serverless-модели. Человек вводит вводит запрос на естественном языке в текстовом или голосовом формате. Задача системы понять, что хочет узнать человек.

Каких видов запросы могут быть:

- Озвучивание текстового или голосового запроса. Если человек опирается на слова, по смыслу схожие на `озвучь`, `прочитай`, `скажи` и прочие, то запрос формализуется с действием `synthesize`, тело запроса просто озвучивается. 
- Анализ текстового или голосового запроса. Если человек задает вопрос, например, связанный с жизнью Пушкина, то система ответит на вопрос, заданный в запросе, действие запроса будет формализовано как `ask`.
- Если по некой причине запрос был неясен, либо произошла ошибка, то действие помечается типом `synthesize`.

## Стек

| Приминение | Технологии |
|---|---|
| **Frontend / BFF** | FastAPI, Jinja2, httpx |
| **Синтез речи** | Piper TTS, ffmpeg |
| **Распознавание речи** | AWS Transcribe (LocalStack) |
| **LLM** | Ollama (`qwen2.5:3b` — формализация, `qwen2.5:3b` — ответы, `nomic-embed-text` — эмбеддинги) |
| **Векторный поиск** | Qdrant |
| **Кэш / Rate limit** | Redis |
| **Оркестрация** | AWS Step Functions (LocalStack) |
| **Очереди** | AWS SQS + DLQ (LocalStack) |
| **Хранилище** | AWS S3 (LocalStack) |
| **Состояние запросов** | AWS DynamoDB (LocalStack), TTL 24ч |
| **Секреты** | AWS Secrets Manager, SSM Parameter Store (LocalStack) |
| **Инфраструктура** | Terraform (провайдер AWS → LocalStack) |
| **Упаковка** | Docker Compose, `build_lambdas.sh` |
| **Тесты** | pytest, pytest-asyncio |

## Архитектура

### Сценарий 1: текстовый запрос по смыслу схож с целью «озвучь»

```mermaid
sequenceDiagram
    participant U as Web Client
    participant AG as API Gateway
    participant I as Lambda: ingest
    participant SQS1 as SQS: input
    participant D as Lambda: dispatcher
    participant SFN as Step Functions
    participant F as Lambda: formalize
    participant E as Lambda: execute
    participant SQS2 as SQS: tts
    participant T as Lambda: tts
    participant TTS as tts-service
    participant S3 as S3: audio-output
    participant DB as DynamoDB

    U->>AG: POST /ask {text}
    AG->>I: invoke
    I->>DB: create_request (IN_PROGRESS)
    I->>SQS1: send message
    I-->>U: {request_id}

    SQS1->>D: trigger
    D->>SFN: start_execution(request_id)

    SFN->>F: invoke
    F-->>SFN: {command: synthesize, params}
    SFN->>E: invoke
    E-->>SFN: {text, voice, speed, ...}
    SFN->>SQS2: send message

    SQS2->>T: trigger
    T->>TTS: POST /synthesize
    TTS-->>T: audio bytes
    T->>S3: put_object
    T->>DB: mark_completed
    T->>SQS2: send to output queue

    U->>AG: GET /result/{request_id} (polling)
    AG->>DB: get_request
    AG-->>U: {status: COMPLETED, audio_url, text}
```

### Сценарий 2: аудио-запрос (распознавание и ответ)

```mermaid
sequenceDiagram
    participant U as Web Client
    participant AG as API Gateway
    participant I as Lambda: ingest
    participant S3I as S3: audio-input
    participant SQS1 as SQS: input
    participant D as Lambda: dispatcher
    participant SFN as Step Functions
    participant TR as Lambda: transcribe
    participant AWS as AWS Transcribe
    participant F as Lambda: formalize
    participant E as Lambda: execute
    participant Q as Qdrant
    participant O as Ollama
    participant SQS2 as SQS: tts
    participant T as Lambda: tts
    participant TTS as tts-service
    participant S3O as S3: audio-output

    U->>U: MediaRecorder → webm
    U->>U: ffmpeg → wav 16kHz mono (base64)
    U->>AG: POST /ask-audio {audio}
    AG->>I: invoke
    I->>S3I: put_object (.wav)
    I->>SQS1: send {s3_uri}
    I-->>U: {request_id}

    SQS1->>D: trigger
    D->>SFN: start_execution

    SFN->>TR: action=start
    TR->>AWS: start_transcription_job
    loop polling (до 60 попыток, шаг 5с)
        SFN->>TR: action=check
        TR->>AWS: get_transcription_job
        TR-->>SFN: status
    end
    SFN->>TR: action=parse
    TR->>S3I: get transcript
    TR-->>SFN: {text}

    SFN->>F: invoke
    F-->>SFN: {command: ask, params: {question}}
    SFN->>E: invoke
    E->>O: embed(question)
    O-->>E: vector
    E->>Q: search(top_k=2)
    Q-->>E: context
    E->>O: chat(question + context)
    O-->>E: answer
    E-->>SFN: {text: answer, ...}

    SFN->>SQS2: send
    SQS2->>T: trigger
    T->>TTS: POST /synthesize
    TTS-->>T: audio
    T->>S3O: put_object
    T-->>SQS2: send to output queue

    U->>AG: GET /result/{request_id}
    AG-->>U: {status: COMPLETED, audio_url, text}
```

## Запуск

Ключевые команды:

**1. Собрать Lambda-артефакты** (zipы в `build/`):

```bash
./build_lambdas.sh 
# можно указать, например, ./build_lambdas.sh execute, и будет собрана только execute лямбда
```

**2. Поднять инфраструктуру в LocalStack** (создаёт S3, SQS, DynamoDB, IAM, Lambda, Step Functions, API Gateway, Secrets Manager, SSM, в рамках данного окружения выполнить после Compose):

```bash
cd terraform/environments/dev && terraform init && terraform apply
```

**3. Запустить сервисы** (LocalStack, Ollama, Qdrant, Redis, tts-service, web-client):

```bash
docker compose up -d
```

После этого:
- Web-клиент — `http://localhost:8092`
- TTS-сервис — `http://localhost:8001`
- LocalStack — `http://localhost:4566`