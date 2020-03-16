#!/usr/bin/env python
# coding: utf-8

# # Quick References
#  - [Aggiunta classi ontologia DBPedia](#addClassDBPedia)
#  - [Aggiunta classi dell'ontologia di Dominio](#addClassDomain)
#  - [Aggiunta Entità (Resource) di DBPedia con il relativo tipo](#addEntityDBPedia)

# In[1]:


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


# In[2]:


#Connessione al Grafo
graph = Graph()
g = graph.traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin','g'))


# In[3]:


#TOP ONTOLOGY LIST
onto_list = ["person","organisation","place","action","activity","work","identifier","event","thing"]


# <a id='addClassDBPedia'></a>
# ## Aggiunta classi dell'ontologia di DBPedia

# In[4]:


onto = None
onto = get_ontology("dbpedia_2016-10.owl")
onto.load()


# In[5]:


#aggiungiamo la classe di Thing non presente nell'ontologia di DBPedia in quanto è di W3C, ricercandola tra gli IS_a della ontologia
for x in onto.classes():
    if x.is_a[0].name == 'Thing':
        thing = x.is_a[0]
        break
tmp = [x for x in onto.classes()]
tmp.insert(0, tmp[6].is_a[0])

v = g.addV("ontology").property("label_vp","ontology").property("name", "Thing").property("iri", "http://www.w3.org/2002/07/owl#Thing").property("group","all").property("level",0).property("owner","all").property("closure","Thing").property("topOntology", "thing")
v.next()
# In[ ]:


#creazione delle classi relative all'ontologia (per i links vedi successivo)
print('creazione delle classi relative all\'ontologia')

for x in tqdm(tmp):
    v = g.addV("ontology").property("label_vp","ontology").property("name", x.name).property("iri", x.iri).property("group","all").property("level",0).property("owner","all")
    try:
        v = v.property("comment",comment[x].en[0]) 
    except:
        pass
    
    topOntology_property = x.name.lower() if x.name.lower() in onto_list else None
    v.property('closure',x.name)
    while len(x.is_a) > 0 :
        v.property('closure',x.is_a[0].name)
        x = x.is_a[0]
        if topOntology_property is None and x.name.lower() in onto_list:
            topOntology_property = x.name.lower()
    v.property('topOntology', topOntology_property)
    try:
        v.next()
    except:
        print('except')


# In[ ]:


#aggiunta link rdfs:subclassof tra le classi dell'ontologia.
print('aggiunta link rdfs:subclassof tra le classi dell\'ontologia')

tmp = [x for x in onto.classes()]
for x in tqdm(tmp):
    if len(x.is_a) != 0:
        #print("1_"+str(x.iri))
        child = g.V().has("iri",x.iri).next()
        #print("2_"+str(x.is_a[0].iri))
        father = g.V().has("iri",x.is_a[0].iri).next()
    g.addE("rdfs:subclassof").from_(child).to(father).property("label_ep","rdfs:subclassof").property("group","all").property("level",0).property("owner","all").next()


# In[ ]:


g.V().count().next()


# <a id='addClassDomain'></a>
# # Aggiunta classi dell'ontologia di Dominio

# In[ ]:


ontoDomain = get_ontology("init_utils/load_ontology/domain_ontology.owl")
ontoDomain.load()


# In[ ]:

print('caricamento ontologia di dominio')
tmp = [x for x in ontoDomain.classes()]
for x in tqdm(tmp):
    v = g.addV("ontology").property("label_vp","ontology").property("name", x.name).property("iri", x.iri).property("group","all").property("level",0).property("owner","all")

    
    commentJoin=""
    try:
        commentJoin+= comment[x].en[0]
    except:
        pass
    try:
        commentJoin+= comment[x].it[0]
    except:
        pass
    
    topOntology_property = x.name.lower() if x.name.lower() in onto_list else None
    v = v.property("comment",commentJoin).property('closure',x.name)
    while len(x.is_a) > 0 :
        v.property('closure',x.is_a[0].name)
        x = x.is_a[0]
        if topOntology_property is None and x.name.lower() in onto_list:
            topOntology_property = x.name.lower()
    v.property('topOntology', topOntology_property)
    v.next()

