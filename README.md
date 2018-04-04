# WikiD - a wicked problem solver

##Etymology

WikiD -  WikiDiscussion or WikiDiyun - ויקידיון  - WikiDiscussion just in hebrew, 
Wiki - means [fast](http://wiki.c2.com/?WikiWiki), so essentially a faster way to discuss stuff

## What is this?

WikiD is a platform for discussion and decision making in large groups.

## That sounds neat, but what does it do?

WikiD lets people write statements they believe in, or want to discuss.

It allows users to vote on these statements, and in the future, will also add the option to tag them with all kinds of informative tags, and link the statements to all kinds of relevant data and resources.

WikiD also lets users connect one statement to another, mapping their relation to each other - for example, 
> <u>statement A</u> supports <u>*statement B*</u>

A cool property of WikiD is that it treats all these relations as if they werestatements on their own right. So they can be linked as well.

All together this will generate a discussion graph, mapping the inputs and opinions of the various users - and it also takes different contexts into account -, WikiD users become participants in the general discussion, and in smaller, more focused discussions they will define.

Besides content creation, WikiD is set to let users follow and browse these statements and discussions, in an easy, engaging, informative and efficient way.

## Is it all really necessary?

It is, because people usually simply can't have a meaningful discussion once agroup becomes slightly large

>To Be Continued


## But you said "wicked problem solver"

It's only a slogan - 

but seriously: Harnessing the input and decision making abilities of the large
number of people involved with them, may help solve [wicked problems](https://en.wikipedia.org/wiki/Wicked_problem)

>To Be Continued

## How does it work?

>To Be Continued

###Hint
This repository started as a fork of the very nice tutorial [neo4j-flask](https://nicolewhite.github.io/neo4j-flask/) by Nicole White, so you may check it
if you need a hint to see where is north and where is up before getting into the mess

## Installation - 

Make sure [Neo4j](http://neo4j.com/download/other-releases/) is running first!

**If you're on Neo4j >= 2.2, make sure to set environment variables `NEO4J_USERNAME` and `NEO4J_PASSWORD`
to your username and password, respectively:**

```
$ export NEO4J_USERNAME=username
$ export NEO4J_PASSWORD=password
```

Or, set `dbms.security.auth_enabled=false` in `conf/neo4j-server.properties`.

Then with bash shell:

```
cd cloned_dir
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```
with fish shell:

```
cd cloned_dir
pip install virtualenv
virtualenv venv
. venv/bin/activate.fish
pip install -r requirements.txt
python run.py
```


[http://localhost:5000](http://localhost:5000)
