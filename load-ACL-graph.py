from owlready2 import *
import gremlin_python
from gremlin_python.structure.graph import Graph
from gremlin_python.driver import client
from tqdm import tqdm
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
import pandas as pd
from gremlin_python.process.traversal import T
from gremlin_python.process.traversal import Order
from gremlin_python.process.traversal import Cardinality
from gremlin_python.process.traversal import Column
from gremlin_python.process.traversal import Direction
from gremlin_python.process.traversal import Operator
from gremlin_python.process.traversal import P
from gremlin_python.process.traversal import Pop
from gremlin_python.process.traversal import Scope
from gremlin_python.process.traversal import Barrier
from gremlin_python.process.traversal import Bindings
from gremlin_python.process.traversal import WithOptions

#Connessione al Grafo
graph = Graph()
g = graph.traversal().withRemote(DriverRemoteConnection('ws://127.0.0.1:8182/gremlin','g'))


boko = g.V().has("name","Boko Haram").next()

#boko haram criminals
abubakar  = g.V().has("name", "Abubakar Shekau").next()

abubakar.property("level",3)
albarnawi = g.addV("person").property("label_vp","person").property("name", "Al Barnawi").property("level",3).next()
abubakar  = g.addV("person").property("label_vp","person").property("name", "Abubakar Shekau").property("level",3).next()
momodu  = g.addV("person").property("label_vp","person").property("name", "Momodu Bama").property("level",3).next()
abatcha  = g.addV("person").property("label_vp","person").property("name", "Abatcha Flatari").property("level",3).next()

#boko haram edges
g.addE("has_member").from_(boko).to(albarnawi).property("label_ep","has_member").property("access_rights","extends_rights").next()
g.addE("has_member").from_(boko).to(abubakar).property("label_ep","has_member").property("access_rights","extends_rights").next()
g.addE("has_member").from_(boko).to(momodu).property("label_ep","has_member").property("access_rights","extends_rights").next()
g.addE("has_member").from_(boko).to(abatcha).property("label_ep","has_member").property("access_rights","extends_rights").next()

g.addE("has_leader").from_(momodu).to(abubakar).property("label_ep","has_leader").next()
g.addE("has_father").from_(momodu).to(abatcha).property("label_ep","has_father").next()

#boko haram documents
intercept = g.addV("work").property("label_vp","work").property("name", "Intercept-003765").property("level",4).next()
report1 = g.addV("work").property("label_vp","work").property("name", "Report-007351").property("level",3).next()
satphoto = g.addV("work").property("label_vp","work").property("name", "N47").property("level",3).next()

#boko haram edges
g.addE("mentioned_in").from_(albarnawi).to(intercept).property("label_ep","mentioned_in").property("access_rights","extends_rights").next()
g.addE("mentioned_in").from_(albarnawi).to(report1).property("label_ep","mentioned_in").property("access_rights","extends_rights").next()
g.addE("mentioned_in").from_(albarnawi).to(satphoto).property("label_ep","mentioned_in").property("access_rights","extends_rights").next()


isis = g.V().has("name","Islamic state").next()
#isis criminals
qurashi = g.addV("person").property("label_vp","person").property("name", "Al Qurashi").property("level",3).next()
baghdadi = g.addV("person").property("label_vp","person").property("name", "Al Baghdadi").property("level",3).next()

#isis edges
g.addE("has_member").from_(isis).to(qurashi).property("label_ep","has_member").property("access_rights","extends_rights").next()
g.addE("has_member").from_(isis).to(baghdadi).property("label_ep","has_member").property("access_rights","extends_rights").next()

#isis documents
report2 = g.addV("work").property("label_vp","work").property("name", "Report-007484").property("level",4).next()
report3 = g.addV("work").property("label_vp","work").property("name", "Report-007507").property("level",3).next()
video = g.addV("work").property("label_vp","work").property("name", "Video 03-05").property("level",3).next()

#isis edges
g.addE("mentioned_in").from_(baghdadi).to(intercept).property("label_ep","mentioned_in").property("access_rights","extends_rights").next()
g.addE("mentioned_in").from_(qurashi).to(report2).property("label_ep","mentioned_in").property("access_rights","extends_rights").next()
g.addE("mentioned_in").from_(qurashi).to(report3).property("label_ep","mentioned_in").property("access_rights","extends_rights").next()


#ben ziane
benziane = g.addV("person").property("label_vp","person").property("name", "Ben Ziane Berhili").property("level",3).next()
report4 = g.addV("work").property("label_vp","work").property("name", "Report-007215").property("level",3).next()
g.addE("mentioned_in").from_(benziane).to(report4).property("label_ep","mentioned_in").property("access_rights","extends_rights").next()
g.addE("mentioned_in").from_(benziane).to(report2).property("label_ep","mentioned_in").property("access_rights","extends_rights").next()
lochphoto = g.addV("work").property("label_vp","work").property("name", "Local Photo").property("level",3).next()
g.addE("has_attachment").from_(report4).to(lochphoto).property("label_ep","has_attachment").property("access_rights","extends_rights").next()

#city
rabat = g.V().has("name","Rabat").next()
g.addE("seen_in").from_(qurashi).to(rabat).property("label_ep","seen_in").next()
g.addE("seen_in").from_(benziane).to(rabat).property("label_ep","seen_in").next()
g.addE("mentioned_in").from_(rabat).to(report2).property("label_ep","mentioned_in").next()



#USER'S EDGES
linda = g.addV("user").property("label_vp","user").property("username", "Agent Linda").property("level",4).next()
rick = g.addV("user").property("label_vp","user").property("username", "Agent Rick").property("level",4).next()
john = g.addV("user").property("label_vp","user").property("username", "Agent John").property("level",3).next()
paul = g.addV("user").property("label_vp","user").property("username", "Agent Paul").property("level",3).next()
patricia = g.addV("user").property("label_vp","user").property("username", "Agent Patricia").property("level",4).next()

africa = g.addV("group").property("label_vp","group").property("groupname", "Africa NSA Dept.").next()
middle = g.addV("group").property("label_vp","group").property("groupname", "Middle East NSA Dept.").next()
office = g.addV("group").property("label_vp","group").property("groupname", "Office").next()
director = g.addV("role").property("label_vp","role").property("rolename", "Director").next()

g.addE("part_of").from_(linda).to(middle).property("label_ep","part_of").next()
g.addE("part_of").from_(rick).to(middle).property("label_ep","part_of").next()

g.addE("part_of").from_(john).to(office).property("label_ep","part_of").next()
g.addE("part_of").from_(paul).to(office).property("label_ep","part_of").next()
g.addE("part_of").from_(office).to(africa).property("label_ep","part_of").next()
g.addE("part_of").from_(patricia).to(africa).property("label_ep","part_of").next()

g.addE("part_of").from_(rick).to(director).property("label_ep","part_of").next()
g.addE("part_of").from_(patricia).to(director).property("label_ep","part_of").next()

#AUTHORIZATION EDGES

g.addE("access_rights").from_(africa).to(boko).property("label_ep","access_rights").property("access_rights","can").next()
g.addE("access_rights").from_(middle).to(isis).property("label_ep","access_rights").property("access_rights","can").next()
g.addE("access_rights").from_(linda).to(benziane).property("label_ep","access_rights").property("access_rights","can").next()
g.addE("access_rights").from_(paul).to(satphoto).property("label_ep","access_rights").property("access_rights","cannot").next()

g.addE("access_rights").from_(director).to(boko).property("label_ep","access_rights").property("access_rights","can").next()
g.addE("access_rights").from_(director).to(isis).property("label_ep","access_rights").property("access_rights","can").next()