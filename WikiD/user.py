from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
from .models import timestamp, date, create_new_event
from .db_connection import graph
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

    def add_post(self, title):
        user = self.find()
        post = Node(
            "Post",
            id=str(uuid.uuid4()),
            title=title,
            timestamp=timestamp(),
            date=date()
        )
        rel = Relationship(user, "PUBLISHED", post)
        graph.create(rel)

#        tags = [x.strip() for x in tags.lower().split(',')]
#        for t in set(tags):
#            tag = graph.merge_one("Tag", "name", t)
#            rel = Relationship(tag, "TAGGED", post)
#            graph.create(rel)

    def votetozero(self, event, post):
        oldvote = graph.match(start_node=event, rel_type=None, end_node=post)
        if oldvote is not None:
            for rel in oldvote:
                graph.delete(rel)

    def agree_with_post(self, post_id, event_name):
        user = self.find()
        post = graph.find_one("Post", "id", post_id)
        cypher_string_find_event = "MATCH (n:User {username:'" + user.properties[
            "username"] + "'})-[r]->(:Enode {name:'" + event_name + "'})            RETURN count(n) "
        # check if user observes this event, and that it exists.
        if not graph.cypher.execute(cypher_string_find_event).one:
            event = create_new_event(user, event_name)
        else:
            event = graph.find_one("Enode", "name", event_name)
        self.votetozero(event, post)
        graph.create_unique(
            Relationship(user, "IN_EVENT", event),
            Relationship(event, "AGREES_WITH", post))

    def disagree_with_post(self, post_id, event_name):
        user = self.find()
        post = graph.find_one("Post", "id", post_id)
        cypher_string = "MATCH (n:User {username:'" + user.properties[
            "username"] + "'})-[r]->(:Enode {name:'" + event_name + "'})            RETURN count(n) "
        # check if user observes this event, and that it exists.
        if not graph.cypher.execute(cypher_string).one:
            event = create_new_event(user, event_name)
        else:
            event = graph.find_one("Enode", "name", event_name)
        self.votetozero(event, post)
        graph.create_unique(
            Relationship(user, "IN_EVENT", event),
            Relationship(event, "DISAGREES_WITH", post))

    def undecided_on_post(self, post_id, event_name):
        user = self.find()
        post = graph.find_one("Post", "id", post_id)
        cypher_string = "MATCH (n:User {username:'" + user.properties[
            "username"] + "'})-[r]->(:Enode {name:'" + event_name + "'})            RETURN count(n) "
        # check if user observes this event, and that it exists.
        if not graph.cypher.execute(cypher_string).one:
            event = create_new_event(user, event_name)
        else:
            event = graph.find_one("Enode", "name", event_name)
        self.votetozero(event, post)
        graph.create_unique(
            Relationship(user, "IN_EVENT", event),
            Relationship(event, "UNDECIDED_ON", post)
        )

    def like_post(self, post_id):
        user = self.find()
        post = graph.find_one("Post", "id", post_id)
        graph.create_unique(Relationship(user, "LIKED", post))

    def get_recent_posts(self):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(post:Post)
        WHERE user.username = {username}
        RETURN post
        ORDER BY post.timestamp DESC LIMIT 500
        """

        return graph.cypher.execute(query, username=self.username)

    def get_similar_users(self):
        # Find three users who are most similar to the logged-in user
        # based on tags they've both blogged about.
        query = """
        MATCH (you:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
              (they:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        WHERE you.username = {username} AND you <> they
        WITH they, COLLECT(DISTINCT tag.name) AS tags, COUNT(DISTINCT tag) AS len
        ORDER BY len DESC LIMIT 3
        RETURN they.username AS similar_user, tags
        """

        return graph.cypher.execute(query, username=self.username)

    def get_commonality_of_user(self, other):
        # Find how many of the logged-in user's posts the other user
        # has liked and which tags they've both blogged about.
        query = """
        MATCH (they:User {username: {they} })
        MATCH (you:User {username: {you} })
        OPTIONAL MATCH (they)-[:LIKED]->(post:Post)<-[:PUBLISHED]-(you)
        OPTIONAL MATCH (they)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
                       (you)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        RETURN COUNT(DISTINCT post) AS likes, COLLECT(DISTINCT tag.name) AS tags
        """

        return graph.cypher.execute(query, they=other.username, you=self.username)[0]

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
