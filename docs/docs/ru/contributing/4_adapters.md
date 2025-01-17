# Create Custom **Propan** Broker

Если вы хотите помочь мне с развитием проекта и разработать **PropanBroker** для еще не поддерживаемого брокера сообщений из [плана](../../#_3)
или вы просто хотите расширить функционал **Propan** для внутреннего использования, вам пригодится эта инструкция по созданию собственного **PropanBroker**.

В данном разделе мы разберемся с деталями реализации брокеров на примерах уже существующих в **Propan**.

## Родительский класс

Все брокеры **Propan** наследуются от родительского класса `propan.brokers.model.BrokerUsecase`.

Для того, чтобы создания полноценного брокера необходимо отнаследоваться от этого класса и реализовать все его абстрактные методы.

```python linenums='1'
{!> docs_src/contributing/adapter/parent.py !}
```

Разберемся со всем по порядку.

## Подключение к брокеру сообщений

За жизненный цикл вашего брокера отвечают два ключевых метода: `_connect` и `close`. После их реализации приложение с вашим адаптером
уже должно корректно запуститься и подключиться к брокеру сообщений (но еще не обрабатывать сообщения).

### _connect

Метод `_connect` инициализирует подключение к вашему брокеру сообщений и возвращает объект этого подключения, который позже будет доступен как `self._connection`.

!!! tip
    Если ваш брокер требует инициализации дополнительных объектов вы также должны инициализировать их в этом методе.

```python linenums='1' hl_lines="8 17-19 24"
{!> docs_src/contributing/adapter/rabbit_connect.py !}
```

!!! note
    `args` и `kwargs` передадутся в ваш метод либо из параметров `__init__`, либо из параметров метода `connect`. Логика разрешения этих аргументов реализована в родительском классе, вам не нужно об этом волноваться.

Обратите внимание на следующие строки: в них мы инициализируем специфичный для **RabbitBroker** объект `_channel`.

```python linenums='8' hl_lines="3 14-15"
{!> docs_src/contributing/adapter/rabbit_connect.py [ln:7-24]!}
```

### close

Теперь нам необходимо корректно завершить работу нашего брокера. Для этого реализуем метод `close`.

```python linenums='8' hl_lines="6-7 10-11"
{!> docs_src/contributing/adapter/rabbit_close.py !}
```

!!! note
    В родительском методе `connect` реализация метода `_connect` вызывается при условии `self._connection is not None`, поэтому важно после остановки соединения также его и обнулить.

После реализации этих методов приложение с вашим брокером уже должно запускаться.

## Регистрация обработчиков

Для того, чтобы ваш брокер начал обрабатывать сообщения необходимо реализовать непосредственно сам метод регистрации обработчика (`handle`) и метод запуска брокера (`start`).

Также ваш брокер должен хранить информацию обо всех зарегистрированных обработчиках, поэтому вам будет необходимо реализовать класс `Handler`, специфичный для каждого брокера.

### handle

```python linenums='1' hl_lines="10-13 17 29-30"
{!> docs_src/contributing/adapter/rabbit_handle.py !}
```

В выделенных фрагментах мы сохраняем информацию о зарегистрированных обработчиках внутри нашего брокера.

Также, очень важным моментом является вызова родительского метода `_wrap_handler` - именно этот метод устанавливает в необъодимом порядке все декораторы, превращающие обычную функцию в обработчик **Propan**.

```python linenums='27' hl_lines="2"
{!> docs_src/contributing/adapter/rabbit_handle.py [ln:27-32] !}
```

### start

В мотоде `start` мы устанавливает подключение к нашему брокеру сообщений и производим все необходимые операции для запуска наших обработчиков.

Здесь представлен несколько упрощенный код регистрации `handler`'ов, однако, концепцию он демонстрирует в полной мере.

```python linenums='1' hl_lines="4 9"
{!> docs_src/contributing/adapter/rabbit_start.py !}
```

Здесь возможны два варианта:

* библиотека, которую мы используем для работы с брокером поддерживает механизм `callbacks` (как *aio-pika*, используемая для *RabbitMQ*)
* библиотека поддерживает только итерирование по сообщениям

Во втором случае нам повезло меньше и нам нужно превратить цикл в `callback`. Этого можно допиться, например, используя `asyncio.Task`, как в примере с *Redis*. Однако, в таком случае, нужно не забыть корректным образом завершить эти задачи в методе `close`.

```python linenums='1' hl_lines="15 25-26 44 54"
{!> docs_src/contributing/adapter/redis_start.py !}
```

После этого ваш брокер уже должен отправлять получаемые сообщения в функции, декорированные с помощью `handle`. Однако, пока эти функции будут падать с ошибкой.

## Обработка входящих сообщений

Для того, чтобы обработка входящих сообщений завершалась корректным образом, необходимо реализовать еще два метода: `_parse_message` и `_process_message`.

### _parse_message

Этот метод отвечает за приведение входящего сообщения к типу сообщений **Propan**.

```python linenums='1' hl_lines="10-12"
{!> docs_src/contributing/adapter/rabbit_parse.py !}
```

При этом обязательными полями являются только `body: bytes` и `raw_message: Any`. Остальные поля могут быть получены как из заголовков входящего сообщения, так и из его тела, если используемый брокер сообщений не имеет встроенных механизмов для передачи соответствующих параметров. Все зависит от вашей реализации метода `publish`.

### _process_message

Здесь все относительно просто: если используемый брокер сообщений поддерживает механизмы `ack`, `nack`, то мы должны обрабатывать их здесь. Также в этом месте просходит формирование ответного сообщения и его отправка для поддержки **RPC over MQ**. Если брокер не поддерживает подтверждение обработки сообщения, то мы просто выполняем наш `handler`.

Вот, например, вариант с обработкой состояния сообщения:

```python linenums='1' hl_lines="30"
{!> docs_src/contributing/adapter/rabbit_process.py !}
```

А вот - без обработки:

```python linenums='1' hl_lines="19"
{!> docs_src/contributing/adapter/redis_process.py !}
```

P.S: вот так уже будет работать, но без обработки состояния и **RPC**

```python
def _process_message(
    self, func: Callable[[PropanMessage], T], watcher: Optional[BaseWatcher]
) -> Callable[[PropanMessage], T]:
    @wraps(func)
    async def wrapper(message: PropanMessage) -> T:
        return await func(message)

    return wrapper
```

## Публикация сообщений

Последним шагом нам необходимо реализовать метод отправки сообщения. Это может быть как самый простой этап (если мы не хотим или не можем реализовать **RPC** сейчас), так и самым сложным и творческим.

В примере ниже я опущу реализацию **RPC**, так как для каждого брокера необходима своя отдельная реализация. Здесь мы будем просто отправлять сообщения.

```python linenums='1' hl_lines="21 23"
{!> docs_src/contributing/adapter/redis_publish.py !}
```

Поздравляю, после реализации всех этих методов у вас уже будет брокер, способный корректно отправлять и принимать сообщения.

## Логирование

Для того, чтобы ваш брокер логировал входящие сообщения в формате, специфичном для него, необходимо также переопределить несколько методов.

Для начала нужно сбросить стандартный способ логирования, переопределив метод `__init__`.

```python linenums='1' hl_lines="10"
{!> docs_src/contributing/adapter/rabbit_init.py !}
```

Затем, вам нужно определить формат логирования

```python linenums='1' hl_lines="17"
{!> docs_src/contributing/adapter/rabbit_fmt.py !}
```

Следующим шагом вам нужно реализовать метод `_get_log_context`, который будет добавлять в сообщение поля, специфичные для вашего брокера.

```python linenums='1' hl_lines="17"
{!> docs_src/contributing/adapter/rabbit_get_log_context.py !}
```

Данный метод всегда принимает первым аргументом `message`. Остальные аргументы вы должны передать туда сами.

Где? - Прямо в методе `handle`

```python linenums='1' hl_lines="11 13-14"
    ...
    def handle(
        self,
        queue: RabbitQueue,
        exchange: Union[RabbitExchange, None] = None,
        *,
        retry: Union[bool, int] = False,
    ) -> HandlerWrapper:

        def wrapper(func: HandlerCallable) -> HandlerCallable:
            func = self._wrap_handler(
                func,
                queue=queue,
                exchange=exchange,
                retry=retry,
            )
            ....
```

Все аргументы кастомные, переданные в функцию `_wrap_handler`, будут в дальнейшем переданы в вашу функцию `_get_log_context`.

Теперь ваш брокер не только отправляет и принимает сообщения, но и логирует входящие сообщения в собственном формате. Поздравляю, вы - великолепны!

!!! success ""
    Если вы реализовали подобный брокер для собственного источника, я очень жду ваш **PR**! Я готов помочь вам с тестированием, реализацией отдельных частей, документацией и всем остальным. Ваш труд обязательно станет частью **Propan**.
