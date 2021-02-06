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

## Основные сущности

```
SQL query -> Lexer -> Parser -> AST -> Interpreter -> Storage -> Table
```

 - TokenType - перечисление возможных токенов. Каждому токену сопоставляется регулярка
 - Token - токен. У токена есть тип, значение которое было считано из текста и позиция в тексте
 - Lexer - преобразует SQL текст в список Token-ов
 - Parser - реализует описанную грамматику. Для каждого правила грамматики - реализован отдельный метод. 
   Парсер считывает с машинной ленты (списка токенов) по одному токену и рекурсивно идет по правилам грамматики.
   В итоге для каждого правила он создает AST-ноду.
   Если не может распарсить правило грамматики, то отдает ошибку с указанием того какой токен ожидается и какой токен ошибочный
 - Nodes - реализация AST дерева. Для каждой сущности создается своя нода.
 - Interpreter - умеет обходить дерево и умеет понимать каким конкретно образом нужно обработать каждую ноду
 - Storage - псевдо-реализация базы данных.
 - Table - Абстракция над таблицами. Данные сохраняются в CSV файл. При поиске учитывается индекс. Т.е если идет поиск по нескольким полям и среди них есть индекс, то в первую очередь будет сделана выборка по индекса.
 - Отдельно есть тесты на каждый компонент

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

## Пример SQL комманд

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
