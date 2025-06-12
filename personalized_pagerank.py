from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, LongType, DoubleType
from pyspark.sql.functions import col
from graphframes import GraphFrame
from termcolor import colored

spark = SparkSession.builder \
    .appName("PersonalizedPageRank") \
    .master("spark://spark-master:7077") \
    .config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.2-s_2.12") \
    .config("spark.driver.memory", "1g") \
    .config("spark.executor.memory", "1g") \
    .getOrCreate()

vertex_schema = StructType([
    StructField("id", LongType(), False),
    StructField("pr", DoubleType(), False),
    StructField("is_source", LongType(), False)
])

edge_schema = StructType([
    StructField("src", LongType(), False),
    StructField("dst", LongType(), False)
])


vertices_data = [
    (1, 1.0, 1),  
    (2, 0.0, 0),  
    (3, 0.0, 0),  
    (4, 0.0, 0),  
    (5, 0.0, 0),  
    (6, 0.0, 0)   
]
vertices = spark.createDataFrame(vertices_data, vertex_schema)

edges_data = [
    (1, 2), (1, 3),
    (3, 1), (3, 2), (3, 5),
    (4, 5), (4, 6),  
    (5, 4), (5, 6),  
    (6, 4)   
]
edges = spark.createDataFrame(edges_data, edge_schema)


g = GraphFrame(vertices, edges)

damping_factor = 0.85
max_iterations = 10
tolerance = 0.0001

def personalized_page_rank(graph, source_id=1):
    prev_pr = graph.vertices.select("id", "pr").rdd
    
    for i in range(max_iterations):

        out_degrees = graph.outDegrees.withColumnRenamed("id", "src").withColumnRenamed("outDegree", "deg")

        messages = graph.edges \
            .join(graph.vertices, graph.edges.src == graph.vertices.id) \
            .join(out_degrees, "src") \
            .withColumn("contribution", col("pr") / col("deg")) \
            .groupBy("dst") \
            .agg({"contribution": "sum"}) \
            .withColumnRenamed("dst", "id") \
            .withColumnRenamed("sum(contribution)", "msg_sum")
        
        new_pr = graph.vertices.join(messages, "id", "left_outer") \
            .select(
                col("id"),
                col("is_source"),
                col("pr").alias("old_pr"),
                col("msg_sum").alias("msg_sum")
            ) \
            .na.fill({"msg_sum": 0}) \
            .withColumn("new_pr", 
                (1 - damping_factor) * col("is_source") + 
                damping_factor * col("msg_sum")
            )

        diff = new_pr.select(
            col("new_pr") - col("old_pr")
        ).rdd.map(lambda x: abs(x[0])).sum()
        
        if diff < tolerance:
            print(f"Converged after {i + 1} iterations with diff {diff}")
            break
        

        graph = GraphFrame(
            new_pr.select("id", "new_pr", "is_source").withColumnRenamed("new_pr", "pr"),
            graph.edges
        )
        prev_pr = new_pr.select("id", "new_pr").withColumnRenamed("new_pr", "pr").rdd
    

    result = graph.vertices.select("id", "pr").collect()
    print(colored("\n=== Personalized PageRank Results ===", "blue", attrs=["bold"]))
    for row in result:
        print(colored(f"Page {row['id']}: {row['pr']:.6f}", "green"))
    print(colored("\n=====================================", "blue", attrs=["bold"]))
    print()

    return graph


result_graph = personalized_page_rank(g)

spark.stop()