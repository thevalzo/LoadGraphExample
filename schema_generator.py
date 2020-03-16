__ip__= "ws://localhost:8182/gremlin"
__file__= "init_utils/schema_generator/schema_acl.yml"




import yaml
from gremlin_python.driver import client
import logging
logging.basicConfig(level=logging.DEBUG)

def add_vertex_label(connection,label):
    logging.info("Adding vertex label: %s"%(label,))
    query = "mgmt = graph.openManagement();\
             mgmt.makeVertexLabel('%s').make();\
             mgmt.commit();"%(label,)
    connection.submit(query).next()
    
def add_edge_label(connection,label,cardinality):
    logging.info("Adding edge label: %s"%(label,))
    query = "mgmt = graph.openManagement();\
             mgmt.makeEdgeLabel('%s')\
             .multiplicity(%s).make();\
             mgmt.commit();"%(label, cardinality)
    connection.submit(query).next()

def add_property(connection, label, dictionary):
    logging.info("Adding property: %s"%(label,))
    query =  "mgmt = graph.openManagement();\
              mgmt.makePropertyKey('%s')\
                .dataType(%s)\
                .cardinality(%s)\
                .make();\
                mgmt.commit()"%(label,\
                                dictionary["type"],\
                                dictionary["cardinality"])
    connection.submit(query).next()
    
    
def add_index(connection, label, dictionary):
    add_key_query = "".join([".addKey(mgmt.getPropertyKey('%s'))"\
                            %(property_label)\
                            for property_label in dictionary["properties"]])
    query = "graph.tx().rollback();\
             mgmt = graph.openManagement();\
             mgmt.buildIndex('%s',%s)"%(label,dictionary["properties_type"])
    query += add_key_query
    if dictionary["unique"]:
        query += ".unique()"
    if dictionary["type"] == "composite":
        query += ".buildCompositeIndex()"
    elif dictionary["type"] == "mixed":
        query += ".buildMixedIndex('search')"
    else:
        raise Exception("type must be mixed or composite")
    query += ";\
                  mgmt.commit();"
    
    
    waiting_query = "ManagementSystem.awaitGraphIndexStatus(graph, '%s').call();true;"%(label,)
    
    reindex_query = "mgmt = graph.openManagement();\
                     mgmt.updateIndex(mgmt.getGraphIndex('%s'), SchemaAction.REINDEX).get();\
                     mgmt.commit();"%(label,)
    logging.info("Generating index: %s"%(label,)) 
    connection.submit(query).next()
    logging.info("Waiting for index generation of: %s"%(label,))
    connection.submit(waiting_query).next()
    logging.info("Data reindexing for index: %s"%(label,))
    connection.submit(reindex_query).next()
              
             
                            

if __name__ == "__main__":
    with open(__file__) as f:
        data = yaml.load(f.read())
    gc = client.Client(__ip__,"g")
    
#    for label in data["vertices"]:
#        add_vertex_label(gc,label)
        
#    for label, cardinality in data["edges"].items():
#    	add_edge_label(gc,label,cardinality)
    
#    for label, dictionary in data["properties"].items():
#        add_property(gc, label, dictionary)
        
    for label, dictionary in data["indices"].items():
        add_index(gc, label, dictionary)

        