for x in tqdm(tmp):
    if len(x.is_a) == 0:
        continue
    child = g.V().has("iri",x.iri).next()
    father = g.V().has("iri",x.is_a[0].iri).next()
    g.addE("rdfs:subclassof").from_(child).to(father).property("label_ep","rdfs:subclassof").property("group","all").property("level",0).property("owner","all").next()


# <a id='addEntityDBPedia'></a>
# # Aggiunta Entità (Resource) di DBPedia con il relativo tipo

# In[ ]:


rdf_df= pd.read_csv("instance_types_en.ttl",delim_whitespace=True,header=None)
rdf_df.drop(3,axis=1,inplace=True)
rdf_df.columns=["s","p","o"]


# In[ ]:


rdf_df = rdf_df[rdf_df["o"].apply(lambda x: "http://dbpedia.org/ontology/" in x or "http://www.w3.org/2002/07/owl#Thing" in x)]
rdf_df = rdf_df.applymap(lambda x : x.replace("<","").replace(">",""))
rdf_df.head()


print('Aggiunta di label, comment e location alle entità')
# ##### Aggiunta Label (EN) alle varie entità caricate

# In[ ]:


label_df = pd.read_csv("labels_en.ttl",escapechar="\\",delim_whitespace=True,header=None)
label_df.drop(3,axis=1,inplace=True)
label_df.columns=["s","p","label"]
label_df.drop("p",axis=1,inplace=True)
label_df = label_df.applymap(lambda x : x.replace("<","").replace(">",""))
label_df["label"] = label_df["label"].apply(lambda x: x.replace("@en","")) 


# In[ ]:


label_df.head()


# ##### Aggiunta Comment (EN) alle varie entità caricate

# In[ ]:


rdf_comment = pd.read_csv("short_abstracts_en.ttl",delim_whitespace=True,encoding="utf-8", escapechar='\\',header=None)
rdf_comment.drop(3,axis=1,inplace=True)
rdf_comment.columns=["s","p","comment"]
rdf_comment = rdf_comment[rdf_comment["p"].apply(lambda x: "http://www.w3.org/2000/01/rdf-schema#comment" in x)]
rdf_comment.drop("p",axis=1,inplace=True)
rdf_comment["s"] = rdf_comment["s"].apply(lambda x : x.replace("<","").replace(">",""))
rdf_comment["comment"] = rdf_comment["comment"].apply(lambda x : x.replace("@en",""))


# In[ ]:


rdf_comment.head()

# ##### Aggiunta GEO Location (LAT LON)(EN) alle varie entità caricate

# In[67]:


rdf_geo = pd.read_csv("geo_coordinates_en.ttl", encoding="utf-8", delim_whitespace=True, escapechar='\\', header=None)
rdf_geo.drop(3, axis=1, inplace=True)
rdf_geo.columns = ["s", "p", "coordinates"]
rdf_geo = rdf_geo[rdf_geo["p"] == "<http://www.georss.org/georss/point>"]
rdf_geo.drop("p", axis=1, inplace=True)
rdf_geo["coordinates"] = rdf_geo["coordinates"].replace(to_replace="\^\^.*", value="", regex=True)
lat_lon = rdf_geo["coordinates"].str.split(" ", n=1, expand=True)
rdf_geo["lat"] = lat_lon[0]
rdf_geo["lon"] = lat_lon[1]
rdf_geo.drop("coordinates", axis=1, inplace=True)
rdf_geo = rdf_geo.applymap(lambda x : x.replace("<","").replace(">",""))
# In[68]:


rdf_geo.head()

# In[69]:


rdf_df = rdf_df.merge(label_df, on="s", how="left")
rdf_df = rdf_df.merge(rdf_comment, on="s", how="left")
rdf_df = rdf_df.merge(rdf_geo, on="s", how="left")

# In[70]:


rdf_df.head()


# In[ ]:


tmp = [x for x in onto.classes()]
tmp.append(tmp[6].is_a[0])
tmp_iri = [x.iri for x in onto.classes()]
tmp_iri.append(tmp[6].is_a[0].iri)



def top_ontology(s):
    if(s["o"]=='http://www.w3.org/2002/07/owl#Thing'):
        return onto_list[-1]
    else:
        t = tmp[tmp_iri.index(s["o"])]
        while len(t.is_a) > 0:
            for to in onto_list:
                if to == t.name.lower():
                    return to
            t = t.is_a[0]
        return onto_list[-1]


