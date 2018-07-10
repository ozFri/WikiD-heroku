from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
from .models import timestamp, date, create_new_discussion,create_new_vote, get_aifNode_by_title, get_aifNode, create_feed_item, add_item_to_feed
from .models import graph
from datetime import datetime
import uuid
import os

class User:

    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.find_one("User", "username", self.username)
        return user

    def register(self, password):
        if not self.find():
            user = Node("User", username=self.username,
                        password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, user['password'])
        else:
            return False

    def add_S_Node(self,schema,sourceID,targetID):
        user= self.find()
        sourceNode=get_aifNode(sourceID)
        targetNode=get_aifNode(targetID)
        schemaNode= Node(
                "SNode",
                id=str(uuid.uuid4()),
                schema=schema,
                source=sourceNode.properties["title"],
                source_id=sourceID,
                target=targetNode.properties["title"],
                target_id=targetID,
                title=sourceNode.properties["title"]+" "+schema+" "+targetNode.properties["title"],
                timestamp=timestamp(),
                date=date()
                )
        authorship = Relationship(user, "PUBLISHED", schemaNode)
        graph.create(authorship)
        graph.create(Relationship(user, "FOLLOWS", schemaNode))
        feedItem = create_feed_item(user,schemaNode,"PUBLISHED")
        add_item_to_feed(feedItem,schemaNode)
        add_item_to_feed(feedItem,sourceNode)
        add_item_to_feed(feedItem,targetNode)
        return schemaNode.properties["id"]

    def add_I_Node(self, title):
        user = self.find()
        iNode = Node(
            "INode",
            id=str(uuid.uuid4()),
            title=title,
            timestamp=timestamp(),
            date=date()
        )
        rel = Relationship(user, "PUBLISHED", iNode)
        graph.create(rel)
        graph.create(Relationship(user, "FOLLOWS", iNode))
        feedItem = create_feed_item(user,iNode,"PUBLISHED")
        add_item_to_feed(feedItem,iNode)
        return iNode.properties["id"]

    #Tags Stuff
        #tags = [x.strip() for x in tags.lower().split(',')]
        #for t in set(tags):
            #tag = graph.merge_one("Tag", "name", t)
            #rel = Relationship(tag, "TAGGED", post)
            #graph.create(rel)

    def vote_on_aifnode(self, aifNode_id, discussion_name, vote_type):
        user = self.find()
        aifNode = get_aifNode(aifNode_id)
        cypher_string_find_discussion = \
            "MATCH (:User {username:'" + user.properties[ "username"] + "'})-[r]->(n:ENode {name:'" + discussion_name + "'})\
            RETURN count(n) "
        cypher_string_find_vote = \
            "MATCH (vote) WHERE \
            (:User {username:'" + user.properties[ "username"] + "'})-[:VOTED]->(vote:VNode)\
            AND (vote)-[:APPLIES_TO]->(:ENode {name:'" + discussion_name + "'})\
            AND (vote)-[:APPLIES_TO]->({id:'" + aifNode_id + "'})\
            RETURN vote"
        # check if user observes this discussion, and that it exists, otherwise, create it.
        vote = graph.evaluate(cypher_string_find_vote)
        if vote is not None:
            if vote["name"] == vote_type:
                # TODO: error
                return 'error'
            vote["name"] = vote_type
            graph.push(vote)
        else:
            if not graph.run(cypher_string_find_discussion).evaluate():
                discussion = create_new_discussion(user, discussion_name)
            else:
                discussion = graph.find_one("ENode", "name", discussion_name)
            create_new_vote(user, vote_type, discussion, aifNode)
        graph.merge(Relationship(user, "FOLLOWS", aifNode))
        feedItem = create_feed_item(user,aifNode,"VOTED '"+vote_type.upper()+"'")
        add_item_to_feed(feedItem,aifNode)

    def get_recent_posts(self):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(aifnode)
        WHERE user.username = {username}
        RETURN aifnode
        ORDER BY aifnode.timestamp DESC LIMIT 500
        """

        return graph.run(query, username=self.username)

    def get_user_feed(self):
        query = """
        MATCH (n),(u) WHERE (u:User)-[:FOLLOWS]-(n)
        AND u.username={username}
        MATCH (n),(latest) WHERE (n)-[:ACTIVITY_FEED]->(latest:FeedItem)
        MATCH (latest)-[:ACTIVITY_FEED_NEXT*""" + '0' + """..""" + '100' + """]->(item:FeedItem)
        MATCH (item)-[:TARGET]->(target)
        MATCH (item)-[:ACTOR]->(actor)
        RETURN DISTINCT item, actor, target
        """
        return graph.run(query,username=self.username)
    def get_news_feed(self):
        query = """
        MATCH (n) 
        WHERE (u:User)-[:FOLLOWS]-(n)
        MATCH (n)-[:ACTIVITY_FEED]->(latest:FeedItem)
        MATCH (latest)-[:ACTIVITY_FEED_NEXT*' + skip + '..' + end + ']->(item:FeedItem)
        MATCH (item)-[:TARGET]->(target)
        MATCH (item)-[:ACTOR]->(actor)
        RETURN DISTINCT item, actor, target
        """
        return graph.run(query).evaluate()

    def get_similar_users(self):
        # Find three users who are most similar to the logged-in user
        # based on tags they've both blogged about.
        query = """
        MATCH (you:User)-[:PUBLISHED]->(:INode)<-[:TAGGED]-(tag:Tag),
              (they:User)-[:PUBLISHED]->(:INode)<-[:TAGGED]-(tag)
        WHERE you.username = {username} AND you <> they
        WITH they, COLLECT(DISTINCT tag.name) AS tags, COUNT(DISTINCT tag) AS len
        ORDER BY len DESC LIMIT 3
        RETURN they.username AS similar_user, tags
        """

        return graph.run(query, username=self.username)

    def get_commonality_of_user(self, other):
        # Find how many of the logged-in user's posts the other user
        # has liked and which tags they've both blogged about.
        query = """
        MATCH (they:User {username: {they} })
        MATCH (you:User {username: {you} })
        OPTIONAL MATCH (they)-[:LIKED]->(post:INode)<-[:PUBLISHED]-(you)
        OPTIONAL MATCH (they)-[:PUBLISHED]->(:INode)<-[:TAGGED]-(tag:Tag),
                       (you)-[:PUBLISHED]->(:INode)<-[:TAGGED]-(tag)
        RETURN COUNT(DISTINCT post) AS likes, COLLECT(DISTINCT tag.name) AS tags
        """

        return graph.run(query, they=other.username, you=self.username)

    def register_validation(flash_func, user_name, password):
        if len(user_name) < 1:
            flash_func('Your username must be at least one character.')
            return False
        elif len(password) < 5:
            flash_func('Your password must be at least 5 characters.')
            return False
        elif not User(user_name).register(password):
            flash_func('A user with that username already exists.')
            return False
        else:
            return True
