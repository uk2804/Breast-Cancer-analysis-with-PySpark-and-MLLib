from pyspark import SparkContext

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('classification').getOrCreate()



#data = spark.read.csv('data.csv', header='true', inferSchema='true')


data = spark.read.csv('/user/hdfs/Breast_Cancer_data.csv', header='true', inferSchema='true')
 


data = data.drop('id')

data = data.drop('_c32')

Cond_feat = ['radius_mean','texture_mean','perimeter_mean','area_mean','smoothness_mean','compactness_mean','concavity_mean','concave points_mean','symmetry_mean','fractal_dimension_mean','radius_se','texture_se','perimeter_se','area_se','smoothness_se','compactness_se','concavity_se','concave points_se','symmetry_se','fractal_dimension_se','radius_worst','texture_worst','perimeter_worst','area_worst','smoothness_worst','compactness_worst','concavity_worst','concave points_worst','symmetry_worst','fractal_dimension_worst']

dec_feat = ['diagnosis']

from pyspark.ml.feature import OneHotEncoder, StringIndexer

labelIndexer = StringIndexer(inputCol="diagnosis", outputCol="indexedLabel").fit(data)

from pyspark.ml.feature import VectorIndexer, VectorAssembler

assemblerAllFeatures = VectorAssembler(inputCols=Cond_feat, outputCol="features")

from pyspark.ml import Pipeline, PipelineModel

pipeline = Pipeline(stages=[labelIndexer, assemblerAllFeatures])

pipelineModel = pipeline.fit(data)

output = pipelineModel.transform(data)

output.limit(3).toPandas()

splits = output.randomSplit([0.8, 0.2])

data_train = splits[0]

data_test = splits[1]

data_train.head()

from pyspark.ml.classification import RandomForestClassifier

dt = RandomForestClassifier(labelCol="indexedLabel", featuresCol="features")

pipeline = Pipeline(stages=[dt])

model = pipeline.fit(data_train)

predictions = model.transform(data_test)

predictions.printSchema()

predictions.select("prediction","indexedLabel","features").show()

from pyspark.ml.evaluation import MulticlassClassificationEvaluator, BinaryClassificationEvaluator

evaluator = MulticlassClassificationEvaluator(labelCol="indexedLabel", predictionCol="prediction", metricName="accuracy")

accuracy = evaluator.evaluate(predictions)

print "Accuracy = %g" % (accuracy)

#accuracy.saveAsTextFile("/user/examples/out2")

print "Test Error = %g" % (1.0 - accuracy)

treeModel = model.stages[-1]

evaluator = BinaryClassificationEvaluator()

print evaluator.evaluate(model.transform(data_test), {evaluator.metricName: "areaUnderROC", evaluator.labelCol: "indexedLabel"})

print evaluator.evaluate(model.transform(data_test), {evaluator.metricName: "areaUnderPR", evaluator.labelCol: "indexedLabel"})

print treeModel