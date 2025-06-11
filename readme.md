cách để chạy file :
-yêu cầu có docker destop
chạy cách lệnh sau :

1.docker-compose up

2.docker exec -it newfolder-spark-master-1 bash

3./opt/spark/bin/spark-submit   --master spark://spark-master:7077   --packages graphframes:graphframes:0.8.2-spark3.2-s_2.12   /opt/spark/personalized_pagerank.py