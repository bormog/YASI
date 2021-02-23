- [Yet Another SQL Interpreter](#yet-another-sql-interpreter)
  * [Цели проекта](#цели-проекта)
  * [Фичи](#фичи)
  * [Грамматика](#грамматика)
  * [Как это работает](#как-это-работает)
    + [Основные понятия](#основные-понятия)
      - [Frontend](#frontend)
      - [Backend](#backend)
    + [Архитектура и основные сущности](#архитектура-и-основные-сущности)
      - [Лексический анализ](#лексический-анализ)
      - [Синтаксический анализ](#синтаксический-анализ)
      - [Интерпретация логики](#интерпретация-логики)
  * [Пример использования](#пример-использования)
  * [Пример SQL](#пример-sql)
  * [Демо](#демо)
  * [Тесты](#тесты)
  * [TODO](#todo)

# Yet Another SQL Interpreter

YASI - интерпретатор для подмножества SQL

## Цели проекта

- Получить знания о том как работают интерпретаторы
- Реализовать frontend-часть интерпретатора для ограниченного количества команд SQL

## Фичи

- Грамматика для SQL
- Lexer - разбивает текст на токены
- Parser - преобразует список токенов в дерево
- AST - хранит промежуточное состояние текста
- Interpreter - обходит дерево и выполняет нужные команды
- Storage - сторадж, который умеет писать/читать данные в csv
- Math expressions - поддержка математических выражений
- Unit and e2e тесты

## Грамматика

```
stmt_list -> stmt (stmt)*
stmt -> create_stmt
        | describe_stmt 
        | insert_stmt
        | select_stmt
create_stmt -> CREATE TABLE ID LPAREN PRIMARY KEY ID (COMMA ID)* RPAREN SEMICOLON
describe_stmt -> DESCRIBE ID SEMICOLON
insert_stmt -> INSERT INTO ID SET assignee_sub_stmt (assignee_sub_stmt)* SEMICOLON
select_stmt -> SELECT select_expr SEMICOLON
select_expr -> expr 
               | ID (COMMA ID)* FROM ID (WHERE assignee_sub_stmt (AND assignee_sub_stmt)* (order_sub_stmt)? (limit_sub_stmt)?)?
assignee_sub_stmt -> ID EQUALS value
order_sub_stmt -> ORDER BY ID (ASC | DESC)
limit_sub_stmt -> LIMIT NUMBER
value -> INT 
         | STRING
expr -> term ((PLUS | MINUS) term)*
term -> factor ((MUL | DIV) factor)*
factor -> INT 
          | LPAREN expr RPAREN
```

## Как это работает

### Основные понятия

**Интерпретатор** - программа, выполняющая построчный анализ, обработку и выполнение исходного кода программы (в отличие от компиляции, где весь текст программы, перед запуском, анализируется и транслируется в машинный или байт-код, без её выполнения).

Условно интерпретатор состоит из двух частей frontend и backend.

#### Frontend

[Чем занимается Frontend?](https://ps-group.github.io/compilers/what_is_frontend)
 - Получает на вход исходный текст программы
 - Проверяет текст на ошибки
 - Строит [Абстрактное Синтаксическое Дерево](https://ps-group.github.io/compilers/ast.html), хранящее логическую модель исхожного файла

В общем случае Frontend имеет 3 компонента: лексический, синтаксический, семантический анализатор

**Лексический анализатор** -  разбивает хаотичный поток входящих символов на лексемы. Он выделяет из исходного текста слова, числа, строковые константы, знаки операций и превращает их в атомарные сущности, с которыми далее удобно работать
**Синтаксический анализатор** - проверяет, что набор лексем, которые дал ему лексический анализатор является осмысленным, что перед нами программа, а не бессмысленный набор букв. Далее формируется AST
**Семантический анализатор** - проверяет программу на наличие семантических ошибок

#### Backend

[Чем занимается Backend?](https://ps-group.github.io/compilers/what_is_backend)
 - Получает на вход Абстрактное Синтаксическое Дерево
 - Backend создаёт на выходе машинный код. Это промежуточный код, который может быть исполнен на процессоре, либо на виртуальной машине


### Архитектура и основные сущности

В проекте реализована frontend-часть интерпретатора: лексический и синтаксический анализ.
Вместо backend-части осуществляется непосредственный обход AST с интерпретацией логики на каждом узле дерева.
Интерпретатор работает в один проход

#### Лексический анализ ####
За эту часть отвечают сущности: TokenType, Token, Lexer

 - TokenType - нужен для перечисления всех возможных токенов. Каждому токену сопоставляется регулярка
 - Token - токен. У токена есть тип, значение которое было считано из текста и позиция в тексте
 - Lexer - преобразует SQL текст в список Token-ов. Умеет отдавать ошибку, если исходный текст содержит незнакомый символ

#### Синтаксический анализ ####
За эту часть отвечают сущности: Parser, Nodes
 - Parser - реализует описанную [грамматику](https://ps-group.github.io/compilers/grammars.html). Для каждого правила грамматики - реализован отдельный метод. 
   Парсер считывает с машинной ленты (списка токенов) по одному токену и рекурсивно идет по правилам грамматики.
   В итоге для каждого правила он создает AST-ноду.
   Если не может распарсить правило грамматики, то отдает ошибку с указанием того какой токен ожидается и какой токен ошибочный
 - Nodes - реализация AST дерева. Для каждой сущности создается своя нода.

#### Интерпретация логики ####
За эту часть отвечают сущности: Interpreter, Storage, Table
 - Interpreter - умеет обходить дерево и умеет понимать каким конкретно образом нужно обработать каждую ноду
 - Storage - псевдо-реализация базы данных.
 - Table - Абстракция над таблицами. Данные сохраняются в CSV файл. При поиске учитывается индекс. Т.е если идет поиск по нескольким полям и среди них есть индекс, то в первую очередь будет сделана выборка по индекса.
 - Отдельно есть тесты на каждый компонент



В итоге порядок вызова всех сущностей при запуске интерпретатора выглядит так:
```
SQL query -> Lexer -> Parser -> AST -> Interpreter -> Storage -> Table
```


## Пример использования

```
from interpreter import Interpreter
from lexer import Lexer
from parser import Parser

working_dir = os.getenv("WORKING_DIR")
text = "create table foobar (primary key uid, foo, bar);"
interpreter = Interpreter(tree=Parser(lex=Lexer(text)).parse(), working_dir=working_dir)
result = interpreter.do()
```

## Пример SQL

```
create table languages (primary key uid, name, num_of_jobs, avg_salary);
describe languages;
insert into languages set uid=11, name='Python', num_of_jobs=19000, avg_salary=120000;
select 1;
select (2+3) * (10-8) / 2;
select uid, name, num_of_jobs, avg_salary from languages;
select uid, num_of_jobs, avg_salary from languages where name='Python';
select name, avg_salary from languages order by avg_salary desc limit 3;
```

## Демо

https://yasqli.herokuapp.com/

## Тесты

``` bash
python -m unittest discover -v
```

## TODO
 - Генератор кода - обходит AST дерево и генерит промежуточный код для интерпретатора
 - Виртуальная машина с поддержкой логических выражений (OR, AND, >, <, >=, <=, !=)
