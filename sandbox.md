
# shell関連
## console
ターミナルの出力用。

```console:console
$ apt-cache depends auditd
auditd
  依存: lsb-base
 |依存: mawk
  依存: gawk
  依存: init-system-helpers
  依存: libaudit1
  依存: libauparse0
  依存: libc6
  依存: libgssapi-krb5-2
  依存: libkrb5-3
  依存: libwrap0
  提案: audispd-plugins
$
```

## bash
[cowgill/spamhaus](https://github.com/cowgill/spamhaus)より`spamhaus.sh`を例示。

```bash:spamhaus.sh
#!/bin/bash

# based off the following two scripts
# http://www.theunsupported.com/2012/07/block-malicious-ip-addresses/
# http://www.cyberciti.biz/tips/block-spamming-scanning-with-iptables.html

# path to iptables
IPTABLES="/sbin/iptables";

# list of known spammers
URL="www.spamhaus.org/drop/drop.lasso";

# save local copy here
FILE="/tmp/drop.lasso";

# iptables custom chain
CHAIN="Spamhaus";

# check to see if the chain already exists
$IPTABLES -L $CHAIN -n

# check to see if the chain already exists
if [ $? -eq 0 ]; then

    # flush the old rules
    $IPTABLES -F $CHAIN

    echo "Flushed old rules. Applying updated Spamhaus list...."    

else

    # create a new chain set
    $IPTABLES -N $CHAIN

    # tie chain to input rules so it runs
    $IPTABLES -A INPUT -j $CHAIN

    # don't allow this traffic through
    $IPTABLES -A FORWARD -j $CHAIN

    echo "Chain not detected. Creating new chain and adding Spamhaus list...."

fi;

# get a copy of the spam list
wget -qc $URL -O $FILE

# iterate through all known spamming hosts
for IP in $( cat $FILE | egrep -v '^;' | awk '{ print $1}' ); do

    # add the ip address log rule to the chain
    $IPTABLES -A $CHAIN -p 0 -s $IP -j LOG --log-prefix "[SPAMHAUS BLOCK]" -m limit --limit 3/min --limit-burst 10

    # add the ip address to the chain
    $IPTABLES -A $CHAIN -p 0 -s $IP -j DROP

    echo $IP

done

echo "Done!"

# remove the spam list
unlink $FILE
```


# Python関連
## python, py, python3, py3
- python, py
 - Python (filenames *.py, *.pyw, *.sc, SConstruct, SConscript, *.tac)
- python3, py3
 - Python 3

これはそのまま、pythonソース。pythonとpython3で微妙に表示が異なる。

### python/python3例
```python:python
import re
import sys
import json
import six
from voluptuous import Schema, Required, Any, Range, Invalid, ALLOW_EXTRA


def validate_io_size(v):
	if re.search("^[0-9]+[bkm]", v) is None:
		raise Invalid("not a valid value (%s)" % str(v))


def get_schema():
	schema = Schema({
		"comment"					: six.text_type,
		Required("operation")		: Any("read", "write"),
		"thread"					: Range(min=1),
		Required("io_size")			: validate_io_size,
		Required("access_percentage")	: Range(min=1, max=100),
	}, extra=ALLOW_EXTRA)
	
	return schema


def main():
	schema	= get_schema()
	
	with open(sys.argv[1], "r") as fp:
		dict_sample	= json.load(fp)
	
	schema(dict_sample)
	six.print_(dict_sample)
	
	return 0


if __name__ == '__main__':
	sys.exit(main())
```

```python3:python3
import re
import sys
import json
import six
from voluptuous import Schema, Required, Any, Range, Invalid, ALLOW_EXTRA


def validate_io_size(v):
	if re.search("^[0-9]+[bkm]", v) is None:
		raise Invalid("not a valid value (%s)" % str(v))


def get_schema():
	schema = Schema({
		"comment"					: six.text_type,
		Required("operation")		: Any("read", "write"),
		"thread"					: Range(min=1),
		Required("io_size")			: validate_io_size,
		Required("access_percentage")	: Range(min=1, max=100),
	}, extra=ALLOW_EXTRA)
	
	return schema


def main():
	schema	= get_schema()
	
	with open(sys.argv[1], "r") as fp:
		dict_sample	= json.load(fp)
	
	schema(dict_sample)
	six.print_(dict_sample)
	
	return 0


if __name__ == '__main__':
	sys.exit(main())
```

## pycon
- Python console session

多分↓のようにコンソールでpython起動したときのコンソール出力用。

```console
# python
Python 2.5.2 (r252:60911, Jan 24 2010, 14:53:14)
[GCC 4.3.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

### pycon例
http://docs.python.jp/2/library/random.html　より
pythonコンソール出力例をpyconで修飾した例。

```pycon:pycon
>>> random.random()        # Random float x, 0.0 <= x < 1.0
0.37444887175646646
>>> random.uniform(1, 10)  # Random float x, 1.0 <= x < 10.0
1.1800146073117523
>>> random.randint(1, 10)  # Integer from 1 to 10, endpoints included
7
>>> random.randrange(0, 101, 2)  # Even integer from 0 to 100
26
>>> random.choice('abcdefghij')  # Choose a random element
'c'

>>> items = [1, 2, 3, 4, 5, 6, 7]
>>> random.shuffle(items)
>>> items
[7, 3, 2, 5, 6, 4, 1]

>>> random.sample([1, 2, 3, 4, 5],  3)  # Choose 3 elements
[4, 1, 5]
```

## pytb/py3tb
- pytb
 - Python Traceback (filenames *.pytb)
- py3tb:
 - Python 3.0 Traceback (filenames *.py3tb)

pythonが出力するスタックトレース用。

### pytb/py3tb例
以下の例ではpytbとpy3tbの違いは見えなかった。

```pytb:pytb
Traceback (most recent call last):
  File "<doctest...>", line 10, in <module>
    lumberjack()
  File "<doctest...>", line 4, in lumberjack
    bright_side_of_death()
IndexError: tuple index out of range
```

```py3tb:py3tb
Traceback (most recent call last):
  File "<doctest...>", line 10, in <module>
    lumberjack()
  File "<doctest...>", line 4, in lumberjack
    bright_side_of_death()
IndexError: tuple index out of range
```


# SQL関連
## sql
SQLクエリ用。

```sql:sql
SELECT hoge FROM table_namme WHERE value > 0
```

## sqlite3

```sqlite3:sqlite3
$ sqlite3
SQLite version 3.8.7.1 2014-10-29 13:59:56
Enter ".help" for usage hints.
Connected to a transient in-memory database.
Use ".open FILENAME" to reopen on a persistent database.
sqlite> create table hoge(key text, value integer);
sqlite> insert into hoge values("a", 1);
sqlite> insert into hoge values("b", 2);
sqlite> insert into hoge values("c", 3);
sqlite>
sqlite> select key, value from hoge;
a|1
b|2
c|3
sqlite>
```


# HTML関連
## HTML
```html:html
<html>
	<head>
		<title>Hello world</title>
	</head>
	<body>
		Hello world
	</body>
</html>
```

## CSS
カスケーディング・スタイル・シート用。

```css:css
h1, h2, h3, h4 { margin-top: 0.5em; margin-bottom: 0.1em; }

h3 { margin-left: 0.5em; }
h4 { margin-left: 1.5em; }

body { counter-reset: part; }
h2 { counter-reset: chapter; }
h2:before {
	content: counter(part) ". ";
	counter-increment: part;
}

h3 { counter-reset: section; }
h3:before {
	content: counter(part) "." counter(chapter) ". ";
	counter-increment: chapter;
}

h4 { counter-reset: subsection; }
h4:before {
	content: counter(part) "." counter(chapter) "." counter(section) ". ";
	counter-increment: section;
}
```


# Linuxコマンド出力
## diff
```diff
--- lhs 2016-01-05 08:13:48.341912876 +0900
+++ rhs 2016-01-05 08:14:19.913913237 +0900
@@ -1,4 +1,4 @@
 hoge
-foo
+aaaaaaaaaaaaa
 bar
-
+bbbbbbbbbbbbbbb
```


# その他
## JSON
一覧にはなかったが、JSONもシンタックスハイライトが有効。

```json:JSON
{
	"text"		: "value",
	"value"		: 100,
	"list"		: ["a", "b", "c"],
	"nest_dict"	: {
		"child"	: 1
	}
}
```


## YAML
pygmentsの[デモ](http://pygments.org/demo/97004/)より

```yaml:yaml
time: 120
title: 'i??i??i?， i≫¨i??i??i?，'
contestpw: '0000'

languages:
  -
    display: 'GNU C 4.6.2'
    compile: 'gcc -lm -O2 -o {:basename}.exe {:mainfile}'
    execute: '{:basename}.exe'
    binary: '{:basename}.exe'
  -
    display: 'GNU C++ 4.6.2'
    compile: 'g++ -O2 -o {:basename}.exe {:mainfile}'
    execute: '{:basename}.exe'
    binary: '{:basename}.exe'
  -
    display: 'Microsoft Visual C++ 2010'
    compile: 'cl /Ox {:mainfile}'
    execute: '{:mainfile}.exe'
    binary: '{:mainfile}.exe'
  -
    display: 'Oracle Java SE 7'
    compile: 'javac {:mainfile}'
    execute: 'java {:basename}'
    binary: '{:basename}.class'

problems:
  -
    title: 'HELLOWORLD'
    input: './problems/HELLOWORLD/helloworld.in'
    output: './problems/HELLOWORLD/helloworld.out'
    timelimit: 10
    external_validation: yes
    validator: './validators/Validator.jar'
    validationcmd: 'java -jar {:validator} {:infile} {:outfile} {:ansfile} {:resfile} rz'
    color: 'color0'
  -
    title: 'HELLOWORLD2'
    input: './problems/HELLOWORLD/helloworld.in'
    output: './problems/HELLOWORLD/helloworld.out'
    timelimit: 1
    external_validation: no
    validator: 1
    validator_ignorecase: yes
    color: 'color1'

judgements:
  - 'Yes'
  - 'No - Compilation Error'
  - 'No - Run-time Error'
  - 'No - Time-limit Exceeded'
  - 'No - Wrong Answer'
  - 'No - Excessive Output'
  - 'No - Output Format Error'
  - 'No - Other - Contact Staff'

groups:
  - { name: 'KAIST', scoreboard: yes }
  - { name: 'Test accounts', scoreboard: no }

accounts:
  admins: # default scoreboard: no
    # default administrator -> 1
    - { name: 'Administrator 2', password: '0000' }

  judges: # default scoreboard: no
    - { name: 'Judge 1', password: 'judge1' }
    - { name: 'Judge 2', password: 'judge2' }

  scoreboards: # default scoreboard: no
    - { name: 'Scoreboard 1', password: 'scoreboard1' }
    - { name: 'Scoreboard 2', password: 'scoreboard2' }

  teams: # default scoreboard: yes
    - { name: 'Team 1', group: 1, password: 'team1' }
    - { name: 'Team 2', group: 2, password: 'team2' }
    - { name: 'Team 3', password: 'team3' }
    - { name: 'Team 4', scoreboard: no, password: 'team4' }
```

ansible playbook形式だとあまり恩恵が見えない。

```yaml:yaml
---
- name: reboot OS
  hosts: server-under-test
  gather_facts: no
  tasks:
    - name: reboot
      shell: reboot
      async: 0
      poll: 0 

    - name: wait for SSH port down
      local_action: wait_for host={{ inventory_hostname }} port=22 state=stopped

    - name: wait for SSH port up
      local_action: wait_for host={{ inventory_hostname }} port=22 state=started delay=10

    - pause: seconds=5
```
