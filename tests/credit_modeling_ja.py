# SPSS Modeler Script for Credit Prediction Model

# Create a new stream
stream = modeler.script.stream()

# Define input file path
input_file = u"C:\\_onedrive\\OneDrive - IBM\\01code\\2026\\260226clembmcp\\spss-clemb-mcp\\tests\\tree_credit_ja.csv"

# Create Variable File node (CSV input)
varfilenode = stream.createAt("variablefile", u"信用データ", 100, 100)
varfilenode.setPropertyValue("full_filename", input_file)
varfilenode.setPropertyValue("encoding", "UTF-8")

# Create Type node to define field metadata
typenode = stream.createAt("type", u"フィールド定義", 250, 100)

# Link Variable File node to Type node
stream.link(varfilenode, typenode)

# Instantiate the Type node by running a temporary table
tempTable = stream.createAt("table", u"一時テーブル", 400, 100)
stream.link(typenode, tempTable)
tempTable.run(None)
stream.delete(tempTable)

# Set field properties in Type node
# 信用度 (Target) - Flag type (0.0/1.0)
typenode.setKeyedPropertyValue("direction", u"信用度", "Target")
typenode.setKeyedPropertyValue("type", u"信用度", "Flag")
typenode.setKeyedPropertyValue("values", u"信用度", [0.0, 1.0])

# 年齢 (Age) - Range type (Input)
typenode.setKeyedPropertyValue("direction", u"年齢", "Input")
typenode.setKeyedPropertyValue("type", u"年齢", "Range")

# 所得 (Income) - Set type (Input)
typenode.setKeyedPropertyValue("direction", u"所得", "Input")
typenode.setKeyedPropertyValue("type", u"所得", "Set")

# クレジットカード (Credit Card) - Set type (Input)
typenode.setKeyedPropertyValue("direction", u"クレジットカード", "Input")
typenode.setKeyedPropertyValue("type", u"クレジットカード", "Set")

# 教育 (Education) - Set type (Input)
typenode.setKeyedPropertyValue("direction", u"教育", "Input")
typenode.setKeyedPropertyValue("type", u"教育", "Set")

# 車ローン (Car Loan) - Set type (Input)
typenode.setKeyedPropertyValue("direction", u"車ローン", "Input")
typenode.setKeyedPropertyValue("type", u"車ローン", "Set")

# Create C5.0 model node
c50node = stream.createAt("c50", u"C5.0モデル", 400, 100)
c50node.setPropertyValue("use_partitioned_data", False)

# Link Type node to C5.0 node
stream.link(typenode, c50node)

# Run the C5.0 model to create model nugget
c50node.run([])

# Get all nodes in the stream
nodes = stream.getNodes()

# Find the model nugget (it will be created after running c50node)
model_nugget = None
for node in nodes:
    if node.getTypeName() == "c50model":
        model_nugget = node
        break

if model_nugget is not None:
    model_nugget.setPropertyValue("label", u"信用度予測モデル")

    # Create Analysis node to evaluate the model
    analysisnode = stream.createAt("analysis", u"モデル評価", 700, 100)
    stream.link(model_nugget, analysisnode)

    # Create Table output node
    tablenode = stream.createAt("table", u"予測結果", 850, 100)
    stream.link(model_nugget, tablenode)

# Save the stream
output_stream_path = u"C:\\_onedrive\\OneDrive - IBM\\01code\\2026\\260226clembmcp\\spss-clemb-mcp\\tests\\credit_model_stream.str"
session = modeler.script.session()
taskrunner = session.getTaskRunner()
taskrunner.saveStreamToFile(stream, output_stream_path)

print u"ストリームが正常に作成され、保存されました: " + output_stream_path

# Made with Bob