# In[ ]:


onto_node_and_closure = {}
tmp_iri.append('http://www.w3.org/2002/07/owl#Thing')

for iri in tqdm(tmp_iri):
    min_type = g.V().has("iri",iri).next()
    closure = g.V(min_type).valueMap("closure").next()["closure"]
    onto_node_and_closure[iri] = {"node":min_type,"closure":closure}

# In[ ]:


rdf_df["top_ontology"] = rdf_df.apply(top_ontology,axis=1)


# In[ ]:


rdf_df.drop_duplicates(subset=["s","o"],inplace=True)


# In[ ]:
print('caricamento entità')

batch_dim = 100
i = 0
add_n = None
add_n_str = ""
for idx,x in tqdm(rdf_df.drop_duplicates("s").iterrows(),total = rdf_df.drop_duplicates("s").shape[0]):
    nec = onto_node_and_closure[x["o"]]
    min_type = nec["node"]
    
    closure = nec["closure"]
    try:
        add_n = add_n.addV(x["top_ontology"])
        #add_n_str = add_n_str+".addV("+x["top_ontology"]+")"
        #add_n = g.addV(x["top_ontology"])
    except:
        add_n = g.addV(x["top_ontology"])
        #add_n_str = add_n_str+"g.addV("+x["top_ontology"]+")"
    add_n = add_n.property("label_vp",x["top_ontology"]).property("iri",x["s"]).property("group","all").property("level",0).property("owner","all")

    for c in closure:
        add_n = add_n.property("closure",c)
        #add_n_str = add_n_str+"add_n.property(\"closure\","+c+")"
    if not (pd.isna(x["label"]) or pd.isnull(x["label"])):
        add_n = add_n.property("name",x["label"])
        #add_n_str = add_n_str+"add_n.property(\"name\","+x["label"]+")"
    if not (pd.isna(x["comment"]) or pd.isnull(x["comment"])):
        add_n = add_n.property("comment",x["comment"])
        #add_n_str = add_n_str+"add_n.property(\"comment\","+x["comment"]+")"
    if not (pd.isna(x["lat"]) or pd.isnull(x["lat"])):
        add_n = add_n.property("lat",float(x["lat"]))
        #add_n_str = add_n_str+"add_n.property(\"lat\","+str(float(x["lat"]))+")"
    if not (pd.isna(x["lon"]) or pd.isnull(x["lon"])):
        add_n = add_n.property("lon",float(x["lon"]))
        #add_n_str = add_n_str+"add_n.property(\"lon\","+str(float(x["lon"]))+")"
    add_n = add_n.addE("rdf:type").to(min_type).property('label_ep', 'rdf:type').fold()
    #add_n_str = add_n_str+".addE(\"rdf:type\").to("+min_type+").property('label_ep', 'rdf:type').fold())"
    i += 1
    #print(str(i))
    if i % batch_dim == 0:
        if(add_n != None):
            #add_n_str = add_n_str+".fold().iterate()"
            #print(add_n_str)
            add_n.fold().iterate()
            
        add_n = None
        i = 0
if i != 0:
    if(add_n != None):
        #add_n_str = add_n_str+".fold().iterate()"
        #print(add_n_str)
        add_n.fold().iterate()
    add_n = None

# In[ ]:


batch_dim = 100
i = 0
add_n = None
for idx, x in tqdm(rdf_df[rdf_df.duplicated("s")].iterrows(), total=rdf_df[rdf_df.duplicated("s")].shape[0]):
    nec = onto_node_and_closure[x["o"]]
    min_type = nec["node"]
    closure = nec["closure"]
    node = g.V().has("iri", x["s"]).next()
    try:
        add_n = add_n.V(node).addE("rdf:type").to(min_type)
    except:
        add_n = g.V(node).addE("rdf:type").to(min_type)
    add_n = add_n.property("label_ep","rdf:type").property("group","all").property("level",0).property("owner","all")

    for c in closure:
        add_n = add_n.property("closure", c)

    i += 1
    if i % batch_dim == 0:
        if(add_n != None):
            add_n.iterate()
        add_n = None
        i = 0
if i != 0:
    if(add_n != None):
        add_n.iterate()
    add_n = None