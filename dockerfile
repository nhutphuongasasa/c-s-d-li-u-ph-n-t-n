FROM openjdk:17-jdk-slim

RUN apt-get update && apt-get install -y curl python3 python3-pip procps && \
    rm -rf /var/lib/apt/lists/*

ENV SPARK_VERSION=3.5.3
ENV SPARK_HOME=/opt/spark
RUN curl -sL https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz -o /tmp/spark.tgz && \
    tar -xzf /tmp/spark.tgz -C /opt/ && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop3 ${SPARK_HOME} && \
    rm /tmp/spark.tgz

RUN pip3 install pyspark==${SPARK_VERSION} numpy termcolor graphframes

RUN curl -sL https://repos.spark-packages.org/graphframes/graphframes/0.8.2-spark3.2-s_2.12/graphframes-0.8.2-spark3.2-s_2.12.jar -o ${SPARK_HOME}/jars/graphframes-0.8.2-spark3.2-s_2.12.jar

COPY personalized_pagerank.py ${SPARK_HOME}/

ENV PATH=${PATH}:${SPARK_HOME}/bin:${SPARK_HOME}/sbin
ENV JAVA_HOME=/usr/local/openjdk-17
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

WORKDIR ${SPARK_HOME}